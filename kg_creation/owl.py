# First, you need to install the rdflib library. You can do this with pip:
# pip install rdflib

import rdflib
import sys
import os

def parse_ontology(file_path):
    """
    Parses an OWL ontology file and returns a graph object.

    Args:
        file_path (str): The path to the OWL ontology file (local or URL).

    Returns:
        rdflib.Graph: The graph containing the parsed ontology data, or None if an error occurs.
    """
    g = rdflib.Graph()
    try:
        # The parse() method can handle local files, URLs, and different formats.
        # We specify the format as 'xml' for OWL/RDF, or 'turtle' for .ttl files.
        # It's often best to let rdflib guess the format if the extension is standard.
        print(f"Parsing ontology from: {file_path}")
        g.parse(file_path)
        print("Parsing successful.")
        return g
    except Exception as e:
        print(f"Error parsing ontology: {e}", file=sys.stderr)
        return None

def main():
    """
    Main function to demonstrate parsing and querying an OWL ontology.
    """
    # Example 1: Loading a publicly available OWL file from a URL.
    # Replace this URL with your own local file path or a different URL.
    # This example uses the W3C's pizza ontology, which is a classic example.
    ontology_url = fr"C:\Users\Noodl\Downloads\hp(1).owl"

    # Example 2: To load a local file, uncomment the line below and provide a valid path.
    # Make sure the file `my_ontology.owl` is in the same directory as this script.
    # local_file_path = "my_ontology.owl"

    # Use the URL for the demonstration. You can switch to the local file path.
    graph = parse_ontology(ontology_url)

    if graph:
        # A knowledge graph is a collection of triples (subject, predicate, object).
        print(f"\nGraph contains {len(graph)} triples.")

        # =================================================================
        # 1. SIMPLE ITERATION: Iterate through and print all triples
        # =================================================================
        print("\n--- Printing all triples (first 10 for brevity) ---")
        count = 0
        for s, p, o in graph:
            print(f"Subject: {s}\nPredicate: {p}\nObject: {o}\n")
            count += 1
            if count >= 10:
                print("...")
                break

        # =================================================================
        # 2. SPARQL QUERY: A more powerful way to retrieve specific data
        # =================================================================
        print("\n--- Running a SPARQL query to find all classes ---")

        # SPARQL query to find all subjects that are an rdf:type of owl:Class.
        # We use a namespace manager to make the query cleaner.
        graph.bind("owl", "http://www.w3.org/2002/07/owl#")
        graph.bind("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#")

        query = """
        SELECT ?class
        WHERE {
            ?class rdf:type owl:Class .
        }
        """

        # Execute the query and print the results
        for row in graph.query(query):
            print(f"Found class: {row:class}")

if __name__ == "__main__":
    main()
