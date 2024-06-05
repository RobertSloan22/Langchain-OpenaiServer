import os
import time
import requests
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI, AssistantEventHandler
from langchain_community.utilities import SQLDatabase
from langchain.chat_models import ChatOpenAI
from tinydb import TinyDB, Query
from discord.ext import commands, tasks
from datetime import datetime, timedelta, timezone
import asyncio
import discord
import psycopg2

load_dotenv()

# Use .env file for API keys
REAL_API_KEY = os.getenv("REAL_OPENAI_API_KEY")
FAKE_API_KEY = os.getenv("FAKE_OPENAI_API_KEY")
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
DB_CONN_DETAILS = os.getenv("DB_CONN_DETAILS", "dbname='' user='' host='' password=''")

# Corrected connection string for SQLAlchemy
DB_CONN_DETAILS_SQLALCHEMY = ""

# Database setup
db = SQLDatabase.from_uri(DB_CONN_DETAILS_SQLALCHEMY)

# Set up TinyDB for storing Discord messages
db_tiny = TinyDB("discord_messages.json")

# Function to switch between fake and real API
def switch_api(use_fake):
    global client
    api_key = FAKE_API_KEY if use_fake else REAL_API_KEY
    client = OpenAI(api_key=api_key)

# Switch API based on sidebar selection
use_fake_server = st.sidebar.radio("Select API Server", ["Real OpenAI API", "Fake OpenAI API"]) == "Fake OpenAI API"
switch_api(use_fake_server)

# OpenAI setup
client = OpenAI(api_key=REAL_API_KEY)

# Discord headers
headers = {
    "Authorization": os.getenv("AUTH_TOKEN"),
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
    "Sec-CH-UA": "\"Not A(Brand\";v=\"99\", \"Microsoft Edge\";v=\"121\"; \"Chromium\";v=\"121\"",
    "Sec-CH-UA-Mobile": "?0",
    "Sec-CH-UA-Platform": "\"Windows\"",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "X-Debug-Options": "bugReporterEnabled",
    "X-Discord-Locale": "en-US",
    "X-Discord-Timezone": "America/Los_Angeles",
}

# Discord channels
channels = [
    {"id": "1132706834340397116", "nickname": "Winners group chat"},
    {"id": "1106390097378684983", "nickname": "TRAC: main-chat"},
    {"id": "1157429728282673264", "nickname": "TRAC: pipe"},
    {"id": "1138509209525297213", "nickname": "TRAC: tap-protocol"},
    {"id": "1236020558488141874", "nickname": "TRAC: gib"},
    {"id": "1115824966470991923", "nickname": "OnlyFarmers: alpha"},
    {"id": "1166459733075579051", "nickname": "Ordicord: ordinals coding club 4/10/2024"},
    {"id": "1224564960575623269", "nickname": "Taproot Alpha: runes"},
    {"id": "1084525778852651190", "nickname": "DogePunks: holder-chat"},
    {"id": "1010230594367655996", "nickname": "Tensor: alpha"},
    {"id": "987504378749538366", "nickname": "Ordicord: general"},
    {"id": "1069465367988142110", "nickname": "Ordicord: tech-support"},
]

# Function to fetch Discord messages
def fetch_discord_messages(channel_id):
    url = f"https://discord.com/api/v9/channels/{channel_id}/messages?limit=100"
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to fetch messages for channel {channel_id}: HTTP {response.status_code} - {response.text}")
            return []
    except requests.exceptions.RequestException as e:
        st.error(f"Request exception for channel {channel_id}: {e}")
        return []
# Function to insert new messages into TinyDB
def insert_new_messages(messages, channel_id, nickname):
    for message in messages:
        Message = Query()
        if not db_tiny.search(Message.id == message["id"]):
            referenced_message = message.get("referenced_message", {})
            if referenced_message is None:
                referenced_message = {}
            attachments = message.get("attachments", [])
            attachment_file_name = None
            attachment_url = None

            if attachments:
                attachment_file_name = attachments[0].get("filename")
                attachment_url = attachments[0].get("url")

            db_tiny.insert({
                "id": message["id"],
                "channel_id": channel_id,
                "nickname": nickname,
                "content": message.get("content"),
                "timestamp": message.get("timestamp"),
                "author_id": message["author"]["id"],
                "author_username": message["author"]["username"],
                "author_global_name": message["author"].get("global_name"),
                "referenced_message_id": referenced_message.get("id"),
                "referenced_message_content": referenced_message.get("content"),
                "referenced_message_username": referenced_message.get("author", {}).get("username"),
                "referenced_message_global_name": referenced_message.get("author", {}).get("global_name"),
                "attachment_file_name": attachment_file_name,
                "attachment_url": attachment_url,
            })
