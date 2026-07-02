#!/usr/bin/env python3
"""
ImportExport Pro — RFQ Generator
Génère des Request For Quote professionnels pour fournisseurs chinois.
Reproduit le feature "Sourcing & Négociation" d'Accio Work.

Usage:
  python3 rfq-generator.py --product "Climatiseur portatif" --quantity 200 --specs specs.json
  python3 rfq-generator.py --interactive     # Mode interactif
"""

import json
import argparse
from pathlib import Path
from datetime import datetime

OUTPUT_DIR = Path(__file__).parent.parent / "data" / "fournisseurs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def generate_rfq(
    product_name: str,
    quantity: int,
    specifications: dict = None,
    target_price: float = None,
    delivery_port: str = "Le Havre, France",
    incoterm: str = "FOB",
    company_name: str = "[Your Company]",
    contact_name: str = "[Your Name]",
    email: str = "[Your Email]",
    notes: str = "",
) -> str:
    """Génère un email RFQ professionnel."""
    
    today = datetime.now().strftime("%B %d, %Y")
    ref = f"RFQ-{datetime.now().strftime('%Y%m%d')}-{product_name[:10].replace(' ', '').upper()}"
    
    specs_text = ""
    if specifications:
        specs_text = "\nProduct Specifications:\n"
        for key, value in specifications.items():
            specs_text += f"  - {key}: {value}\n"
    
    price_text = ""
    if target_price:
        price_text = f"""
Target Price:
  Our target price is ${target_price:.2f} per unit ({incoterm}).
  Please provide your best price for the requested quantity.
"""
    
    rfq = f"""
Subject: {ref} — Request for Quotation: {product_name}

Dear Supplier,

{company_name} is looking for a reliable supplier for the following product. 
Please provide your best quotation.

REFERENCE: {ref}
DATE: {today}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PRODUCT: {product_name}
QUANTITY: {quantity} units (first order)
{specs_text}
{price_text}
REQUIREMENTS:
  - Incoterm: {incoterm}
  - Destination: {delivery_port}
  - Required certifications: CE, RoHS (please provide valid certificates)
  - Sample availability: YES / NO (circle one)
  - Sample price: $_______
  - Sample lead time: _______ days
  - Production lead time: _______ days
  - Payment terms: _______
  - Packaging: Standard export packaging (double corrugated cartons)

PLEASE PROVIDE:
  1. ✅ Unit price ({incoterm}) for {quantity} units
  2. ✅ Unit price for larger volume (500, 1000 units)
  3. ✅ Production lead time
  4. ✅ Sample availability and cost
  5. ✅ Valid CE and RoHS certificates (PDF)
  6. ✅ Product catalog / photos
  7. ✅ Company profile and export experience
  8. ✅ Trade Assurance availability on Alibaba.com

{f'ADDITIONAL NOTES:\n  {notes}' if notes else ''}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

We look forward to your quotation.

Best regards,
{contact_name}
{company_name}
{email}

---
⚠️ ANTI-FRAUD: We verify all certificates with independent labs (SGS/Bureau Veritas).
   Please ensure all documents are authentic.
"""
    return rfq

def interactive_mode():
    """Mode interactif pour générer une RFQ."""
    print("📝 ImportExport Pro — RFQ Generator (mode interactif)")
    print("=" * 50)
    
    product_name = input("\n📦 Nom du produit: ").strip()
    quantity = int(input("📦 Quantité souhaitée: ").strip())
    
    print("\n📋 Spécifications (laisser vide si aucune):")
    specs = {}
    spec_fields = [
        ("Matière/Material", "material"),
        ("Dimensions", "dimensions"),
        ("Couleur(s)", "colors"),
        ("Poids", "weight"),
        ("Capacité/Power", "capacity"),
        ("Certifications requises", "certifications"),
    ]
    
    for label, key in spec_fields:
        val = input(f"  {label}: ").strip()
        if val:
            specs[label] = val
    
    target_price = input("\n💰 Prix cible FOB par unité ($): ").strip()
    target_price = float(target_price) if target_price else None
    
    incoterm = input("🚢 Incoterm (FOB/CIF/DDP) [FOB]: ").strip() or "FOB"
    port = input("📍 Port de destination [Le Havre, France]: ").strip() or "Le Havre, France"
    
    company = input("\n🏢 Nom de votre société: ").strip() or "[Your Company]"
    contact = input("👤 Votre nom: ").strip() or "[Your Name]"
    email = input("📧 Votre email: ").strip() or "[Your Email]"
    
    notes = input("\n📝 Notes supplémentaires: ").strip()
    
    rfq = generate_rfq(
        product_name=product_name,
        quantity=quantity,
        specifications=specs if specs else None,
        target_price=target_price,
        delivery_port=port,
        incoterm=incoterm,
        company_name=company,
        contact_name=contact,
        email=email,
        notes=notes,
    )
    
    # Sauvegarder
    filename = f"RFQ-{datetime.now().strftime('%Y%m%d')}-{product_name[:15].replace(' ', '_')}.txt"
    filepath = OUTPUT_DIR / filename
    filepath.write_text(rfq, encoding='utf-8')
    
    print(f"\n{'='*50}")
    print(rfq)
    print(f"{'='*50}")
    print(f"\n💾 RFQ sauvegardée: {filepath}")
    
    # Anti-biais reminder
    print(f"\n⚠️ RAPPEL ANTI-BAIS:")
    print(f"  - Demandez TOUJOURS les certificats CE/RoHS en PDF")
    print(f"  - 90% des certificats par défaut sont non conformes → vérifiez avec SGS")
    print(f"  - Le prix FOB n'est PAS le coût complet (×1.4-1.6 pour coût réel)")
    print(f"  - Comparez au moins 5 fournisseurs avant de commander")
    print(f"  - Ne payez JAMAIS 100% à l'avance (standard: 30/70)")

def main():
    parser = argparse.ArgumentParser(description="ImportExport Pro — RFQ Generator")
    parser.add_argument("--interactive", action="store_true", help="Mode interactif")
    parser.add_argument("--product", type=str, help="Nom du produit")
    parser.add_argument("--quantity", type=int, help="Quantité")
    parser.add_argument("--target-price", type=float, help="Prix cible FOB")
    parser.add_argument("--incoterm", type=str, default="FOB")
    parser.add_argument("--port", type=str, default="Le Havre, France")
    parser.add_argument("--specs", type=str, help="Fichier JSON de specs")
    parser.add_argument("--output", type=str)
    
    args = parser.parse_args()
    
    if args.interactive:
        interactive_mode()
    elif args.product and args.quantity:
        specs = None
        if args.specs:
            specs = json.loads(Path(args.specs).read_text())
        
        rfq = generate_rfq(
            product_name=args.product,
            quantity=args.quantity,
            specifications=specs,
            target_price=args.target_price,
            incoterm=args.incoterm,
            delivery_port=args.port,
        )
        
        print(rfq)
        
        filename = f"RFQ-{datetime.now().strftime('%Y%m%d')}-{args.product[:15].replace(' ', '_')}.txt"
        filepath = OUTPUT_DIR / filename
        filepath.write_text(rfq, encoding='utf-8')
        print(f"\n💾 Sauvegardé: {filepath}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
