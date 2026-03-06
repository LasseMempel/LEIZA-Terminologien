import requests
import pandas as pd
import json
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import SKOS, RDF, DCTERMS, RDFS, VANN
from io import StringIO

def fetch_turtle(url):
    """Fetch turtle format directly from API"""
    response = requests.get(url)
    response.raise_for_status()
    return response.text

def fetch_json(url):
    """Fetch JSON format from API"""
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def convert_json_to_dataframe(json_data, is_scheme=False):
    """Convert JSON API response to DataFrame matching CSV format"""
    if not isinstance(json_data, list):
        json_data = [json_data]
    
    if len(json_data) == 0:
        return pd.DataFrame()
    
    # Handle scheme data
    if is_scheme:
        scheme = json_data[0]
        row = {
            "ConceptScheme": scheme.get("uri", ""),
            "namespace": scheme.get("namespace", ""),
            "notation": scheme.get("notation", [""])[0] if isinstance(scheme.get("notation", []), list) else scheme.get("notation", ""),
            "created": scheme.get("created", ""),
            "modified": scheme.get("modified", ""),
            "issued": scheme.get("issued", "")
        }
        
        # Handle labels in all available languages
        for lang, label in scheme.get("prefLabel", {}).items():
            row[f"prefLabel@{lang}"] = label
            
        # Handle definitions in all available languages
        for lang, definition in scheme.get("definition", {}).items():
            row[f"definition@{lang}"] = definition
            
        # Handle subjects in all available languages
        for lang, subjects in scheme.get("subject", {}).items():
            if isinstance(subjects, list):
                row[f"subject@{lang}"] = "|".join(subjects)
            else:
                row[f"subject@{lang}"] = subjects
                
        # Handle publisher
        publishers = []
        for publisher in scheme.get("publisher", []):
            if "prefLabel" in publisher:
                for lang, label in publisher["prefLabel"].items():
                    row[f"publisher@{lang}"] = label
            else:
                publishers.append(publisher.get("uri", ""))
        if publishers:
            row["publisher"] = "|".join(publishers)
            
        # Handle license
        licenses = []
        for license in scheme.get("license", []):
            licenses.append(license.get("uri", ""))
        if licenses:
            row["license"] = "|".join(licenses)
            
        # Handle contributors
        contributors = []
        for contributor in scheme.get("contributor", []):
            if isinstance(contributor, str):
                contributors.append(contributor)
            elif "prefLabel" in contributor:
                for lang, label in contributor["prefLabel"].items():
                    contributors.append(label)
        if contributors:
            row["contributor"] = "|".join(contributors)
            
        # Handle creator
        creators = []
        for creator in scheme.get("creator", []):
            if isinstance(creator, str):
                creators.append(creator)
            elif "prefLabel" in creator:
                for lang, label in creator["prefLabel"].items():
                    creators.append(label)
        if creators:
            row["creator"] = "|".join(creators)
            
        # Handle description
        for lang, description in scheme.get("description", {}).items():
            row[f"description@{lang}"] = description
            
        # Handle title
        for lang, title in scheme.get("title", {}).items():
            row[f"title@{lang}"] = title
            
        return pd.DataFrame([row])
    
    # Handle concepts data
    else:
        rows = []
        for concept in json_data:
            row = {
                "notation": concept.get("notation", [""])[0] if isinstance(concept.get("notation", []), list) else concept.get("notation", ""),
                "created": concept.get("created", ""),
                "modified": concept.get("modified", ""),
                "issued": concept.get("issued", "")
            }
            
            # Handle labels in all available languages
            for lang, label in concept.get("prefLabel", {}).items():
                row[f"prefLabel@{lang}"] = label
                
            # Handle alt labels in all available languages
            for lang, alt_labels in concept.get("altLabel", {}).items():
                if isinstance(alt_labels, list):
                    row[f"altLabel@{lang}"] = "|".join(alt_labels)
                else:
                    row[f"altLabel@{lang}"] = alt_labels
                    
            # Handle hidden labels in all available languages
            for lang, hidden_labels in concept.get("hiddenLabel", {}).items():
                if isinstance(hidden_labels, list):
                    row[f"hiddenLabel@{lang}"] = "|".join(hidden_labels)
                else:
                    row[f"hiddenLabel@{lang}"] = hidden_labels
                    
            # Handle scope notes in all available languages
            for lang, scope_notes in concept.get("scopeNote", {}).items():
                if isinstance(scope_notes, list):
                    row[f"scopeNote@{lang}"] = "|".join(scope_notes)
                else:
                    row[f"scopeNote@{lang}"] = scope_notes
                    
            # Handle definitions in all available languages
            for lang, definitions in concept.get("definition", {}).items():
                if isinstance(definitions, list):
                    row[f"definition@{lang}"] = "|".join(definitions)
                else:
                    row[f"definition@{lang}"] = definitions
                    
            # Handle examples in all available languages
            for lang, examples in concept.get("example", {}).items():
                if isinstance(examples, list):
                    row[f"example@{lang}"] = "|".join(examples)
                else:
                    row[f"example@{lang}"] = examples
                    
            # Handle history notes in all available languages
            for lang, history_notes in concept.get("historyNote", {}).items():
                if isinstance(history_notes, list):
                    row[f"historyNote@{lang}"] = "|".join(history_notes)
                else:
                    row[f"historyNote@{lang}"] = history_notes
                    
            # Handle change notes in all available languages
            for lang, change_notes in concept.get("changeNote", {}).items():
                if isinstance(change_notes, list):
                    row[f"changeNote@{lang}"] = "|".join(change_notes)
                else:
                    row[f"changeNote@{lang}"] = change_notes
                    
            # Handle editorial notes in all available languages
            for lang, editorial_notes in concept.get("editorialNote", {}).items():
                if isinstance(editorial_notes, list):
                    row[f"editorialNote@{lang}"] = "|".join(editorial_notes)
                else:
                    row[f"editorialNote@{lang}"] = editorial_notes
                    
            # Handle broader relationships
            broader_uris = []
            for broader in concept.get("broader", []):
                if broader and broader.get("uri"):
                    broader_uris.append(broader["uri"])
            if broader_uris:
                row["broader"] = "|".join(broader_uris)
            else:
                row["broader"] = "top"
                
            # Handle narrower relationships
            narrower_uris = []
            for narrower in concept.get("narrower", []):
                if narrower and narrower.get("uri"):
                    narrower_uris.append(narrower["uri"])
            if narrower_uris:
                row["narrower"] = "|".join(narrower_uris)
                
            # Handle related relationships
            related_uris = []
            for related in concept.get("related", []):
                if related and related.get("uri"):
                    related_uris.append(related["uri"])
            if related_uris:
                row["related"] = "|".join(related_uris)
                
            # Handle exact matches
            exact_matches = []
            for match in concept.get("exactMatch", []):
                if match and match.get("uri"):
                    exact_matches.append(match["uri"])
            if exact_matches:
                row["exactMatch"] = "|".join(exact_matches)
                
            # Handle close matches
            close_matches = []
            for match in concept.get("closeMatch", []):
                if match and match.get("uri"):
                    close_matches.append(match["uri"])
            if close_matches:
                row["closeMatch"] = "|".join(close_matches)
                
            # Handle broad matches
            broad_matches = []
            for match in concept.get("broadMatch", []):
                if match and match.get("uri"):
                    broad_matches.append(match["uri"])
            if broad_matches:
                row["broadMatch"] = "|".join(broad_matches)
                
            # Handle narrow matches
            narrow_matches = []
            for match in concept.get("narrowMatch", []):
                if match and match.get("uri"):
                    narrow_matches.append(match["uri"])
            if narrow_matches:
                row["narrowMatch"] = "|".join(narrow_matches)
                
            # Handle related matches
            related_matches = []
            for match in concept.get("relatedMatch", []):
                if match and match.get("uri"):
                    related_matches.append(match["uri"])
            if related_matches:
                row["relatedMatch"] = "|".join(related_matches)
                
            # Handle sources
            sources = []
            for source in concept.get("source", []):
                if isinstance(source, str):
                    sources.append(source)
                elif "uri" in source:
                    sources.append(source["uri"])
                elif "prefLabel" in source:
                    for lang, label in source["prefLabel"].items():
                        sources.append(label)
            if sources:
                row["source"] = "|".join(sources)
                
            # Handle seeAlso
            see_also = []
            for item in concept.get("seeAlso", []):
                if isinstance(item, str):
                    see_also.append(item)
                elif "uri" in item:
                    see_also.append(item["uri"])
            if see_also:
                row["seeAlso"] = "|".join(see_also)
                
            rows.append(row)
            
        return pd.DataFrame(rows)

