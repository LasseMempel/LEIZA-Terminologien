import requests
import json
import os

if not os.path.exists("scheme.json"):
    schemeJSON = requests.get("https://api.dante.gbv.de/voc/leiza_archlink?properties=*")
    with open("scheme.json", "w") as f:
        json.dump(schemeJSON.json(), f, indent=2)
with open("scheme.json", "r") as f:
    schemeJSON = json.load(f)

if not os.path.exists("topConcepts.json"):
    conceptsJSON = requests.get("https://api.dante.gbv.de/voc/leiza_archlink/top")
    with open("topConcepts.json", "w") as f:
        json.dump(conceptsJSON.json(), f, indent=2)
with open("topConcepts.json", "r") as f:
    conceptsJSON = json.load(f)

def crawlConcept(uri, conceptArray, i):
    print(f"  → Processing concept {i}: {uri}")
    conceptTree = requests.get(f"https://api.dante.gbv.de/data?uri={uri}&properties=*")
    concept = conceptTree.json()[0]
    conceptArray.append(concept)
    for narrower in (concept.get("narrower") or []):
        conceptArray, i = crawlConcept(narrower["uri"], conceptArray, i)
    return conceptArray, i+1

# Crawl and save each top concept tree individually

for topConcept in conceptsJSON:
    topConceptUri = topConcept["uri"]
    print("/n")
    print(f"\nProcessing top concept: {topConceptUri}")
    concept_id = topConceptUri.split("/")[-1]
    filename = f"{concept_id}.json"

    if not os.path.exists(filename):
        print(f"Crawling tree of {topConceptUri}")
        i = 1
        conceptArray = crawlConcept(topConceptUri, [], i)
        with open(filename, "w") as f:
            json.dump(conceptArray, f, indent=2)
        print(f"  → Saved {len(conceptArray)} concepts to {filename}")
    else:
        print(f"Skipping {filename} (already exists)")

# Combine all individual files into concepts.json
if not os.path.exists("concepts.json"):
    allConcepts = []
    for topConcept in conceptsJSON:
        concept_id = topConcept["uri"].split("/")[-1]
        filename = f"{concept_id}.json"
        with open(filename, "r") as f:
            allConcepts.extend(json.load(f))
    with open("concepts.json", "w") as f:
        json.dump(allConcepts, f, indent=2)
    print(f"\nCombined {len(allConcepts)} total concepts into concepts.json")

with open("concepts.json", "r") as f:
    conceptsJSON = json.load(f)
print(json.dumps(conceptsJSON, indent=2))