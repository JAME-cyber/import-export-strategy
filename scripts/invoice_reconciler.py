#!/usr/bin/env python3
"""
Invoice Reconciler — ImportExport Pro
Vérifie automatiquement les factures d'agent contre les commandes Shopify et la grille COGs.

Inspiré du podcast Zezinho Ecom × Antoine (juil 2026):
  "J'ai perdu 70K€ en ne vérifiant pas les factures de mes agents"

Le process manuel recommandé dans le podcast:
  1. Export CSV des commandes Shopify
  2. Facture détaillée de l'agent
  3. Grille COGs (prix produit + shipping par SKU)
  → Comparaison ligne par ligne

Ce script automatise les étapes 1-3.

Usage:
  python3 invoice_reconciler.py reconcile \
    --orders data/reconciliation/sample_orders.csv \
    --cogs data/reconciliation/cogs_grid.json \
    --invoice data/reconciliation/sample_invoice.csv \
    --output data/reconciliation/report.html

  python3 invoice_reconciler.py demo \
    --scenarios all \
    --output data/reconciliation/

  python3 invoice_reconciler.py demo \
    --scenarios overcharge \
    --output data/reconciliation/
"""

import csv
import json
import argparse
import hashlib
import re
import sys
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from typing import Optional


# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class OrderItem:
    sku: str
    product_name: str
    quantity: int
    unit_price: float  # prix de vente


@dataclass
class ShopifyOrder:
    order_id: str
    date: str
    customer_email: str
    shipping_country: str
    items: list  # list[OrderItem]
    total: float  # total payé par le client


@dataclass
class InvoiceLine:
    """Une ligne de facture d'agent — idéalement une par commande."""
    order_ref: str       # ref commande côté agent
    shopify_id: str      # matching vers Shopify (peut être vide)
    sku: str
    product_name: str
    quantity: int
    unit_cogs: float     # prix facturé par l'agent (produit + shipping)
    line_total: float
    notes: str = ""


@dataclass
class CogsEntry:
    sku: str
    product_name: str
    product_cost: float
    shipping_cost: float
    shipping_cost_by_country: dict = field(default_factory=dict)  # {country: cost}


@dataclass
class Discrepancy:
    severity: str       # CRITICAL, WARNING, INFO
    category: str       # MISSING_INVOICE, EXTRA_INVOICE, PRICE_MISMATCH, QUANTITY_MISMATCH, etc.
    order_id: str
    sku: str
    description: str
    expected_amount: float
    actual_amount: float
    delta: float        # actual - expected (positif = on a trop payé)


@dataclass
class ReconciliationResult:
    run_date: str
    period_start: str
    period_end: str
    total_orders_shopify: int
    total_lines_invoice: int
    total_expected_cogs: float
    total_invoiced_cogs: float
    total_delta: float
    discrepancies: list  # list[Discrepancy]
    orders_matched: int
    orders_missing_from_invoice: int
    lines_extra_in_invoice: int


# ============================================================================
# PARSERS
# ============================================================================

def parse_shopify_csv(filepath: str) -> list[ShopifyOrder]:
    """Parse un export CSV Shopify (format simplifié)."""
    orders = []
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Supporte plusieurs items par commande (séparés par ;)
            skus = row.get('sku', '').split(';')
            names = row.get('product_name', '').split(';')
            qtys = row.get('quantity', '').split(';')
            prices = row.get('unit_price', '').split(';')

            items = []
            for i in range(len(skus)):
                if skus[i].strip():
                    items.append(OrderItem(
                        sku=skus[i].strip(),
                        product_name=names[i].strip() if i < len(names) else '',
                        quantity=int(qtys[i]) if i < len(qtys) and qtys[i].strip() else 1,
                        unit_price=float(prices[i]) if i < len(prices) and prices[i].strip() else 0,
                    ))

            orders.append(ShopifyOrder(
                order_id=row['order_id'],
                date=row.get('date', ''),
                customer_email=row.get('customer_email', ''),
                shipping_country=row.get('shipping_country', 'FR'),
                items=items,
                total=float(row.get('total', 0)),
            ))
    return orders


