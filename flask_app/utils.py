import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
import google.generativeai as genai
import tiktoken
import concurrent.futures
import pickle
import hashlib
import time
import random

load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Initialize Gemini model
model = genai.GenerativeModel('gemini-1.5-pro')

# Cache directory for scraped content
CACHE_DIR = "cache"
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

def count_tokens(text: str) -> int:
    """Count tokens using tiktoken (approximation for Gemini)"""
    try:
        encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
        return len(encoding.encode(text))
    except Exception as e:
        print(f"Token counting error: {str(e)}")
        return 0

def get_cache_file(url):
    """Generate cache file path based on URL hash"""
    url_hash = hashlib.md5(url.encode()).hexdigest()
    return os.path.join(CACHE_DIR, f"{url_hash}.pkl")

def cache_content(url, content):
    """Cache content to disk"""
    try:
        with open(get_cache_file(url), 'wb') as f:
            pickle.dump(content, f)
    except Exception as e:
        print(f"Cache write error for {url}: {str(e)}")

def load_cached_content(url):
    """Load cached content from disk"""
    try:
        cache_file = get_cache_file(url)
        if os.path.exists(cache_file):
            with open(cache_file, 'rb') as f:
                content = pickle.load(f)
                print(f"Cache hit for {url}: {len(content)} characters")
                return content
        else:
            print(f"Cache miss for {url}")
            return None
    except Exception as e:
        print(f"Cache read error for {url}: {str(e)}")
        return None

def search_articles(query):
    """Search using Serper API with retries and generic fallback"""
    headers = {'X-API-KEY': os.getenv("SERPER_API_KEY")}
    for attempt in range(3):
        try:
            response = requests.post(
                'https://google.serper.dev/search',
                headers=headers,
                json={'q': query, 'num': 10},
                timeout=30
            )
            response.raise_for_status()
            articles = response.json().get('organic', [])
            
            # Filter out problematic domains
            problematic_domains = ['quora.com', 'researchgate.net', 'youtube.com', 'vimeo.com', 'linkedin.com']
            filtered_articles = [
                article for article in articles
                if not any(domain in article.get('link', '').lower() for domain in problematic_domains)
            ]
            
            print(f"Search returned {len(articles)} articles, {len(filtered_articles)} after filtering: {[a['link'] for a in filtered_articles]}")
            return filtered_articles[:5]
        except requests.exceptions.RequestException as e:
            print(f"Search API Error (attempt {attempt + 1}): {type(e).__name__}: {e}")
            if attempt == 2:
                print("Serper API failed; returning empty list")
                return []
            wait_time = (2 ** attempt) + random.uniform(0, 0.1)
            print(f"Waiting {wait_time:.2f}s before retry")
            time.sleep(wait_time)

