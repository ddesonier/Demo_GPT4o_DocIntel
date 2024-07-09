import configparser
import json
import ssl
import streamlit as st
import pandas as pd
from io import StringIO
import os
import requests
import base64
from dotenv import load_dotenv
import urllib.request
import urllib.error
 
# Function to download an image from a given URL
def download_image(image_url):
    response = requests.get(image_url)
    print(image_url)
    print(response.status_code)
    if response.status_code == 200:
        # Extract filename and ensure directory
        filename = os.path.join("downloaded_images", image_url.split("/")[-1])
        if "?" in filename:
            filename = filename.split("?")
            filename = filename[0]
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        with open(filename, 'wb') as f:
            f.write(response.content)
        return filename
    else:
        raise Exception("Failed to download image.")


def uploaded_file(uploaded_file):
    if uploaded_file is not None:
        # To read file as bytes:
        bytes_data = uploaded_file.getvalue()
        st.write(bytes_data)

        # To convert to a string based IO:
        stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
        st.write(stringio)

        # To read file as string:
        string_data = stringio.read()
        st.write(string_data)

        # Can be used wherever a "file-like" object is accepted:
        dataframe = pd.read_csv(uploaded_file)
        st.write(dataframe)

# Function to create prompt req
def construct_prompt(s_prompt, u_prompt, imageURL):
    # Prepare the data for the API request
    data = {
        "messages": [
            {
            "role": "system",
            "content": [
                {
                "type": "text",
                "text": s_prompt
                }
            ]
            },
            {
            "role": "user",
            "content": [
                {
                "type": "image_url",
                "image_url": {
                    "url": imageURL
                }
                },
                {
                "type": "text",
                "text": u_prompt
                }
            ]
            }
        ],
        "temperature": 0.7,
        "top_p": 0.95,
        "max_tokens": 1800
    }
    return data

# Function to allow self-signed HTTPS certificates
def allowSelfSignedHttps(allowed):
    # Bypass the server certificate verification on the client side
    if allowed and not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None):
        ssl._create_default_https_context = ssl._create_unverified_context

# Initialize the ConfigParser
config = configparser.ConfigParser()

config_file_path = 'config.ini'

# Check if the config file exists
if os.path.exists(config_file_path):
    # Read the configuration file
    config.read(config_file_path)

    # Access the values
    GPT4V_ENDPOINT = config['DEFAULT']['url']
    GPT4V_KEY = config['DEFAULT']['api_key']
else:
    GPT4V_ENDPOINT = st.text_input("Enter the AOAI Endpoint", value="Https://")
    GPT4V_KEY = st.text_input("Enter a API Key", type="password")


# Set up the Streamlit page
st.title("GPT-4o Document Intelligence AI Assistant")
allowSelfSignedHttps(True) # This line is needed if you use a self-signed certificate in your scoring service.

# Set up the default prompt for the AI assistant
default_prompt = """
You are an AI assistant that helps extract information from invoices in a JSON format.
"""
system_prompt = st.sidebar.text_area("System Prompt", default_prompt, height=100)

# Define the seed message for the conversation
seed_message = {"role": "system", "content": system_prompt}

# Prompt the user to enter Image URL and User prompt
imageurl = st.text_input("Enter URL for image", value="")
user_input = st.sidebar.text_area("Enter Prompt", value="Extract the invoice details from the image as a JSON object.")

# Check if a URL has been entered
if imageurl:
    # Display the image on the Streamlit page
    st.image(imageurl, caption="Downloaded Image")
else:
    # Display a message prompting the user to enter a URL
    st.write("Please enter a URL to proceed.")

history = st.container()

with history:
    responses = st.container(border=True)

# Add a button to clear the conversation history
if st.sidebar.button('Clear Conversation'):
    history.empty()  # Reset the conversation history

jsonfile = None
json_string = ''
if imageurl:
    # User input form
    with st.sidebar:
        messages = st.container(border=True)
        if user_input := st.chat_input("Say something"):
            prompt_message = construct_prompt(system_prompt, user_input, imageurl)
            data = json.dumps(prompt_message).encode('utf-8')
            headers = {'Content-Type':'application/json', "api-key": GPT4V_KEY}
            #response = urllib.request.urlopen(prompt_message)
            print(GPT4V_ENDPOINT)
            request = urllib.request.Request(url=GPT4V_ENDPOINT, data=data, headers=headers)  # Replace YOUR_API_ENDPOINT_URL with the actual URL
            try:
                response = urllib.request.urlopen(request)
                result = response.read()

                result_dict = json.loads(result.decode('utf-8'))
                jsonfile = 'result.json'
                with open(jsonfile, 'w') as file:
                    message_content = result_dict['choices'][0]['message']['content']
                    json_string = message_content.strip('```')
                    json_string = json_string.replace("'json", "").rstrip("'")
                    json_string = json_string.replace('\n', '')
                    json.dump(json_string, file)

            except urllib.error.URLError as e:
                st.error(f"Failed to fetch data: {e.reason}")

            if jsonfile is not None:
                with open(jsonfile, "rb") as file:
                    btn = st.download_button(
                            label="Download JSON File",
                            data=file,
                            file_name="jsonfile",
                            mime="json"
                        )
                print(f"Result saved locally as {jsonfile}.")

    with history:
        responses.chat_message("user").write(f"response: {user_input}")
        responses.chat_message("AI").write(f"response: {json_string}")