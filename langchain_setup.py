from db_connection import execute_query

def query_data(query: str):
    try:
        result = execute_query(query)
        return result
    except Exception as e:
        print(f"Error executing query: {e}")
        return []

# Example usage
if __name__ == "__main__":
    sample_query = "SELECT * FROM discord_messages LIMIT 10;"
    data = query_data(sample_query)
    for row in data:
        print(row)
