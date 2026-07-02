#!/usr/bin/env python3
"""
ImportExport Pro — Price Monitor
Surveille les prix sur Alibaba/1688 et alerte sur les changements.
Reproduit le "scheduled task" d'Accio Work.

Usage:
  python3 price-monitor.py --add "climatiseur portatif" --platform alibaba
  python3 price-monitor.py --run                  # Scan tous les produits enregistrés
  python3 price-monitor.py --report               # Rapport des évolutions de prix
  python3 price-monitor.py --history "climatiseur" # Historique prix d'un produit
"""

import json
import argparse
from pathlib import Path
from datetime import datetime

DATA_DIR = Path(__file__).parent.parent / "data" / "prix"
DATA_DIR.mkdir(parents=True, exist_ok=True)

WATCHLIST_FILE = DATA_DIR / "watchlist.json"
HISTORY_FILE = DATA_DIR / "price-history.json"

def load_watchlist() -> list:
    if WATCHLIST_FILE.exists():
        return json.loads(WATCHLIST_FILE.read_text(encoding='utf-8'))
    return []

def save_watchlist(watchlist: list):
    WATCHLIST_FILE.write_text(json.dumps(watchlist, indent=2, ensure_ascii=False), encoding='utf-8')

def load_history() -> dict:
    if HISTORY_FILE.exists():
        return json.loads(HISTORY_FILE.read_text(encoding='utf-8'))
    return {}

def save_history(history: dict):
    HISTORY_FILE.write_text(json.dumps(history, indent=2, ensure_ascii=False), encoding='utf-8')

def add_product(query: str, platform: str, target_price_eur: float = None):
    """Ajouter un produit à surveiller."""
    watchlist = load_watchlist()
    
    product = {
        "id": f"p{len(watchlist)+1:03d}",
        "query": query,
        "platform": platform,
        "target_price_eur": target_price_eur,
        "added_at": datetime.now().isoformat(),
        "last_scan": None,
        "last_price": None,
        "alert": False,
    }
    
    watchlist.append(product)
    save_watchlist(watchlist)
    print(f"✅ Produit ajouté à la watchlist: {query} ({platform})")
    if target_price_eur:
        print(f"   ⚠️ Prix cible: {target_price_eur}€ (coût complet, pas FOB)")

def run_scan():
    """Scanner tous les produits de la watchlist."""
    from scrapling import StealthyFetcher
    
    watchlist = load_watchlist()
    history = load_history()
    
    if not watchlist:
        print("📋 Watchlist vide. Ajoutez des produits avec --add")
        return
    
    print(f"🔍 Scan de {len(watchlist)} produit(s)...")
    
    for product in watchlist:
        query = product["query"]
        platform = product["platform"]
        print(f"\n  📦 {query} ({platform})")
        
        try:
            if platform == "alibaba":
                url = f"https://www.alibaba.com/trade/search?SearchText={query.replace(' ', '+')}"
            else:
                url = f"https://s.1688.com/selloffer/offer_search.htm?keywords={query}"
            
            page = StealthyFetcher.fetch(url)
            
            # Extraire premiers prix trouvés
            price_els = page.css('[class*="price"], [class*="Price"]')
            prices = []
            for p in price_els[:5]:
                price_text = p.text.strip()
                # Nettoyer le prix
                import re
                numbers = re.findall(r'[\d.]+', price_text)
                if numbers:
                    prices.append(float(numbers[0]))
            
            if prices:
                avg_price = sum(prices) / len(prices)
                min_price = min(prices)
                
                print(f"     💰 Prix trouvés: {prices}")
                print(f"     📊 Moyenne: {avg_price:.2f} | Min: {min_price:.2f}")
                
                # Convertir ¥ en € si 1688
                if platform == "1688":
                    avg_eur = avg_price * 0.13
                    min_eur = min_price * 0.13
                    print(f"     🇪🇺 Estimé: Moy {avg_eur:.2f}€ | Min {min_eur:.2f}€ (×0.13)")
                    print(f"     ⚠️ Anti-biais: Coût complet estimé ×1.5 = {min_eur*1.5:.2f}€ à {avg_eur*1.5:.2f}€")
                
                # Mettre à jour watchlist
                product["last_scan"] = datetime.now().isoformat()
                product["last_price"] = min_price
                
                # Vérifier alerte
                if product.get("target_price_eur") and platform == "alibaba":
                    if min_price <= product["target_price_eur"]:
                        product["alert"] = True
                        print(f"     🔔 ALERTE: Prix {min_price}€ ≤ cible {product['target_price_eur']}€!")
                
                # Sauvegarder historique
                key = product["id"]
                if key not in history:
                    history[key] = {"query": query, "platform": platform, "entries": []}
                history[key]["entries"].append({
                    "date": datetime.now().isoformat(),
                    "avg_price": avg_price,
                    "min_price": min_price,
                    "prices": prices,
                })
                
            else:
                print(f"     ❌ Aucun prix trouvé")
                
        except Exception as e:
            print(f"     ❌ Erreur: {e}")
    
    save_watchlist(watchlist)
    save_history(history)
    print(f"\n✅ Scan terminé. Historique mis à jour.")

