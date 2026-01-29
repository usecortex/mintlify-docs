import json
import sys

# Get generation type from command line argument
# Usage: python fix_openapi.py [docs|sdk]
# Default: sdk
if len(sys.argv) > 1:
    genr_type = sys.argv[1].lower()
    if genr_type not in ['docs', 'sdk']:
        print(f"Error: Invalid argument '{sys.argv[1]}'. Use 'docs' or 'sdk'")
        sys.exit(1)
else:
    genr_type = 'sdk'  # Default to sdk mode

print(f"Running in '{genr_type}' mode")

defaults = {
    "tenant_id": "tenant_1234",
    "sub_tenant_id": "sub_tenant_4567",
    "memory_id": "memory_1234",
    "user_memory": "I prefer detailed technical explanations and works in the Pacific timezone",
    "query": "Which mode does user prefer",
    "user_query": "Which mode does user prefer",
    "max_count": 5,
    "web_url": "https://www.usecortex.ai/",
    "file_id": "CortexDoc1234",
    "id": "CortexDoc1234",
    "user_name": "John Doe",
    # "message": "<string>",÷
    "embeddings": [[0.123413, 0.655367, 0.987654, 0.123456, 0.789012], [0.123413, 0.655367, 0.987654, 0.123456, 0.789012]],
    "question": "What is Cortex AI",
    "session_id": "chat_session_1234",
    "tenant_metadata_schema": [
        {
            "key": "department",
            "type": "string",
            "searchable": True,
            "filterable": True
        },
        {
            "key": "compliance_framework",
            "type": "string",
            "searchable": True,
            "filterable": False
        },
        {
            "key": "data_classification",
            "type": "string",
            "searchable": False,
            "filterable": True
        }
    ],
    "operator": "and",
    "user_message": "I prefer detailed technical explanations and works in the Pacific timezone",
    # "tenant_metadata": "{}",
    # "document_metadata": "{}",
    "sub_tenant_ids": ["sub_tenant_1234", "sub_tenant_4567"],
    "ids": ["CortexDoc1234", "CortexDoc4567"],
    "chunk_ids": ["CortexEmbeddings123_0", "CortexEmbeddings123_1"],
    "user_memories": [
        {
            "memory_id": "memory_1234",
            "memory_content": "I prefer detailed technical explanations and works in the Pacific timezone"
        },
        {
            "memory_id": "memory_4567",
            "memory_content": "I prefer dark mode"
        }
    ],
    "retrieved_user_memories": [
        {
            "memory_id": "memory_1234",
            "memory_content": "I prefer detailed technical explanations and works in the Pacific timezone"
        },
        {
            "memory_id": "memory_4567",
            "memory_content": "I prefer dark mode"
        }
    ],
    "generated_user_memories": [
        {
            "memory_id": "memory_1234",
            "memory_content": "User prefers detailed technical explanations and works in the Pacific timezone"
        },
        {
            "memory_id": "memory_4567",
            "memory_content": "User prefers dark mode"
        }
    ],
    "uploaded":  [
        {
            "file_id": "CortexDoc1234",
            "filename": "document1.pdf"
        },
        {
            "file_id": "CortexDoc4567",
            "filename": "document2.docx"
        }
    ]
}

full_text_query = "John Smith Jake"

update_embeddings_emb = {
    "CortexEmbeddings123_0": [0.123413, 0.655367, 0.987654, 0.123456, 0.789012],
    "CortexEmbeddings123_1": [0.123413, 0.655367, 0.987654, 0.123456, 0.789012]
}

example_exclusion_by_schema_name = {
    # "Body_upload_files_upload_upload_document_post": ["tenant_metadata", "document_metadata"]
    "SourceModel": ["attachments"],
    "EmbeddingsSearchData": ["scores", "chunk_ids"]
}

defaults_by_schema_name = {
    "Body_batch_upload_upload_batch_upload_post": {
        "tenant_metadata": "{}",
        "document_metadata": "{}"
    },
    "Body_batch_update_upload_batch_update_patch": {
        "tenant_metadata": "{}",
        "document_metadata": "{}"
    }
} if genr_type != 'sdk' else {}

schemas_to_ignore = {"ErrorResponse"}

properties_to_ignore = {"message", "status", "tenant_metadata",
                        "document_metadata", "files", "sources", "not_found_chunk_ids"}