def fetch_article_content(url):
    """Scrape content using ScrapingBee with retries, backoff, and refined paywall handling"""
    cached_content = load_cached_content(url)
    if cached_content:
        return cached_content
    
    try:
        if url.startswith("http://"):
            url = url.replace("http://", "https://")
        
        credit_cost = 1  # Standard page, adjust to 10 for JS rendering
        print(f"Estimated ScrapingBee call cost for {url}: {credit_cost} credits")
        
        for attempt in range(3):
            try:
                response = requests.get(
                    "https://app.scrapingbee.com/api/v1/",
                    params={
                        'api_key': os.getenv("SCRAPINGBEE_API_KEY"),
                        'url': url,
                        'render_js': 'true',
                        'country_code': 'us',
                        'timeout': 15000
                    },
                    timeout=60
                )
                print(f"ScrapingBee status code for {url}: {response.status_code} (API key: {os.getenv('SCRAPINGBEE_API_KEY')[:4]}...)")
                
                if response.status_code == 429:
                    wait_time = (2 ** attempt) + random.uniform(0, 0.1)
                    print(f"429 Too Many Requests for {url}. Waiting {wait_time:.2f}s before retry {attempt + 1}")
                    time.sleep(wait_time)
                    continue
                if response.status_code == 403:
                    error_msg = response.text
                    print(f"Authentication error for {url}: {error_msg}")
                    if "invalid_api_key" in error_msg.lower() or "no_credits" in error_msg.lower():
                        return f"Error: ScrapingBee API key invalid or credit limit exceeded for {url}. Please check dashboard."
                    raise requests.exceptions.RequestException(f"403 Forbidden: {error_msg}")
                
                response.raise_for_status()
                break
            except requests.exceptions.RequestException as e:
                print(f"Attempt {attempt + 1} failed for {url}: {str(e)}")
                if attempt == 2:
                    raise e
            time.sleep(1)
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        raw_content = soup.get_text(strip=True)
        print(f"Raw content length for {url}: {len(raw_content)} characters")
        print(f"Raw content snippet: {raw_content[:200]}...")
        
        paywall_indicators = ['paywall', 'subscribe now', 'sign in to continue', 'login to view']
        body_text = soup.body.get_text(strip=True).lower() if soup.body else ""
        is_paywalled = any(indicator in body_text for indicator in paywall_indicators) and len(body_text) < 500
        if is_paywalled:
            print(f"Confirmed paywall at {url} (content too short: {len(body_text)} characters)")
            return ""
        
        for element in soup(['script', 'style', 'nav', 'footer', 'iframe', 'img']):
            element.decompose()
        
        content = ""
        main_content = soup.find('article') or soup.find('main')
        if main_content:
            content = ' '.join(p.get_text(strip=True) for p in main_content.find_all(['p', 'h1', 'h2', 'h3']))
        
        if not content:
            content = ' '.join(p.get_text(strip=True) for p in soup.find_all('p'))
        
        if not content:
            content = ' '.join(soup.body.get_text(strip=True).split() if soup.body else [])
        
        if not content or len(content) < 200:
            print(f"Insufficient content extracted from {url} ({len(content)} characters)")
            return ""
        
        print(f"Extracted {len(content)} characters from {url}")
        cache_content(url, content)
        return content
    except requests.exceptions.RequestException as e:
        print(f"ScrapingBee Error ({url}): {str(e)}")
        return ""
    except Exception as e:
        print(f"General Scraping Error ({url}): {str(e)}")
        return ""

def concatenate_content(articles):
    """Smart content concatenation with token awareness, truncation, and parallel scraping"""
    context = []
    total_tokens = 0
    max_tokens = 24000
    max_article_tokens = 8000
    max_articles = 4
    
    def process_article(article):
        link = article.get('link')
        if not link:
            print(f"Skipping article with no link: {article.get('title', 'Unknown')}")
            return None
        
        content = fetch_article_content(link)
        if not content:
            print(f"No content fetched for {link}")
            return None
            
        source_info = f"Source: {article.get('title', 'Unknown')}\nURL: {link}\n"
        article_text = source_info + content
        article_tokens = count_tokens(article_text)
        print(f"Article '{article.get('title')}' has {article_tokens} tokens")
        
        if article_tokens == 0:
            print(f"Skipping article '{article.get('title')}' due to empty content")
            return None
        
        if article_tokens > max_article_tokens:
            print(f"Truncating article '{article.get('title')}' from {article_tokens} to {max_article_tokens} tokens")
            encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
            tokens = encoding.encode(article_text)[:max_article_tokens]
            article_text = encoding.decode(tokens)
            article_tokens = max_article_tokens
        
        return (article_text, article_tokens)
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        results = executor.map(process_article, articles[:max_articles])
    
    for result in results:
        if result is None:
            continue
        article_text, article_tokens = result
        if total_tokens + article_tokens <= max_tokens:
            context.append(article_text)
            total_tokens += article_tokens
            print(f"Included article ({article_tokens} tokens)")
        else:
            print(f"Skipping article due to token limit")
            break
    
    time.sleep(1)
    final_context = "\n\n".join(context)
    print(f"Final context length: {len(final_context)} characters, {count_tokens(final_context)} tokens")
    return final_context

def generate_answer(context, query):
    """Generate answer using Gemini API with generic fallback"""
    try:
        if not context:
            print("No context provided; attempting fallback response")
            return (
                "Unable to fetch sufficient content due to search or scraping limitations. "
                "Please try again with a more specific query or check source accessibility."
            )
        
        prompt = f"""
        Using the provided context, answer the query: '{query}'.
        Ensure the response:
        - Directly addresses all aspects of the query with specific details (e.g., facts, figures, examples).
        - Uses information from multiple sources, avoiding reliance on a single source.
        - Is structured clearly, using bullet points or sections for readability.
        - Is concise yet comprehensive, focusing on relevance to the query.
        If context is insufficient, state: 'Limited information available; please try again.'
        Context: {context}
        """
        response = model.generate_content(prompt)
        answer = response.text
        print(f"Generated answer: {answer[:100]}...")
        return answer
    except Exception as e:
        print(f"Generation Error: {str(e)}")
        return "Error generating response"