import streamlit as st
import plotly.graph_objects as go
#from components.market_metrics import MarketMetrics
from components.market_metrics import CurrencyMetrics
#from components.sentiment_analysis import SentimentAnalysis
#from components.technical_fundamentals import TechnicalFundamentals

# Page configuration
st.set_page_config(
    page_title="Crypto Analysis Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
with open('assets/style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def main():
    st.title("Cryptocurrency Analysis Dashboard")
    
    # Sidebar for settings
    st.sidebar.title("Settings")
    selected_crypto = st.sidebar.selectbox(
        "Select Cryptocurrency",
        ["BTC", "ETH", "BNB", "XRP", "ADA"]
    )
    
 #   timeframe = st.sidebar.selectbox(
 #       "Select Timeframe",
  #      ["24h", "7d", "30d", "90d"]
  #  )
    
    # Create tabs for different sections
#     tab1, tab2, tab3 = st.tabs([
#         "Market Metrics",
#         "Sentiment Analysis",
#         "Technical Fundamentals"
#     ])
    
    # Initialize components
#    market_metrics = MarketMetrics()
    currency_metrics = CurrencyMetrics()
    #sentiment_analysis = SentimentAnalysis()
    #technical_fundamentals = TechnicalFundamentals()
    
#     with tab1:
#    market_metrics.display(selected_crypto, timeframe)
    currency_metrics.display(selected_crypto)
    
 #    with tab2:
    #sentiment_analysis.display(selected_crypto, timeframe)
    
 #    with tab3:
    #technical_fundamentals.display(selected_crypto)
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center'>
        <p>Data refreshed every 5 minutes. Last update: {}</p>
        </div>
        """.format(
            st.experimental_get_query_params().get('last_update', ['Loading...'])[0]
        ),
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
