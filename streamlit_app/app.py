import streamlit as st
import requests
from datetime import datetime

# Page configuration with better title and icon
st.set_page_config(
    page_title="LLM RAG Search Engine",
    page_icon="🔍"
)

# Add some custom styling
st.markdown("""
    <style>
        .stTextInput input {
            padding: 12px;
        }
        .stButton button {
            background-color: #4CAF50;
            color: white;
        }
        .stButton button:hover {
            background-color: #45a049;
        }
        .answer-section {
            margin-top: 1.5rem;
        }
        .subheading {
            font-weight: bold;
            margin-top: 1rem;
            margin-bottom: 0.5rem;
        }
    </style>
""", unsafe_allow_html=True)

# Main app with enhanced elements
st.title("🔍 LLM-based RAG Search")
st.caption("Enter your question to get AI-powered answers from web documents")

# Add a clear button in the same line as search
col1, col2 = st.columns([4, 1])
with col1:
    query = st.text_input("Enter your query:", 
                         placeholder="e.g. What is India-Pakistan relations?",
                         label_visibility="collapsed")
with col2:
    if st.button("Clear"):
        query = ""  # This clears the input field

if st.button("Search", type="primary"):
    if not query.strip():
        st.warning("Please enter a query")
    else:
        with st.spinner(f"🔎 Searching for: '{query}'..."):
            try:
                start_time = datetime.now()
                response = requests.post(
                    "http://localhost:5001/query",
                    json={"query": query},
                    timeout=120
                )
                
                processing_time = (datetime.now() - start_time).total_seconds()
                
                if response.status_code == 200:
                    data = response.json()
                    answer = data.get('answer', "No answer found in response")
                    
                    # Format the answer with proper subheadings and bullets
                    formatted_answer = answer.replace('• ', '• ')\
                                           .replace('*•', '**•')\
                                           .replace(':*•', ':**\n•')
                    
                    st.markdown("### Answer:")
                    st.markdown(f"""
                    <div class="answer-section">
                        {formatted_answer}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Display metadata if available
                    if 'sources' in data:
                        st.caption(f"ℹ️ Found {len(data['sources'])} relevant sources")
                    
                    # Enhanced expander with processing time
                    with st.expander(f"Technical Details (processed in {processing_time:.2f}s)"):
                        st.json(data)
                else:
                    st.error(f"API Error {response.status_code}: {response.text[:200]}...")
                    
            except requests.exceptions.RequestException as e:
                st.error(f"⚠️ Connection error: {str(e)}")
                st.info("Please ensure: \n1. The Flask server is running\n2. It's on port 5001\n3. The endpoint /query exists")

# Add a small footer
st.markdown("---")
st.caption("Powered by RAG technology | Search accuracy may vary")