def row2Triple(value, g, subj, pred, obj, isLang, namespace, scheme, lang):

    value = value.strip()
    if value == "":
        print("Empty cell")
        print(subj, pred, obj)
        return g
    if obj == URIRef:
        if pred in [SKOS.broader, SKOS.narrower, SKOS.related]:
            if value != "top":
                g.add ((subj, pred, URIRef(namespace + value)))
                if pred == SKOS.broader:
                    g.add ((URIRef(namespace + value), SKOS.narrower, subj))
            else:
                g.add ((subj, SKOS.topConceptOf, scheme))
        else:
            g.add ((subj, pred, URIRef(value)))
    else:
        if isLang:
            g.add ((subj, pred, obj(value, lang= lang)))
        else:
            g.add ((subj, pred, obj(value)))
    return g

def propertyWalk(df, row, g, subj, scheme, namespace):

    #for prop, pred, obj, isLang in propertyDict:
    for col in df.columns:
        if "@" in col:
            colProp, lang = col.split("@")
        else:
            colProp, lang = col, baseLanguageLabel
        
        if colProp in propertyDict:
            pred, obj, isLang = propertyDict[colProp]
            if not isinstance(row[col], float):
                if seperator in row[col]:
                    seperatedValues = row[col].split(seperator)
                else:
                    seperatedValues = [row[col]]
                for value in seperatedValues:
                    g = row2Triple(value, g, subj, pred, obj, isLang, namespace, scheme, lang)
    return g

