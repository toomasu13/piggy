import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from textblob import TextBlob
from wordcloud import WordCloud

def process_market_data(raw_data):
    df = pd.DataFrame(raw_data['prices'], columns=['timestamp', 'price'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    
    # Calculate OHLC
    ohlc = df.set_index('timestamp').resample('1H').agg({
        'price': ['first', 'max', 'min', 'last']
    }).dropna()
    
    return {
        'current_price': df['price'].iloc[-1],
        'price_change_24h': ((df['price'].iloc[-1] - df['price'].iloc[-24]) / df['price'].iloc[-24]) * 100,
        'market_cap': raw_data['market_caps'][-1][1],
        'market_cap_change_24h': ((raw_data['market_caps'][-1][1] - raw_data['market_caps'][-24][1]) / raw_data['market_caps'][-24][1]) * 100,
        'volume_24h': raw_data['total_volumes'][-1][1],
        'volume_change_24h': ((raw_data['total_volumes'][-1][1] - raw_data['total_volumes'][-24][1]) / raw_data['total_volumes'][-24][1]) * 100,
        'timestamps': ohlc.index,
        'open': ohlc['price']['first'],
        'high': ohlc['price']['max'],
        'low': ohlc['price']['min'],
        'close': ohlc['price']['last'],
        'volume_by_hour': create_volume_heatmap(raw_data['total_volumes'])
    }

def process_sentiment_data(raw_data):
    sentiments = []
    texts = []
    
    for post in raw_data:
        text = post['data']['title'] + " " + post['data']['selftext']
        blob = TextBlob(text)
        sentiments.append(blob.sentiment.polarity)
        texts.append(text)
    
    # Generate word cloud
    text = " ".join(texts)
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
    
    return {
        'sentiment_score': np.mean(sentiments),
        'sentiment_change': np.mean(sentiments[-10:]) - np.mean(sentiments[:-10]),
        'mention_count': len(raw_data),
        'mention_change': calculate_mention_change(raw_data),
        'sentiment_strength': abs(np.mean(sentiments)) * 100,
        'strength_change': calculate_strength_change(sentiments),
        'sentiment_trend': create_sentiment_trend(sentiments),
        'wordcloud_image': wordcloud.to_array(),
        'mention_frequency': create_mention_frequency(raw_data)
    }

def process_github_data(raw_data):
    repo_data = raw_data['repo_data']
    commit_data = raw_data['commit_data']
    
    return {
        'active_developers': repo_data['subscribers_count'],
        'developer_change': calculate_developer_change(repo_data),
        'total_commits': sum(week['total'] for week in commit_data),
        'commit_change': calculate_commit_change(commit_data),
        'open_issues': repo_data['open_issues_count'],
        'issues_change': repo_data['open_issues_count'] - repo_data.get('closed_issues', 0),
        'commit_history': create_commit_history(commit_data),
        'developer_distribution': create_developer_distribution(repo_data),
        'repo_health': calculate_repo_health(repo_data)
    }

def create_volume_heatmap(volume_data):
    df = pd.DataFrame(volume_data, columns=['timestamp', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df['hour'] = df['timestamp'].dt.hour
    df['day'] = df['timestamp'].dt.day_name()
    return df.pivot_table(values='volume', index='day', columns='hour', aggfunc='mean')

def create_sentiment_trend(sentiments):
    return pd.DataFrame({
        'timestamp': pd.date_range(end=datetime.now(), periods=len(sentiments), freq='H'),
        'sentiment': sentiments
    })

def create_mention_frequency(raw_data):
    df = pd.DataFrame([{'timestamp': post['data']['created_utc']} for post in raw_data])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
    df['hour'] = df['timestamp'].dt.hour
    return df.groupby('hour').size().reset_index(name='count')

def create_commit_history(commit_data):
    return pd.DataFrame([{
        'date': datetime.fromtimestamp(week['week']),
        'commits': week['total']
    } for week in commit_data])

def create_developer_distribution(repo_data):
    total = repo_data['subscribers_count']
    return pd.DataFrame([
        {'category': 'Active Contributors', 'count': total * 0.1},
        {'category': 'Regular Contributors', 'count': total * 0.3},
        {'category': 'Occasional Contributors', 'count': total * 0.6}
    ])

def calculate_repo_health(repo_data):
    return {
        'Code Quality': min(repo_data['stargazers_count'] / 1000 * 10, 100),
        'Documentation': min(repo_data['size'] / 1000 * 5, 100),
        'Community Activity': min(repo_data['subscribers_count'] / 100 * 10, 100),
        'Issue Resolution': min((repo_data['open_issues_count'] / (repo_data.get('closed_issues', 1) + 1)) * 100, 100)
    }

def calculate_mention_change(raw_data):
    return len(raw_data) - len([post for post in raw_data if 
        datetime.fromtimestamp(post['data']['created_utc']) < datetime.now() - timedelta(days=1)])

def calculate_strength_change(sentiments):
    return (abs(np.mean(sentiments[-10:])) - abs(np.mean(sentiments[:-10]))) * 100

def calculate_developer_change(repo_data):
    return ((repo_data['subscribers_count'] - repo_data.get('previous_subscribers', 0)) / 
            max(repo_data.get('previous_subscribers', 1), 1)) * 100

def calculate_commit_change(commit_data):
    recent_commits = sum(week['total'] for week in commit_data[-4:])
    previous_commits = sum(week['total'] for week in commit_data[-8:-4])
    return ((recent_commits - previous_commits) / max(previous_commits, 1)) * 100
