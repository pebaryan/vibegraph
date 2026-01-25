import litellm
from SPARQLWrapper import SPARQLWrapper, JSON
import re
import json

# ==========================================
# CONFIGURATION
# ==========================================

# 1. LLM Configuration (llama.cpp via LiteLLM)
# Ensure your llama.cpp server is running with --server --port 8080
LLM_API_BASE = "http://localhost:8080/v1"
LLM_MODEL_NAME = "openai/GLM-4.7-Flash-UD-Q4_K_XL.gguf" # LiteLLM proxy name, usually matches the model you are running

# 2. SPARQL Configuration
# We use DBpedia as an example. You can change this to your local triplestore.
SPARQL_ENDPOINT = "http://localhost:5000/sparql/query"

# ==========================================
# SETUP
# ==========================================

# Initialize LiteLLM
# We set a dummy key because local servers don't always require one, 
# but LiteLLM checks for it.
litellm.api_key = "dummy-key"
litellm.set_verbose=False

# Initialize SPARQL Client
sparql = SPARQLWrapper(SPARQL_ENDPOINT)
sparql.setReturnFormat(JSON)

# ==========================================
# FUNCTIONS
# ==========================================

def get_sparql_query(user_question):
    """
    Uses the LLM to convert a natural language question into SPARQL.
    """
    system_prompt = """
    You are an expert SPARQL developer. Your task is to convert a user's 
    natural language question into a valid SPARQL SELECT query for Wikidata.
    
    Use standard Wikidata prefixes (wd, wds, wdv, wdt, wikibase, p, ps, pq, rdfs, bd).
    Return ONLY the raw SPARQL code. Do not include markdown formatting (like ```sql).
    """
    
    user_prompt = f"Question: {user_question}"

    try:
        response = litellm.completion(
            model=LLM_MODEL_NAME,
            api_base=LLM_API_BASE,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2
        )
        
        # Extract text from the response
        raw_text = response.choices[0].message.content
        
        # Clean the text: remove markdown code blocks if present
        clean_text = re.sub(r'```sparql|```sql|```', '', raw_text).strip()
        
        return clean_text

    except Exception as e:
        print(f"Error generating SPARQL: {e}")
        return None

def execute_sparql(query):
    """
    Executes the SPARQL query and returns the results.
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
    """
    # Convert results to a readable string for the LLM
    # We limit the preview to avoid hitting token limits with huge datasets
    results_preview = json.dumps(results, indent=2)
    
    system_prompt = """
    You are a helpful data analyst assistant. 
    The user asked: "{question}"
    
    Here are the raw results from the database:
    {results}
    
    Please explain these results to the user in simple, human-readable language.
    """
    
    user_prompt = "Please explain the data above."

    try:
        response = litellm.completion(
            model=LLM_MODEL_NAME,
            api_base=LLM_API_BASE,
            messages=[
                {"role": "system", "content": system_prompt.format(question=user_question, results=results_preview)},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3
        )
        
        return response.choices[0].message.content

    except Exception as e:
        print(f"Error explaining results: {e}")
        return "Sorry, I couldn't generate an explanation."
    
#
#
#

def analyze_intent(user_input):
    system_prompt = """
    Analyze the user's question for a Knowledge Graph query. 
    Output ONLY a JSON object with this schema:
    {
      "intent": "SELECT" | "COUNT" | "ASK",
      "main_subject": "the primary entity or class",
      "properties": ["list of relationships or attributes requested"],
      "constraints": ["any filters like dates, locations, or limits"]
    }
    """
    try:
        response = litellm.completion(
            model=LLM_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Question: {user_input}"}
            ],
            response_format={ "type": "json_object" } # Ensures valid JSON output
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"Analysis failed: {e}")
        return None
    
def find_uris(label_keyword):
    """
    Search any KG for URIs that match a keyword using standard RDFS labels.
    """
    discovery_query = f"""
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT DISTINCT ?uri ?label WHERE {{
      ?uri rdfs:label ?label .
      FILTER(contains(lcase(str(?label)), lcase("{label_keyword}")))
    }} LIMIT 3
    """
    # Use your execute_sparql function here
    return execute_sparql(discovery_query)
    
