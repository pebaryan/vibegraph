from flask import Blueprint, jsonify, request
import litellm

from llm_config import load_config, save_config, public_config
from routes.graphs import graph_manager
from routes.search import search_engine
import re
from difflib import SequenceMatcher
import json

llm_bp = Blueprint("llm_bp", __name__)


def _schema_context(graph_id: str) -> str:
    graph_obj = graph_manager.get_graph_object(graph_id)
    if not graph_obj:
        return ""


def _prefix_context() -> str:
    prefixes = graph_manager.prefixes or {}
    if not prefixes:
        return ""
    lines = [f"PREFIX {k}: <{v}>" for k, v in prefixes.items()]
    return "\n".join(lines)


def _ensure_prefixes(query: str) -> str:
    if "PREFIX" in query.upper():
        return query
    # If query uses prefixed names, prepend all known prefixes.
    if ":" in query:
        prefix_block = _prefix_context()
        if prefix_block:
            return f"{prefix_block}\n\n{query}"
    return query


def _extract_prefixed_terms(query: str):
    terms = []
    for line in query.splitlines():
        stripped = line.strip()
        if stripped.upper().startswith("PREFIX") or stripped.upper().startswith("BASE"):
            continue
        for match in re.finditer(r"\b([A-Za-z_][\w\-]*)\:([A-Za-z_][\w\-.]*)\b", line):
            prefix, local = match.group(1), match.group(2)
            terms.append((prefix, local))
    return terms


def _extract_json_payload(raw: str):
    if not raw:
        return None
    try:
        return json.loads(raw)
    except Exception:
        pass
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        return None
    snippet = match.group(0)
    try:
        return json.loads(snippet)
    except Exception:
        return None


def _extract_predicate_terms(query: str):
    predicates = set()
    for line in query.splitlines():
        stripped = line.strip()
        if not stripped or stripped.upper().startswith("PREFIX") or stripped.upper().startswith("BASE"):
            continue
        parts = [part.strip() for part in stripped.split(";") if part.strip()]
        if not parts:
            continue
        first = parts[0]
        match = re.match(r"^\S+\s+([A-Za-z_][\w\-]*\:[A-Za-z_][\w\-.]*)\s+.+", first)
        if match:
            predicates.add(match.group(1))
        for part in parts[1:]:
            match = re.match(r"^([A-Za-z_][\w\-]*\:[A-Za-z_][\w\-.]*)\s+.+", part)
            if match:
                predicates.add(match.group(1))
    return predicates


