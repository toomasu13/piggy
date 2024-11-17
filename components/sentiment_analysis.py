import streamlit as st
import plotly.express as px
from utils.api_client import RedditAPIClient
from utils.data_processing import process_sentiment_data

class SentimentAnalysis:
    def __init__(self):
        self.api_client = RedditAPIClient()
    
    @st.cache_data(ttl=300)
    def fetch_sentiment_data(self, crypto, timeframe):
        return self.api_client.get_sentiment_data(crypto, timeframe)
    
    def display(self, crypto, timeframe):
        st.header("Social Sentiment Analysis")
        
        try:
            data = self.fetch_sentiment_data(crypto, timeframe)
            processed_data = process_sentiment_data(data)
            
            # Overall Sentiment
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Sentiment Score",
                    f"{processed_data['sentiment_score']:.2f}",
                    f"{processed_data['sentiment_change']:.2f}",
                    delta_color="normal"
                )
            
            with col2:
                st.metric(
                    "Mention Count",
                    processed_data['mention_count'],
                    f"{processed_data['mention_change']}%"
                )
            
            with col3:
                st.metric(
                    "Sentiment Strength",
                    processed_data['sentiment_strength'],
                    f"{processed_data['strength_change']}%"
                )
            
            # Sentiment Trend Chart
            fig = px.line(
                processed_data['sentiment_trend'],
                x='timestamp',
                y='sentiment',
                title=f"{crypto} Sentiment Trend",
                labels={'timestamp': 'Date', 'sentiment': 'Sentiment Score'}
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Word Cloud
            st.subheader("Popular Discussion Topics")
            st.image(processed_data['wordcloud_image'], use_column_width=True)
            
            # Mention Frequency
            mention_fig = px.bar(
                processed_data['mention_frequency'],
                x='hour',
                y='count',
                title="Mention Frequency by Hour",
                labels={'hour': 'Hour of Day', 'count': 'Mention Count'}
            )
            
            st.plotly_chart(mention_fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error fetching sentiment data: {str(e)}")
