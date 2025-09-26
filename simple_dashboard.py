#!/usr/bin/env python3
"""
Simple Interactive Dashboard for InsightLens
Creates basic Plotly visualizations that work reliably
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.offline as pyo

def create_simple_dashboard():
    """Create a simple working dashboard"""
    print("Creating InsightLens Simple Dashboard...")

    # Load data
    df = pd.read_csv('data/cleaned_ecommerce_data.csv')
    df['transaction_date'] = pd.to_datetime(df['transaction_date'])
    df['month'] = df['transaction_date'].dt.to_period('M').astype(str)

    # Create dashboard with subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Revenue by Category', 'Regional Distribution',
                       'Monthly Revenue Trend', 'Customer Age Distribution'),
        specs=[[{"type": "bar"}, {"type": "pie"}],
               [{"type": "scatter"}, {"type": "histogram"}]]
    )

    # 1. Revenue by Category
    category_revenue = df.groupby('product_category')['total_amount'].sum().sort_values(ascending=False)
    fig.add_trace(
        go.Bar(x=category_revenue.index, y=category_revenue.values,
               name="Category Revenue", marker_color='lightblue'),
        row=1, col=1
    )

    # 2. Regional Distribution
    regional_revenue = df.groupby('region')['total_amount'].sum()
    fig.add_trace(
        go.Pie(labels=regional_revenue.index, values=regional_revenue.values,
               name="Regional Revenue"),
        row=1, col=2
    )

    # 3. Monthly Revenue Trend
    monthly_revenue = df.groupby('month')['total_amount'].sum()
    fig.add_trace(
        go.Scatter(x=list(range(len(monthly_revenue))), y=monthly_revenue.values,
                  mode='lines+markers', name="Monthly Revenue",
                  line=dict(color='green', width=3)),
        row=2, col=1
    )

    # 4. Customer Age Distribution
    fig.add_trace(
        go.Histogram(x=df['customer_age'], name="Age Distribution",
                    marker_color='orange'),
        row=2, col=2
    )

    # Update layout
    fig.update_layout(
        height=800,
        title_text="InsightLens E-Commerce Analytics Dashboard",
        title_x=0.5,
        showlegend=False
    )

    # Save dashboard
    fig.write_html("insightlens_dashboard.html")
    print("✅ Dashboard saved as insightlens_dashboard.html")

    # Create KPI summary
    total_revenue = df['total_amount'].sum()
    total_customers = df['customer_id'].nunique()
    avg_order_value = df['total_amount'].mean()

    kpi_html = f"""
    <h2>Key Performance Indicators</h2>
    <div style="display: flex; justify-content: space-around; margin: 20px 0;">
        <div style="text-align: center; padding: 20px; background: #f0f8ff; border-radius: 10px;">
            <h3>${total_revenue:,.0f}</h3>
            <p>Total Revenue</p>
        </div>
        <div style="text-align: center; padding: 20px; background: #f0f8ff; border-radius: 10px;">
            <h3>{total_customers:,}</h3>
            <p>Unique Customers</p>
        </div>
        <div style="text-align: center; padding: 20px; background: #f0f8ff; border-radius: 10px;">
            <h3>${avg_order_value:.0f}</h3>
            <p>Avg Order Value</p>
        </div>
    </div>
    """

    # Add KPI to existing HTML
    with open("insightlens_dashboard.html", "r") as f:
        content = f.read()

    # Insert KPI after body tag
    content = content.replace("<body>", f"<body>{kpi_html}")

    with open("insightlens_dashboard.html", "w") as f:
        f.write(content)

    return fig

if __name__ == "__main__":
    dashboard = create_simple_dashboard()
    print("🎉 Simple dashboard completed successfully!")
    print("📊 Open 'insightlens_dashboard.html' in your web browser to view the interactive dashboard")