def df2Skos(schemeDf, conceptsDf):

    g = Graph()
    # extract and declare conceptScheme and namespace
    for index, row in schemeDf.iterrows():
        if row["ConceptScheme"] and isinstance(row["ConceptScheme"], str) and row["namespace"] and isinstance(row["namespace"], str):
            scheme = URIRef(row["ConceptScheme"])
            g.add ((scheme, RDF.type, SKOS.ConceptScheme))
            namespace = row["namespace"]
            g.add((scheme, VANN.preferredNamespaceUri, Literal(namespace)))
            g = propertyWalk(schemeDf, row, g, scheme, scheme, namespace)

    # declare concepts
    for index, row in conceptsDf.iterrows():
        # check if prefLabel and notation have a non empty string value
        if row["prefLabel"+"@" + baseLanguageLabel] and isinstance(row["prefLabel"+"@" + baseLanguageLabel], str) and row["notation"] and isinstance(row["notation"], str):
            concept = URIRef(namespace + row['notation'])
            g.add ((concept, RDF.type, SKOS.Concept))
            g.add ((concept, SKOS.inScheme, scheme))
            g = propertyWalk(conceptsDf, row, g, concept, scheme, namespace)
            if row["broader"] == "top":
                g.add ((scheme, SKOS.hasTopConcept, concept))
                g.add ((concept, SKOS.topConceptOf, scheme))
    return g

