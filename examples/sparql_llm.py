import litellm
from SPARQLWrapper import SPARQLWrapper, JSON
import re
import json
import os

# ==========================================
# CONFIGURATION
# ==========================================

# 1. LLM Configuration (llama.cpp via LiteLLM)
# Ensure your llama.cpp server is running with --server --port 8080
LLM_API_BASE = "http://localhost:8080/v1"
LLM_MODEL_NAME = "openai/GLM-4.7-Flash-UD-Q4_K_XL.gguf"  # LiteLLM proxy name, usually matches the model you are running

# 2. SPARQL Configuration
# Local VibeGraph SPARQL endpoint
SPARQL_ENDPOINT = "http://localhost:5000/sparql/query"

# 3. Namespace Configuration
# Load from nsprefixes.json if available
NS_PREFIXES_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "backend", "nsprefixes.json"
)
NS_PREFIXES = {}

try:
    with open(NS_PREFIXES_FILE, "r", encoding="utf-8") as f:
        ns_data = json.load(f)
        for prefix, uri in ns_data.items():
            NS_PREFIXES[prefix] = uri
except Exception as e:
    print(f"Could not load namespace prefixes: {e}")
    # Fallback default prefixes
    NS_PREFIXES = {
        "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
        "owl": "http://www.w3.org/2002/07/owl#",
        "vg": "http://vibe.graph/default/",
    }

# ==========================================
# SETUP
# ==========================================

# Initialize LiteLLM
# We set a dummy key because local servers don't always require one,
# but LiteLLM checks for it.
litellm.api_key = "dummy-key"
litellm.set_verbose = False

# Initialize SPARQL Client
sparql = SPARQLWrapper(SPARQL_ENDPOINT)
sparql.setReturnFormat(JSON)

# ==========================================
# FUNCTIONS
# ==========================================


def get_sparql_query(user_question, available_prefixes=None):
    """
    Uses the LLM to convert a natural language question into SPARQL.

    Parameters
    ----------
    user_question : str
        The natural language question to convert
    available_prefixes : dict, optional
        Dictionary of namespace prefixes available in the graph

    Returns
    -------
    str or None
        Generated SPARQL query or None if failed
    """
    # Build system prompt with available prefixes
    prefix_info = "\n\nAvailable namespace prefixes:"
    if available_prefixes:
        for prefix, uri in available_prefixes.items():
            prefix_info += f"\nPREFIX {prefix}: <{uri}>"
    else:
        prefix_info = "\n\nUse standard RDF/S prefixes (rdf, rdfs, owl) and any others that seem appropriate."

    system_prompt = f"""
    You are an expert SPARQL developer. Your task is to convert a user's 
    natural language question into a valid SPARQL SELECT query.
    
    {prefix_info}
    
    Return ONLY the raw SPARQL code. Do not include markdown formatting (like ```sparql).
    If you're unsure about the schema, use generic queries with common predicates like rdf:type, rdfs:label, etc.
    """

    user_prompt = f"Question: {user_question}"

    try:
        response = litellm.completion(
            model=LLM_MODEL_NAME,
            api_base=LLM_API_BASE,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
        )

        # Extract text from the response
        raw_text = response.choices[0].message.content

        print(f"raw response : --\n{raw_text}\n--\n")

        # Clean the text: remove markdown code blocks if present
        clean_text = re.sub(r"```sparql|```sql|```", "", raw_text).replace('</|assistant|>', '').strip()

        return clean_text

    except Exception as e:
        print(f"Error generating SPARQL: {e}")
        return None


def execute_sparql(query):
    """
    Executes the SPARQL query and returns the results.

    Parameters
    ----------
    query : str
        SPARQL query string

    Returns
    -------
    dict or None
        Query results in JSON format or None if failed
    """
    try:
        sparql.setQuery(query)
        results = sparql.query()
        return results.convert()
    except Exception as e:
        print(f"Error executing SPARQL: {e}")
        return None


def explain_results(results, user_question):
    """
    Uses the LLM to explain the SPARQL results in natural language.

    Parameters
    ----------
    results : dict
        Query results from SPARQL endpoint
    user_question : str
        Original user question

    Returns
    -------
    str
        Human-readable explanation
    """
    # Convert results to a readable string for the LLM
    # We limit the preview to avoid hitting token limits with huge datasets
    if isinstance(results, dict) and "results" in results:
        # VibeGraph format
        result_count = results.get("count", 0)
        vars_list = results.get("vars", [])
        results_preview = f"Found {result_count} results with variables: {vars_list}"

        if (
            result_count > 0
            and "results" in results
            and isinstance(results["results"], list)
        ):
            results_preview += (
                f"\nFirst 3 results:\n{json.dumps(results['results'][:3], indent=2)}"
            )
    else:
        # Fallback for other formats
        results_preview = json.dumps(results, indent=2)

    system_prompt = """
    You are a helpful SPARQL data analyst assistant. 
    The user asked: "{question}"
    
    Here are the raw results from the triple store:
    {results}
    
    Please explain these results to the user in simple, human-readable language.
    """

    user_prompt = "Please explain the data above."

    try:
        response = litellm.completion(
            model=LLM_MODEL_NAME,
            api_base=LLM_API_BASE,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt.format(
                        question=user_question, results=results_preview
                    ),
                },
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
        )

        return response.choices[0].message.content

    except Exception as e:
        print(f"Error explaining results: {e}")
        return "Sorry, I couldn't generate an explanation."


