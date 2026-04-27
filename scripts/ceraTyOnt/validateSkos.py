from pyshacl import validate

shacl_graph = "/home/mempellaenger/repos/LEIZA-Terminologien/shapes/skohub.shacl.ttl"
data_graph = "/home/mempellaenger/repos/LEIZA-Terminologien/scripts/ceraTyOnt/ceratyont_skos.ttl"

r = validate(data_graph,
      shacl_graph=shacl_graph,
      #ont_graph=ont_graph,
      inference='rdfs',
      abort_on_first=False,
      allow_infos=False,
      allow_warnings=False,
      meta_shacl=False,
      advanced=False,
      js=False,
      debug=False)
conforms, results_graph, results_text = r

print(conforms)
for result in results_graph:
    print(result)
print(results_text)


