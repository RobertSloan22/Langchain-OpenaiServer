from langchain_setup import query_data
from model_integration import query_fake_openai, query_llama

def summarize_data(model, query):
    data = query_data(query)
    # Format the data as needed for the model
    formatted_data = "\n".join([str(row) for row in data])
    
    if model == "fake_openai":
        summary = query_fake_openai(f"Summarize the following data:\n{formatted_data}")
    elif model == "llama":
        summary = query_llama(f"Summarize the following data:\n{formatted_data}", model_path="models/mistral-7b-instruct-v0.1.Q4_K_M.gguf")
    else:
        raise ValueError("Unsupported model specified.")
    
    return summary

# Example usage
if __name__ == "__main__":
    query = "SELECT * FROM your_table LIMIT 10;"
    model = "fake_openai"  # or "llama"
    summary = summarize_data(model, query)
    print("Summary:", summary)
