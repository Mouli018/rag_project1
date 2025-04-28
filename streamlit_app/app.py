import streamlit as st
import requests

st.title("LLM-based RAG Search")
st.caption("Enter a query to search and generate answers from web content")

query = st.text_input("Enter your query:", placeholder="e.g. What is RAG in AI?")

if st.button("Search"):
    if not query.strip():
        st.warning("Please enter a query")
    else:
        with st.spinner("Searching and generating answer..."):
            try:
                response = requests.post(
                    "http://localhost:5001/query",
                    json={"query": query},
                    timeout=120
                )
                
                if response.status_code == 200:
                    answer = response.json().get('answer')
                    st.markdown("### Answer:")
                    st.write(answer)
                    
                    # Show raw JSON in expander
                    with st.expander("Show API response"):
                        st.json(response.json())
                else:
                    st.error(f"API Error: {response.status_code} - {response.text}")
                    
            except requests.exceptions.RequestException as e:
                st.error(f"Connection error: {str(e)}")
                st.info("Make sure the Flask server is running on port 5001")