OPEN_API_PATH = "./api-reference/openapi.json"

with open(OPEN_API_PATH, "r") as f:
    openapi = json.load(f)

def nullify_endpoint_descriptions(spec: dict) -> None:
    """
    For every path+method operation, set `description` to JSON null.
    (Python `None` serializes to `null` in json.dump.)
    """
    paths = spec.get("paths", {})
    if not isinstance(paths, dict):
        return

    for _, path_item in paths.items():
        if not isinstance(path_item, dict):
            continue
        for method, operation in path_item.items():
            # Skip non-operation keys allowed in a Path Item Object
            if method in {"parameters", "summary", "description"}:
                continue
            if not isinstance(operation, dict):
                continue
            operation["description"] = None

print("Adding example values to query params")
for endpoint in openapi["paths"]:
    for method in openapi["paths"][endpoint]:
        if "parameters" in openapi["paths"][endpoint][method]:
            for param in openapi["paths"][endpoint][method]["parameters"]:
                if param["in"] == "query":
                    param["schema"]["example"] = defaults.get(
                        param["name"], f"<{type(param['name']).__name__}>")
print("Default values added to query params.")

print("Adding example values to components.schemas")
if "components" in openapi and "schemas" in openapi["components"]:
    for schema_name, schema_def in openapi["components"]["schemas"].items():
        if schema_name in schemas_to_ignore:
            continue
        if "properties" in schema_def:
            for prop_name, prop_def in schema_def["properties"].items():
                if schema_name in defaults_by_schema_name:
                    if prop_name in defaults_by_schema_name[schema_name]:
                        prop_def["default"] = defaults_by_schema_name[schema_name][prop_name]
                        print(f"Adding example value for {prop_name} for {schema_name}")
                        continue
                if prop_name in properties_to_ignore:
                    print(f"Skipping {prop_name} for {schema_name}")
                    continue
                if schema_name in example_exclusion_by_schema_name:
                    if prop_name in example_exclusion_by_schema_name[schema_name]:
                        print(f"Skipping {prop_name} for {schema_name}")
                        continue
                # Special case for FullTextSearchRequest query property
                if schema_name == "FullTextSearchRequest" and prop_name == "query":
                    prop_def["example"] = full_text_query
                elif schema_name == "EmbeddingsUpdateRequest" and prop_name == "embeddings":
                    prop_def["example"] = update_embeddings_emb
                elif prop_name in defaults:
                    prop_def["example"] = defaults[prop_name]
                elif "type" in prop_def:
                    if prop_def["type"] == "string":
                        prop_def["example"] = f"<{prop_name}>"
                    elif prop_def["type"] == "integer":
                        prop_def["example"] = 1
                    elif prop_def["type"] == "number":
                        prop_def["example"] = 1.0
                    elif prop_def["type"] == "boolean":
                        prop_def["example"] = True
                    elif prop_def["type"] == "array":
                        prop_def["example"] = []            
print("Default values added to components.schemas.")


property_tag_to_hide = "x-cortex-docs-hide"


def recursive_filter(data):
    """
    Recursively filters a Python object (dict or list) to remove elements
    containing the property_tag_to_hide.
    """
    # If the data is a dictionary...
    if isinstance(data, dict):
        # Base case: If the hide tag is in the current dictionary,
        # return None to signal its removal.
        if property_tag_to_hide in data:
            return None

        # Recursive step: Build a new dictionary
        new_dict = {}
        for key, value in data.items():
            # Recursively filter the value
            filtered_value = recursive_filter(value)
            # Only add the key-value pair if the value was not filtered out
            if filtered_value is not None:
                new_dict[key] = filtered_value
        return new_dict

    # If the data is a list...
    elif isinstance(data, list):
        # Recursive step: Build a new list
        new_list = []
        for item in data:
            # Recursively filter the item
            filtered_item = recursive_filter(item)
            # Only add the item if it was not filtered out
            if filtered_item is not None:
                new_list.append(filtered_item)
        return new_list

    # If the data is any other type (string, int, etc.), return it as is.
    else:
        return data


# Process the original openapi spec
nullify_endpoint_descriptions(openapi)
final_open_api_spec = recursive_filter(openapi)

with open(OPEN_API_PATH, "w") as f:
    json.dump(final_open_api_spec, f, indent=2)
