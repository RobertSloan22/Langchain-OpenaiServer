from openai import OpenAI
from llama_cpp import Llama

# Initialize Fake OpenAI client
client = OpenAI(api_key="jhjhjh1234", base_url="http://localhost:8000/v1")

# Example function to use Fake OpenAI's GPT model
def query_fake_openai(prompt: str):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=150
    )
    return response.choices[0].message.content.strip()

# Example function to use a local Llama model
def query_llama(prompt: str, model_path: str):
    llm = Llama(model_path=model_path)
    response = llm.generate(prompt)
    # Handle the generator response
    response_text = "".join([r['text'] for r in response])
    return response_text

# Example usage
if __name__ == "__main__":
    prompt = "Summarize the latest data from the database."
    fake_openai_response = query_fake_openai(prompt)
    print("Fake OpenAI Response:", fake_openai_response)

    llama_model_path = "models/mistral-7b-instruct-v0.1.Q4_K_M.gguf"  # Replace with the actual path
    llama_response = query_llama(prompt, llama_model_path)
    print("Llama Response:", llama_response)
