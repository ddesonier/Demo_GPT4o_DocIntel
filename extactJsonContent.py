import json

# Open and load the JSON file
with open('result.json', 'r') as file:
    data = json.load(file)
    # Extract the message content

with open('invoice_content.json', 'w') as file:
    message_content = data['choices'][0]['message']['content']
    json_string = message_content.strip('```')
    json_string = json_string.replace("'json", "").rstrip("'")
    json_string = json_string.replace('\n', '')
    json_string = json_string.replace('\\', '')
    json.dump(json_string, file)
# Print or process the extracted content
print(json_string)