#
#
#


def analyze_intent(user_input):
    """
    Analyze the user's question to understand query intent.

    Parameters
    ----------
    user_input : str
        Natural language question

    Returns
    -------
    dict or None
        Query intent analysis or None if failed
    """
    system_prompt = """
    Analyze the user's question for a Knowledge Graph query. 
    Output ONLY a JSON object with this schema:
    {
      "intent": "SELECT" | "COUNT" | "ASK" | "DESCRIBE",
      "main_subject": "the primary entity or class",
      "properties": ["list of relationships or attributes requested"],
      "constraints": ["any filters like dates, locations, or limits"]
    }
    """
    try:
        response = litellm.completion(
            model=LLM_MODEL_NAME,
            api_base=LLM_API_BASE,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Question: {user_input}"},
            ],
            response_format={"type": "json_object"},  # Ensures valid JSON output
        )
        content = response.choices[0].message.content
        if content:
            return json.loads(content)
        return None
    except Exception as e:
        print(f"Analysis failed: {e}")
        return None


def find_uris(label_keyword):
    """
    Search any KG for URIs that match a keyword using standard RDFS labels.

    Parameters
    ----------
    label_keyword : str
        Keyword to search for in labels

    Returns
    -------
    dict or None
        Query results or None if failed
    """
    discovery_query = f"""
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT DISTINCT ?uri ?label WHERE {{
      ?uri rdfs:label ?label .
      FILTER(contains(lcase(str(?label)), lcase("{label_keyword}")))
    }} LIMIT 3
    """
    return execute_sparql(discovery_query)


def find_uri_matches(term):
    """
    A generic tool to find URIs in any KG by searching labels.
    Works best on graphs that use rdfs:label or skos:prefLabel.

    Parameters
    ----------
    term : str
        Search term for labels

    Returns
    -------
    dict or None
        Query results or None if failed
    """
    search_query = f"""
    SELECT DISTINCT ?uri ?label WHERE {{
      ?uri rdfs:label ?label .
      FILTER(regex(str(?label), "{term}", "i"))
    }} LIMIT 5
    """
    return execute_sparql(search_query)


def get_schema_info():
    """
    Returns a summary of the most common classes and properties in the KG.

    Returns
    -------
    dict
        Schema information with classes and properties
    """
    discovery_query = """
    SELECT DISTINCT ?class (COUNT(?s) AS ?count) WHERE { ?s a ?class }
    GROUP BY ?class ORDER BY DESC(?count) LIMIT 10
    """
    try:
        sparql.setQuery(discovery_query)
        res = sparql.query().convert()
        if isinstance(res, dict) and "results" in res:
            if "bindings" in res["results"]:
                classes = [
                    b.get("class", {}).get("value", "")
                    for b in res["results"]["bindings"]
                ]
                return {
                    "top_classes": classes,
                    "message": f"Found {len(classes)} distinct classes",
                }
        return {
            "top_classes": [],
            "message": "Could not discover classes automatically",
        }
    except Exception as e:
        print(f"Schema discovery error: {e}")
        return {"top_classes": [], "message": "Could not discover schema automatically"}


def execute_sparql_with_repair(query):
    """
    Executes query and returns results OR a detailed error message.

    Parameters
    ----------
    query : str
        SPARQL query to execute

    Returns
    -------
    dict
        Result with status and data/error message
    """
    try:
        sparql.setQuery(query)
        return {"status": "success", "data": sparql.query().convert()}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def run_generic_query(user_question):
    """
    Run a complete query workflow with schema discovery and error recovery.

    Parameters
    ----------
    user_question : str
        Natural language question

    Returns
    -------
    dict or None
        Query results or None if all attempts failed
    """
    # Step 1: Bootstrap context by discovering the schema
    schema_info = get_schema_info()
    schema_context = schema_info.get("message", "No schema information available")

    messages = [
        {
            "role": "system",
            "content": f"You are a SPARQL expert. Use this schema context: {schema_context}. Return ONLY raw SPARQL.",
        },
        {"role": "user", "content": f"Question: {user_question}"},
    ]

    for attempt in range(3):
        # Generate the query
        response = litellm.completion(
            model=LLM_MODEL_NAME, api_base=LLM_API_BASE, messages=messages
        )
        query = response.choices[0].message.content.strip()

        print(f"--- Attempt {attempt + 1} Query ---\n{query}")

        # Execute and check for errors
        result = execute_sparql_with_repair(query)

        if result["status"] == "success":
            print("Query Successful!")
            return result["data"]
        else:
            print(f"Query Failed: {result['message'][:100]}...")
            # Feedback Loop: Feed the error back to the LLM
            messages.append({"role": "assistant", "content": query})
            messages.append(
                {
                    "role": "user",
                    "content": f"That query failed with error: {result['message']}. Please fix it.",
                }
            )

    return None


