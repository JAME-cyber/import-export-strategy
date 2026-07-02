#!/usr/bin/env python3
"""
ImportExport Pro — Browser Scanner v2
Scraping Alibaba/1688 avec Fetcher (pas Stealthy = moins de blocage).
Extraction prix, titres, MOQ pour analyse de niche.

Usage:
  python3 browser-scanner.py --platform alibaba --query "portable air cooler"
  python3 browser-scanner.py --niche heat-wave        # Scan complet niche canicule
  python3 browser-scanner.py --url "https://..."
"""

import json, re, argparse, time
from pathlib import Path
from datetime import datetime
from scrapling import Fetcher

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# ========================================
# Niche prédéfinies
# ========================================
NICHES = {
    "heat-wave": {
        "name": "🌿 Niche Canicule Europe",
        "products": [
            ("evaporative air cooler portable", "Refroidisseur évaporatif"),
            ("misting fan outdoor commercial", "Brumisateur terrasse pro"),
            ("portable ice maker countertop", "Machine à glace portable"),
            ("outdoor misting system kit", "Kit brumisation terrasse"),
            ("solar fan camping outdoor portable", "Ventilateur solaire camping"),
            ("neck fan portable wearable USB", "Ventilateur cou portable"),
            ("cooling towel sport ice towel", "Serviette rafraîchissante"),
            ("portable fan handheld rechargeable", "Ventilateur portable USB"),
            ("swamp cooler 3 in 1 fan humidifier", "Refroidisseur 3-en-1"),
            ("misting line outdoor cooling system", "Ligne brumisation extérieure"),
            ("portable air conditioner mobile", "Climatiseur mobile"),
            ("ceiling fan portable battery operated", "Ventilateur plafond batterie"),
            ("ice pack gel reusable cooler", "Bloc de glace gel"),
            ("outdoor umbrella misting fan", "Parasol brumisateur"),
            ("portable evaporative cooler battery", "Refroidisseur evaporatif batterie"),
        ],
    },
}

def scan_alibaba(query: str, limit: int = 20) -> dict:
    """Scan Alibaba.com via Fetcher (non-headless)."""
    url = f"https://www.alibaba.com/trade/search?SearchText={query.replace(' ', '+')}"
    
    try:
        page = Fetcher().get(url)
    except Exception as e:
        return {"error": str(e)[:100], "query": query}
    
    # Extraction
    prices_usd = []
    products = []
    
    # Chercher tous les éléments avec prix
    for el in page.css("[class*='price'], [class*='Price']"):
        text = el.text.strip()
        nums = re.findall(r'[\d.]+', text)
        for n in nums:
            val = float(n)
            if 0.5 < val < 10000:  # Filtrer prix aberrants
                prices_usd.append(val)
    
    # Chercher titres produits
    seen_titles = set()
    for el in page.css("h2, h3, [class*='title'], [class*='Title']"):
        text = el.text.strip()
        if 20 < len(text) < 200 and text not in seen_titles:
            if not any(kw in text.lower() for kw in ['alibaba', 'sign in', 'join', 'ready to ship']):
                seen_titles.add(text)
                products.append(text)
    
    # MOQ
    moqs = []
    for el in page.css("[class*='min-order'], [class*='moq'], [class*='MinOrder']"):
        text = el.text.strip()
        if text:
            moqs.append(text)
    
    # Filtrer prix (garder zone raisonnable)
    if prices_usd:
        # Garder les 20 premiers prix uniques
        unique_prices = sorted(set(prices_usd))[:20]
    else:
        unique_prices = []
    
    return {
        "query": query,
        "url": url,
        "scanned_at": datetime.now().isoformat(),
        "num_products": len(seen_titles),
        "num_prices": len(unique_prices),
        "prices_usd": unique_prices[:15],
        "price_min": min(unique_prices) if unique_prices else None,
        "price_max": max(unique_prices) if unique_prices else None,
        "price_avg": round(sum(unique_prices)/len(unique_prices), 2) if unique_prices else None,
        "sample_products": list(seen_titles)[:5],
        "moqs": moqs[:3],
    }

def enrich_with_cost(price_usd: float) -> dict:
    """Calculer le coût complet import depuis prix FOB USD."""
    if not price_usd:
        return {}
    
    eur_rate = 0.92  # Approx USD→EUR
    price_eur_fob = price_usd * eur_rate
    cost_multiplier = 1.5  # Transport + douane + TVA
    
    cost_complete = price_eur_fob * cost_multiplier
    marketing_pct = 0.20  # 20% du prix de vente
    returns_pct = 0.08
    
    return {
        "price_usd": price_usd,
        "price_eur_fob": round(price_eur_fob, 2),
        "cost_complete_eur": round(cost_complete, 2),
        "price_vente_min_b2b": round(cost_complete * 1.5, 2),  # Marge 33% B2B
        "price_vente_min_b2c": round(cost_complete * 2.2, 2),  # Marge 55% B2C
        "marge_nette_b2b_pct": round((1 - (cost_complete + cost_complete*marketing_pct*0.5 + cost_complete*returns_pct) / (cost_complete*1.5)) * 100, 1),
        "marge_nette_b2c_pct": round((1 - (cost_complete + cost_complete*marketing_pct + cost_complete*returns_pct) / (cost_complete*2.2)) * 100, 1),
    }

