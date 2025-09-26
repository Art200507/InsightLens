#!/usr/bin/env python3
"""
InsightLens - Data Upload & Analysis Web App

Upload any CSV file and get instant business intelligence:
- Automatic data analysis
- Interactive visualizations
- Downloadable reports
- Smart column detection
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import io
from sklearn.preprocessing import LabelEncoder
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestRegressor
import warnings
warnings.filterwarnings('ignore')

# Configure Streamlit page
st.set_page_config(
    page_title="InsightLens - Data Analytics",
    page_icon="🔍",
    layout="wide"
)

class SmartDataAnalyzer:
    def __init__(self, df):
        self.df = df
        self.numeric_columns = []
        self.categorical_columns = []
        self.date_columns = []
        self.potential_revenue_cols = []
        self.potential_customer_cols = []
        self.potential_date_cols = []

        self._detect_column_types()

    def _detect_column_types(self):
        """Smart detection of column types and business meaning"""
        for col in self.df.columns:
            col_lower = col.lower()

            # Detect numeric columns
            if pd.api.types.is_numeric_dtype(self.df[col]):
                self.numeric_columns.append(col)

                # Detect potential revenue columns
                if any(word in col_lower for word in ['price', 'cost', 'revenue', 'amount', 'value', 'total', 'sales']):
                    self.potential_revenue_cols.append(col)

            # Detect categorical columns
            elif self.df[col].dtype == 'object':
                self.categorical_columns.append(col)

                # Detect potential customer columns
                if any(word in col_lower for word in ['customer', 'client', 'user', 'id']):
                    self.potential_customer_cols.append(col)

                # Try to convert to datetime
                try:
                    pd.to_datetime(self.df[col])
                    self.potential_date_cols.append(col)
                except:
                    pass

    def get_basic_stats(self):
        """Get basic dataset statistics"""
        return {
            'total_rows': len(self.df),
            'total_columns': len(self.df.columns),
            'numeric_columns': len(self.numeric_columns),
            'categorical_columns': len(self.categorical_columns),
            'missing_values': self.df.isnull().sum().sum(),
            'duplicate_rows': self.df.duplicated().sum()
        }

    def create_overview_plots(self):
        """Create overview visualizations"""
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Missing Values', 'Data Types',
                          'Numeric Columns Distribution', 'Top Categories'),
            specs=[[{"type": "bar"}, {"type": "pie"}],
                   [{"type": "box"}, {"type": "bar"}]]
        )

        # 1. Missing values
        missing = self.df.isnull().sum()
        missing = missing[missing > 0]
        if len(missing) > 0:
            fig.add_trace(
                go.Bar(x=missing.index, y=missing.values, name="Missing Values"),
                row=1, col=1
            )

        # 2. Data types
        dtype_counts = {'Numeric': len(self.numeric_columns),
                       'Categorical': len(self.categorical_columns)}
        fig.add_trace(
            go.Pie(labels=list(dtype_counts.keys()), values=list(dtype_counts.values()),
                   name="Data Types"),
            row=1, col=2
        )

        # 3. Numeric distributions (first few numeric columns)
        for i, col in enumerate(self.numeric_columns[:3]):
            fig.add_trace(
                go.Box(y=self.df[col], name=col),
                row=2, col=1
            )

        # 4. Top categories (first categorical column)
        if self.categorical_columns:
            top_cats = self.df[self.categorical_columns[0]].value_counts().head(10)
            fig.add_trace(
                go.Bar(x=top_cats.values, y=top_cats.index, orientation='h',
                      name="Top Categories"),
                row=2, col=2
            )

        fig.update_layout(height=600, title_text="Data Overview Dashboard")
        return fig

    def create_revenue_analysis(self, revenue_col, customer_col=None, date_col=None):
        """Create revenue-focused analysis"""
        if revenue_col not in self.df.columns:
            return None

        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Revenue Distribution', 'Top Revenue Sources',
                          'Revenue Trend', 'Revenue Statistics'),
            specs=[[{"type": "histogram"}, {"type": "bar"}],
                   [{"type": "scatter"}, {"type": "table"}]]
        )

        # 1. Revenue distribution
        fig.add_trace(
            go.Histogram(x=self.df[revenue_col], name="Revenue Distribution"),
            row=1, col=1
        )

        # 2. Top revenue by category (if available)
        if customer_col and customer_col in self.df.columns:
            top_revenue = self.df.groupby(customer_col)[revenue_col].sum().nlargest(10)
            fig.add_trace(
                go.Bar(x=top_revenue.index, y=top_revenue.values, name="Top Revenue"),
                row=1, col=2
            )

        # 3. Revenue trend over time (if date available)
        if date_col and date_col in self.df.columns:
            df_temp = self.df.copy()
            df_temp[date_col] = pd.to_datetime(df_temp[date_col])
            daily_revenue = df_temp.groupby(df_temp[date_col].dt.date)[revenue_col].sum()

            fig.add_trace(
                go.Scatter(x=daily_revenue.index, y=daily_revenue.values,
                          mode='lines+markers', name="Revenue Trend"),
                row=2, col=1
            )

        # 4. Statistics table
        stats = self.df[revenue_col].describe()
        fig.add_trace(
            go.Table(
                header=dict(values=['Statistic', 'Value']),
                cells=dict(values=[list(stats.index), [f"${x:,.2f}" for x in stats.values]])
            ),
            row=2, col=2
        )

        fig.update_layout(height=600, title_text=f"Revenue Analysis - {revenue_col}")
        return fig

    def perform_clustering(self, n_clusters=5):
        """Perform customer clustering if possible"""
        if len(self.numeric_columns) < 2:
            return None

        # Use numeric columns for clustering
        cluster_data = self.df[self.numeric_columns].fillna(0)

        # Perform KMeans clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        clusters = kmeans.fit_predict(cluster_data)

        # Create cluster visualization
        fig = px.scatter(
            x=cluster_data.iloc[:, 0],
            y=cluster_data.iloc[:, 1] if len(self.numeric_columns) > 1 else cluster_data.iloc[:, 0],
            color=clusters,
            title=f"Customer Segmentation ({n_clusters} Clusters)",
            labels={'x': self.numeric_columns[0],
                   'y': self.numeric_columns[1] if len(self.numeric_columns) > 1 else self.numeric_columns[0]}
        )

        return fig, clusters

    def generate_insights(self, revenue_col=None):
        """Generate business insights"""
        insights = []

        # Basic insights
        stats = self.get_basic_stats()
        insights.append(f"📊 Dataset contains {stats['total_rows']:,} rows and {stats['total_columns']} columns")

        if stats['missing_values'] > 0:
            insights.append(f"⚠️ Found {stats['missing_values']} missing values that need attention")

        if stats['duplicate_rows'] > 0:
            insights.append(f"🔄 Found {stats['duplicate_rows']} duplicate rows")

        # Revenue insights
        if revenue_col and revenue_col in self.df.columns:
            total_revenue = self.df[revenue_col].sum()
            avg_revenue = self.df[revenue_col].mean()
            insights.append(f"💰 Total Revenue: ${total_revenue:,.2f}")
            insights.append(f"📈 Average Revenue: ${avg_revenue:.2f}")

            # Find top performers
            if len(self.categorical_columns) > 0:
                cat_col = self.categorical_columns[0]
                top_category = self.df.groupby(cat_col)[revenue_col].sum().idxmax()
                top_revenue = self.df.groupby(cat_col)[revenue_col].sum().max()
                insights.append(f"🏆 Top {cat_col}: {top_category} (${top_revenue:,.2f})")

        # Date insights
        if self.potential_date_cols:
            date_col = self.potential_date_cols[0]
            df_temp = self.df.copy()
            df_temp[date_col] = pd.to_datetime(df_temp[date_col])
            date_range = df_temp[date_col].max() - df_temp[date_col].min()
            insights.append(f"📅 Data spans {date_range.days} days")

        return insights

def main():
    st.title("🔍 InsightLens - Smart Data Analytics")
    st.markdown("Upload any CSV file and get instant business intelligence!")

    # File upload
    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type=['csv'],
        help="Upload your business data in CSV format. The system will automatically detect columns and create analysis."
    )

    if uploaded_file is not None:
        try:
            # Load data
            df = pd.read_csv(uploaded_file)

            st.success(f"✅ Successfully loaded {len(df):,} rows and {len(df.columns)} columns!")

            # Initialize analyzer
            analyzer = SmartDataAnalyzer(df)

            # Sidebar for configuration
            st.sidebar.header("🎛️ Analysis Configuration")

            # Column selection
            st.sidebar.subheader("Select Key Columns")

            revenue_col = st.sidebar.selectbox(
                "Revenue/Amount Column:",
                ["None"] + analyzer.potential_revenue_cols + analyzer.numeric_columns,
                help="Select the column containing revenue, sales, or amount data"
            )

            customer_col = st.sidebar.selectbox(
                "Customer/ID Column:",
                ["None"] + analyzer.potential_customer_cols + analyzer.categorical_columns,
                help="Select the column containing customer or ID information"
            )

            date_col = st.sidebar.selectbox(
                "Date Column:",
                ["None"] + analyzer.potential_date_cols,
                help="Select the column containing date information"
            )

            # Analysis options
            st.sidebar.subheader("Analysis Options")
            show_overview = st.sidebar.checkbox("📊 Data Overview", value=True)
            show_revenue = st.sidebar.checkbox("💰 Revenue Analysis", value=True)
            show_clustering = st.sidebar.checkbox("👥 Customer Clustering", value=False)

            # Main analysis area
            col1, col2 = st.columns([2, 1])

            with col2:
                st.subheader("📈 Quick Stats")
                stats = analyzer.get_basic_stats()
                st.metric("Total Rows", f"{stats['total_rows']:,}")
                st.metric("Columns", stats['total_columns'])
                st.metric("Missing Values", stats['missing_values'])

                # Show data sample
                st.subheader("📋 Data Preview")
                st.dataframe(df.head(10), use_container_width=True)

                # Column information
                st.subheader("📊 Column Types")
                col_info = pd.DataFrame({
                    'Column': df.columns,
                    'Type': df.dtypes,
                    'Non-Null': df.count(),
                    'Unique': [df[col].nunique() for col in df.columns]
                })
                st.dataframe(col_info, use_container_width=True)

            with col1:
                # Data Overview
                if show_overview:
                    st.subheader("📊 Data Overview")
                    overview_fig = analyzer.create_overview_plots()
                    st.plotly_chart(overview_fig, use_container_width=True)

                # Revenue Analysis
                if show_revenue and revenue_col != "None":
                    st.subheader("💰 Revenue Analysis")
                    revenue_fig = analyzer.create_revenue_analysis(
                        revenue_col,
                        customer_col if customer_col != "None" else None,
                        date_col if date_col != "None" else None
                    )
                    if revenue_fig:
                        st.plotly_chart(revenue_fig, use_container_width=True)

                # Customer Clustering
                if show_clustering and len(analyzer.numeric_columns) >= 2:
                    st.subheader("👥 Customer Segmentation")
                    n_clusters = st.slider("Number of Clusters", 2, 10, 5)
                    cluster_result = analyzer.perform_clustering(n_clusters)
                    if cluster_result:
                        cluster_fig, clusters = cluster_result
                        st.plotly_chart(cluster_fig, use_container_width=True)

                        # Show cluster statistics
                        cluster_df = df.copy()
                        cluster_df['Cluster'] = clusters
                        cluster_stats = cluster_df.groupby('Cluster')[analyzer.numeric_columns].mean()
                        st.dataframe(cluster_stats, use_container_width=True)

            # Business Insights
            st.subheader("💡 Business Insights")
            insights = analyzer.generate_insights(revenue_col if revenue_col != "None" else None)
            for insight in insights:
                st.write(insight)

            # Export functionality
            st.subheader("📥 Export Results")

            col1, col2, col3 = st.columns(3)

            with col1:
                # Download processed data
                csv_buffer = io.StringIO()
                df.to_csv(csv_buffer, index=False)
                st.download_button(
                    label="📊 Download Processed Data",
                    data=csv_buffer.getvalue(),
                    file_name=f"processed_{uploaded_file.name}",
                    mime="text/csv"
                )

            with col2:
                # Download summary report
                report = f"""
