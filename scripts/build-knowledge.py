#!/usr/bin/env python3
"""
ImportExport Pro — Build Knowledge Base
Processes raw transcripts into structured knowledge for agents.
"""

import os
import json
import re
from pathlib import Path
from collections import Counter, defaultdict

BASE_DIR = Path(__file__).parent.parent
TRANSCRIPTS_DIR = BASE_DIR / "knowledge-base" / "transcripts"
OUTPUT_DIR = BASE_DIR / "data"

def parse_transcript(filepath: Path) -> dict:
    """Parse a transcript file into structured data."""
    content = filepath.read_text(encoding='utf-8')
    lines = content.split('\n')
    
    metadata = {}
    text_start = 0
    for i, line in enumerate(lines):
        if line.startswith('# '):
            key = line.split(':')[0].replace('# ', '').lower().strip()
            value = ':'.join(line.split(':')[1:]).strip()
            metadata[key] = value
            text_start = i + 1
        elif line.strip() == '':
            continue
        else:
            break
    
    text = '\n'.join(lines[text_start:])
    
    # Extract potential topics/keywords
    words = re.findall(r'\b[a-zA-Zàâäéèêëïîôùûüÿçñ]{4,}\b', text.lower())
    
    # Filter common words
    stop_words = {'avec', 'dans', 'pour', 'mais', 'donc', 'fait', 'aussi', 
                  'bien', 'tout', 'tous', 'cette', 'cela', 'leurs', 'cette',
                  'which', 'that', 'this', 'with', 'from', 'they', 'have',
                  'their', 'about', 'would', 'there', 'these', 'other'}
    filtered_words = [w for w in words if w not in stop_words]
    
    word_freq = Counter(filtered_words).most_common(30)
    
    return {
        "file": filepath.name,
        "metadata": metadata,
        "text_length": len(text),
        "top_keywords": word_freq,
        "preview": text[:500],
    }

def build_knowledge_index():
    """Build a searchable index of all knowledge."""
    index = {
        "transcripts": [],
        "channels": defaultdict(list),
        "keyword_map": defaultdict(list),
        "stats": {
            "total_transcripts": 0,
            "total_chars": 0,
            "by_channel": {},
        }
    }
    
    for f in TRANSCRIPTS_DIR.glob("*.txt"):
        parsed = parse_transcript(f)
        index["transcripts"].append(parsed)
        
        channel = parsed["metadata"].get("channel", "unknown")
        index["channels"][channel].append({
            "file": f.name,
            "title": parsed["metadata"].get("title", "Unknown"),
            "chars": parsed["text_length"],
        })
        
        for word, count in parsed["top_keywords"][:10]:
            index["keyword_map"][word].append({
                "file": f.name,
                "count": count,
            })
        
        index["stats"]["total_transcripts"] += 1
        index["stats"]["total_chars"] += parsed["text_length"]
    
    index["stats"]["by_channel"] = {
        ch: len(vids) for ch, vids in index["channels"].items()
    }
    
    return index

def main():
    print("🏗️ Construction de la base de connaissances ImportExport Pro...")
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Build index
    index = build_knowledge_index()
    
    # Save index
    index_file = OUTPUT_DIR / "knowledge-index.json"
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"✅ Index créé : {index_file}")
    print(f"\n📊 Statistiques :")
    print(f"   Transcripts : {index['stats']['total_transcripts']}")
    print(f"   Taille totale : {index['stats']['total_chars']:,} caractères")
    print(f"   Chaînes :")
    for ch, count in index['stats']['by_channel'].items():
        print(f"     - {ch}: {count} vidéos")
    
    # Build per-channel extracts
    print(f"\n📁 Extraction par canal :")
    for channel, videos in index["channels"].items():
        channel_data = {
            "channel": channel,
            "videos": videos,
            "total_content_chars": sum(v["chars"] for v in videos),
        }
        ch_file = OUTPUT_DIR / "fournisseurs" / f"channel-{channel}.json"
        ch_file.parent.mkdir(parents=True, exist_ok=True)
        with open(ch_file, 'w', encoding='utf-8') as f:
            json.dump(channel_data, f, ensure_ascii=False, indent=2)
        print(f"   ✅ {channel}: {len(videos)} vidéos → {ch_file.name}")
    
    # Build keyword-frequency product database
    print(f"\n🏷️ Top keywords globaux :")
    all_keywords = Counter()
    for t in index["transcripts"]:
        for word, count in t["top_keywords"]:
            all_keywords[word] += count
    
    for word, count in all_keywords.most_common(50):
        print(f"   {word}: {count}")
    
    print(f"\n✅ Base de connaissances prête !")

if __name__ == "__main__":
    main()