def run_agentic_workflow(user_input):
    """
    Run a complete agentic workflow to answer user questions.

    Parameters
    ----------
    user_input : str
        Natural language question

    Returns
    -------
    dict or None
        Query results or None if failed
    """
    # 1. Understand what they want
    blueprint = analyze_intent(user_input)
    if not blueprint:
        print("Could not analyze intent")
        return None

    print(f"Intent Blueprint: {json.dumps(blueprint, indent=2)}")

    # 2. Find the real terms in the KG
    subject_matches = find_uris(blueprint.get("main_subject", ""))
    if not subject_matches:
        print("Could not find matching URIs for main subject")
        return None

    # 3. Final Prompt (The 'Synthesizer')
    # We give the LLM the EXACT URIs we found so it doesn't guess.
    final_prompt = f"""
    Based on this blueprint: {blueprint}
    And these discovered URIs from the database: {subject_matches}
    Write a valid SPARQL query for this endpoint.
    """

    # Generate query from final prompt
    response = litellm.completion(
        model=LLM_MODEL_NAME,
        api_base=LLM_API_BASE,
        messages=[
            {
                "role": "system",
                "content": "You are a SPARQL expert. Return ONLY raw SPARQL.",
            },
            {"role": "user", "content": final_prompt},
        ],
    )
    query = response.choices[0].message.content.strip()

    # Execute the query
    return execute_sparql_with_repair(query)


# ==========================================
# MAIN EXECUTION
# ==========================================


def format_results(results):
    """
    Format SPARQL results in a user-friendly way.

    Parameters
    ----------
    results : dict
        Query results from SPARQL endpoint

    Returns
    -------
    str
        Formatted results string
    """
    if not results or not isinstance(results, dict):
        return "No results to display"

    result_count = results.get("count", 0)
    vars_list = results.get("vars", [])
    graph_id = results.get("graph_id", "unknown")

    output = f"Query Results (Graph: {graph_id})\n"
    output += f"Count: {result_count}\n"
    output += f"Variables: {', '.join(vars_list)}\n\n"

    if result_count == 0:
        return output + "No data found matching the query.\n"

    # Display results in a table-like format
    if "results" in results and isinstance(results["results"], list):
        for i, row in enumerate(results["results"][:5], 1):
            output += f"Result {i}:\n"
            for var in vars_list:
                value = row.get(var, {}).get("value", "N/A")
                output += f"  {var}: {value}\n"
            output += "\n"

    if result_count > 5:
        output += f"... and {result_count - 5} more results\n"

    return output


if __name__ == "__main__":
    print("--- SPARQL Chatbot with Llama.cpp ---")
    print(f"Available namespace prefixes: {NS_PREFIXES}\n")

    # Example User Question
    user_input = "List all entities and their types"

    print(f"User: {user_input}\n")

    # Step 1: Generate SPARQL with available prefixes
    sparql_query = get_sparql_query(user_input, NS_PREFIXES)

    if sparql_query:
        print(f"Generated SPARQL:\n'{sparql_query}'\n")

        # Step 2: Execute SPARQL
        raw_results = execute_sparql(sparql_query)

        if raw_results:
            # Display formatted results
            formatted = format_results(raw_results)
            print(formatted)

            if raw_results.get("count", 0) > 0:
                # Step 3: Explain Results
                explanation = explain_results(raw_results, user_input)

                print("\n--- AI Explanation ---")
                print(explanation)
            else:
                print("\n I have no information about the content in the graph")
                
        else:
            print("Failed to execute SPARQL query.")
    else:
        print("Failed to generate SPARQL query.")

    # print("\n--- Testing Agentic Workflow ---")
    # user_input2 = "Find entities related to food"
    # print(f"User: {user_input2}\n")

    # agentic_result = run_agentic_workflow(user_input2)
    # if agentic_result and agentic_result["status"] == "success":
    #     formatted = format_results(agentic_result["data"])
    #     print(formatted)
    # else:
    #     print("Agentic workflow failed.")
