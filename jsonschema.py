import json

def generate_schema_from_json(data, key=None):
    """
    Recursively generate a JSON schema from the given JSON data.
    """
    if isinstance(data, dict):
        properties = {k: generate_schema_from_json(v, k) for k, v in data.items()}
        return {"type": "object", "properties": properties}
    elif isinstance(data, list):
        if data:  # Non-empty list
            return {"type": "array", "items": generate_schema_from_json(data[0])}
        else:  # Empty list
            return {"type": "array"}
    elif isinstance(data, str):
        # Special handling for date-like strings, adjust the pattern as needed
        if key and key.lower().replace(" ", "_") == "date_quoted":
            return {"type": "string", "pattern": "^[A-Z]{3} [0-9]{2}, [0-9]{4}$"}
        return {"type": "string"}
    elif isinstance(data, bool):
        return {"type": "boolean"}
    elif isinstance(data, int):
        return {"type": "integer"}
    elif isinstance(data, float):
        return {"type": "number"}
    else:
        return {}

def main():
    json_file_path = 'result.json'
    
    # Read the JSON file
    with open(json_file_path, 'r') as file:
        json_data = json.load(file)
    
    # Generate JSON Schema
    schema = generate_schema_from_json(json_data)
    
    # Print or save the generated schema
    print(json.dumps(schema, indent=4))

if __name__ == "__main__":
    main()