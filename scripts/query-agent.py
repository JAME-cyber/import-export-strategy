#!/usr/bin/env python3
"""
ImportExport Pro — Agent Orchestrator v2
Route les requêtes vers l'agent spécialisé approprié
en injectant le module anti-biais dans chaque contexte.
"""

import os
import json
import yaml
from pathlib import Path
from datetime import datetime

# ============================================================
# Configuration
# ============================================================

BASE_DIR = Path(__file__).parent.parent
KB_DIR = BASE_DIR / "knowledge-base"
TRANSCRIPTS_DIR = KB_DIR / "transcripts"
SYNTHESIS_DIR = KB_DIR / "synthesis"
GUIDES_DIR = KB_DIR / "guides"
TEMPLATES_DIR = KB_DIR / "templates"
ANTI_BIAS_MODULE = BASE_DIR / "agents" / "COMMUN-ANTI-BAIS.md"

AGENTS = {
    "sourcing": {
        "name": "🏭 Sourcing Master v2",
        "path": BASE_DIR / "agents" / "sourcing-master",
        "synthesis": "01-SOURCING-ACHATS-CHINE.md",
        "anti_bias_level": "HIGH",
        "bias_note": "Source StartBusinessWorld vend 'Sourcing Pro' → prix FOB présentés comme coûts complets",
        "keywords": ["sourcing", "fournisseur", "1688", "alibaba", "taobao", "prix",
                     "usine", "chine", "acheter", "commander", "plateforme", "canton fair",
                     "échantillon", "qualité", "négocier", "MOQ"],
    },
    "logistique": {
        "name": "🚢 Logistique Pro v2",
        "path": BASE_DIR / "agents" / "logistique-pro",
        "synthesis": "02-LOGISTIQUE-TRANSPORT.md",
        "anti_bias_level": "LOW",
        "bias_note": "Source CargoFamily = NEUTRE (pas de formation vendue). Le plus fiable.",
        "keywords": ["transport", "container", "logistique", "douane", "fret", "maritime",
                     "aérien", "incoterm", "FOB", "CIF", "DDP", "EXW", "assurance",
                     "cargo", "expédition", "dédouanement", "transitaire"],
    },
    "legal": {
        "name": "⚖️ Legal & Fiscal v2",
        "path": BASE_DIR / "agents" / "legal-fiscal",
        "synthesis": "03-JURIDIQUE-FISCALITE.md",
        "anti_bias_level": "CRITICAL",
        "bias_note": "⚠️ CRITICAL: StartBusinessWorld vend création HK Ltd → '0% impôts' trompeur pour résident français",
        "keywords": ["juridique", "statut", "société", "impôt", "TVA", "fiscal", "taxe",
                     "SASU", "SAS", "micro", "hong kong", "marque", "déposer", "contrat",
                     "NDA", "NNN", "certification", "CE", "RoHS", "INPI"],
    },
    "market": {
        "name": "📊 Market Analyzer v2",
        "path": BASE_DIR / "agents" / "market-analyzer",
        "synthesis": "05-MARCHES-OPPORTUNITES.md",
        "anti_bias_level": "HIGH",
        "bias_note": "Marges YouTube gonflées (FOB uniquement). Marge nette réaliste = 20-40% (pas 300%).",
        "keywords": ["marché", "niche", "opportunité", "concurrence", "tendance", "marge",
                     "rentabilité", "produit", "secteur", "afrique", "europe", "analyser",
                     "potentiel", "croissance"],
    },
    "brand": {
        "name": "🎨 Brand Builder v2",
        "path": BASE_DIR / "agents" / "brand-builder",
        "synthesis": "04-MARQUES-BUSINESS-MODELS.md",
        "anti_bias_level": "HIGH",
        "bias_note": "SINOSOURCING + LineBorrajo + Sebastien vendent tous des formations → budgets et marges minimisés",
        "keywords": ["marque", "brand", "private label", "OEM", "ODM", "logo", "packaging",
                     "identité", "e-commerce", "shopify", "boutique", "lancer", "créer",
                     "mini-brand", "DTC"],
    },
}

# ============================================================
# Knowledge Base Functions
# ============================================================

def load_anti_bias() -> str:
    """Load the anti-bias module."""
    if ANTI_BIAS_MODULE.exists():
        return ANTI_BIAS_MODULE.read_text(encoding='utf-8')
    return "# ⚠️ Module anti-biais non trouvé\n"

def load_divergent_analysis() -> str:
    """Load the divergent analysis."""
    path = SYNTHESIS_DIR / "06-ANALYSE-DIVERGENTE.md"
    if path.exists():
        return path.read_text(encoding='utf-8')
    return ""

def load_synthesis(synthesis_file: str) -> str:
    path = SYNTHESIS_DIR / synthesis_file
    if path.exists():
        return path.read_text(encoding='utf-8')
    return ""

