# SPARQLWrapper test script to validate backend endpoint

from SPARQLWrapper import SPARQLWrapper, JSON

# Endpoint expected to be running locally on port 5000
SPARQL_ENDPOINT = "http://localhost:5000/sparql/query"

# Minimal SPARQLWrapper test for the vibegraph triplestore
# Uses generic prefixes with fallback to dataset-specific ones (update if needed).
SAMPLE_QUERY = """
# Generic SPARQL query for any triples
SELECT ?subject ?predicate ?object WHERE {
  ?subject ?predicate ?object .
}
LIMIT 10
"""


def run_test(query: str = SAMPLE_QUERY) -> None:
    """Execute the SPARQL query and print results in a readable format.

    Parameters
    ----------
    query:
        SPARQL query string. Defaults to SAMPLE_QUERY.
    """
    sparql = SPARQLWrapper(SPARQL_ENDPOINT, returnFormat=JSON)
    print(sparql)
    try:
        sparql.setQuery(query)
        results = sparql.query().convert()

        print("--- SPARQL Result Summary ---")
        print(f"Query returned {results.get('count', 0)} results")
        print(f"Variables: {results.get('vars', [])}")
        print(f"Graph ID: {results.get('graph_id', 'N/A')}")
        print("\n--- Query Execution Successful ---")
    except Exception as exc:
        print(f"Error executing SPARQL query: {exc}")


if __name__ == "__main__":
    run_test()
