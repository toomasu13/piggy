import streamlit as st
import pandas as pd
import os
import plotly.graph_objects as go
import plotly.express as px
from utils.api_client import YahooAPIClient
from utils.api_client import GroqHelper
from utils.data_processing import process_market_data


api_key=os.environ.get("GROQ_API_KEY")

class CurrencyMetrics:
    def __init__(self):
        self.api_client = GroqHelper(api_key)
    
    @st.cache_data(ttl=300)
    def fetch_market_data(_self, symbol):
        prompt = f'''
            Search input for coin: {symbol}
            We would like to assess the invest-ability risk of <coin> and whether I should go ahead and think of investing in the coin. 
            There will be an overall score of promise / risk from 1-100 and a colour for it - red, amber, green to flag the coin. 
            Please give me the following metrics for the coin above:
            - ticker of the coin 
            - when was the coin founded
            - market size 
            - current price 
            - are there any other metrics I should consider that will help flag risk 
            Supply metrics:
            - market supply of coin
            - max supply 
            - market cap 
            - 24 hour volume 
            - think about whether this is helpful for risk.
            - what are the strengths of the coin
            Community metrics score: 
            - security score
            - liquidity score
            - volatility score
            Please return in a JSON format and follow the structure of an example
            {{'coin': 'ETH',
                'ticker': 'ETH',
                'founded': '2014-07-30T00:00:00.000Z',
                'market_size': 24022038474.1443,
                'current_price': 3957.7603,
                'metrics_to_consider': ['Burn Rate', 'Miner Distribution','Open Source Development'],
                'market_supply': 1122334521345.0,
                'max_supply': 124333453545.0,
                'market_cap': 454543345334.0,
                '24_hour_volume': 125445454534.0,
                'risk_flags': ['Burn Rate', 'Miner Distribution'],
                'key_strengths': ['Strong security track record', 'Active developer community'],
                'security_score': 60,
                'liquidity_score': 80,
                'volatility_score': 90,
                'promise_risk_score': 85, 
                'risk_colour': 'amber'}},
            '''
        
        return _self.api_client.request(prompt)
    
    def display(self, crypto):
        st.header("Risk Factors")
        
        try:
            data = self.fetch_market_data(crypto)
            
            dict_scores = {ik: [iv] for ik, iv in data.items() if 'score' in ik}
            # pd.DataFrame.from_dict(dict_scores, orient='index').T
            df_chart = pd.DataFrame.from_dict(dict_scores, orient='index', columns=['score']) #pd.DataFrame.from_dict(dict_scores)

            st.bar_chart(df_chart, horizontal=True)
            
            #st.metric("Current Price", content[:100])
            # processed_data = process_market_data(data)
            st.subheader('Key Warnings', divider=True)
            for ic in data.get('risk_flags'):
                st.markdown(f'- {ic}')
            st.subheader('Key Strengths', divider=True)
            for ic in data.get('key_strengths'):
                st.markdown(f'- {ic}')
            
            
            st.subheader('Coin Overview', divider=False)
            
            
            # Price and Market Cap metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Coin",
                    f"{data.get('ticker')}",
                )
            
            with col2:
                st.metric(
                    "Price",
                    f"{data.get('current_price')}",
                )
            
            with col3:
                st.metric(
                    "Market size",
                    f"{data.get('market_size')}",
                )
            
            col1b, col2b, col3b = st.columns(3)
            
            with col1b:
                st.metric(
                    "Market Supply",
                    f"{data.get('market_supply')}",
                )
            
            with col2b:
                st.metric(
                    "Market Cap",
                    f"{data.get('market_cap')}",
                )
            
            with col3b:
                st.metric(
                    "24h Volume",
                    f"{data.get('24_hour_volume')}%"
                )
            
        except Exception as e:
            st.error(f"Error fetching market data: {str(e)}")
            

class MarketMetrics:
    def __init__(self):
        self.api_client = YahooAPIClient()
    
    @st.cache_data(ttl=300)
    def fetch_market_data(_self, crypto, timeframe):
        
        return _self.api_client.get_market_data(crypto, timeframe)
    
    def display(self, crypto, timeframe):
        st.header("Market Metrics")
        
        try:
            data = self.fetch_market_data(crypto, timeframe)
            processed_data = process_market_data(data)
            
            # Price and Market Cap metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Current Price",
                    f"${processed_data['current_price']:,.2f}",
                    f"{processed_data['price_change_24h']:.2f}%"
                )
            
            with col2:
                st.metric(
                    "Market Cap",
                    f"${processed_data['market_cap']:,.0f}",
                    f"{processed_data['market_cap_change_24h']:.2f}%"
                )
            
            with col3:
                st.metric(
                    "24h Volume",
                    f"${processed_data['volume_24h']:,.0f}",
                    f"{processed_data['volume_change_24h']:.2f}%"
                )
            
            # Price Chart
            fig = go.Figure()
            fig.add_trace(go.Candlestick(
                x=processed_data['timestamps'],
                open=processed_data['open'],
                high=processed_data['high'],
                low=processed_data['low'],
                close=processed_data['close'],
                name='Price'
            ))
            
            fig.update_layout(
                title=f"{crypto} Price Chart",
                yaxis_title="Price (USD)",
                xaxis_title="Date",
                height=500,
                template="plotly_white"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Volume Heatmap
            volume_fig = px.density_heatmap(
                processed_data['volume_by_hour'],
                title="Trading Volume Heatmap",
                labels={'x': 'Hour', 'y': 'Day', 'color': 'Volume'},
                color_continuous_scale="Viridis"
            )
            
            st.plotly_chart(volume_fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error fetching market data: {str(e)}")
