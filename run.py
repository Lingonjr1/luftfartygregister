import os
import json
import time
import subprocess
import luftfartygsregistret as lfr
from services.writer import Writer

GITHUB_USER = "Lingonjr1"
REPO = "luftfartygregister"
TOKEN = "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"  

def git_commit_and_push(message="Auto update"):
    """Push changes to GitHub automatically."""
    remote_url = f"https://{GITHUB_USER}:{TOKEN}@github.com/{GITHUB_USER}/{REPO}.git"
    try:
        subprocess.run(["git", "remote", "set-url", "origin", remote_url], check=True)
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", message], check=True)
        subprocess.run(["git", "push", "origin", "main"], check=True)
        print("✅ Changes committed and pushed to GitHub.")
    except subprocess.CalledProcessError as e:
        print("⚠️ Git push failed:", e)

start_time = time.time()

print("📡 Hämtar alla luftfartyg med detaljer...\n")
register = lfr.get_aircrafts_with_details()

Writer.write_json(register, "register.json")

register_light = [lfr.remove_anonymous_owners(a) for a in register]

Writer.write_json(register_light, "register_light.json")
Writer.write_csv(register_light, "register.csv")

print("✅ Hämtning klar.\n")

previous_file = "register_previous.json"
if os.path.exists(previous_file):
    with open(previous_file, "r", encoding="utf-8") as f:
        old_data = json.load(f)
else:
    old_data = []

def index_by_code(data):
    """Indexera registerposter per flygplanscode"""
    return {a["code"]: a for a in data if "code" in a}

old = index_by_code(old_data)
new = index_by_code(register)

def normalize(obj):
    """Sortera register för stabil jämförelse"""
    return json.dumps(obj, sort_keys=True, ensure_ascii=False)

added = [a for code, a in new.items() if code not in old]
removed = [a for code, a in old.items() if code not in new]
changed = [
    {"code": code, "old": old[code], "new": new[code]}
    for code in new
    if code in old and normalize(old[code]) != normalize(new[code])
]

summary = {
    "added_count": len(added),
    "removed_count": len(removed),
    "changed_count": len(changed),
    "added": [a["code"] for a in added],
    "removed": [a["code"] for a in removed],
    "changed": [a["code"] for a in changed],
}

Writer.write_json(summary, "updates.json")

os.replace("register.json", previous_file)

git_commit_and_push("Automatisk uppdatering av luftfartygsregister")

end_time = time.time()
elapsed = end_time - start_time
minutes, seconds = divmod(round(elapsed), 60)
print(f"\nTog {minutes} minuter och {seconds} sekunder att skanna.")