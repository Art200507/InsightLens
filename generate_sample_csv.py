#!/usr/bin/env python3
"""
Sample CSV Generator for Testing InsightLens
Creates different types of business data for testing the upload system
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def generate_sales_data(n_records=1000):
    """Generate sample sales data"""
    print(f"Generating {n_records} sales records...")

    # Generate data
    start_date = datetime.now() - timedelta(days=365)
    data = []

    products = ['Laptop', 'Mouse', 'Keyboard', 'Monitor', 'Tablet', 'Phone', 'Headphones', 'Webcam']
    regions = ['North', 'South', 'East', 'West', 'Central']
    sales_reps = ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve', 'Frank']

    for i in range(n_records):
        record = {
            'order_id': f'ORD-{i+1:05d}',
            'customer_id': f'CUST-{random.randint(1, 200):04d}',
            'product': random.choice(products),
            'quantity': random.randint(1, 5),
            'unit_price': round(random.uniform(29.99, 999.99), 2),
            'total_amount': 0,  # Will calculate
            'order_date': start_date + timedelta(days=random.randint(0, 365)),
            'region': random.choice(regions),
            'sales_rep': random.choice(sales_reps),
            'customer_age': random.randint(18, 70)
        }

        record['total_amount'] = round(record['quantity'] * record['unit_price'], 2)
        data.append(record)

    df = pd.DataFrame(data)
    df.to_csv('sample_sales_data.csv', index=False)
    print("✅ Created: sample_sales_data.csv")
    return df

def generate_customer_data(n_records=500):
    """Generate sample customer data"""
    print(f"Generating {n_records} customer records...")

    segments = ['Premium', 'Standard', 'Basic']
    industries = ['Technology', 'Healthcare', 'Finance', 'Retail', 'Manufacturing']

    data = []
    for i in range(n_records):
        record = {
            'customer_id': f'CUST-{i+1:04d}',
            'company_name': f'Company {i+1}',
            'industry': random.choice(industries),
            'segment': random.choice(segments),
            'annual_revenue': round(random.uniform(100000, 10000000), 2),
            'employee_count': random.randint(10, 1000),
            'signup_date': datetime.now() - timedelta(days=random.randint(30, 1095)),
            'last_purchase': datetime.now() - timedelta(days=random.randint(0, 90)),
            'total_spent': round(random.uniform(5000, 500000), 2),
            'satisfaction_score': round(random.uniform(1.0, 5.0), 1)
        }
        data.append(record)

    df = pd.DataFrame(data)
    df.to_csv('sample_customer_data.csv', index=False)
    print("✅ Created: sample_customer_data.csv")
    return df

def generate_website_analytics(n_records=2000):
    """Generate sample website analytics data"""
    print(f"Generating {n_records} website analytics records...")

    pages = ['/', '/products', '/about', '/contact', '/blog', '/pricing', '/support']
    devices = ['Desktop', 'Mobile', 'Tablet']
    browsers = ['Chrome', 'Firefox', 'Safari', 'Edge']
    countries = ['USA', 'Canada', 'UK', 'Germany', 'France', 'Japan', 'Australia']

    data = []
    for i in range(n_records):
        record = {
            'session_id': f'SES-{i+1:06d}',
            'user_id': f'USER-{random.randint(1, 500):04d}',
            'page_url': random.choice(pages),
            'visit_date': datetime.now() - timedelta(days=random.randint(0, 30)),
            'page_views': random.randint(1, 20),
            'session_duration': random.randint(30, 1800),  # seconds
            'device_type': random.choice(devices),
            'browser': random.choice(browsers),
            'country': random.choice(countries),
            'bounce_rate': round(random.uniform(0.1, 0.8), 2),
            'conversion': random.choice([0, 1]) if random.random() > 0.7 else 0
        }
        data.append(record)

    df = pd.DataFrame(data)
    df.to_csv('sample_website_analytics.csv', index=False)
    print("✅ Created: sample_website_analytics.csv")
    return df

def main():
    print("📊 InsightLens Sample Data Generator")
    print("=" * 40)

    print("\nWhat type of sample data would you like to generate?")
    print("1. Sales Data (orders, revenue, customers)")
    print("2. Customer Data (companies, segments, spending)")
    print("3. Website Analytics (visits, sessions, conversions)")
    print("4. All of the above")

    try:
        choice = input("\nEnter your choice (1-4): ").strip()

        if choice == '1':
            generate_sales_data()
        elif choice == '2':
            generate_customer_data()
        elif choice == '3':
            generate_website_analytics()
        elif choice == '4':
            generate_sales_data()
            generate_customer_data()
            generate_website_analytics()
        else:
            print("Invalid choice. Generating sales data by default...")
            generate_sales_data()

        print("\n🎉 Sample data generation complete!")
        print("\nNext steps:")
        print("1. Run: ./run_web_app.sh")
        print("2. Upload the generated CSV files")
        print("3. Explore your data with InsightLens!")

    except KeyboardInterrupt:
        print("\n\n👋 Data generation cancelled.")

if __name__ == "__main__":
    main()