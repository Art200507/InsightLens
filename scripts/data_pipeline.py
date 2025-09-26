import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sqlite3
from faker import Faker
import random

class ECommerceDataPipeline:
    def __init__(self):
        self.fake = Faker()

    def generate_sample_data(self, num_records=1000000):
        """Generate sample e-commerce transaction data"""
        print(f"Generating {num_records:,} e-commerce transaction records...")

        categories = ['Electronics', 'Clothing', 'Home & Garden', 'Sports', 'Books', 'Beauty', 'Toys']
        regions = ['North', 'South', 'East', 'West', 'Central']

        data = []
        for i in range(num_records):
            transaction_date = self.fake.date_between(start_date='-2y', end_date='today')
            customer_id = self.fake.random_int(min=1, max=50000)
            product_category = random.choice(categories)

            # Create seasonal patterns
            month = transaction_date.month
            seasonal_multiplier = 1.5 if month in [11, 12] else (1.2 if month in [6, 7, 8] else 1.0)

            price = round(random.uniform(10, 500) * seasonal_multiplier, 2)
            quantity = random.randint(1, 5)

            data.append({
                'transaction_id': f'TXN_{i+1:06d}',
                'customer_id': customer_id,
                'product_id': f'PROD_{self.fake.random_int(min=1, max=10000):05d}',
                'product_category': product_category,
                'transaction_date': transaction_date,
                'price': price,
                'quantity': quantity,
                'total_amount': round(price * quantity, 2),
                'region': random.choice(regions),
                'customer_age': random.randint(18, 80),
                'is_repeat_customer': random.choice([True, False])
            })

            if (i + 1) % 100000 == 0:
                print(f"Generated {i+1:,} records...")

        df = pd.DataFrame(data)
        print("Sample data generation completed!")
        return df

    def clean_data(self, df):
        """Clean and preprocess the data"""
        print("Cleaning data...")

        # Handle missing values
        df = df.dropna()

        # Remove duplicates
        df = df.drop_duplicates(subset=['transaction_id'])

        # Data type conversions
        df['transaction_date'] = pd.to_datetime(df['transaction_date'])
        df['price'] = df['price'].astype(float)
        df['quantity'] = df['quantity'].astype(int)
        df['total_amount'] = df['total_amount'].astype(float)

        # Create derived features
        df['year'] = df['transaction_date'].dt.year
        df['month'] = df['transaction_date'].dt.month
        df['day_of_week'] = df['transaction_date'].dt.day_name()
        df['quarter'] = df['transaction_date'].dt.quarter

        # Calculate customer metrics
        customer_stats = df.groupby('customer_id').agg({
            'total_amount': ['sum', 'mean', 'count'],
            'transaction_date': ['min', 'max']
        }).reset_index()

        customer_stats.columns = ['customer_id', 'total_spent', 'avg_order_value',
                                'transaction_count', 'first_purchase', 'last_purchase']

        # Calculate customer lifetime in days
        customer_stats['customer_lifetime_days'] = (
            customer_stats['last_purchase'] - customer_stats['first_purchase']
        ).dt.days

        # Merge customer stats back to main dataframe
        df = df.merge(customer_stats, on='customer_id', how='left')

        print(f"Data cleaned. Final dataset shape: {df.shape}")
        return df

    def analyze_trends(self, df):
        """Perform trend analysis"""
        print("Analyzing purchasing trends...")

        # Monthly sales trends
        monthly_sales = df.groupby(['year', 'month']).agg({
            'total_amount': 'sum',
            'transaction_id': 'count'
        }).reset_index()
        monthly_sales.columns = ['year', 'month', 'revenue', 'transaction_count']

        # Category performance
        category_performance = df.groupby('product_category').agg({
            'total_amount': 'sum',
            'transaction_id': 'count',
            'customer_id': 'nunique'
        }).reset_index()
        category_performance.columns = ['category', 'revenue', 'transactions', 'unique_customers']

        # Regional analysis
        regional_analysis = df.groupby('region').agg({
            'total_amount': 'sum',
            'customer_id': 'nunique'
        }).reset_index()
        regional_analysis.columns = ['region', 'revenue', 'unique_customers']

        # Customer segmentation based on RFM
        current_date = df['transaction_date'].max()
        rfm = df.groupby('customer_id').agg({
            'transaction_date': lambda x: (current_date - x.max()).days,
            'transaction_id': 'count',
            'total_amount': 'sum'
        }).reset_index()
        rfm.columns = ['customer_id', 'recency', 'frequency', 'monetary']

        # Calculate RFM scores
        rfm['r_score'] = pd.qcut(rfm['recency'], 5, labels=[5, 4, 3, 2, 1])
        rfm['f_score'] = pd.qcut(rfm['frequency'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5])
        rfm['m_score'] = pd.qcut(rfm['monetary'], 5, labels=[1, 2, 3, 4, 5])

        rfm['rfm_score'] = rfm['r_score'].astype(str) + rfm['f_score'].astype(str) + rfm['m_score'].astype(str)

        return {
            'monthly_sales': monthly_sales,
            'category_performance': category_performance,
            'regional_analysis': regional_analysis,
            'rfm_analysis': rfm
        }

    def save_to_sqlite(self, df, db_path='data/ecommerce_data.db'):
        """Save data to SQLite database"""
        conn = sqlite3.connect(db_path)
        df.to_sql('transactions', conn, if_exists='replace', index=False)
        conn.close()
        print(f"Data saved to {db_path}")

    def run_pipeline(self, num_records=100000):
        """Run the complete data pipeline"""
        # Generate sample data
        df = self.generate_sample_data(num_records)

        # Clean data
        df_clean = self.clean_data(df)

        # Save cleaned data
        df_clean.to_csv('data/cleaned_ecommerce_data.csv', index=False)
        self.save_to_sqlite(df_clean)

        # Analyze trends
        analysis_results = self.analyze_trends(df_clean)

        return df_clean, analysis_results

if __name__ == "__main__":
    pipeline = ECommerceDataPipeline()
    df, results = pipeline.run_pipeline()
    print("Data pipeline completed successfully!")