def parse_invoice_csv(filepath: str) -> list[InvoiceLine]:
    """Parse la facture de l'agent."""
    lines = []
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            lines.append(InvoiceLine(
                order_ref=row.get('order_ref', ''),
                shopify_id=row.get('shopify_id', ''),
                sku=row['sku'],
                product_name=row.get('product_name', ''),
                quantity=int(row.get('quantity', 1)),
                unit_cogs=float(row.get('unit_cogs', 0)),
                line_total=float(row.get('line_total', 0)),
                notes=row.get('notes', ''),
            ))
    return lines


def load_cogs_grid(filepath: str) -> dict[str, CogsEntry]:
    """Charge la grille COGs depuis JSON."""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    grid = {}
    for item in data.get('cogs', []):
        entry = CogsEntry(
            sku=item['sku'],
            product_name=item['product_name'],
            product_cost=float(item['product_cost']),
            shipping_cost=float(item.get('shipping_cost', 0)),
            shipping_cost_by_country=item.get('shipping_cost_by_country', {}),
        )
        grid[entry.sku] = entry
    return grid


# ============================================================================
# RECONCILIATION ENGINE
# ============================================================================

def get_expected_cogs(cogs_entry: CogsEntry, country: str) -> float:
    """Calcule le COGs attendu pour un SKU vers un pays donné."""
    base = cogs_entry.product_cost + cogs_entry.shipping_cost
    # Override par pays si défini
    if country in cogs_entry.shipping_cost_by_country:
        base = cogs_entry.product_cost + cogs_entry.shipping_cost_by_country[country]
    return round(base, 2)


