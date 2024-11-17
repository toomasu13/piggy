import requests
from datetime import datetime, timedelta
import pandas as pd
import yfinance as yf
import os

from groq import Groq
import json

class GroqHelper():
    
    def __init__(self, api_key):
        
        self.client = Groq(
            api_key=api_key,
        )
        
    def request(self, prompt):
        
        chat_completion = self.client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama3-8b-8192",
            response_format={"type": "json_object"},
        )
        content = chat_completion.choices[0].message.content
        return json.loads(content)


class YahooAPIClient:
    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
    
    def get_market_data(self, symbol, timeframe):
        
        data = yf.Ticker(f'{symbol}-USD')
        hist = data.history(period='1mo', interval='1h')
        return hist
    

class CryptoAPIClient:
    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
    
    def get_market_data(self, crypto, timeframe):
        days = {
            "24h": 1,
            "7d": 7,
            "30d": 30,
            "90d": 90
        }[timeframe]
        
        endpoint = f"/coins/{crypto.lower()}/market_chart"
        params = {
            "vs_currency": "usd",
            "days": days,
            "interval": "hourly"
        }
        
        response = requests.get(f"{self.base_url}{endpoint}", params=params)
        response.raise_for_status()
        return response.json()

class RedditAPIClient:
    def __init__(self):
        self.base_url = "https://api.reddit.com"
    
    def get_sentiment_data(self, crypto, timeframe):
        subreddits = ["cryptocurrency", f"{crypto.lower()}", "cryptomarkets"]
        posts = []
        
        for subreddit in subreddits:
            endpoint = f"/r/{subreddit}/search"
            params = {
                "q": crypto,
                "sort": "new",
                "limit": 100
            }
            
            response = requests.get(f"{self.base_url}{endpoint}", params=params)
            response.raise_for_status()
            posts.extend(response.json()['data']['children'])
        
        return posts

class GitHubAPIClient:
    def __init__(self):
        self.base_url = "https://api.github.com"
    
    def get_github_metrics(self, crypto):
        crypto_repos = {
            "BTC": "bitcoin/bitcoin",
            "ETH": "ethereum/go-ethereum",
            "BNB": "bnb-chain/bsc",
            "XRP": "ripple/rippled",
            "ADA": "cardano-foundation/cardano-node"
        }
        
        repo = crypto_repos.get(crypto)
        if not repo:
            raise ValueError(f"No GitHub repository mapped for {crypto}")
        
        endpoint = f"/repos/{repo}"
        response = requests.get(f"{self.base_url}{endpoint}")
        response.raise_for_status()
        
        # Get commit activity
        commits_endpoint = f"/repos/{repo}/stats/commit_activity"
        commits_response = requests.get(f"{self.base_url}{commits_endpoint}")
        commits_response.raise_for_status()
        
        return {
            "repo_data": response.json(),
            "commit_data": commits_response.json()
        }
