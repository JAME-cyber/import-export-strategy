#!/usr/bin/env python3
"""
ImportExport Pro — Transcript Fetcher v2.0
- Télécharge les transcripts via youtube-transcript-api (sous-titres YouTube)
- Pour les vidéos sans sous-titres: option Whisper via Groq/OpenAI
- Ne retente que les vidéos manquantes
- Gère le rate limiting automatiquement

Usage:
  python3 fetch_transcripts.py              # Mode normal (API sous-titres)
  python3 fetch_transcripts.py --whisper    # Mode Whisper pour vidéos sans subs
  python3 fetch_transcripts.py --status     # Affiche le statut uniquement
"""

import os
import sys
import time
import json
from pathlib import Path
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

# Configuration
OUTPUT_DIR = Path(__file__).parent.parent / "knowledge-base" / "transcripts"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

VIDEO_IDS = [
    # StartBusinessWorld (12 avec subs / 12 testés)
    ("5EXMyoXcdvQ", "Comprendre TOUT le Business L'IMPORT-EXPORT avec la Chine", "StartBusinessWorld"),
    ("mMeqI6_Ysfk", "Import depuis la Chine : logistique et containers", "StartBusinessWorld"),
    ("PCbSTToM_z4", "11 plateformes pour commander en chine", "StartBusinessWorld"),
    ("ipP-VUwngtE", "Trouver facilement des fournisseurs en chine", "StartBusinessWorld"),
    ("NdUHEt2qcbE", "TUTO 1688 : commander pas cher en Chine", "StartBusinessWorld"),
    ("-R8nOZ82jPQ", "TUTO Taobao: commander en chine petit budget", "StartBusinessWorld"),
    ("s_vz4MkCyO8", "Canton Fair 2025: What Nobody Shows You", "StartBusinessWorld"),
    ("1ZiuOawfrNE", "Commander en ligne ou Aller en Chine", "StartBusinessWorld"),
    ("S3znvv0G3AY", "Made in China : machines industrielles et agricoles", "StartBusinessWorld"),
    ("brVD0CFzgJM", "Créer une société à Hong Kong", "StartBusinessWorld"),
    ("zOqLUYaVF1E", "Créer une entreprise : impôts, statut juridique, TVA", "StartBusinessWorld"),
    ("vXvxzZiSiu8", "La Foire de Canton : Guide complet", "StartBusinessWorld"),
    # CargoFamily (7 avec subs / 7 testés)
    ("ak3yl_fZkXA", "L'import export, un secteur passionnant et complexe", "CargoFamily"),
    ("qVLp83wK4AY", "20 ans de négoce et d'Import-Export", "CargoFamily"),
    ("oOGD_JjYBoM", "Exporter en Afrique : Les clés du succès", "CargoFamily"),
    ("SjTnsPE7iHg", "NABU révolutionne la douane import export avec l'IA", "CargoFamily"),
    ("ZOl1-0rMUas", "digitalise et sécurise vos transactions import export", "CargoFamily"),
    ("XWJod-4bzrM", "Douane & IA, de Roissy à Montréal", "CargoFamily"),
    ("9Sb4X6uvBl4", "Customs Bridge, les innov'acteurs de la Douane", "CargoFamily"),
    # SINOSOURCING (5 avec subs / 30+ testés)
    ("VV4t5bfua6k", "Canton Fair Phase 2: Import Strategies", "SINOSOURCING"),
    ("4wIUebP8Ols", "Inside a Factory in China: Spa and Sauna", "SINOSOURCING"),
    ("53Q2rEOWNMQ", "Buying in China: Is it worth it in 2025", "SINOSOURCING"),
    ("qTlX99mYZ2I", "Goods stuck in customs, lost, broken: Who is responsible", "SINOSOURCING"),
    ("9CYhDmbvw0g", "Creating your brand in China", "SINOSOURCING"),
    # === VIDÉOS SANS SUBS (nécessitent Whisper) ===
    # SINOSOURCING (vidéos importantes - factory tours, prix réels)
    ("k7iCyvLmS30", "Capsule House in China: Factory Tour", "SINOSOURCING"),
    ("n_rxim8Ku2E", "Spa Factory in China: Real Factory Prices", "SINOSOURCING"),
    ("ZuMDNJ3XpVY", "I infiltrated the secret manufacturer of Foshan", "SINOSOURCING"),
    ("LZgrp9U6qUA", "These Chinese machines cost LESS than a salary", "SINOSOURCING"),
    ("dS4NXYhw_j0", "The Chinese factory that will kill the construction industry", "SINOSOURCING"),
    ("yDQIx8eAf1w", "The Sea Cartel: What your freight forwarder will never tell you", "SINOSOURCING"),
    ("DDn-XRzcd2s", "He imported an ENTIRE gym from China", "SINOSOURCING"),
    ("dPncDtMDBhA", "He equips his restaurants using Chinese products", "SINOSOURCING"),
    ("mJteTopF_hE", "They resell snack equipment imported from China", "SINOSOURCING"),
    ("6Nfqqy41Ql8", "Il importe un Food Truck sur-mesure de Chine", "SINOSOURCING"),
    ("vLtUHRijizk", "At 22 he imported a container to furnish 15 apartments", "SINOSOURCING"),
    # LineBorrajo (toutes sans subs)
    ("wMJQk-nDAJw", "LES 12 ÉTAPES POUR CRÉER UNE MARQUE E-COMMERCE", "LineBorrajo"),
    ("dQTr8VInXUE", "COMMENT J'AI CRÉÉ MES MARQUES À PLUSIEURS MILLIONS", "LineBorrajo"),
    ("iWjrwJJN1ks", "LES MEILLEURS PRODUITS EN CHINE", "LineBorrajo"),
    ("FeCYBC8b6tw", "10 PRODUITS À LANCER EN 2026", "LineBorrajo"),
    # Sebastien.selfmadeprogram (toutes sans subs)
    ("NhvK3SVfGjI", "The NEW e-commerce model replacing DROPSHIPPING", "Sebastien"),
    ("qVkRUCE5DVI", "6 years of e-commerce experience in 20 minutes", "Sebastien"),
    ("zhOi00aQZAI", "The real hidden methods of Shopify brands", "Sebastien"),
]