def _normalize_local(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def _to_prefixed(uri: str):
    for prefix, ns in graph_manager.prefixes.items():
        ns_str = str(ns)
        if uri.startswith(ns_str):
            return f"{prefix}:{uri[len(ns_str):]}"
    return None


def _search_results(query: str, search_by: str, graph_id: str | None):
    results = search_engine.search(query, search_by=search_by)
    if not results or "results" not in results:
        return []
    if graph_id:
        return [r for r in results["results"] if r.get("graph_id") == graph_id]
    return results["results"]


def _search_exact_iri(uri: str, graph_id: str | None) -> bool:
    for result in _search_results(uri, "iri", graph_id):
        if result.get("iri") == uri:
            return True
    return False


def _search_namespace_iris(ns_uri: str, graph_id: str | None):
    matches = []
    for result in _search_results(ns_uri, "iri", graph_id):
        iri = result.get("iri")
        if iri and iri.startswith(ns_uri):
            matches.append(iri)
    return matches


def _search_namespace_entities(ns_uri: str, query: str, search_by: str, graph_id: str | None):
    matches = []
    for result in _search_results(query, search_by, graph_id):
        iri = result.get("iri")
        if iri and iri.startswith(ns_uri):
            matches.append(result)
    return matches


def _candidate_iris_from_search(local_part: str, graph_id: str | None):
    candidates = set()
    for result in _search_results(local_part, "label", graph_id):
        iri = result.get("iri")
        if iri:
            candidates.add(iri)
    for result in _search_results(local_part, "iri", graph_id):
        iri = result.get("iri")
        if iri:
            candidates.add(iri)
    return list(candidates)


def _auto_replace_terms(query: str, graph_id: str | None, question: str | None = None):
    prefixes = graph_manager.prefixes or {}
    if not prefixes:
        return query, {}
    replacements = {}
    terms = _extract_prefixed_terms(query)
    predicate_terms = _extract_predicate_terms(query)
    question_text = question or ""
    question_tokens = re.findall(r"[a-zA-Z]+", question_text.lower())
    stopwords = {
        "a", "an", "the", "of", "to", "in", "on", "for", "with", "and", "or",
        "by", "from", "which", "what", "who", "where", "when", "how", "is",
        "are", "was", "were", "be", "been", "that", "this", "these", "those",
    }
    question_focus = " ".join(token for token in question_tokens if token not in stopwords)
    for prefix, local in terms:
        if prefix not in prefixes:
            continue
        ns_uri = str(prefixes[prefix])
        uri = f"{ns_uri}{local}"
        if _search_exact_iri(uri, graph_id):
            continue

        candidates = _search_namespace_iris(ns_uri, graph_id)
        if candidates:
            target = _normalize_local(local)
            best = None
            best_score = 0.0
            for candidate_uri in candidates:
                cand_local = candidate_uri[len(ns_uri):]
                score = SequenceMatcher(None, target, _normalize_local(cand_local)).ratio()
                if score > best_score:
                    best = cand_local
                    best_score = score
            if best and best_score >= 0.6 and best != local:
                replacements[f"{prefix}:{local}"] = f"{prefix}:{best}"
                continue

        term_key = f"{prefix}:{local}"
        if term_key in predicate_terms and question_focus:
            entities = _search_namespace_entities(ns_uri, question_focus, "label", graph_id)
            if not entities:
                entities = _search_namespace_entities(ns_uri, question_focus, "iri", graph_id)
            if entities:
                question_norm = _normalize_local(question_focus) or _normalize_local(question_text)
                best = None
                best_score = 0.0
                for entity in entities:
                    iri = entity.get("iri")
                    if not iri:
                        continue
                    cand_local = iri[len(ns_uri):]
                    label = entity.get("label") or cand_local
                    score = max(
                        SequenceMatcher(None, question_norm, _normalize_local(label)).ratio(),
                        SequenceMatcher(None, question_norm, _normalize_local(cand_local)).ratio(),
                    )
                    if score > best_score:
                        best = cand_local
                        best_score = score
                if best and best_score >= 0.35 and best != local:
                    replacements[f"{prefix}:{local}"] = f"{prefix}:{best}"
                    continue

        candidates = _candidate_iris_from_search(local, graph_id)
        prefixed = [p for p in (_to_prefixed(c) for c in candidates) if p]
        if not prefixed:
            continue
        target = _normalize_local(local)
        best = None
        best_score = 0.0
        for candidate in prefixed:
            cand_local = candidate.split(":", 1)[1]
            score = SequenceMatcher(None, target, _normalize_local(cand_local)).ratio()
            if score > best_score:
                best = candidate
                best_score = score
        if best and best_score >= 0.6:
            replacements[f"{prefix}:{local}"] = best

    updated = query
    for old, new in replacements.items():
        updated = re.sub(rf"\b{re.escape(old)}\b", new, updated)
    return updated, replacements


def _completion(messages):
    config = load_config()
    if not config.get("enabled"):
        raise ValueError("LLM features are disabled")
    model = config.get("model")
    provider = config.get("provider")
    if not model:
        raise ValueError("LLM model is not configured")
    return litellm.completion(
        model=f"{provider}/{model}",
        api_base=config.get("api_base"),
        api_key=config.get("api_key") or None,
        messages=messages,
        temperature=config.get("temperature"),
        max_tokens=config.get("max_tokens"),
    )


@llm_bp.route("/api/llm/config", methods=["GET", "POST"])
def llm_config_endpoint():
    if request.method == "GET":
        return jsonify(public_config(load_config())), 200

    data = request.get_json(silent=True) or {}
    updated = save_config(data)
    return jsonify(public_config(updated)), 200


@llm_bp.route("/api/llm/sparql", methods=["POST"])
def llm_generate_sparql():
    data = request.get_json(silent=True) or {}
    question = data.get("question")
    graph_id = data.get("graph_id")
    if not question:
        return jsonify({"error": "Question is required"}), 400

    schema = _schema_context(graph_id) if graph_id else ""
    prefixes = _prefix_context()
    system = (
        "You are a SPARQL expert. Return ONLY the raw SPARQL query. "
        "Do not include markdown. Include required PREFIX declarations."
    )
    parts = [f"Question: {question}"]
    if prefixes:
        parts.append(f"Available prefixes:\n{prefixes}")
    if schema:
        parts.append(schema)
    user = "\n".join(parts)

    try:
        response = _completion([
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ])
        query = response.choices[0].message.content.strip()
        query = _ensure_prefixes(query)
        replacements = {}
        if graph_id:
                query, replacements = _auto_replace_terms(query, graph_id, question)
        return jsonify({"query": query, "replacements": replacements}), 200
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@llm_bp.route("/api/llm/repair", methods=["POST"])
def llm_repair_sparql():
    data = request.get_json(silent=True) or {}
    query = data.get("query")
    error = data.get("error")
    if not query or not error:
        return jsonify({"error": "Query and error are required"}), 400

    system = (
        "You are a SPARQL expert. Fix the query based on the error. "
        "Return ONLY the corrected SPARQL query."
    )
    user = f"Query:\n{query}\n\nError:\n{error}"

    try:
        response = _completion([
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ])
        fixed = response.choices[0].message.content.strip()
        return jsonify({"query": fixed}), 200
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@llm_bp.route("/api/llm/explain", methods=["POST"])
def llm_explain_results():
    data = request.get_json(silent=True) or {}
    question = data.get("question")
    results = data.get("results")
    if not results:
        return jsonify({"error": "Results are required"}), 400

    system = (
        "You are a helpful data analyst. Explain the query results clearly and concisely."
    )
    user = f"Question: {question}\nResults:\n{results}"

    try:
        response = _completion([
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ])
        explanation = response.choices[0].message.content.strip()
        return jsonify({"explanation": explanation}), 200
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@llm_bp.route("/api/llm/extract", methods=["POST"])
def llm_extract_entities():
    data = request.get_json(silent=True) or {}
    text = data.get("text")
    if not text:
        return jsonify({"error": "Text is required"}), 400

    system = (
        "You extract entities and relationships from text. "
        "Return ONLY valid JSON with keys: "
        "entities (array of {id, text, type}), "
        "relationships (array of {subject, predicate, object}). "
        "Use entity ids in relationships. Use short ids like e1, e2."
    )
    user = f"Text:\n{text}"

    try:
        response = _completion([
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ])
        raw = response.choices[0].message.content.strip()
        payload = _extract_json_payload(raw)
        if not payload:
            return jsonify({"error": "Failed to parse LLM JSON response", "raw": raw}), 500
        entities = payload.get("entities") or []
        if isinstance(entities, list):
            normalized = []
            for idx, entity in enumerate(entities, start=1):
                if not isinstance(entity, dict):
                    continue
                entity_id = entity.get("id") or f"e{idx}"
                normalized.append({
                    "id": entity_id,
                    "text": entity.get("text") or "",
                    "type": entity.get("type"),
                })
            payload["entities"] = normalized
        else:
            payload["entities"] = []
        relationships = payload.get("relationships")
        payload["relationships"] = relationships if isinstance(relationships, list) else []
        return jsonify(payload), 200
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


def _local_part(iri: str):
    if not iri:
        return ""
    if "#" in iri:
        return iri.rsplit("#", 1)[-1]
    return iri.rsplit("/", 1)[-1]


def _recommend_for_entity(text: str, graph_id: str | None, limit: int = 5):
    candidates = []
    seen = set()
    for result in _search_results(text, "label", graph_id) + _search_results(text, "iri", graph_id):
        iri = result.get("iri")
        if not iri or iri in seen:
            continue
        seen.add(iri)
        label = result.get("label") or iri
        local = _local_part(iri)
        score = max(
            SequenceMatcher(None, _normalize_local(text), _normalize_local(label)).ratio(),
            SequenceMatcher(None, _normalize_local(text), _normalize_local(local)).ratio(),
        )
        candidates.append({
            "iri": iri,
            "label": label,
            "prefixed": _to_prefixed(iri),
            "score": round(score, 3),
        })
    candidates.sort(key=lambda item: item["score"], reverse=True)
    return candidates[:limit]


@llm_bp.route("/api/llm/link", methods=["POST"])
def llm_link_entities():
    data = request.get_json(silent=True) or {}
    graph_id = data.get("graph_id")
    entities = data.get("entities") or []
    limit = data.get("limit") or 5

    if not graph_id:
        return jsonify({"error": "graph_id is required"}), 400
    if not entities:
        return jsonify({"error": "entities are required"}), 400

    recommendations = {}
    for entity in entities:
        text = (entity or {}).get("text")
        entity_id = (entity or {}).get("id") or text
        if not text:
            continue
        recommendations[entity_id] = _recommend_for_entity(text, graph_id, limit)

    return jsonify({"recommendations": recommendations}), 200
