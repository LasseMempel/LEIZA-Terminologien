from rdflib import Graph
import sys
from pathlib import Path

generated = Path("scripts/konservierungsthesaurus/scheme.ttl")
current = Path("data/scheme.ttl")

if not current.exists():
    print("No existing scheme.ttl in data/ → treat as changed")
    sys.exit(1)

g_new = Graph().parse(generated, format="turtle")
g_old = Graph().parse(current, format="turtle")

diff_new = g_new - g_old
diff_old = g_old - g_new

if len(diff_new) == 0 and len(diff_old) == 0:
    print("RDF graphs are identical")
    sys.exit(0)
else:
    print(f"Graphs differ: +{len(diff_new)} / -{len(diff_old)} triples")
    sys.exit(1)