def already_downloaded(vid_id: str) -> bool:
    return (OUTPUT_DIR / f"{vid_id}.txt").exists()

def download_via_api(vid_id: str, title: str, channel: str) -> dict:
    """Download transcript via YouTube subtitle API."""
    ytt_api = YouTubeTranscriptApi()
    for lang_list in [['fr'], ['en'], ['fr', 'en'], None]:
        try:
            if lang_list:
                td = ytt_api.fetch(vid_id, languages=lang_list)
            else:
                td = ytt_api.fetch(vid_id)
            text = "\n".join(e.text for e in td)
            (OUTPUT_DIR / f"{vid_id}.txt").write_text(
                f"# Title: {title}\n# Channel: {channel}\n# Video ID: {vid_id}\n"
                f"# URL: https://www.youtube.com/watch?v={vid_id}\n"
                f"# Language: {td.language}\n# Source: youtube-api\n\n{text}\n",
                encoding='utf-8'
            )
            return {"status": "success", "chars": len(text), "lang": td.language}
        except TranscriptsDisabled:
            return {"status": "disabled", "error": "Transcripts disabled"}
        except NoTranscriptFound:
            continue
        except Exception as e:
            if "429" in str(e) or "Too Many" in str(e):
                return {"status": "rate_limited", "error": str(e)}
            continue
    return {"status": "no_transcript", "error": "No transcript in any language"}