def reconcile(
    orders: list[ShopifyOrder],
    invoice_lines: list[InvoiceLine],
    cogs_grid: dict[str, CogsEntry],
    price_tolerance: float = 0.02,
) -> ReconciliationResult:
    """
    Reconciliation engine.
    Compare 3 sources et flag les écarts.
    """
    discrepancies = []

    # Index invoice by shopify_id + sku
    invoice_index: dict[str, list[InvoiceLine]] = defaultdict(list)
    for line in invoice_lines:
        key = f"{line.shopify_id}|{line.sku}" if line.shopify_id else f"NO_REF|{line.sku}"
        invoice_index[key].append(line)

    # Also index by order_ref (agent's ref) for fallback matching
    invoice_by_ref: dict[str, list[InvoiceLine]] = defaultdict(list)
    for line in invoice_lines:
        if line.order_ref:
            invoice_by_ref[line.order_ref].append(line)

    matched_invoice_lines = set()  # track which invoice lines we've consumed
    orders_matched = 0
    total_expected = 0.0
    total_invoiced = 0.0

    # --- PASS 1: Orders → Invoice matching ---
    for order in orders:
        order_matched = True
        for item in order.items:
            sku = item.sku
            qty = item.quantity
            country = order.shipping_country

            # Expected COGs
            if sku not in cogs_grid:
                discrepancies.append(Discrepancy(
                    severity="WARNING",
                    category="UNKNOWN_SKU",
                    order_id=order.order_id,
                    sku=sku,
                    description=f"SKU '{sku}' absent de la grille COGs — impossible de vérifier",
                    expected_amount=0,
                    actual_amount=0,
                    delta=0,
                ))
                order_matched = False
                continue

            expected_unit = get_expected_cogs(cogs_grid[sku], country)
            expected_total = expected_unit * qty
            total_expected += expected_total

            # Find matching invoice line(s)
            key = f"{order.order_id}|{sku}"
            inv_lines = invoice_index.get(key, [])

            if not inv_lines:
                # Try fuzzy match: same SKU, quantity, no shopify_id link
                inv_lines = [
                    l for l in invoice_lines
                    if l.sku == sku and l.quantity == qty
                    and id(l) not in matched_invoice_lines
                    and not l.shopify_id
                ]

            if not inv_lines:
                discrepancies.append(Discrepancy(
                    severity="CRITICAL",
                    category="MISSING_INVOICE",
                    order_id=order.order_id,
                    sku=sku,
                    description=f"Commande {order.order_id}: {qty}x {sku} ({cogs_grid[sku].product_name}) — absent de la facture agent",
                    expected_amount=expected_total,
                    actual_amount=0,
                    delta=-expected_total,
                ))
                order_matched = False
                continue

            # Match found — verify pricing
            inv_line = inv_lines[0]
            matched_invoice_lines.add(id(inv_line))

            actual_total = inv_line.line_total if inv_line.line_total else inv_line.unit_cogs * inv_line.quantity
            total_invoiced += actual_total
            price_diff = actual_total - expected_total

            if abs(price_diff) > price_tolerance:
                severity = "CRITICAL" if abs(price_diff) > 2.0 else "WARNING"
                direction = "SURFACTURATION" if price_diff > 0 else "SOUSFACTURATION"
                discrepancies.append(Discrepancy(
                    severity=severity,
                    category="PRICE_MISMATCH",
                    order_id=order.order_id,
                    sku=sku,
                    description=(
                        f"{order.order_id}: {qty}x {sku} → "
                        f"Attendu {expected_total:.2f}€ ({expected_unit:.2f}€/u) | "
                        f"Facturé {actual_total:.2f}€ ({inv_line.unit_cogs:.2f}€/u) | "
                        f"Δ {price_diff:+.2f}€ ({direction})"
                    ),
                    expected_amount=expected_total,
                    actual_amount=actual_total,
                    delta=price_diff,
                ))

            # Check quantity mismatch
            if inv_line.quantity != qty:
                discrepancies.append(Discrepancy(
                    severity="WARNING",
                    category="QUANTITY_MISMATCH",
                    order_id=order.order_id,
                    sku=sku,
                    description=(
                        f"{order.order_id}: Qté Shopify={qty} vs Qté facture={inv_line.quantity}"
                    ),
                    expected_amount=qty,
                    actual_amount=inv_line.quantity,
                    delta=inv_line.quantity - qty,
                ))

        if order_matched:
            orders_matched += 1

    # --- PASS 2: Extra invoice lines (not matched to any Shopify order) ---
    orders_missing = sum(1 for d in discrepancies if d.category == "MISSING_INVOICE")
    extra_lines = 0
    for i, line in enumerate(invoice_lines):
        if id(line) not in matched_invoice_lines:
            extra_lines += 1
            total_invoiced += line.line_total
            discrepancies.append(Discrepancy(
                severity="WARNING",
                category="EXTRA_INVOICE",
                order_id="—",
                sku=line.sku,
                description=(
                    f"Ligne facture sans commande Shopify correspondante: "
                    f"{line.quantity}x {line.sku} @ {line.unit_cogs:.2f}€ "
                    f"(ref agent: {line.order_ref})"
                ),
                expected_amount=0,
                actual_amount=line.line_total,
                delta=line.line_total,
            ))

    total_delta = total_invoiced - total_expected

    return ReconciliationResult(
        run_date=datetime.now().isoformat(timespec='seconds'),
        period_start=orders[0].date if orders else "",
        period_end=orders[-1].date if orders else "",
        total_orders_shopify=len(orders),
        total_lines_invoice=len(invoice_lines),
        total_expected_cogs=round(total_expected, 2),
        total_invoiced_cogs=round(total_invoiced, 2),
        total_delta=round(total_delta, 2),
        discrepancies=discrepancies,
        orders_matched=orders_matched,
        orders_missing_from_invoice=orders_missing,
        lines_extra_in_invoice=extra_lines,
    )