def main():
    # Use JSON approach directly (more reliable for maintaining structure)
    print("Using JSON approach to maintain proper structure")
    
    # Get scheme metadata
    scheme_url = "https://api.dante.gbv.de/voc/leiza_archlink?format=jskos"
    scheme_data = fetch_json(scheme_url)
    
    # Get top concepts
    top_concepts_url = "https://api.dante.gbv.de/voc/leiza_archlink/top?format=jskos"
    top_concepts = fetch_json(top_concepts_url)
    
    # Get all concepts by fetching descendants for each top concept
    all_concepts = []
    print(f"Found {len(top_concepts)} top concepts. Fetching all descendants...")
    
    for i, concept in enumerate(top_concepts):
        if not concept or not concept.get("uri"):
            continue
            
        concept_uri = concept["uri"]
        print(f"  Fetching descendants for concept {i+1}/{len(top_concepts)}: {concept_uri}")
        
        # Fetch all descendants recursively with complete properties
        descendants_url = f"https://api.dante.gbv.de/descendants?uri={concept_uri}&format=jskos&properties=*"
        descendants = fetch_json(descendants_url)
        all_concepts.extend(descendants)
    
    # Convert to DataFrames matching original CSV structure
    print("Converting JSON data to DataFrames")
    schemeDf = convert_json_to_dataframe(scheme_data, is_scheme=True)
    conceptsDf = convert_json_to_dataframe(all_concepts)
    
    # Generate SKOS graph using existing transformation functions
    print("Generating SKOS graph from DataFrames")
    graph = df2Skos(schemeDf, conceptsDf)
    
    # Fix concept scheme URI to use the canonical identifier
    print("Updating scheme URI to canonical identifier")
    
    # The expected canonical URI
    canonical_scheme_uri = "https://www.w3id.org/archlink/terms/conservationthesaurus"
    
    # Create a new graph with corrected URIs
    g_fixed = Graph()
    
    # Copy all triples with possible URI replacement
    for s, p, o in graph:
        # Replace scheme URI in subject position
        if str(s) == str(schemeDf["ConceptScheme"][0]):
            s = URIRef(canonical_scheme_uri)
            
        # Replace scheme URI in object position
        if str(o) == str(schemeDf["ConceptScheme"][0]):
            o = URIRef(canonical_scheme_uri)
            
        # Add to new graph with fixed URIs
        g_fixed.add((s, p, o))
    
    # Save the canonical URI as preferred namespace
    g_fixed.add((URIRef(canonical_scheme_uri), VANN.preferredNamespaceUri, 
                Literal("https://www.w3id.org/archlink/terms/conservationthesaurus/")))
    
    # Final validation
    print(f"Total triples after processing: {len(g_fixed)}")
    
    # Output to file
    print("Writing final output")
    g_fixed.serialize(destination='scheme.ttl', format='turtle')
    
    print(f"\nSuccessfully generated Turtle output with {len(g_fixed)} triples")

baseLanguageLabel = "de"

propertyDict = {
    # SKOS Mapping Properties
    "broadMatch": (SKOS.broadMatch, URIRef, False),
    "narrowMatch": (SKOS.narrowMatch, URIRef, False),
    "relatedMatch": (SKOS.relatedMatch, URIRef, False),
    "closeMatch": (SKOS.closeMatch, URIRef, False),
    "exactMatch": (SKOS.exactMatch, URIRef, False),
    
    # SKOS Semantic Relations
    "broader": (SKOS.broader, URIRef, False),
    "narrower": (SKOS.narrower, URIRef, False),
    "related": (SKOS.related, URIRef, False),

    # SKOS Lexical Labels
    "prefLabel": (SKOS.prefLabel, Literal, True),
    "altLabel": (SKOS.altLabel, Literal, True),
    "hiddenLabel": (SKOS.hiddenLabel, Literal, True),   
    
    # SKOS Notations
    "notation": (SKOS.notation, Literal, False),

    # SKOS Documentation Properties
    "note": (SKOS.note, Literal, True),
    "changeNote": (SKOS.changeNote, Literal, True),
    "definition": (SKOS.definition, Literal, True),
    "editorialNote": (SKOS.editorialNote, Literal, True),
    "example": (SKOS.example, Literal, True),
    "historyNote": (SKOS.historyNote, Literal, True),
    "scopeNote": (SKOS.scopeNote, Literal, True),

    # DCTERMS Metadata Properties
    "creator": (DCTERMS.creator, Literal, False),
    "contributor": (DCTERMS.contributor, Literal, False),
    "publisher": (DCTERMS.publisher, Literal, False),
    "rights": (DCTERMS.rights, Literal, False),
    "source": (DCTERMS.source, Literal, False),
    "subject": (DCTERMS.subject, Literal, True),
    "created": (DCTERMS.created, Literal, False),
    "license": (DCTERMS.license, URIRef, False),
    "modified": (DCTERMS.modified, Literal, False),
    "title": (DCTERMS.title, Literal, True),
    "description": (DCTERMS.description, Literal, True),
    
    # Other Properties
    "seeAlso": (RDFS.seeAlso, Literal, False),
}

seperator = "|"

if __name__ == "__main__":
    main()