def download_via_whisper(vid_id: str, title: str, channel: str) -> dict:
    """Download audio via yt-dlp and transcribe via watch skill (Whisper)."""
    watch_script = Path.home() / ".pi/skills/watch/scripts/watch.py"
    if not watch_script.exists():
        return {"status": "error", "error": "Watch skill not found"}
    
    url = f"https://www.youtube.com/watch?v={vid_id}"
    tmp_dir = Path(f"/tmp/ie-whisper-{vid_id}")
    tmp_dir.mkdir(exist_ok=True)
    
    # Download audio only
    import subprocess
    print(f"  📥 Downloading audio...")
    result = subprocess.run(
        ["yt-dlp", "-x", "--audio-format", "mp3", "-o", str(tmp_dir / "audio.%(ext)s"), url],
        capture_output=True, text=True, timeout=300
    )
    if result.returncode != 0:
        return {"status": "error", "error": f"yt-dlp failed: {result.stderr[:100]}"}
    
    # Find audio file
    audio_files = list(tmp_dir.glob("audio.*"))
    if not audio_files:
        return {"status": "error", "error": "No audio file downloaded"}
    
    audio_path = audio_files[0]
    file_size_mb = audio_path.stat().st_size / (1024 * 1024)
    
    if file_size_mb > 25:
        return {"status": "error", "error": f"Audio too large ({file_size_mb:.0f}MB > 25MB Whisper limit)"}
    
    # Transcribe via watch.py
    print(f"  🎤 Transcribing ({file_size_mb:.1f}MB)...")
    result = subprocess.run(
        ["python3", str(watch_script), str(audio_path), "--no-whisper"],
        capture_output=True, text=True, timeout=120
    )
    
    # Try Whisper API directly
    try:
        import httpx
        # Check for Groq key
        env_file = Path.home() / ".config/watch/.env"
        api_key = None
        api_url = None
        
        if env_file.exists():
            for line in env_file.read_text().splitlines():
                if line.startswith("GROQ_API_KEY="):
                    api_key = line.split("=", 1)[1].strip()
                    api_url = "https://api.groq.com/openai/v1/audio/transcriptions"
                    break
                elif line.startswith("OPENAI_API_KEY="):
                    api_key = line.split("=", 1)[1].strip()
                    api_url = "https://api.openai.com/v1/audio/transcriptions"
                    break
        
        if not api_key:
            return {"status": "error", "error": "No Whisper API key found"}
        
        with open(audio_path, "rb") as f:
            response = httpx.post(
                api_url,
                headers={"Authorization": f"Bearer {api_key}"},
                files={"file": ("audio.mp3", f, "audio/mpeg")},
                data={"model": "whisper-large-v3" if "groq" in api_url else "whisper-1"},
                timeout=120
            )
        
        if response.status_code == 200:
            text = response.json()["text"]
            (OUTPUT_DIR / f"{vid_id}.txt").write_text(
                f"# Title: {title}\n# Channel: {channel}\n# Video ID: {vid_id}\n"
                f"# URL: https://www.youtube.com/watch?v={vid_id}\n"
                f"# Language: auto\n# Source: whisper\n\n{text}\n",
                encoding='utf-8'
            )
            # Cleanup
            import shutil
            shutil.rmtree(tmp_dir, ignore_errors=True)
            return {"status": "success", "chars": len(text), "lang": "whisper-auto"}
        else:
            return {"status": "error", "error": f"Whisper API error: {response.status_code}"}
    
    except ImportError:
        return {"status": "error", "error": "httpx not installed for Whisper API"}
    except Exception as e:
        return {"status": "error", "error": str(e)[:100]}