# ============================================================================
# HTML REPORT GENERATOR
# ============================================================================

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Audit Factures Agent — {run_date}</title>
<style>
  :root {{
    --bg: #0f1117;
    --card: #1a1d28;
    --border: #2a2d3a;
    --text: #e4e6eb;
    --muted: #8b8fa3;
    --critical: #ef4444;
    --warning: #f59e0b;
    --info: #3b82f6;
    --success: #22c55e;
    --accent: #8b5cf6;
  }}
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.6;
    padding: 2rem;
    max-width: 1100px;
    margin: 0 auto;
  }}
  header {{
    text-align: center;
    margin-bottom: 2rem;
    padding-bottom: 1.5rem;
    border-bottom: 1px solid var(--border);
  }}
  header h1 {{
    font-size: 1.8rem;
    background: linear-gradient(135deg, var(--accent), #ec4899);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }}
  header .subtitle {{ color: var(--muted); font-size: 0.9rem; margin-top: 0.5rem; }}

  .summary-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 1rem;
    margin-bottom: 2rem;
  }}
  .stat-card {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.2rem;
    text-align: center;
  }}
  .stat-card .label {{ font-size: 0.75rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.05em; }}
  .stat-card .value {{ font-size: 1.8rem; font-weight: 700; margin-top: 0.3rem; }}
  .stat-card .delta {{ font-size: 0.85rem; margin-top: 0.2rem; }}
  .stat-card.alert .value {{ color: var(--critical); }}
  .stat-card.warning .value {{ color: var(--warning); }}
  .stat-card.ok .value {{ color: var(--success); }}

  .delta-bar {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 2rem;
  }}
  .delta-bar .left {{ display: flex; flex-direction: column; }}
  .delta-bar .amount {{
    font-size: 2.5rem;
    font-weight: 800;
  }}
  .delta-bar.overcharge .amount {{ color: var(--critical); }}
  .delta-bar.undercharge .amount {{ color: var(--info); }}
  .delta-bar.ok .amount {{ color: var(--success); }}
  .delta-bar .label {{ color: var(--muted); font-size: 0.9rem; }}

  table {{
    width: 100%;
    border-collapse: collapse;
    background: var(--card);
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid var(--border);
  }}
  th {{
    background: #21252e;
    padding: 0.8rem 1rem;
    text-align: left;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--muted);
    border-bottom: 1px solid var(--border);
  }}
  td {{
    padding: 0.8rem 1rem;
    border-bottom: 1px solid var(--border);
    font-size: 0.85rem;
  }}
  tr:last-child td {{ border-bottom: none; }}
  tr:hover {{ background: rgba(255,255,255,0.02); }}

  .badge {{
    display: inline-block;
    padding: 0.15rem 0.5rem;
    border-radius: 4px;
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.03em;
  }}
  .badge.critical {{ background: rgba(239,68,68,0.15); color: var(--critical); }}
  .badge.warning {{ background: rgba(245,158,11,0.15); color: var(--warning); }}
  .badge.info {{ background: rgba(59,130,246,0.15); color: var(--info); }}

  .cat-badge {{
    display: inline-block;
    padding: 0.15rem 0.5rem;
    border-radius: 4px;
    font-size: 0.7rem;
    font-weight: 500;
    background: rgba(139,92,246,0.12);
    color: var(--accent);
  }}

  .monospace {{ font-family: 'JetBrains Mono', 'Fira Code', monospace; font-size: 0.8rem; }}

  footer {{
    text-align: center;
    margin-top: 2rem;
    padding-top: 1rem;
    color: var(--muted);
    font-size: 0.8rem;
    border-top: 1px solid var(--border);
  }}

  .empty-state {{
    text-align: center;
    padding: 3rem;
    color: var(--muted);
  }}

  .section-title {{
    font-size: 1.1rem;
    margin-bottom: 0.8rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }}
  .section-title .count {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 0.1rem 0.6rem;
    font-size: 0.75rem;
    color: var(--muted);
  }}

  details summary {{
    cursor: pointer;
    padding: 0.5rem 0;
    color: var(--muted);
  }}
</style>
</head>
<body>

<header>
  <h1>🔍 Audit Factures Agent</h1>
  <p class="subtitle">ImportExport Pro · Réconciliation automatique · {run_date}</p>
</header>

<div class="summary-grid">
  <div class="stat-card">
    <div class="label">Commandes Shopify</div>
    <div class="value">{total_orders}</div>
  </div>
  <div class="stat-card">
    <div class="label">Lignes facture</div>
    <div class="value">{total_invoice_lines}</div>
  </div>
  <div class="stat-card">
    <div class="label">Commandes matchées</div>
    <div class="value {match_class}">{orders_matched}</div>
  </div>
  <div class="stat-card {alert_class}">
    <div class="label">Écarts détectés</div>
    <div class="value">{discrepancy_count}</div>
  </div>
</div>

