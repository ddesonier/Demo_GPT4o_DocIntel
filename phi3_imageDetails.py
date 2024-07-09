import json
import os
import ssl
import requests
from io import StringIO
import configparser
from PIL import Image
from PIL.ExifTags import TAGS
import streamlit as st
from streamlit_chat import message
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

# Function to create prompt req
def construct_prompt(prompt, image_url):
    # Prepare the data for the API request
    data = {
        "input_data": {
            "input_string": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_url
                            },
                        },
                        {
                            "type": "text",
                            "text": prompt,
                        },
                    ],
                },
            ],
            "parameters": {"temperature": 0.7, "max_new_tokens": 2048},
        }
    }

    input_data = data.get("input_data", {})

    # Extract 'input_string' information
    input_strings = input_data.get("input_string", [])

    for item in input_strings:
        role = item.get("role", "No role specified")
        contents = item.get("content", [])
        for content in contents:
            content_type = content.get("type", "No type specified")
            # Process based on content type
            if content_type == "image_url":
                image_url = content.get("image_url", {}).get("url", "No URL specified")
            elif content_type == "text":
                text = content.get("text", "No text specified")

    body = str.encode(json.dumps(data))
    print("Body")
    print(body)
    if not api_key:
        raise Exception("A key should be provided to invoke the endpoint")

    headers = {'Content-Type':'application/json', 'Authorization':('Bearer '+ api_key)}
    print("Headers")
    print(headers)
    req = urllib.request.Request(url, body, headers)
    return req

# Function to extract metadata from an image
def extract_metadata(image_path):
    image_path = download_image(imageurl)
    print("Image Path" + image_path)

    # Open the downloaded image file
    image = Image.open(image_path)

    # Extract EXIF data
    exif_data = image._getexif()

    # Initialize a dictionary to hold the readable EXIF data
    readable_exif = {}

    # Iterate over the EXIF data
    if exif_data:
        for tag, value in exif_data.items():
            # Decode the tag
            readable_tag = TAGS.get(tag, tag)
            readable_exif[readable_tag] = value

    # `readable_exif` contains the EXIF data in a readable format
    return readable_exif

# Initialize the ConfigParser
config = configparser.ConfigParser()

config_file_path = 'config.ini'

# Check if the config file exists
if os.path.exists(config_file_path):
    # Read the configuration file
    config.read(config_file_path)

    # Access the values
    url = config['DEFAULT']['url']
    api_key = config['DEFAULT']['api_key']
else:
    url = st.text_input("Enter the AOAI Endpoint", value="https://{deployment_name}.{region}.inference.ml.azure.com/score")
    api_key = st.text_input("Enter a API Key", type="password")

# Function to allow self-signed HTTPS certificates
def allowSelfSignedHttps(allowed):
    # Bypass the server certificate verification on the client side
    if allowed and not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None):
        ssl._create_default_https_context = ssl._create_unverified_context

# Set up the Streamlit page
st.title("Phi-3-Vision-128k-Instruct Image Analysis Demo")
allowSelfSignedHttps(True) # This line is needed if you use a self-signed certificate in your scoring service.

# Get the system prompt from the sidebar
# Set up the default prompt for the AI assistant
default_prompt = """
You are an AI assistant that helps analysts investigate images.
"""
system_prompt = st.sidebar.text_area("System Prompt", default_prompt, height=200)

# Prompt the user to enter a URL
imageurl = st.text_input("Enter URL for image", value="")
#userprompt = st.sidebar.text_area("Enter Prompt", value="What are GPS coordinates for where this image was taken using the EXIF metadata provided here ")
metadata_str = ''
get_exif = False
exif_data = False
# Check if a URL has been entered
if imageurl:
    # Download the image first
    metadata_str = str(extract_metadata(imageurl))

    # Display the image on the Streamlit page
    st.image(imageurl, caption="Downloaded Image")
else:
    # Display a message prompting the user to enter a URL
    st.write("Please enter a URL to proceed.")

# Add a button to clear the conversation history
if st.sidebar.button('Clear Conversation'):
    st.session_state.conversation_history = ""  # Reset the conversation history


history = st.container()

with history:
    responses = st.container(border=True)

# User input form
with st.sidebar:
    messages = st.container(border=True)
    if metadata_str:
        # Add a checkbox to include metadata in prompt
        exif_data = st.checkbox('Include EXIF data?')
    if user_input := st.chat_input("Say something"):
        #messages.chat_message("user").write(user_input)
        if exif_data:
            prompt = construct_prompt(user_input + metadata_str, imageurl)
        else:
            prompt = construct_prompt(user_input, imageurl)
        response = urllib.request.urlopen(prompt)
        result = response.read().decode('utf-8')  # Decoding from bytes to string
        #messages.chat_message("assistant").write(f"Echo: {result}")
        with history:
            responses.chat_message("user").write(f"response: {user_input}")
            responses.chat_message("AI").write(f"response: {result}")


if metadata_str:
    # Add a checkbox to display metadata
    get_exif = st.checkbox('Display EXIF data?')

# Display the metadata
exifdata = st.container()
if get_exif:
    with exifdata:
        st.text_area("Image Meta Data", value=metadata_str, height=500, disabled=True)
with exifdata:
    exif = st.container(border=True)