def find_uri_matches(term):
    """
    A generic tool to find URIs in any KG by searching labels.
    Works best on graphs that use rdfs:label or skos:prefLabel.
    """
    search_query = f"""
    SELECT DISTINCT ?uri ?label WHERE {{
      ?uri rdfs:label ?label .
      FILTER(regex(str(?label), "{term}", "i"))
    }} LIMIT 5
    """
    # Execute this on the endpoint to give the LLM real URIs to work with.
    return execute_sparql(search_query)

def get_schema_info():
    """Tool: Returns a summary of the most common classes and properties in the KG."""
    discovery_query = """
    SELECT DISTINCT ?class (COUNT(?s) AS ?count) WHERE { ?s a ?class } 
    GROUP BY ?class ORDER BY DESC(?count) LIMIT 10
    """
    try:
        sparql.setQuery(discovery_query)
        res = sparql.query().convert()
        classes = [b['class']['value'] for b in res['results']['bindings']]
        return f"Top Classes: {', '.join(classes)}"
    except:
        return "Could not discover schema automatically."
    
def execute_sparql_with_repair(query):
    """Tool: Executes query and returns results OR a detailed error message."""
    try:
        sparql.setQuery(query)
        return {"status": "success", "data": sparql.query().convert()}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def run_generic_query(user_question):
    # Step 1: Bootstrap context by discovering the schema
    schema = get_schema_info()
    
    messages = [
        {"role": "system", "content": f"You are a SPARQL expert. Use this schema context: {schema}. Return ONLY raw SPARQL."},
        {"role": "user", "content": f"Question: {user_question}"}
    ]

    for attempt in range(3):
        # Generate the query
        response = litellm.completion(model=LLM_MODEL_NAME, messages=messages)
        query = response.choices[0].message.content.strip()
        
        print(f"--- Attempt {attempt+1} Query ---\n{query}")
        
        # Execute and check for errors
        result = execute_sparql_with_repair(query)
        
        if result["status"] == "success":
            print("Query Successful!")
            return result["data"]
        else:
            print(f"Query Failed: {result['message'][:100]}...")
            # Feedback Loop: Feed the error back to the LLM
            messages.append({"role": "assistant", "content": query})
            messages.append({"role": "user", "content": f"That query failed with error: {result['message']}. Please fix it."})
            
    return None

def run_agentic_workflow(user_input):
    # 1. Understand what they want
    blueprint = analyze_intent(user_input)
    print(f"Intent Blueprint: {json.dumps(blueprint, indent=2)}")

    # 2. Find the real terms in the KG
    subject_matches = find_uris(blueprint['main_subject'])
    # ... repeat for properties ...
    
    # 3. Final Prompt (The 'Synthesizer')
    # We give the LLM the EXACT URIs we found so it doesn't guess.
    final_prompt = f"""
    Based on this blueprint: {blueprint}
    And these discovered URIs from the database: {subject_matches}
    Write a valid SPARQL query for this endpoint.
    """
    
    return generate_and_execute(final_prompt)

# ==========================================
# MAIN EXECUTION
# ==========================================

if __name__ == "__main__":
    print("--- SPARQL Chatbot with Llama.cpp ---")
    
    # Example User Question
    user_input = "How many computer scientists are there from Indonesia?"
    
    print(f"\nUser: {user_input}\n")
    
    # Step 1: Generate SPARQL
    sparql_query = get_sparql_query(user_input)
    
    if sparql_query:
        print(f"Generated SPARQL:\n{sparql_query}\n")
        
        # Step 2: Execute SPARQL
        raw_results = execute_sparql(sparql_query)
        
        if raw_results:
            print(f"Raw Results (First 5 rows):")
            # Just printing a snippet for readability
            for i, row in enumerate(raw_results["results"]["bindings"][:5]):
                print(row)
            
            # Step 3: Explain Results
            explanation = explain_results(raw_results, user_input)
            
            print("\n--- AI Explanation ---")
            print(explanation)
    else:
        print("Failed to generate SPARQL query.")
