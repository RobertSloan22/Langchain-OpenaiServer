from model_integration import query_fake_openai, query_llama

def test_models():
    prompt = "Summarize the latest data from the database."

    try:
        fake_openai_response = query_fake_openai(prompt)
        print("Fake OpenAI Response:", fake_openai_response)
    except Exception as e:
        print("Fake OpenAI model failed:", str(e))

    try:
        llama_model_path = "models/mistral-7b-instruct-v0.1.Q4_K_M.gguf"  # Replace with the actual path
        llama_response = query_llama(prompt, llama_model_path)
        print("Llama Response:", llama_response)
    except Exception as e:
        print("Llama model failed:", str(e))

if __name__ == "__main__":
    test_models()