def show_status():
    """Show current download status."""
    print("🌍 ImportExport Pro — Statut des Transcripts")
    print("=" * 60)
    
    downloaded = []
    missing = []
    
    for vid_id, title, channel in VIDEO_IDS:
        if already_downloaded(vid_id):
            fpath = OUTPUT_DIR / f"{vid_id}.txt"
            size = fpath.stat().st_size
            downloaded.append((vid_id, title, channel, size))
        else:
            missing.append((vid_id, title, channel))
    
    print(f"\n✅ Téléchargés : {len(downloaded)}/{len(VIDEO_IDS)}")
    by_channel = {}
    for vid, title, ch, size in downloaded:
        by_channel.setdefault(ch, []).append((vid, title, size))
    
    for ch, vids in by_channel.items():
        total_chars = sum(s for _, _, s in vids)
        print(f"   {ch}: {len(vids)} vidéos ({total_chars:,} chars)")
    
    if missing:
        print(f"\n❌ Manquants : {len(missing)}")
        by_ch = {}
        for vid, title, ch in missing:
            by_ch.setdefault(ch, []).append((vid, title))
        for ch, vids in by_ch.items():
            print(f"   {ch}: {len(vids)} vidéos")
            for vid, title in vids[:3]:
                print(f"      - {title[:55]}...")
            if len(vids) > 3:
                print(f"      ... et {len(vids)-3} autres")
        print(f"\n💡 Utilisez --whisper pour télécharger via audio→texte")
    
    total_chars = sum(s for _, _, _, s in downloaded)
    print(f"\n📊 Total : {total_chars:,} caractères de contenu expert")

def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    
    if mode == "--status":
        show_status()
        return
    
    use_whisper = mode == "--whisper"
    
    print("🌍 ImportExport Pro — Transcript Fetcher v2.0")
    print("=" * 60)
    
    if use_whisper:
        print("🎯 Mode : Whisper (audio → texte)")
    else:
        print("🎯 Mode : YouTube API (sous-titres)")
    
    missing = [(vid, title, ch) for vid, title, ch in VIDEO_IDS if not already_downloaded(vid)]
    already = len(VIDEO_IDS) - len(missing)
    
    print(f"\n📊 Déjà téléchargés : {already}/{len(VIDEO_IDS)}")
    print(f"⏳ À télécharger : {len(missing)}")
    
    if not missing:
        print("\n✅ Tous les transcripts sont déjà téléchargés !")
        return
    
    print(f"\n🚀 Démarrage...\n")
    
    results = {"success": [], "failed": [], "rate_limited": []}
    
    for i, (vid_id, title, channel) in enumerate(missing):
        print(f"[{i+1}/{len(missing)}] {vid_id} ({channel}): {title[:45]}...")
        
        if use_whisper:
            result = download_via_whisper(vid_id, title, channel)
        else:
            result = download_via_api(vid_id, title, channel)
        
        if result["status"] == "success":
            results["success"].append(vid_id)
            print(f"  ✅ {result['chars']:,} chars [{result.get('lang', '?')}]")
        elif result["status"] == "rate_limited":
            results["rate_limited"].append(vid_id)
            print(f"  ⏸️ Rate limited — pause 30s...")
            time.sleep(30)
        elif result["status"] == "disabled":
            results["failed"].append({"id": vid_id, "error": "disabled"})
            print(f"  ❌ Subs désactivés → essayez --whisper")
        else:
            results["failed"].append({"id": vid_id, "error": result.get("error", "?")})
            if use_whisper:
                print(f"  ❌ {result.get('error', '?')[:60]}")
            else:
                print(f"  ❌ Pas de sous-titres → essayez --whisper")
        
        time.sleep(3 if not use_whisper else 5)
    
    print(f"\n{'='*60}")
    print(f"📊 Résultats : ✅ {len(results['success'])} | ❌ {len(results['failed'])} | ⏸️ {len(results['rate_limited'])}")
    total = already + len(results['success'])
    print(f"📈 Progression : {total}/{len(VIDEO_IDS)} ({total*100//len(VIDEO_IDS)}%)")
    
    if results['rate_limited']:
        print(f"\n💡 Relancez dans 30-60 min pour les vidéos restantes.")

if __name__ == "__main__":
    main()