<div class="delta-bar {delta_class}">
  <div class="left">
    <span class="label">Écart total (facturé vs attendu)</span>
    <span class="amount">{delta_sign}{abs_delta:.2f}€</span>
  </div>
  <div class="right" style="text-align:right">
    <div style="font-size:0.85rem;color:var(--muted)">
      Attendu: <strong style="color:var(--text)">{expected:.2f}€</strong><br>
      Facturé: <strong style="color:var(--text)">{invoiced:.2f}€</strong>
    </div>
  </div>
</div>

{discrepancy_table}

<footer>
  <p>Invoice Reconciler v1.0 · Généré le {run_date}</p>
  <p style="margin-top:0.3rem">Tolérance prix: ±{tolerance:.2f}€ · Période: {period}</p>
</footer>

</body>
</html>"""


def generate_html_report(result: ReconciliationResult, tolerance: float = 0.02) -> str:
    """Génère le rapport HTML."""

    # Sort: CRITICAL first, then WARNING, then INFO
    severity_order = {"CRITICAL": 0, "WARNING": 1, "INFO": 2}
    sorted_disc = sorted(result.discrepancies, key=lambda d: (severity_order.get(d.severity, 3), -abs(d.delta)))

    critical_count = sum(1 for d in result.discrepancies if d.severity == "CRITICAL")
    warning_count = sum(1 for d in result.discrepancies if d.severity == "WARNING")

    if not result.discrepancies:
        disc_table = """
<div class="empty-state">
  <h2>✅ Aucun écart détecté</h2>
  <p>Toutes les factures correspondent aux commandes et à la grille COGs.</p>
</div>"""
    else:
        rows = []
        for d in sorted_disc:
            rows.append(f"""
<tr>
  <td><span class="badge {d.severity.lower()}">{d.severity}</span></td>
  <td><span class="cat-badge">{d.category}</span></td>
  <td class="monospace">{d.order_id}</td>
  <td class="monospace">{d.sku}</td>
  <td>{d.description}</td>
  <td style="text-align:right;color:var(--muted)">{d.expected_amount:.2f}€</td>
  <td style="text-align:right;color:var(--muted)">{d.actual_amount:.2f}€</td>
  <td style="text-align:right;font-weight:600;color:{'var(--critical)' if d.delta > 0 else 'var(--info)' if d.delta < 0 else 'var(--muted)'}">
    {d.delta:+.2f}€
  </td>
</tr>""")

        disc_table = f"""
<div class="section-title">
  ⚠️ Écarts détectés
  <span class="count">{len(result.discrepancies)} ({critical_count} critiques, {warning_count} avertissements)</span>
</div>
<table>
<thead>
<tr>
  <th>Sévérité</th>
  <th>Type</th>
  <th>Commande</th>
  <th>SKU</th>
  <th>Description</th>
  <th style="text-align:right">Attendu</th>
  <th style="text-align:right">Facturé</th>
  <th style="text-align:right">Δ</th>
