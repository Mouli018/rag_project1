# DeepEdge RAG Chatbot

A Retrieval-Augmented Generation (RAG) chatbot built for DeepEdge AI, designed to answer queries about recent news (e.g., "India Pakistan conflict news 2025 April recent tensions escalation Kashmir attacks") with bullet-point responses, source citations, and image captions.

# The system uses:

Flask for the backend
Streamlit for the frontend
Gemini API for generation

# Key Features:

✅ Conversational Memory
✅ Computer Vision
✅ Evaluation Metrics

## Table of Contents

[Overview](#overview)
[Features](#features)
[Requirements](#requirements)
[Setup Instructions](#SetupInstructions)
[Usage](#Usage)
[Directory Structure](#DirectoryStructure)
[Notes](#notes)

## Overview:
This project implements a RAG chatbot that combines:
Web search (Serper)
Content scraping (ScrapingBee)
Answer generation (Gemini API)

It provides accurate, context-aware responses with:
Follow-up query support (via LangChain ChatMessageHistory)
Image extraction & captioning (via Gemini API)
Performance evaluation (via NDCG and BLEU metrics)

The Streamlit UI offers a user-friendly interface with:
📌 Chat history
📌 Expandable source citations

## Features:
🔹 RAG Pipeline
Searches for relevant articles, scrapes content, and generates bullet-point answers with source citations.

🔹 Conversational Memory
Handles follow-up queries (e.g., "What is The Resistance Front?").

🔹 Computer Vision
Scrapes images from articles and generates captions using Gemini API.

🔹 Evaluation Metrics
Implements NDCG (retrieval quality) and BLEU (answer quality).

🔹 Streamlit UI
Displays chat history, responses, and collapsible source details.

🔹 Robust Scraping
Handles premium news sites (CNN, Reuters, The Hindu) with ScrapingBee’s premium proxy and deduplication logic.

## Requirements
Software:
Python: 3.8 or higher
Virtual Environment: Recommended (e.g., venv)
Web Browser: To access Streamlit UI (http://localhost:8501)

Dependencies
Install via requirements.txt:
streamlit==1.24.0
requests==2.31.0
flask==2.3.2
flask-cors==3.0.10
python-dotenv==1.0.0
langchain-community==0.0.38
nltk==3.8.1
scikit-learn==1.3.0
google-generativeai==0.3.2
tiktoken==0.5.1
beautifulsoup4==4.12.2

API Keys
Add to .env (see env.example):
SCRAPINGBEE_API_KEY=your_scrapingbee_key
SERPER_API_KEY=your_serper_key
GEMINI_API_KEY=your_gemini_key

Hardware:
RAM: 8GB or higher
Internet: Required for API calls
Disk Space: ~500MB (including optional cache/)

## Setup Instructions
1.Clone or Extract:
git clone [repo_url]  # If applicable
cd DeepEdge_RAG_Mouli

2.Create Virtual Environment
python -m venv venv
source venv/bin/activate  # macOS/Linux
.\venv\Scripts\activate  # Windows

3.Install Dependencies
pip install -r requirements.txt

4.Download NLTK Data
python setup_nltk.py

5.Set API Keys
Copy env.example to .env:
cp env.example .env  # macOS/Linux
copy env.example .env  # Windows
Add your API keys to .env.

6.Run Flask Backend
cd flask_app
python app.py  # Runs on http://localhost:5000

7.Run Streamlit Frontend
cd ..
streamlit run streamlit_app/app.py  # Open http://localhost:8501

## Usage
Enter a Query
Example:
India Pakistan conflict news 2025 April recent tensions escalation Kashmir attacks.
Follow-Up Queries
Ask related questions (e.g., "What is The Resistance Front?") to leverage conversational memory.

Notes
⚠ ScrapingBee Credits: Premium proxy is required for news sites (CNN, Reuters, The Hindu).
⚠ Python Version: Use 3.8+ to avoid dependency issues.
⚠ Testing: Test queries in Streamlit to verify RAG functionality, memory, and metrics.
