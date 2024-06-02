import os 
from api_key import api_key



import streamlit as st 
from langchain.llms import openai
from langchan.llms import llama

os.environ["OPENAI_API_KEY"] = api_key


st.title("🚀 Fake OpenAI Server App (...llama cpp)")

prompt = st.text_input("Pass your prompt here")
llm = OpenAI(tempreture=0.5)

if prompt:
    st.write("User: ", prompt)

    openai_response = openai.query_openai(prompt)
    st.write("OpenAI Response: ", openai_response)

    llama_model_path = "../mistral-7b-instruct-v0.1.Q4_K_M.gguf"
    llama_response = llama.query_llama(prompt, llama_model_path)
    st.write("Llama Response: ", llama_response)
    