</tr>
</thead>
<tbody>
{''.join(rows)}
</tbody>
</table>"""

    delta = result.total_delta
    if abs(delta) < tolerance:
        delta_class = "ok"
        delta_sign = "±"
    elif delta > 0:
        delta_class = "overcharge"
        delta_sign = "+"
    else:
        delta_class = "undercharge"
        delta_sign = ""

    return HTML_TEMPLATE.format(
        run_date=result.run_date,
        total_orders=result.total_orders_shopify,
        total_invoice_lines=result.total_lines_invoice,
        orders_matched=f"{result.orders_matched}/{result.total_orders_shopify}",
        match_class="ok" if result.orders_matched == result.total_orders_shopify else "warning",
        alert_class="alert" if critical_count > 0 else "",
        discrepancy_count=len(result.discrepancies),
        delta_class=delta_class,
        delta_sign=delta_sign,
        abs_delta=abs(delta),
        expected=result.total_expected_cogs,
        invoiced=result.total_invoiced_cogs,
        discrepancy_table=disc_table,
        tolerance=tolerance,
        period=f"{result.period_start} → {result.period_end}",
    )


# ============================================================================
# DEMO DATA GENERATOR
# ============================================================================

DEMO_PRODUCTS = {
    "TSHIRT-BLK-M": {"name": "T-shirt Premium Noir M", "cost": 3.50, "ship": 4.50},
    "TSHIRT-WHT-L": {"name": "T-shirt Premium Blanc L", "cost": 3.50, "ship": 4.50},
    "HOODIE-GRY-XL": {"name": "Hoodie Gris XL", "cost": 8.20, "ship": 5.50},
    "JOGGER-BLK-L": {"name": "Jogging Noir L", "cost": 6.80, "ship": 5.00},
    "CAP-BLK-OS": {"name": "Casquette Noire", "cost": 2.20, "ship": 3.80},
    "SOCKS-5PK": {"name": "Lot 5 paires chaussettes", "cost": 1.80, "ship": 3.50},
    "WALLET-BRN": {"name": "Portefeuille Cuir Brun", "cost": 4.50, "ship": 4.00},
    "WATCH-BLK": {"name": "Montre Minimaliste Noire", "cost": 7.50, "ship": 5.50},
}

DEMO_COUNTRIES = ["FR", "BE", "DE", "ES", "IT", "NL"]


def generate_cogs_grid(filepath: str):
    """Génère la grille COGs JSON."""
    cogs_data = {
        "description": "Grille COGs de référence — prix négociés avec l'agent",
        "last_updated": datetime.now().strftime("%Y-%m-%d"),
        "currency": "EUR",
        "cogs": [
            {
                "sku": sku,
                "product_name": info["name"],
                "product_cost": info["cost"],
                "shipping_cost": info["ship"],
                "shipping_cost_by_country": {
                    "FR": info["ship"],
                    "BE": round(info["ship"] - 0.50, 2),
                    "DE": round(info["ship"] - 0.30, 2),
                    "ES": round(info["ship"] + 0.50, 2),
                    "IT": round(info["ship"] + 0.70, 2),
                    "NL": round(info["ship"] - 0.50, 2),
                }
            }
            for sku, info in DEMO_PRODUCTS.items()
        ]
    }
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(cogs_data, f, indent=2, ensure_ascii=False)
    return filepath


def generate_shopify_orders(
    filepath: str,
    num_orders: int = 80,
    start_date: datetime = None,
    error_scenario: str = "clean"
):
    """Génère des commandes Shopify simulées.
    Scenarios:
      clean: tout est correct
      overcharge: l'agent surfacture sur certains SKU
      missing: certaines commandes absentes de la facture
      bundle_errors: erreurs sur quantités bundle
      all: tous les scénarios mélangés
    """
    if start_date is None:
        start_date = datetime(2026, 7, 1)

    import random
    random.seed(42 if error_scenario == "clean" else 99)

    skus = list(DEMO_PRODUCTS.keys())
    orders = []

    for i in range(num_orders):
        date = start_date + timedelta(hours=i * 3 + random.randint(-1, 1))
        order_id = f"#10{i:04d}"
        country = random.choice(DEMO_COUNTRIES)

        # 70% single item, 30% multi-item (with distinct SKUs per order)
        num_items = 1 if random.random() < 0.7 else random.randint(2, 3)
        chosen_skus = random.sample(skus, min(num_items, len(skus)))
        items = []
        for sku in chosen_skus:
            qty = 1 if random.random() < 0.8 else random.randint(2, 4)
            price = round(DEMO_PRODUCTS[sku]["cost"] * random.uniform(2.8, 4.5), 2)
            items.append((sku, DEMO_PRODUCTS[sku]["name"], qty, price))

        total = round(sum(q * p for _, _, q, p in items), 2)
        orders.append({
            "order_id": order_id,
            "date": date.strftime("%Y-%m-%d %H:%M"),
            "customer_email": f"customer{i}@example.com",
            "shipping_country": country,
            "sku": ";".join(it[0] for it in items),
            "product_name": ";".join(it[1] for it in items),
            "quantity": ";".join(str(it[2]) for it in items),
            "unit_price": ";".join(f"{it[3]:.2f}" for it in items),
            "total": f"{total:.2f}",
        })

    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=[
            "order_id", "date", "customer_email", "shipping_country",
            "sku", "product_name", "quantity", "unit_price", "total"
        ])
        writer.writeheader()
        writer.writerows(orders)

    return filepath, orders


def generate_invoice_from_orders(
    filepath: str,
    orders: list,
    cogs_grid_path: str,
    error_scenario: str = "clean"
):
    """
    Génère la facture de l'agent à partir des commandes.
    Selon le scenario, injecte des erreurs.
    """
    with open(cogs_grid_path, 'r') as f:
        cogs = {c["sku"]: c for c in json.load(f)["cogs"]}

    import random
    random.seed(42 if error_scenario == "clean" else 99)

    invoice_lines = []
    corrupted_indices = set()

    # Determine which orders to corrupt
    if error_scenario in ("overcharge", "all"):
        # 15% of orders get overcharged by 1-3€ per unit
        num_corrupt = int(len(orders) * 0.15)
        corrupted_indices.update(random.sample(range(len(orders)), num_corrupt))

    skip_indices = set()
    if error_scenario in ("missing", "all"):
        # 8% of orders completely missing from invoice
        num_skip = int(len(orders) * 0.08)
        skip_indices.update(random.sample(range(len(orders)), num_skip))

    for idx, order in enumerate(orders):
        if idx in skip_indices:
            continue

        country = order["shipping_country"]
        skus = order["sku"].split(";")
        qtys = order["quantity"].split(";")

        for sku, qty_str in zip(skus, qtys):
            qty = int(qty_str)
            entry = cogs[sku]

            # Get expected shipping by country
            ship_cost = entry["shipping_cost_by_country"].get(country, entry["shipping_cost"])
            unit_cogs = round(entry["product_cost"] + ship_cost, 2)

            # Inject overcharge
            if idx in corrupted_indices:
                unit_cogs = round(unit_cogs + random.uniform(1.0, 3.0), 2)

            # Bundle quantity error
            if error_scenario in ("bundle_errors", "all") and random.random() < 0.05:
                qty = qty + random.randint(1, 2)  # agent bills more units

            line_total = round(unit_cogs * qty, 2)

            invoice_lines.append({
                "order_ref": order["order_id"],
                "shopify_id": order["order_id"],
                "sku": sku,
                "product_name": entry["product_name"],
                "quantity": qty,
                "unit_cogs": f"{unit_cogs:.2f}",
                "line_total": f"{line_total:.2f}",
                "notes": "",
            })

    # Extra lines (phantom charges)
    if error_scenario in ("missing", "all") and random.random() < 0.5:
        invoice_lines.append({
            "order_ref": "N/A",
            "shopify_id": "",
            "sku": "SOCKS-5PK",
            "product_name": "Lot 5 paires chaussettes",
            "quantity": 5,
            "unit_cogs": "5.30",
            "line_total": "26.50",
            "notes": "Batch补充",
        })

    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=[
            "order_ref", "shopify_id", "sku", "product_name",
            "quantity", "unit_cogs", "line_total", "notes"
        ])
        writer.writeheader()
        writer.writerows(invoice_lines)

    return filepath


# ============================================================================
# CLI
# ============================================================================

def cmd_reconcile(args):
    """Run reconciliation on provided files."""
    orders = parse_shopify_csv(args.orders)
    invoice = parse_invoice_csv(args.invoice)
    cogs = load_cogs_grid(args.cogs)

    result = reconcile(orders, invoice, cogs, price_tolerance=args.tolerance)

    # Generate HTML
    html = generate_html_report(result, tolerance=args.tolerance)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding='utf-8')

    # Console summary
    print(f"\n{'='*60}")
    print(f"  AUDIT FACTURES — {result.run_date}")
    print(f"{'='*60}")
    print(f"  Commandes Shopify:     {result.total_orders_shopify}")
    print(f"  Lignes facture agent:  {result.total_lines_invoice}")
    print(f"  Commandes matchées:    {result.orders_matched}/{result.total_orders_shopify}")
    print(f"  Manquantes (facture):  {result.orders_missing_from_invoice}")
    print(f"  Lignes excédentaires:  {result.lines_extra_in_invoice}")
    print(f"  COGs attendu:          {result.total_expected_cogs:.2f}€")
    print(f"  COGs facturé:          {result.total_invoiced_cogs:.2f}€")
    print(f"  Δ TOTAL:               {result.total_delta:+.2f}€")
    print(f"  Écarts détectés:       {len(result.discrepancies)}")
    print(f"{'='*60}")

    critical = [d for d in result.discrepancies if d.severity == "CRITICAL"]
    if critical:
        print(f"\n  ⚠️  {len(critical)} ÉCARTS CRITIQUES:")
        for d in critical[:5]:
            print(f"    [{d.category}] {d.description}")
            print(f"      Δ = {d.delta:+.2f}€")
        if len(critical) > 5:
            print(f"    ... et {len(critical) - 5} autres")

    print(f"\n  📄 Rapport: {output_path.absolute()}")
    print()

    return result


def cmd_demo(args):
    """Generate demo data + run reconciliation."""
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    data_dir = output_dir / "data"

    # 1. Generate COGs grid
    cogs_path = str(data_dir / "cogs_grid.json")
    generate_cogs_grid(cogs_path)
    print(f"  ✓ Grille COGs: {cogs_path}")

    scenarios = ["clean", "overcharge", "missing", "bundle_errors", "all"] \
        if args.scenarios == "all" else [args.scenarios]

    for scenario in scenarios:
        scenario_dir = output_dir / scenario
        data_s = scenario_dir / "data"
        data_s.mkdir(parents=True, exist_ok=True)

        # 2. Generate Shopify orders
        orders_path = str(data_s / "orders.csv")
        orders_path_gen, orders_data = generate_shopify_orders(
            orders_path, num_orders=args.num_orders, error_scenario=scenario
        )

        # 3. Generate agent invoice (with injected errors)
        invoice_path = str(data_s / "invoice.csv")
        generate_invoice_from_orders(
            invoice_path, orders_data, cogs_path, error_scenario=scenario
        )

        # 4. Run reconciliation
        orders = parse_shopify_csv(orders_path)
        invoice = parse_invoice_csv(invoice_path)
        cogs = load_cogs_grid(cogs_path)
        result = reconcile(orders, invoice, cogs)

        # 5. Generate HTML report
        html = generate_html_report(result)
        report_path = scenario_dir / "report.html"
        report_path.write_text(html, encoding='utf-8')

        print(f"\n  📊 Scénario: {scenario.upper()}")
        print(f"     Commandes: {result.total_orders_shopify} | "
              f"Facturé: {result.total_invoiced_cogs:.2f}€ | "
              f"Attendu: {result.total_expected_cogs:.2f}€ | "
              f"Δ: {result.total_delta:+.2f}€")
        print(f"     Écarts: {len(result.discrepancies)} "
              f"({sum(1 for d in result.discrepancies if d.severity == 'CRITICAL')} critiques)")
        print(f"     Rapport: {report_path.absolute()}")

    print(f"\n  Ouvre les rapports dans un navigateur pour voir le détail.")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Invoice Reconciler — audit automatique des factures d'agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # reconcile
    rec = subparsers.add_parser("reconcile", help="Lance la réconciliation sur des fichiers fournis")
    rec.add_argument("--orders", required=True, help="Export CSV Shopify")
    rec.add_argument("--cogs", required=True, help="Grille COGs JSON")
    rec.add_argument("--invoice", required=True, help="Facture agent CSV")
    rec.add_argument("--output", required=True, help="Fichier HTML de sortie")
    rec.add_argument("--tolerance", type=float, default=0.02, help="Tolérance de prix en € (défaut: 0.02)")
    rec.set_defaults(func=cmd_reconcile)

    # demo
    demo = subparsers.add_parser("demo", help="Génère données de démo + lance la réconciliation")
    demo.add_argument("--scenarios", default="all",
                      choices=["clean", "overcharge", "mode", "missing", "bundle_errors", "all"],
                      help="Scénario d'erreur à simuler")
    demo.add_argument("--output", default="reconciliation_demo",
                      help="Dossier de sortie")
    demo.add_argument("--num-orders", type=int, default=80, help="Nombre de commandes à générer")
    demo.set_defaults(func=cmd_demo)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