def load_guide(guide_name: str) -> str:
    path = GUIDES_DIR / guide_name
    if path.exists():
        return path.read_text(encoding='utf-8')
    return ""

def list_transcripts() -> list:
    transcripts = []
    for f in TRANSCRIPTS_DIR.glob("*.txt"):
        content = f.read_text(encoding='utf-8')
        lines = content.split('\n')
        title = lines[0].replace("# Title: ", "") if lines else "Unknown"
        channel = lines[1].replace("# Channel: ", "") if len(lines) > 1 else "Unknown"
        transcripts.append({
            "file": f.name,
            "title": title,
            "channel": channel,
            "size": len(content),
        })
    return transcripts

def search_transcripts(query: str, limit: int = 5) -> list:
    query_lower = query.lower()
    results = []
    for f in TRANSCRIPTS_DIR.glob("*.txt"):
        content = f.read_text(encoding='utf-8')
        score = sum(1 for word in query_lower.split() if word in content.lower())
        if score > 0:
            lines = content.split('\n')
            title = lines[0].replace("# Title: ", "") if lines else "Unknown"
            # Check source bias
            channel = lines[1].replace("# Channel: ", "") if len(lines) > 1 else "Unknown"
            bias_map = {
                "StartBusinessWorld": "⚠️ VEND FORMATION",
                "SINOSOURCING": "⚠️ VEND ACCOMPAGNEMENT",
                "Sebastien": "⚠️ VEND FORMATION",
                "CargoFamily": "✅ NEUTRE",
                "LineBorrajo": "⚠️ VEND MÉTHODE",
            }
            results.append({
                "file": f.name,
                "title": title,
                "channel": channel,
                "bias": bias_map.get(channel, "?"),
                "score": score,
                "size": len(content),
            })
    results.sort(key=lambda x: x['score'], reverse=True)
    return results[:limit]

# ============================================================
# Agent Router with Anti-Bias
# ============================================================

def detect_agent(query: str) -> str:
    query_lower = query.lower()
    scores = {}
    for agent_key, agent_info in AGENTS.items():
        score = sum(1 for kw in agent_info["keywords"] if kw.lower() in query_lower)
        scores[agent_key] = score
    best_agent = max(scores, key=scores.get)
    if scores[best_agent] == 0:
        return "market"
    return best_agent

def get_agent_context(agent_key: str) -> dict:
    """Get full context for an agent WITH anti-bias module."""
    agent = AGENTS[agent_key]
    
    agent_md = ""
    agent_file = agent["path"] / "AGENT.md"
    if agent_file.exists():
        agent_md = agent_file.read_text(encoding='utf-8')
    
    return {
        "agent_name": agent["name"],
        "anti_bias_level": agent["anti_bias_level"],
        "bias_note": agent["bias_note"],
        "agent_config": agent_md,
        "anti_bias_module": load_anti_bias(),
        "divergent_analysis": load_divergent_analysis(),
        "synthesis": load_synthesis(agent["synthesis"]),
        "bias_warning": generate_bias_warning(agent_key),
    }

def generate_bias_warning(agent_key: str) -> str:
    """Generate a specific bias warning for this agent."""
    agent = AGENTS[agent_key]
    level = agent["anti_bias_level"]
    
    warnings = {
        "CRITICAL": "🚨 ATTENTION : Cette agent a un niveau de biais CRITIQUE. "
                    "La source principale vend un service directement lié au conseil donné. "
                    "CROISEZ TOUJOURS avec un professionnel indépendant.",
        "HIGH": "⚠️ ATTENTION : Cette agent a un niveau de biais ÉLEVÉ. "
                "Les chiffres de prix et marges proviennent de sources vendant des formations. "
                "Les coûts complets sont systématiquement sous-estimés dans les sources.",
        "LOW": "✅ Ce agent est basé sur des sources NEUTRES (professionnels indépendants). "
               "Le niveau de confiance est le plus élevé de l'équipe.",
    }
    
    return warnings.get(level, "⚠️ Biais non évalué")

def export_agent_full(agent_key: str) -> dict:
    """Export full agent context as JSON for LLM injection."""
    context = get_agent_context(agent_key)
    
    return {
        "version": "2.0",
        "timestamp": datetime.now().isoformat(),
        "agent": agent_key,
        "agent_name": context["agent_name"],
        "anti_bias_level": context["anti_bias_level"],
        "bias_warning": context["bias_warning"],
        
        # Load order for LLM:
        # 1. Anti-bias module (always first)
        "1_anti_bias_module": context["anti_bias_module"],
        
        # 2. Divergent analysis
        "2_divergent_analysis": context["divergent_analysis"][:5000],  # Truncated for token limit
        
        # 3. Agent-specific system prompt
        "3_agent_system_prompt": context["agent_config"],
        
        # 4. Knowledge synthesis
        "4_knowledge_synthesis": context["synthesis"],
        
        # 5. Bias note specific to this agent
        "5_bias_note": context["bias_note"],
    }

