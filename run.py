import os
import json
import time
import luftfartygsregistret as lfr
from services.writer import Writer

# === Start timer ===
start_time = time.time()

print("📡 Hämtar alla luftfartyg med detaljer...\n")
register = lfr.get_aircrafts_with_details()

# Spara aktuellt register
Writer.write_json(register, "register.json")

# Ta bort anonyma ägare
register_light = [lfr.remove_anonymous_owners(a) for a in register]

# Spara lätt version + CSV
Writer.write_json(register_light, "register_light.json")
Writer.write_csv(register_light, "register.csv")

print("✅ Hämtning klar.\n")

# === Jämför med tidigare fil ===
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

# === Hitta tillagda, borttagna och ändrade poster ===
def normalize(obj):
    """Sortera nycklar för stabil jämförelse"""
    return json.dumps(obj, sort_keys=True, ensure_ascii=False)

added = [a for code, a in new.items() if code not in old]
removed = [a for code, a in old.items() if code not in new]
changed = [
    {"code": code, "old": old[code], "new": new[code]}
    for code in new
    if code in old and normalize(old[code]) != normalize(new[code])
]

# === Sammanfattning ===
summary = {
    "added_count": len(added),
    "removed_count": len(removed),
    "changed_count": len(changed),
    "added": [a["code"] for a in added],
    "removed": [a["code"] for a in removed],
    "changed": [a["code"] for a in changed],
}

Writer.write_json(summary, "updates.json")

# === Resultat i terminalen ===
print("=========================================")
print(f"\033[92mTillagda poster:\033[0m {len(added)}")
print(f"\033[91mBorttagna poster:\033[0m {len(removed)}")
print(f"\033[93mÄndrade poster:\033[0m {len(changed)}")
print("=========================================")
print("Sparade sammanställning till updates.json")

# === Flytta över aktuellt register som nytt "previous" ===
os.replace("register.json", previous_file)

# === Mät tid ===
end_time = time.time()
elapsed = end_time - start_time
minutes, seconds = divmod(round(elapsed), 60)
print(f"\n Tog {minutes} minuter och {seconds} sekunder att skanna.")