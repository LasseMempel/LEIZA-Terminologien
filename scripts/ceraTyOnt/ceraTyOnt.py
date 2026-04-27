#import requests
import rdflib

"""
fetchPath = "https://raw.githubusercontent.com/archaeolink/CeraTyOnt-Termonology/refs/heads/main/output/ceratyont_skos.ttl"

response = requests.get(fetchPath)
with open("ceratyont_skos.ttl", "wb") as f:
    f.write(response.content)
"""

g = rdflib.Graph()
g.parse("ceratyont_skos.ttl")

property_query = """
SELECT DISTINCT ?property
WHERE {
  ?concept a skos:Concept .
  ?concept ?property ?value .
}
ORDER BY ?property"""

properties = g.query(property_query)

# collect all predicates that skos:concepts using a sparql query

for property in properties:
    print(property)

"""
(rdflib.term.URIRef('http://purl.org/dc/terms/created'),)
(rdflib.term.URIRef('http://purl.org/dc/terms/creator'),)
(rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'),)
(rdflib.term.URIRef('http://www.w3.org/2000/01/rdf-schema#label'),)
(rdflib.term.URIRef('http://www.w3.org/2004/02/skos/core#altLabel'),)
(rdflib.term.URIRef('http://www.w3.org/2004/02/skos/core#broader'),)
(rdflib.term.URIRef('http://www.w3.org/2004/02/skos/core#definition'),)
(rdflib.term.URIRef('http://www.w3.org/2004/02/skos/core#exactMatch'),)
(rdflib.term.URIRef('http://www.w3.org/2004/02/skos/core#historyNote'),)
(rdflib.term.URIRef('http://www.w3.org/2004/02/skos/core#inScheme'),)
(rdflib.term.URIRef('http://www.w3.org/2004/02/skos/core#narrower'),)
(rdflib.term.URIRef('http://www.w3.org/2004/02/skos/core#notation'),)
(rdflib.term.URIRef('http://www.w3.org/2004/02/skos/core#note'),)
(rdflib.term.URIRef('http://www.w3.org/2004/02/skos/core#prefLabel'),)
(rdflib.term.URIRef('http://www.w3.org/2004/02/skos/core#related'),)
(rdflib.term.URIRef('http://www.w3.org/2004/02/skos/core#scopeNote'),)
(rdflib.term.URIRef('http://www.w3.org/2004/02/skos/core#topConceptOf'),)
(rdflib.term.URIRef('http://www.w3id.org/lado/hasSameFlute'),)
(rdflib.term.URIRef('http://www.w3id.org/lado/hasSameFootring'),)
(rdflib.term.URIRef('http://www.w3id.org/lado/hasSameGroove'),)
(rdflib.term.URIRef('http://www.w3id.org/lado/hasSameRim'),)
(rdflib.term.URIRef('http://www.w3id.org/lado/hasSameRoulette'),)
(rdflib.term.URIRef('http://xmlns.com/foaf/0.1/depiction'),)
"""