def show_report():
    """Rapport des évolutions de prix."""
    watchlist = load_watchlist()
    history = load_history()
    
    if not history:
        print("📋 Aucun historique. Lancez --run d'abord.")
        return
    
    print("📊 RAPPORT D'ÉVOLUTION DES PRIX")
    print("=" * 50)
    
    for product_id, data in history.items():
        entries = data["entries"]
        if len(entries) < 2:
            continue
        
        first = entries[0]
        last = entries[-1]
        change = ((last["min_price"] - first["min_price"]) / first["min_price"]) * 100
        
        icon = "📈" if change > 0 else "📉" if change < 0 else "➡️"
        
        print(f"\n  {icon} {data['query']} ({data['platform']})")
        print(f"     Premier scan: {first['min_price']:.2f} ({first['date'][:10]})")
        print(f"     Dernier scan: {last['min_price']:.2f} ({last['date'][:10]})")
        print(f"     Évolution: {change:+.1f}%")
        if abs(change) > 10:
            print(f"     ⚠️ Mouvement significatif détecté!")

def show_history(query: str):
    """Historique détaillé d'un produit."""
    history = load_history()
    
    for product_id, data in history.items():
        if query.lower() in data["query"].lower():
            print(f"📋 Historique: {data['query']} ({data['platform']})")
            print("-" * 40)
            for entry in data["entries"]:
                date = entry["date"][:16]
                print(f"  {date} | Min: {entry['min_price']:.2f} | Moy: {entry['avg_price']:.2f}")

def main():
    parser = argparse.ArgumentParser(description="ImportExport Pro — Price Monitor")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--add", nargs=2, metavar=("QUERY", "PLATFORM"), help="Ajouter produit à surveiller")
    group.add_argument("--run", action="store_true", help="Scanner tous les produits")
    group.add_argument("--report", action="store_true", help="Rapport évolutions prix")
    group.add_argument("--history", type=str, help="Historique d'un produit")
    group.add_argument("--list", action="store_true", help="Lister watchlist")
    
    parser.add_argument("--target", type=float, help="Prix cible en € (coût complet)")
    
    args = parser.parse_args()
    
    if args.add:
        add_product(args.add[0], args.add[1], args.target)
    elif args.run:
        run_scan()
    elif args.report:
        show_report()
    elif args.history:
        show_history(args.history)
    elif args.list:
        wl = load_watchlist()
        if not wl:
            print("📋 Watchlist vide.")
        for p in wl:
            status = f"💰 {p['last_price']}" if p.get('last_price') else "⏳ Pas encore scanné"
            alert = " 🔔 ALERTE!" if p.get('alert') else ""
            print(f"  [{p['id']}] {p['query']} ({p['platform']}) — {status}{alert}")

if __name__ == "__main__":
    main()