# Function to insert new messages into TinyDB
#def insert_new_messages(messages, channel_id, nickname):
 #   for message in messages:
  #      Message = Query()
   #     if not db_tiny.search(Message.id == message["id"]):
    #        referenced_message = message.get("referenced_message", {})
          #  attachment = message.get("attachments", [{}])
           # attachment_file_name = attachment[0].get("filename") if attachment else None
            #attachment_url = attachment[0].get("url") if attachment else None
           # db_tiny.insert({
            #    "id": message["id"],
           #     "channel_id": channel_id,
          #     "nickname": nickname,
          #      "content": message.get("content"),
         #       "timestamp": message.get("timestamp"),
        #        "author_id": message["author"]["id"],
       #         "author_username": message["author"]["username"],
      #          "author_global_name": message["author"].get("global_name"),
     #           "referenced_message_id": referenced_message.get("id"),
          #      "referenced_message_content": referenced_message.get("content"),
         #       "referenced_message_username": referenced_message.get("author", {}).get("username"),
        #        "referenced_message_global_name": referenced_message.get("author", {}).get("global_name"),
       #         "attachment_file_name": attachment_file_name,
      #          "attachment_url": attachment_url,
     #       })

# Function to fetch messages with references from the database
def fetch_messages_with_references(channel_id, since):
    with psycopg2.connect(DB_CONN_DETAILS) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT m.message_id, m.content, m.author_username, m.timestamp, m.referenced_message_id, ref.message_id AS ref_message_id, ref.content AS ref_content, ref.author_username AS ref_author_username
                FROM discord_messages m
                LEFT JOIN discord_messages ref ON m.referenced_message_id = ref.message_id
                WHERE m.channel_id = %s AND m.timestamp > %s
                ORDER BY m.timestamp ASC
            """, (channel_id, since))
            messages = cur.fetchall()
    return messages

# Function to pass data to assistant and display output
def run_assistant():
    client = OpenAI(api_key=REAL_API_KEY)

    assistant = client.beta.assistants.create(
        name="Data Analyzer Assistant",
        instructions="You are a helpful assistant, acting as an alpha caller to summarize important information from the messages, including any replies to referenced messages by the referenced user.The messages include content, author username, timestamp, and if applicable, referenced message content and referenced message author username. Do not mention the user names specifically we want to keep them private. Summarize in bullet points in medium (discord message) format.Disregard any information that is just chatter. pay close attention and be detailed if the alpha or information is important.",
        model="gpt-4o",
        tools=[{"type": "file_search"}],
    )

    # Use TinyDB file as the data source
    file_paths = ["discord_messages.json"]
    file_streams = [open(path, "rb") for path in file_paths]

    vector_store = client.beta.vector_stores.create(name="Data Files")
    file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
        vector_store_id=vector_store.id, files=file_streams
    )

    vector_store_files = client.beta.vector_stores.files.list(vector_store_id=vector_store.id)
    file_ids = [file.id for file in vector_store_files]

    assistant = client.beta.assistants.update(
        assistant_id=assistant.id,
        tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}}
    )

    thread = client.beta.threads.create(
        messages=[
            {
                "role": "user",
                "content": "Please analyze the data in the uploaded files.",
                "attachments": [
                    {"file_id": file_id, "tools": [{"type": "file_search"}]} for file_id in file_ids
                ],
            }
        ]
    )

    class EventHandler(AssistantEventHandler):
        def on_text_created(self, text) -> None:
            st.write(f"assistant > {text}")

        def on_tool_call_created(self, tool_call):
            st.write(f"assistant > {tool_call.type}")

        def on_message_done(self, message) -> None:
            message_content = message.content[0].text
            annotations = message_content.annotations
            citations = []
            for index, annotation in enumerate(annotations):
                message_content.value = message_content.value.replace(
                    annotation.text, f"[{index}]"
                )
                if file_citation := getattr(annotation, "file_citation", None):
                    cited_file = client.files.retrieve(file_citation.file_id)
                    citations.append(f"[{index}] {cited_file.filename}")

            st.write(message_content.value)
            st.write("\n".join(citations))

    with client.beta.threads.runs.stream(
        thread_id=thread.id,
        assistant_id=assistant.id,
        instructions="Please address the user as Data Analyst. The user has a premium account.",
        event_handler=EventHandler(),
    ) as stream:
        stream.until_done()

    for stream in file_streams:
        stream.close()



# Streamlit app setup
st.title("Assistant Dashboard")
st.sidebar.title("Options")

# Function to handle commands
command = st.sidebar.selectbox(
    "Choose a command",
    ["Fetch Discord Messages", "Natural Language Query", "Analyze Data"]
)

if command == "Fetch Discord Messages":
    channel_selection = st.selectbox(
        "Choose a Discord Channel",
        options=[{"id": channel["id"], "label": f'{channel["nickname"]} (ID: {channel["id"]})'} for channel in channels],
        format_func=lambda option: option["label"]
    )
    if channel_selection:
        channel_id = channel_selection["id"]
        channel_nickname = [channel["nickname"] for channel in channels if channel["id"] == channel_id][0]
        if st.button("Fetch Messages"):
            messages = fetch_discord_messages(channel_id)
            if messages:
                st.write(f"Fetched {len(messages)} messages")
                insert_new_messages(messages, channel_id, channel_nickname)
                run_assistant()  # Automatically run the assistant after fetching messages

if command == "Natural Language Query":
    user_input = st.text_input("Ask a question")
    if st.button("Ask"):
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "user", "content": user_input},
                ],
            )
            answer = response.choices[0].message['content']
            st.write(answer)
        except Exception as e:
            st.error(f"Error generating response: {e}")

if command == "Analyze Data":
    if st.button("Run Assistant"):
        run_assistant()