INSIGHTLENS ANALYSIS REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

DATASET SUMMARY:
- Rows: {stats['total_rows']:,}
- Columns: {stats['total_columns']}
- Missing Values: {stats['missing_values']}
- Duplicate Rows: {stats['duplicate_rows']}

BUSINESS INSIGHTS:
"""
                for insight in insights:
                    report += f"- {insight}\n"

                st.download_button(
                    label="📋 Download Report",
                    data=report,
                    file_name=f"analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain"
                )

            with col3:
                st.info("💡 **Pro Tip:** Use the sidebar to customize your analysis and focus on specific business metrics!")

        except Exception as e:
            st.error(f"❌ Error processing file: {str(e)}")
            st.info("💡 Make sure your CSV file is properly formatted with headers in the first row.")

    else:
        # Show example
        st.info("👆 Upload a CSV file to get started!")

        st.subheader("📋 Example CSV Format")
        example_data = pd.DataFrame({
            'customer_id': [1, 2, 3, 4, 5],
            'product_name': ['Laptop', 'Mouse', 'Keyboard', 'Monitor', 'Tablet'],
            'amount': [999.99, 29.99, 79.99, 299.99, 499.99],
            'date': ['2024-01-15', '2024-01-16', '2024-01-17', '2024-01-18', '2024-01-19'],
            'region': ['North', 'South', 'East', 'West', 'Central']
        })
        st.dataframe(example_data, use_container_width=True)

        st.markdown("""
        ### 🎯 What InsightLens Can Analyze:
        - **💰 Revenue & Sales Data** - Automatically detects amount, price, revenue columns
        - **👥 Customer Analytics** - Finds customer IDs and analyzes behavior patterns
        - **📅 Time Series Analysis** - Detects date columns for trend analysis
        - **🎭 Customer Segmentation** - Groups customers by behavior using ML
        - **📊 Business Intelligence** - Generates actionable insights automatically

        ### 🚀 Features:
        - **Smart Column Detection** - Automatically identifies revenue, customer, date columns
        - **Interactive Visualizations** - Click and explore your data
        - **Export Results** - Download processed data and reports
        - **No Coding Required** - Just upload and analyze!
        """)

if __name__ == "__main__":
    main()