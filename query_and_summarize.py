from langchain_setup import query_data
from model_integration import query_fake_openai, query_llama

# Function to estimate token count based on text length (approximation)
def estimate_token_count(text):
    return len(text.split())

# Function to truncate text to fit within model's token limit
def truncate_text(text, max_tokens=2000):
    words = text.split()
    if len(words) > max_tokens:
        return ' '.join(words[:max_tokens])
    return text

# Function to split data into batches that fit within the token limit
def split_into_batches(data, max_tokens_per_batch=2000):
    batches = []
    current_batch = []
    current_batch_tokens = 0

    for row in data:
        row_text = str(row)
        row_tokens = estimate_token_count(row_text)

        if current_batch_tokens + row_tokens > max_tokens_per_batch:
            batches.append(current_batch)
            current_batch = [row_text]
            current_batch_tokens = row_tokens
        else:
            current_batch.append(row_text)
            current_batch_tokens += row_tokens
    
    if current_batch:
        batches.append(current_batch)

    return batches

def summarize_data_in_batches(model, query, max_tokens_per_batch=2000):
    data = query_data(query)
    summaries = []

    batches = split_into_batches(data, max_tokens_per_batch)

    for batch in batches:
        formatted_data = "\n".join(batch)
        
        if model == "fake_openai":
            summary = query_fake_openai(f"Summarize the following data:\n{formatted_data}")
        elif model == "llama":
            summary = query_llama(f"Summarize the following data:\n{formatted_data}", model_path="/path/to/your/llama/model")
        else:
            raise ValueError("Unsupported model specified.")
        
        summaries.append(summary)
    
    return "\n".join(summaries)

def summarize_data(model, query):
    try:
        summary = summarize_data_in_batches(model, query)
        return summary
    except Exception as e:
        raise RuntimeError(f"Failed to execute query: {str(e)}")

# Example usage
if __name__ == "__main__":
    query = "SELECT * FROM discord_messages LIMIT 1000;"  # Example query
    model = "fake_openai"  # or "llama"
    summary = summarize_data(model, query)
    print("Summary:", summary)