def scan_niche(niche_key: str) -> dict:
    """Scan complet d'une niche prédéfinie."""
    niche = NICHES.get(niche_key)
    if not niche:
        print(f"❌ Niche inconnue: {niche_key}")
        print(f"   Disponibles: {list(NICHES.keys())}")
        return {}
    
    print(f"\n{'='*60}")
    print(f"🔍 NICHE: {niche['name']}")
    print(f"{'='*60}")
    
    results = []
    
    for query_en, name_fr in niche["products"]:
        print(f"\n  📦 {name_fr} / {query_en}")
        
        data = scan_alibaba(query_en)
        
        if data.get("price_min"):
            cost = enrich_with_cost(data["price_min"])
            data["cost_analysis"] = cost
            print(f"     💰 Usine: ${data['price_min']:.1f}-${data['price_max']:.1f}")
            print(f"     🇪🇺 Coût complet: €{cost['cost_complete_eur']:.0f}")
            print(f"     📊 Vente B2B: €{cost['price_vente_min_b2b']:.0f} | B2C: €{cost['price_vente_min_b2c']:.0f}")
            print(f"     📈 Marge nette B2B: {cost['marge_nette_b2b_pct']}% | B2C: {cost['marge_nette_b2c_pct']}%")
        else:
            print(f"     ❌ Pas de prix trouvés")
        
        results.append({
            "name_fr": name_fr,
            **data,
        })
        
        time.sleep(1)
    
    # Trier par potentiel (prix trouvés + marge)
    scored = []
    for r in results:
        score = 0
        if r.get("num_prices", 0) > 0:
            score += 30
        if r.get("cost_analysis", {}).get("marge_nette_b2b_pct", 0) > 25:
            score += 40
        if r.get("num_products", 0) > 3:
            score += 20
        score += min(r.get("num_prices", 0) * 2, 10)
        r["score"] = score
        scored.append(r)
    
    scored.sort(key=lambda x: x.get("score", 0), reverse=True)
    
    # Rapport final
    print(f"\n{'='*60}")
    print(f"📊 CLASSEMENT NICHE: {niche['name']}")
    print(f"{'='*60}")
    
    for i, r in enumerate(scored):
        if r.get("price_min"):
            cost = r.get("cost_analysis", {})
            print(f"\n  {i+1}. {r['name_fr']} (score: {r['score']})")
            print(f"     Usine: ${r['price_min']:.1f}-${r['price_max']:.1f} → Coût: €{cost.get('cost_complete_eur', '?')}")
            print(f"     Vente B2B: €{cost.get('price_vente_min_b2b', '?')} | B2C: €{cost.get('price_vente_min_b2c', '?')}")
            print(f"     Marge nette B2B: {cost.get('marge_nette_b2b_pct', '?')}%")
            print(f"     ⚠️ Ces marges sont BRUTES → nétte après marketing: {max(cost.get('marge_nette_b2b_pct', 0)-10, 5)}%")
    
    # Sauvegarder
    output = DATA_DIR / f"niche-{niche_key}-results.json"
    with open(output, 'w', encoding='utf-8') as f:
        json.dump({
            "niche": niche_key,
            "name": niche["name"],
            "timestamp": datetime.now().isoformat(),
            "anti_bias_warning": "Prix FOB usine. Coût complet = ×1.5. Marges nettes réalistes = 20-40% après marketing+retours.",
            "results": scored,
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Résultats: {output}")
    return scored

def main():
    parser = argparse.ArgumentParser(description="ImportExport Pro — Browser Scanner v2")
    parser.add_argument("--platform", choices=["alibaba", "1688"], default="alibaba")
    parser.add_argument("--query", type=str)
    parser.add_argument("--niche", type=str, help="Niche prédéfinie (heat-wave)")
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--url", type=str)
    parser.add_argument("--output", type=str, default=None)
    
    args = parser.parse_args()
    
    if args.niche:
        scan_niche(args.niche)
    elif args.query:
        print(f"🔍 Scanning {args.platform}: {args.query}")
        data = scan_alibaba(args.query, args.limit)
        
        print(f"\n📋 Résultats:")
        if data.get("price_min"):
            cost = enrich_with_cost(data["price_min"])
            print(f"  Prix usine: ${data['price_min']:.1f} - ${data['price_max']:.1f}")
            print(f"  Coût complet EU: €{cost['cost_complete_eur']:.0f}")
            print(f"  Prix vente B2B: €{cost['price_vente_min_b2b']:.0f}")
            print(f"  Prix vente B2C: €{cost['price_vente_min_b2c']:.0f}")
            print(f"  ⚠️ Anti-biais: Marge nette RÉELLE après marketing = ~{cost['marge_nette_b2b_pct']-10}%")
        
        for p in data.get("sample_products", []):
            print(f"  📌 {p[:100]}")
        
        output = Path(args.output) if args.output else DATA_DIR / f"scan-{args.query[:20].replace(' ','_')}.json"
        output.parent.mkdir(parents=True, exist_ok=True)
        with open(output, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"\n💾 Sauvegardé: {output}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
