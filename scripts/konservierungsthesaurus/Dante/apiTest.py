import requests
import json
from rdflib import Graph, BNode, Literal, URIRef
from rdflib.namespace import SKOS, DCTERMS, RDF

voc = "archlink_conservationthesaurus"
searchQuery = f"http://api.dante.gbv.de/search?voc={voc}&limit=5000&query=*&properties=*&cache=0&format=jskos"

response = requests.get(searchQuery)
with open("archlink_conservationthesaurus.json", "w", encoding="utf-8") as f:
    json.dump(response.json(), f, ensure_ascii=False, indent=2)

g = Graph()
g.parse("archlink_conservationthesaurus.json", format="json-ld")
g.serialize("archlink_conservationthesaurus.ttl", format="turtle")

FLATTEN_PROPS = {DCTERMS.publisher, DCTERMS.source}
OLD_URI = URIRef("http://uri.gbv.de/terminology/archlink_conservationthesaurus/")
NEW_URI = URIRef("https://www.w3id.org/archlink/terms/conservationthesaurus")
OLD_PRED = URIRef("http://uri.gbv.de/terminology/ontologic_relation/ce8215a4-17ad-433c-a3e6-0c941de67abc")
_uri_cache: dict[str, URIRef | None] = {}

for prop in FLATTEN_PROPS:
    # list() because we mutate the graph inside the loop
    for s, p, o in list(g.triples((None, prop, None))):
        if not isinstance(o, BNode):
            continue

        labels = list(g.objects(o, SKOS.prefLabel))
        if not labels:
            continue  # blank node has no prefLabel — leave it alone

        # Remove the original triple pointing to the blank node
        g.remove((s, p, o))

        # Remove all triples *about* the blank node (clean up orphans)
        for pred, obj in list(g.predicate_objects(o)):
            g.remove((o, pred, obj))

        # Add one direct triple per label (handles multiple values naturally)
        for label in labels:
            g.add((s, p, Literal(str(label))))

for scheme in g.subjects(RDF.type, SKOS.ConceptScheme):
    for label in list(g.objects(scheme, SKOS.prefLabel)):
        g.remove((scheme, SKOS.prefLabel, label))
        g.add((scheme, DCTERMS.title, label))

for s, p, o in list(g):
    ns = NEW_URI if s == OLD_URI else s
    no = NEW_URI if o == OLD_URI else o
    if ns is not s or no is not o:
        g.remove((s, p, o))
        g.add((ns, p, no))

def resolve_jskos_uri(dante_uri: str) -> URIRef | None:
    if dante_uri in _uri_cache:
        return _uri_cache[dante_uri]
    try:
        resp = requests.get(dante_uri, headers={"Accept": "application/json"}, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if isinstance(data, list):
            data = data[0]
        canonical = data.get("uri")
        result = URIRef(canonical) if canonical else None
    except Exception as e:
        print(f"Warning: could not resolve {dante_uri}: {e}")
        result = None
    _uri_cache[dante_uri] = result
    return result


for s, p, o in list(g.triples((None, OLD_PRED, None))):
    if not isinstance(o, BNode):
        continue

    # Extract the actual target URI from the blank node's rdf:object
    rdf_objects = list(g.objects(o, RDF.object))
    if not rdf_objects:
        print(f"Warning: blank node for {s} has no rdf:object — skipping")
        continue

    canonical_uri = resolve_jskos_uri(str(rdf_objects[0]))
    if not canonical_uri:
        continue

    # Remove old triple and clean up blank node
    g.remove((s, p, o))
    for pred, obj in list(g.predicate_objects(o)):
        g.remove((o, pred, obj))

    g.add((s, SKOS.related, canonical_uri))

g.serialize("archlink_conservationthesaurus_flattened.ttl", format="turtle")

print(f"Number of triples in the graph: {len(g)}")