import requests
import csv
import json
import os
from datetime import datetime, timedelta
from collections import Counter
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer

# Configuration
CACHE_DIR = "api_cache"
CACHE_EXPIRY_HOURS = 24  # Cache validity duration
TAVILY_API_KEY = "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"
APIFY_API_KEY = "apify_api_bpXFGvbqINGT3bhToKgyGIaM0QfsjS3NRsV1"

# Initialize NLTK
stopwords_list = set(stopwords.words("english"))
tokenizer = RegexpTokenizer(r'\b\w{4,}\b')

# Create cache directory
os.makedirs(CACHE_DIR, exist_ok=True)

# Caching System
def get_cache_filename(source):
    return os.path.join(CACHE_DIR, f"{source}_cache.json")

def read_cache(source):
    cache_file = get_cache_filename(source)
    if not os.path.exists(cache_file):
        return None
    
    with open(cache_file, 'r') as f:
        data = json.load(f)
        expiry = datetime.fromisoformat(data['expiry'])
        if datetime.now() < expiry:
            return data['keywords']
    return None

def write_cache(source, keywords):
    cache_file = get_cache_filename(source)
    expiry = datetime.now() + timedelta(hours=CACHE_EXPIRY_HOURS)
    
    data = {
        'created': datetime.now().isoformat(),
        'expiry': expiry.isoformat(),
        'keywords': keywords
    }
    
    with open(cache_file, 'w') as f:
        json.dump(data, f)

# Tavily Web Scraping
def fetch_web_keywords():
    if cached := read_cache("web"):
        print("✅ Using cached Tavily results")
        return cached

    print("🌐 Fetching fresh results from Tavily...")
    
    url = "https://api.tavily.com/search"
    payload = {
        "query": "sustainability OR carbon tracking OR climate policy OR green finance",
        "include_domains": ["linkedin.com"],
        "search_depth": "advanced",
        "max_results": 50,
    }
    headers = {"Authorization": f"Bearer {TAVILY_API_KEY}", "Content-Type": "application/json"}
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        
        extracted = []
        for item in response.json().get("results", []):
            text = BeautifulSoup(item.get("content", ""), 'html.parser').get_text()
            extracted.extend(extract_keywords(text))
        
        write_cache("web", extracted)
        return extracted
    
    except Exception as e:
        print(f"⚠️ Web scraping error: {str(e)}")
        return []

# Google Trends Integration using Apify
def fetch_google_trends_keywords():
    if cached := read_cache("google_trends"):
        print("✅ Using cached Google Trends results")
        return cached

    print("📈 Fetching fresh Google Trends data...")
    
    url = f"https://api.apify.com/v2/acts/google~trends-scraper/run-sync-get-dataset-items"
    
    payload = {
        "queries": ["sustainability", "renewable energy", "climate policy"],
        "timeRange": "last7Days",
    }
    
    headers = {"Authorization": f"Bearer {APIFY_API_KEY}", "Content-Type": "application/json"}
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        
        trends_data = response.json()
        
        extracted_keywords = []
        
        for trend in trends_data:
            related_queries = trend.get('relatedQueries', [])
            for query in related_queries:
                extracted_keywords.append(query.get('query'))
        
        write_cache("google_trends", extracted_keywords)
        
        return extracted_keywords
    
    except requests.exceptions.HTTPError as e:
        print(f"⚠️ Google Trends error: {str(e)}")
        return []

# Keyword Processing Functions
def extract_keywords(text):
    try:
        text = text.lower()
        words = tokenizer.tokenize(text)
        return [word for word in words if word.isalpha() and word not in stopwords_list and len(word) > 3]
    except Exception as e:
        print(f"⚠️ Error extracting keywords: {str(e)}")
        return []

def get_top_keywords(keywords):
    return sorted(Counter(keywords).items(), key=lambda x: x[1], reverse=True)

# Save Results to CSV
def save_to_csv(keywords):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    filename = f"planetwise_keywords_{timestamp}.csv"
    
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Keyword", "Frequency"])
        
        for keyword, frequency in keywords:
            writer.writerow([keyword, frequency])
    
    print(f"✅ Saved {len(keywords)} keywords to {filename}")

# Main Execution
if __name__ == "__main__":
    print("🚀 Starting PlanetWise keyword aggregator...")
    
    web_keywords = fetch_web_keywords()
    google_trends_keywords = fetch_google_trends_keywords()
    
    all_keywords = web_keywords + google_trends_keywords
    
    top_keywords = get_top_keywords(all_keywords)
    
    save_to_csv(top_keywords)
    
    print("🏁 Process completed successfully!")
