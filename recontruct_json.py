## THIS IS FOR FUTURE WHEN WE SHIFT TO YAML

## RUN THIS TO RECONSTRUCT THE OPENAPI.JSON IF NEEDED
## RENAME THE OLD-OPENAPI TO OPENAPI AND THEN YOU CAN USE THAT
## THIS WILL PRESERVE OUT ABILITY TO GO BACK IF WE EVER WANT

import yaml
import json
from pathlib import Path

def load_yaml(file_path):
    with open(file_path, 'r') as f:
        return yaml.safe_load(f)

def find_key_with_slash_fallback(data, key):
    # Try exact key
    if key in data:
        return data[key]
    # Try with leading slash
    if not key.startswith('/') and ('/' + key) in data:
        return data['/' + key]
    # Try without leading slash
    if key.startswith('/') and key[1:] in data:
        return data[key[1:]]
    # Not found
    raise ValueError(f"Key '{key}' not found. Available keys: {list(data.keys())}")

def resolve_ref(ref, base_path):
    if '#' in ref:
        file_path, internal_path = ref.split('#', 1)
        file_path = file_path.strip()
        internal_path = internal_path.lstrip('/')
        ref_file = (base_path / file_path).resolve()
        data = load_yaml(ref_file)
        return find_key_with_slash_fallback(data, internal_path)
    else:
        # No internal path, just load the file
        ref_file = (base_path / ref).resolve()
        return load_yaml(ref_file)

def resolve_refs(obj, base_path):
    if isinstance(obj, dict):
        if '$ref' in obj:
            resolved = resolve_ref(obj['$ref'], base_path)
            # Recursively resolve refs in the resolved object
            return resolve_refs(resolved, base_path)
        else:
            return {k: resolve_refs(v, base_path) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [resolve_refs(item, base_path) for item in obj]
    else:
        return obj

def yaml_to_json_with_refs(main_file, output_file=None):
    try:
        base_path = Path(main_file).parent
        data = load_yaml(main_file)
        resolved = resolve_refs(data, base_path)
        json_output = json.dumps(resolved, indent=2)
        if output_file:
            with open(output_file, 'w') as f:
                f.write(json_output)
            print(f"Resolved JSON saved to {output_file}")
        return json_output
    except Exception as e:
        print(f"Error: {e}")
        return None


result = yaml_to_json_with_refs('api-reference/openapi.yaml', 'api-reference/openapi.json')
if result is not None:
    print("Conversion successful! Preview:")
    print(result[:500] + "..." if len(result) > 500 else result)
else:
    print("No result to display due to previous errors.")