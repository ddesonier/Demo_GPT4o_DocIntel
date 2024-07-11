from azure.cosmos import CosmosClient, PartitionKey
import json

def upsert_item(container, doc_id):
    print('\n1.8 Upserting an item\n')

    read_item = container.read_item(item=doc_id, partition_key=doc_id)
    read_item['subtotal'] = read_item['subtotal'] + 1
    response = container.upsert_item(body=read_item)

    print('Upserted Item\'s Id is {0}, new subtotal={1}'.format(response['id'], response['subtotal']))

# Azure Cosmos DB configuration
ENDPOINT = "https://docinteldemo.documents.azure.com:443/"
KEY = ""
DATABASE_NAME = "mouser"
CONTAINER_NAME = "mouser"

# Path to your JSON file
json_file_path = "result.json"

# Read the JSON file
with open(json_file_path, 'r') as file:
    json_data = json.load(file)

# Initialize the Cosmos client
client = CosmosClient(ENDPOINT, KEY)

# Get a reference to the database
database = client.get_database_client(DATABASE_NAME)

# Get a reference to the container
container = database.get_container_client(CONTAINER_NAME)

container.create_item(body=json_data,
    enable_automatic_id_generation=True)


#print(f"Item inserted with id: {response['id']}")