import streamlit as st
import plotly.express as px
from utils.api_client import GitHubAPIClient
from utils.data_processing import process_github_data

class TechnicalFundamentals:
    def __init__(self):
        self.api_client = GitHubAPIClient()
    
    @st.cache_data(ttl=3600)
    def fetch_github_data(self, crypto):
        return self.api_client.get_github_metrics(crypto)
    
    def display(self, crypto):
        st.header("Technical Fundamentals")
        
        try:
            data = self.fetch_github_data(crypto)
            processed_data = process_github_data(data)
            
            # Developer Activity Metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Active Developers",
                    processed_data['active_developers'],
                    f"{processed_data['developer_change']}%"
                )
            
            with col2:
                st.metric(
                    "Total Commits",
                    processed_data['total_commits'],
                    f"{processed_data['commit_change']}%"
                )
            
            with col3:
                st.metric(
                    "Open Issues",
                    processed_data['open_issues'],
                    f"{processed_data['issues_change']}"
                )
            
            # Commit Activity Chart
            commit_fig = px.line(
                processed_data['commit_history'],
                x='date',
                y='commits',
                title="Daily Commit Activity",
                labels={'date': 'Date', 'commits': 'Number of Commits'}
            )
            
            st.plotly_chart(commit_fig, use_container_width=True)
            
            # Developer Distribution
            dev_fig = px.pie(
                processed_data['developer_distribution'],
                values='count',
                names='category',
                title="Developer Activity Distribution"
            )
            
            st.plotly_chart(dev_fig, use_container_width=True)
            
            # Repository Health
            st.subheader("Repository Health Metrics")
            health_metrics = processed_data['repo_health']
            
            for metric, value in health_metrics.items():
                st.progress(value)
                st.caption(f"{metric}: {value}%")
            
        except Exception as e:
            st.error(f"Error fetching GitHub data: {str(e)}")
