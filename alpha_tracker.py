import requests
import json
import os
import re
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

# CORE CONFIG (SAFE MODE)
# Keys are pulled from Environment Variables for Security
CRYPTOPANIC_API_KEY = os.getenv("CRYPTOPANIC_API_KEY") or ""
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN") or ""

# INDUSTRY FILTERS
CRYPTO_SIGNALS = ["blockchain", "crypto", "web3", "ethereum", "solana", "mainnet", "testnet", "onchain", "token", "contract", "wallet", "decentralized"]
JUNK_SIGNALS = ["fps", "tweak", "resume", " cv", "pdf", "youtube", "music", "windows optimizer", "adblock", "cookie"]

TAXONOMY = {
    "AI": {
        "keywords": ["ai agent", "autonomous agent", "agentic", "ai sdk", "llm", "ai model", "inference"],
        "tags": ["AI Agents", "Multi-Agent Systems", "Agent Frameworks", "Agent Orchestration", "AI Infrastructure", "AI Tool-Use Systems", "AI Developer Tools"],
        "strict_crypto": False
    },
    "zk / Privacy / zkML": {
        "keywords": ["zkml", "zk-proof", "zkvm", "fhe", "zero knowledge", "cryptography", "snark", "stark"],
        "required_one": ["zk", "fhe", "cryptography", "zero", "knowledge", "snark", "stark", "prover"],
        "strict_crypto": True
    },
    "DePIN": {
        "keywords": ["gpu marketplace", "distributed compute", "nodes", "storage network", "bandwidth", "physical infrastructure"],
        "required_one": ["compute", "gpu", "nodes", "infrastructure", "mining", "bandwidth", "storage"],
        "strict_crypto": True
    },
    "RWA": {
        "keywords": ["rwa tokenization", "real world assets", "onchain credit", "tokenized bonds", "treasury yield"],
        "required_one": ["tokenization", "real world", "credit", "treasury", "assets", "bonds"],
        "strict_crypto": True
    },
    "Prediction Markets": {
        "keywords": ["prediction markets", "infofi", "forecasting protocol", "onchain betting", "polymarket signal"],
        "required_one": ["prediction", "betting", "forecast", "market", "outcome"],
        "strict_crypto": True
    },
    "Stablecoin Infrastructure": {
        "keywords": ["stablecoin infra", "yield stable", "synthetic dollar", "stablecoin payments"],
        "required_one": ["stablecoin", "yield", "synthetic", "euro", "dollar", "payment"],
        "strict_crypto": True
    },
    "Cross-chain / Interoperability": {
        "keywords": ["cross chain", "interoperability", "bridge security", "chain abstraction", "messaging protocol"],
        "required_one": ["bridge", "interop", "abstraction", "cross", "messaging"],
        "strict_crypto": True
    }
}

def get_market_news():
    """Fetch live trending news via CryptoPanic API."""
    if not CRYPTOPANIC_API_KEY: return []
    url = f"https://cryptopanic.com/api/v1/posts/?auth_token={CRYPTOPANIC_API_KEY}&public=true&filter=hot&kind=news"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        news = []
        for post in data.get('results', [])[:4]:
            source = post.get('domain', 'News')
            # Keeping full title for maximum curiosity/clarity
            news.append({
                "title": post['title'],
                "source": source.split('.')[0].upper(),
                "type": "Market Alpha",
                "color": "text-orange-500",
                "url": post['url']
            })
        return news
    except: return []

def get_arxiv_papers():
    url = 'http://export.arxiv.org/api/query?search_query=all:blockchain+OR+all:"autonomous+agents"&start=0&max_results=2&sortBy=submittedDate&sortOrder=descending'
    try:
        response = requests.get(url, timeout=10)
        root = ET.fromstring(response.content)
        papers = []
        for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
            title = entry.find('{http://www.w3.org/2005/Atom}title').text.strip()
            link = entry.find('{http://www.w3.org/2005/Atom}id').text
            # No title truncation here either
            papers.append({"title": title, "source": "ArXiv", "type": "Research Alpha", "color": "text-indigo-600", "url": link})
        return papers
    except: return []

def search_github(keywords):
    base_url = "https://api.github.com/search/repositories"
    headers = {"Accept": "application/vnd.github.v3+json"}
    
    # Bypass Rate Limits using GITHUB_TOKEN (5000 req/hr)
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"
        
    date_limit = (datetime.now() - timedelta(days=14)).strftime('%Y-%m-%d')
    query = f"({' OR '.join(keywords[:5])}) created:>{date_limit}"
    
    try:
        response = requests.get(f"{base_url}?q={query}&sort=stars&order=desc", headers=headers, timeout=15)
        if response.status_code == 200:
            return response.json().get('items', [])
        elif response.status_code == 403:
            print("GitHub Rate Limit hit. Waiting 60s or use Token...")
            return []
        return []
    except: return []

def classify_project(name, description, searched_cat):
    text = (name + " " + (description or "")).lower()
    if not any(junk in text for junk in JUNK_SIGNALS):
        if "ai" in text or "agent" in text or "llm" in text:
            if any(sig in text for sig in CRYPTO_SIGNALS) or any(kw in text for kw in ["inference", "model", "compute"]):
                for tag in TAXONOMY["AI"]["tags"]:
                    if tag.lower().replace(" ", "") in text.replace(" ", ""): return "AI", tag
                return "AI", "AI General"
        config = TAXONOMY.get(searched_cat)
        if config and (not config["strict_crypto"] or any(sig in text for sig in CRYPTO_SIGNALS)):
            if "required_one" not in config or any(req in text for req in config["required_one"]):
                return searched_cat, None
    return None, None

def run():
    all_projects = []
    seen_urls = set()
    
    print("--- AlphaTrace v4.2: Rate-Limit Proof Engine ---")

    for cat_name, config in TAXONOMY.items():
        print(f"Scanning: {cat_name}...")
        raw_repos = search_github(config["keywords"])
        
        for r in raw_repos:
            if r['html_url'] in seen_urls: continue
            final_cat, sub_tag = classify_project(r['name'], r['description'], cat_name)
            if final_cat:
                seen_urls.add(r['html_url'])
                all_projects.append({
                    "main_cat": final_cat, "sub_cat": sub_tag,
                    "name": r['name'], "full_name": r['full_name'],
                    "description": r['description'] or "No description",
                    "url": r['html_url'], "stars": r['stargazers_count'],
                    "forks": r['forks_count'], "score": min(99, int(30 + (r['stargazers_count'] * 0.5 + r['forks_count'] * 2) // ((datetime.now() - datetime.strptime(r['created_at'], "%Y-%m-%dT%H:%M:%SZ")).days + 3)))
                })
        
        # Throttling to stay safe even without token
        time.sleep(2) 

    signals = get_market_news() + get_arxiv_papers()
    output = {"projects": sorted(all_projects, key=lambda x: x['score'], reverse=True), "news": signals[:5], "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M')}
    
    # RELATIVE PATH (Safe for local & cloud)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(base_dir, "data", "data.js")
    os.makedirs(os.path.dirname(data_file), exist_ok=True)
    
    with open(data_file, "w") as f:
        f.write(f"const ALPHA_DATA_V2 = {json.dumps(output, indent=4)};")
    print(f"Sync Successful. Data saved to: {data_file}")

if __name__ == "__main__":
    run()
