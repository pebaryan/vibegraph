import json, os

PREFIX_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../nsprefixes.json")

# Load prefixes from file

def load_prefixes():
    try:
        with open(PREFIX_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}

# Save prefixes to file

def save_prefixes(prefixes):
    try:
        with open(PREFIX_FILE, 'w', encoding='utf-8') as f:
            json.dump(prefixes, f, indent=2)
    except Exception:
        pass

# CRUD operations

def add_prefix(prefix, uri):
    prefixes = load_prefixes()
    if prefix in prefixes:
        raise ValueError("Prefix already exists")
    prefixes[prefix] = uri
    save_prefixes(prefixes)
    return prefixes

def update_prefix(prefix, uri):
    prefixes = load_prefixes()
    if prefix not in prefixes:
        raise ValueError("Prefix does not exist")
    prefixes[prefix] = uri
    save_prefixes(prefixes)
    return prefixes

def remove_prefix(prefix):
    prefixes = load_prefixes()
    if prefix in prefixes:
        del prefixes[prefix]
        save_prefixes(prefixes)
        return True
    return False