# ============================================================
# CLI Interface
# ============================================================

def main():
    import sys
    
    if len(sys.argv) < 2:
        print("🌍 ImportExport Pro v2 — Agent Orchestrator (avec anti-biais)")
        print("=" * 60)
        
        print(f"\n📚 Sources et leurs biais :")
        print(f"   ✅ CargoFamily      → NEUTRE (podcast pro)")
        print(f"   ⚠️ StartBusinessWorld → VEND 'Sourcing Pro'")
        print(f"   ⚠️ SINOSOURCING      → VEND 'Incubator'")
        print(f"   ⚠️ LineBorrajo       → VEND méthode marque")
        print(f"   ⚠️ Sebastien         → VEND formation e-com")
        
        print(f"\n🤖 Agents v2 (avec anti-biais intégré) :")
        for key, agent in AGENTS.items():
            level = agent["anti_bias_level"]
            icon = {"CRITICAL": "🔴", "HIGH": "🟡", "LOW": "🟢"}.get(level, "⚪")
            print(f"   {icon} {agent['name']} [biais: {level}]")
        
        print(f"\n💡 Usage :")
        print(f"   python {sys.argv[0]} \"Votre question\"")
        print(f"   python {sys.argv[0]} --agent sourcing \"Votre question\"")
        print(f"   python {sys.argv[0]} --export-agent <agent>")
        print(f"   python {sys.argv[0]} --search \"mots clés\"")
        print(f"   python {sys.argv[0]} --bias-report")
        return
    
    command = sys.argv[1]
    
    if command == "--list-transcripts":
        print("📋 Transcripts disponibles (avec biais source) :")
        bias_map = {
            "StartBusinessWorld": "⚠️ VEND",
            "SINOSOURCING": "⚠️ VEND",
            "Sebastien": "⚠️ VEND",
            "CargoFamily": "✅ OK",
            "LineBorrajo": "⚠️ VEND",
        }
        for t in list_transcripts():
            bias = bias_map.get(t["channel"], "?")
            print(f"   [{bias}] {t['channel']}: {t['title'][:50]}... ({t['size']//1024}KB)")
    
    elif command == "--search":
        query = " ".join(sys.argv[2:])
        results = search_transcripts(query)
        print(f"🔍 Résultats pour '{query}' (avec indication biais) :")
        for r in results:
            print(f"   [{r['bias']}] [{r['score']}] {r['title'][:50]}...")
    
    elif command == "--bias-report":
        print("📊 Rapport de biais des sources :")
        print()
        for key, agent in AGENTS.items():
            level = agent["anti_bias_level"]
            icon = {"CRITICAL": "🔴", "HIGH": "🟡", "LOW": "🟢"}.get(level, "⚪")
            print(f"{icon} {agent['name']}")
            print(f"   Niveau biais: {level}")
            print(f"   Note: {agent['bias_note']}")
            print()
    
    elif command == "--agent":
        agent_key = sys.argv[2] if len(sys.argv) > 2 else "market"
        query = " ".join(sys.argv[3:]) if len(sys.argv) > 3 else ""
        context = get_agent_context(agent_key)
        print(f"🤖 Agent : {context['agent_name']}")
        print(f"🛡️ Anti-biais : {context['anti_bias_level']}")
        print(f"⚠️ Note biais : {context['bias_note']}")
        print(f"📊 Avertissement : {context['bias_warning']}")
    
    elif command == "--export-agent":
        agent_key = sys.argv[2] if len(sys.argv) > 2 else "market"
        export = export_agent_full(agent_key)
        
        output_file = BASE_DIR / "data" / f"agent-{agent_key}-context-v2.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Agent {agent_key} v2 exporté : {output_file}")
        print(f"   Taille : {output_file.stat().st_size // 1024} KB")
        print(f"   Anti-biais : {export['anti_bias_level']}")
        print(f"   ⚠️ Biais : {export.get('5_bias_note', 'N/A')[:80]}...")
    
    else:
        query = " ".join(sys.argv[1:])
        agent_key = detect_agent(query)
        agent = AGENTS[agent_key]
        context = get_agent_context(agent_key)
        
        print(f"🤖 Agent détecté : {context['agent_name']}")
        print(f"🛡️ Anti-biais : {context['anti_bias_level']}")
        print(f"⚠️ Biais : {context['bias_warning']}")
        print(f"❓ Question : {query}")
        
        relevant = search_transcripts(query, 3)
        print(f"\n🔍 Sources pertinentes (avec biais) :")
        for r in relevant:
            print(f"   [{r['bias']}] {r['title'][:55]}...")

if __name__ == "__main__":
    main()
