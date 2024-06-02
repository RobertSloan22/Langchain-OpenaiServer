import streamlit as st
from query_and_summarize import summarize_data

def main():
    st.title("Data Summarization App")

    st.sidebar.header("Configuration")
    
    query = st.sidebar.text_area("SQL Query", "SELECT * FROM discord_messages LIMIT 1000;")
    model = st.sidebar.selectbox("Model", ["fake_openai", "llama"])

    if st.sidebar.button("Summarize"):
        if query and model:
            try:
                summary = summarize_data(model, query)
                st.success("Summary generated successfully!")
                st.write(summary)
            except Exception as e:
                st.error(f"Error: {str(e)}")
        else:
            st.error("Please provide both a query and a model.")

if __name__ == "__main__":
    main()
