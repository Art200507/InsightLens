import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.offline as pyo
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class ECommerceDashboard:
    def __init__(self, data_path='data/cleaned_ecommerce_data.csv'):
        self.df = pd.read_csv(data_path)
        self.df['transaction_date'] = pd.to_datetime(self.df['transaction_date'])

        # Set style
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")

    def create_kpi_summary(self):
        """Create KPI summary metrics"""
        total_revenue = self.df['total_amount'].sum()
        total_transactions = len(self.df)
        unique_customers = self.df['customer_id'].nunique()
        avg_order_value = self.df['total_amount'].mean()

        # Calculate churn rate (customers with no purchase in last 90 days)
        latest_date = self.df['transaction_date'].max()
        cutoff_date = latest_date - timedelta(days=90)
        recent_customers = set(self.df[self.df['transaction_date'] >= cutoff_date]['customer_id'])
        all_customers = set(self.df['customer_id'])
        churned_customers = all_customers - recent_customers
        churn_rate = len(churned_customers) / len(all_customers) * 100

        kpis = {
            'Total Revenue': f"${total_revenue:,.2f}",
            'Total Transactions': f"{total_transactions:,}",
            'Unique Customers': f"{unique_customers:,}",
            'Average Order Value': f"${avg_order_value:.2f}",
            'Churn Rate': f"{churn_rate:.1f}%"
        }

        return kpis

    def plot_revenue_trends(self):
        """Create revenue trends visualization"""
        # Monthly revenue trends
        monthly_revenue = self.df.groupby([self.df['transaction_date'].dt.year,
                                         self.df['transaction_date'].dt.month])['total_amount'].sum().reset_index()
        monthly_revenue['date'] = pd.to_datetime(monthly_revenue[['transaction_date', 'month']].assign(day=1))

        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Monthly Revenue Trend', 'Daily Revenue Distribution',
                          'Revenue by Quarter', 'Revenue Growth Rate'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )

        # Monthly trend
        fig.add_trace(
            go.Scatter(x=monthly_revenue['date'], y=monthly_revenue['total_amount'],
                      mode='lines+markers', name='Monthly Revenue',
                      line=dict(width=3, color='#1f77b4')),
            row=1, col=1
        )

        # Daily distribution
        daily_revenue = self.df.groupby('transaction_date')['total_amount'].sum()
        fig.add_trace(
            go.Histogram(x=daily_revenue.values, name='Daily Revenue Distribution',
                        marker_color='#ff7f0e', opacity=0.7),
            row=1, col=2
        )

        # Quarterly revenue
        quarterly_revenue = self.df.groupby([self.df['transaction_date'].dt.year,
                                           self.df['transaction_date'].dt.quarter])['total_amount'].sum().reset_index()
        quarterly_revenue['quarter_label'] = (quarterly_revenue['transaction_date'].astype(str) +
                                             '-Q' + quarterly_revenue['quarter'].astype(str))

        fig.add_trace(
            go.Bar(x=quarterly_revenue['quarter_label'], y=quarterly_revenue['total_amount'],
                  name='Quarterly Revenue', marker_color='#2ca02c'),
            row=2, col=1
        )

        # Growth rate
        monthly_revenue['growth_rate'] = monthly_revenue['total_amount'].pct_change() * 100
        fig.add_trace(
            go.Scatter(x=monthly_revenue['date'], y=monthly_revenue['growth_rate'],
                      mode='lines+markers', name='Growth Rate (%)',
                      line=dict(width=2, color='#d62728')),
            row=2, col=2
        )

        fig.update_layout(height=800, title_text="Revenue Analysis Dashboard", showlegend=False)
        return fig

    def plot_customer_analysis(self):
        """Create customer analysis visualizations"""
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Customer Acquisition by Month', 'Customer Lifetime Value Distribution',
                          'Top 10 Customers by Revenue', 'Customer Age Distribution'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )

        # Customer acquisition
        first_purchase = self.df.groupby('customer_id')['transaction_date'].min().reset_index()
        first_purchase['month'] = first_purchase['transaction_date'].dt.to_period('M')
        acquisition_by_month = first_purchase.groupby('month').size().reset_index(name='new_customers')
        acquisition_by_month['month'] = acquisition_by_month['month'].dt.start_time

        fig.add_trace(
            go.Scatter(x=acquisition_by_month['month'], y=acquisition_by_month['new_customers'],
                      mode='lines+markers', name='New Customers',
                      fill='tozeroy', fillcolor='rgba(31, 119, 180, 0.3)'),
            row=1, col=1
        )

        # Customer lifetime value
        clv = self.df.groupby('customer_id')['total_amount'].sum()
        fig.add_trace(
            go.Histogram(x=clv.values, name='CLV Distribution',
                        marker_color='#ff7f0e', opacity=0.7),
            row=1, col=2
        )

        # Top customers
        top_customers = self.df.groupby('customer_id')['total_amount'].sum().nlargest(10).reset_index()
        top_customers['customer_id'] = 'Customer ' + top_customers['customer_id'].astype(str)

        fig.add_trace(
            go.Bar(x=top_customers['total_amount'], y=top_customers['customer_id'],
                  orientation='h', name='Top Customers', marker_color='#2ca02c'),
            row=2, col=1
        )

        # Age distribution
        age_revenue = self.df.groupby('customer_age')['total_amount'].sum().reset_index()
        fig.add_trace(
            go.Scatter(x=age_revenue['customer_age'], y=age_revenue['total_amount'],
                      mode='markers', name='Revenue by Age',
                      marker=dict(size=8, color='#d62728', opacity=0.6)),
            row=2, col=2
        )

        fig.update_layout(height=800, title_text="Customer Analysis Dashboard", showlegend=False)
        return fig

    def plot_product_category_analysis(self):
        """Create product category analysis"""
        category_metrics = self.df.groupby('product_category').agg({
            'total_amount': ['sum', 'mean', 'count'],
            'customer_id': 'nunique'
        }).round(2)

        category_metrics.columns = ['total_revenue', 'avg_order_value', 'total_orders', 'unique_customers']
        category_metrics = category_metrics.reset_index()

        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Revenue by Category', 'Orders by Category',
                          'Average Order Value by Category', 'Category Market Share'),
            specs=[[{"type": "bar"}, {"type": "bar"}],
                   [{"type": "bar"}, {"type": "pie"}]]
        )

        # Revenue by category
        fig.add_trace(
            go.Bar(x=category_metrics['product_category'], y=category_metrics['total_revenue'],
                  name='Revenue', marker_color='#1f77b4'),
            row=1, col=1
        )

        # Orders by category
        fig.add_trace(
            go.Bar(x=category_metrics['product_category'], y=category_metrics['total_orders'],
                  name='Orders', marker_color='#ff7f0e'),
            row=1, col=2
        )

        # Average order value
        fig.add_trace(
            go.Bar(x=category_metrics['product_category'], y=category_metrics['avg_order_value'],
                  name='AOV', marker_color='#2ca02c'),
            row=2, col=1
        )

        # Market share pie chart
        fig.add_trace(
            go.Pie(labels=category_metrics['product_category'],
                  values=category_metrics['total_revenue'],
                  name="Market Share"),
            row=2, col=2
        )

        fig.update_layout(height=800, title_text="Product Category Analysis Dashboard", showlegend=False)
        return fig

    def plot_regional_analysis(self):
        """Create regional analysis dashboard"""
        regional_metrics = self.df.groupby('region').agg({
            'total_amount': 'sum',
            'customer_id': 'nunique',
            'transaction_id': 'count'
        }).reset_index()
        regional_metrics.columns = ['region', 'revenue', 'customers', 'transactions']

        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Revenue by Region', 'Customers by Region',
                          'Transactions by Region', 'Revenue per Customer by Region'),
            specs=[[{"type": "bar"}, {"type": "bar"}],
                   [{"type": "bar"}, {"type": "bar"}]]
        )

        # Revenue by region
        fig.add_trace(
            go.Bar(x=regional_metrics['region'], y=regional_metrics['revenue'],
                  name='Revenue', marker_color='#1f77b4'),
            row=1, col=1
        )

        # Customers by region
        fig.add_trace(
            go.Bar(x=regional_metrics['region'], y=regional_metrics['customers'],
                  name='Customers', marker_color='#ff7f0e'),
            row=1, col=2
        )

        # Transactions by region
        fig.add_trace(
            go.Bar(x=regional_metrics['region'], y=regional_metrics['transactions'],
                  name='Transactions', marker_color='#2ca02c'),
            row=2, col=1
        )

        # Revenue per customer
        regional_metrics['revenue_per_customer'] = regional_metrics['revenue'] / regional_metrics['customers']
        fig.add_trace(
            go.Bar(x=regional_metrics['region'], y=regional_metrics['revenue_per_customer'],
                  name='Revenue per Customer', marker_color='#d62728'),
            row=2, col=2
        )

        fig.update_layout(height=800, title_text="Regional Analysis Dashboard", showlegend=False)
        return fig

    def plot_seasonal_trends(self):
        """Create seasonal trends analysis"""
        # Add seasonal features
        self.df['month'] = self.df['transaction_date'].dt.month
        self.df['day_of_week'] = self.df['transaction_date'].dt.day_name()
        self.df['hour'] = self.df['transaction_date'].dt.hour

        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Revenue by Month', 'Revenue by Day of Week',
                          'Transactions by Hour', 'Seasonal Patterns Heatmap'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"type": "heatmap"}]]
        )

        # Monthly patterns
        monthly_revenue = self.df.groupby('month')['total_amount'].sum()
        fig.add_trace(
            go.Scatter(x=monthly_revenue.index, y=monthly_revenue.values,
                      mode='lines+markers', name='Monthly Revenue',
                      fill='tozeroy', fillcolor='rgba(31, 119, 180, 0.3)'),
            row=1, col=1
        )

        # Day of week patterns
        dow_revenue = self.df.groupby('day_of_week')['total_amount'].sum()
        dow_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        dow_revenue = dow_revenue.reindex(dow_order)

        fig.add_trace(
            go.Bar(x=dow_revenue.index, y=dow_revenue.values,
                  name='DOW Revenue', marker_color='#ff7f0e'),
            row=1, col=2
        )

        # Hourly patterns
        hourly_transactions = self.df.groupby('hour').size()
        fig.add_trace(
            go.Scatter(x=hourly_transactions.index, y=hourly_transactions.values,
                      mode='lines+markers', name='Hourly Transactions',
                      line=dict(width=3, color='#2ca02c')),
            row=2, col=1
        )

        # Seasonal heatmap
        seasonal_data = self.df.groupby(['month', 'day_of_week'])['total_amount'].sum().unstack()
        seasonal_data = seasonal_data.reindex(columns=dow_order)

        fig.add_trace(
            go.Heatmap(z=seasonal_data.values,
                      x=seasonal_data.columns,
                      y=seasonal_data.index,
                      colorscale='Viridis',
                      name='Seasonal Heatmap'),
            row=2, col=2
        )

        fig.update_layout(height=800, title_text="Seasonal Trends Analysis", showlegend=False)
        return fig

    def generate_full_dashboard(self, output_dir='visualizations/'):
        """Generate complete dashboard with all visualizations"""
        print("Generating comprehensive dashboard...")

        # Create KPI summary
        kpis = self.create_kpi_summary()
        print("Key Performance Indicators:")
        for kpi, value in kpis.items():
            print(f"  {kpi}: {value}")

        # Generate all visualizations
        dashboards = {
            'revenue_trends': self.plot_revenue_trends(),
            'customer_analysis': self.plot_customer_analysis(),
            'product_category': self.plot_product_category_analysis(),
            'regional_analysis': self.plot_regional_analysis(),
            'seasonal_trends': self.plot_seasonal_trends()
        }

        # Save individual dashboards
        for name, fig in dashboards.items():
            html_file = f"{output_dir}{name}_dashboard.html"
            fig.write_html(html_file)
            print(f"Saved {name} dashboard to {html_file}")

        # Create combined dashboard
        combined_fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=('Monthly Revenue Trend', 'Customer Age vs Revenue',
                          'Category Revenue Distribution', 'Regional Performance',
                          'Seasonal Revenue Patterns', 'Key Metrics Summary'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"type": "pie"}, {"type": "bar"}],
                   [{"secondary_y": False}, {"type": "table"}]]
        )

        # Add key visualizations to combined dashboard
        monthly_revenue = self.df.groupby([self.df['transaction_date'].dt.year,
                                         self.df['transaction_date'].dt.month])['total_amount'].sum().reset_index()
        monthly_revenue['date'] = pd.to_datetime(monthly_revenue[['transaction_date', 'month']].assign(day=1))

        combined_fig.add_trace(
            go.Scatter(x=monthly_revenue['date'], y=monthly_revenue['total_amount'],
                      mode='lines+markers', name='Monthly Revenue'),
            row=1, col=1
        )

        # Save combined dashboard
        combined_html = f"{output_dir}combined_dashboard.html"
        combined_fig.write_html(combined_html)
        print(f"Saved combined dashboard to {combined_html}")

        return dashboards, kpis

if __name__ == "__main__":
    # Create dashboard
    dashboard = ECommerceDashboard()
    dashboards, kpis = dashboard.generate_full_dashboard()

    print("Dashboard generation completed successfully!")
    print("\nAccess your dashboards:")
    print("- Revenue Trends: visualizations/revenue_trends_dashboard.html")
    print("- Customer Analysis: visualizations/customer_analysis_dashboard.html")
    print("- Product Categories: visualizations/product_category_dashboard.html")
    print("- Regional Analysis: visualizations/regional_analysis_dashboard.html")
    print("- Seasonal Trends: visualizations/seasonal_trends_dashboard.html")
    print("- Combined View: visualizations/combined_dashboard.html")