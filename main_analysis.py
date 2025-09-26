#!/usr/bin/env python3
"""
InsightLens - Large-Scale E-Commerce Data Analysis

A comprehensive data analysis pipeline for e-commerce transaction data featuring:
- Data cleaning and preprocessing
- Predictive modeling for sales forecasting and customer segmentation
- Interactive dashboards for business insights
- Customer retention and churn analysis

Author: InsightLens Team
Version: 1.0.0
"""

import os
import sys
import time
from datetime import datetime
import pandas as pd
import numpy as np

# Import custom modules
sys.path.append('scripts')
sys.path.append('models')
sys.path.append('visualizations')

from data_pipeline import ECommerceDataPipeline
from predictive_models import ModelManager
from dashboard import ECommerceDashboard

class InsightLensAnalyzer:
    def __init__(self):
        self.pipeline = ECommerceDataPipeline()
        self.model_manager = ModelManager()
        self.dashboard = None
        self.df = None
        self.analysis_results = None
        self.model_results = None

    def run_data_pipeline(self, num_records=100000):
        """Run the complete data pipeline"""
        print("=" * 60)
        print("INSIGHTLENS - E-COMMERCE DATA ANALYSIS PIPELINE")
        print("=" * 60)
        print(f"Starting analysis with {num_records:,} transaction records...")

        start_time = time.time()

        # Generate and process data
        self.df, self.analysis_results = self.pipeline.run_pipeline(num_records)

        pipeline_time = time.time() - start_time
        print(f"\nData pipeline completed in {pipeline_time:.2f} seconds")

        return self.df

    def train_predictive_models(self):
        """Train all predictive models"""
        print("\n" + "=" * 60)
        print("TRAINING PREDICTIVE MODELS")
        print("=" * 60)

        if self.df is None:
            print("Error: No data available. Please run data pipeline first.")
            return None

        start_time = time.time()

        # Train models
        self.model_results = self.model_manager.train_all_models(self.df)

        # Save models
        os.makedirs('models', exist_ok=True)
        self.model_manager.save_models('models/trained_models.pkl')

        model_time = time.time() - start_time
        print(f"\nModel training completed in {model_time:.2f} seconds")

        # Display model performance
        self.display_model_performance()

        return self.model_results

    def display_model_performance(self):
        """Display performance metrics for all trained models"""
        print("\n" + "-" * 50)
        print("MODEL PERFORMANCE SUMMARY")
        print("-" * 50)

        if self.model_results:
            # Sales forecasting performance
            if 'sales_forecast' in self.model_results:
                rmse = self.model_results['sales_forecast']['rmse']
                print(f"Sales Forecasting RMSE: ${rmse:.2f}")

                print("\nTop Feature Importances (Sales Forecasting):")
                feature_imp = self.model_results['sales_forecast']['feature_importance']
                for feature, importance in sorted(feature_imp.items(), key=lambda x: x[1], reverse=True)[:5]:
                    print(f"  {feature}: {importance:.4f}")

            # High-value customer prediction
            if 'high_value_sklearn' in self.model_results:
                accuracy = self.model_results['high_value_sklearn']['accuracy']
                print(f"\nHigh-Value Customer Prediction Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")

                print("\nTop Feature Importances (Customer Prediction):")
                feature_imp = self.model_results['high_value_sklearn']['feature_importance']
                for feature, importance in sorted(feature_imp.items(), key=lambda x: x[1], reverse=True)[:5]:
                    print(f"  {feature}: {importance:.4f}")

            # PyTorch model performance
            if 'high_value_pytorch' in self.model_results:
                pytorch_accuracy = self.model_results['high_value_pytorch']['accuracy']
                print(f"\nPyTorch Neural Network Accuracy: {pytorch_accuracy:.4f} ({pytorch_accuracy*100:.2f}%)")

            # Customer segmentation results
            if 'customer_segmentation' in self.model_results:
                print("\nCustomer Segmentation Analysis:")
                cluster_analysis = self.model_results['customer_segmentation']['cluster_analysis']
                print(cluster_analysis.to_string())

    def generate_insights(self):
        """Generate business insights from the analysis"""
        print("\n" + "=" * 60)
        print("BUSINESS INSIGHTS & RECOMMENDATIONS")
        print("=" * 60)

        if self.df is None or self.analysis_results is None:
            print("Error: No analysis results available.")
            return

        # Revenue insights
        total_revenue = self.df['total_amount'].sum()
        avg_order_value = self.df['total_amount'].mean()
        unique_customers = self.df['customer_id'].nunique()

        print(f"📊 REVENUE ANALYSIS")
        print(f"   Total Revenue: ${total_revenue:,.2f}")
        print(f"   Average Order Value: ${avg_order_value:.2f}")
        print(f"   Unique Customers: {unique_customers:,}")
        print(f"   Revenue per Customer: ${total_revenue/unique_customers:.2f}")

        # Category insights
        print(f"\n📈 CATEGORY PERFORMANCE")
        category_revenue = self.analysis_results['category_performance'].sort_values('revenue', ascending=False)
        print(f"   Top Category: {category_revenue.iloc[0]['category']} (${category_revenue.iloc[0]['revenue']:,.2f})")
        print(f"   Growth Category: {category_revenue.iloc[1]['category']} (${category_revenue.iloc[1]['revenue']:,.2f})")

        # Regional insights
        print(f"\n🌍 REGIONAL ANALYSIS")
        regional_revenue = self.analysis_results['regional_analysis'].sort_values('revenue', ascending=False)
        print(f"   Top Region: {regional_revenue.iloc[0]['region']} (${regional_revenue.iloc[0]['revenue']:,.2f})")
        print(f"   Revenue Distribution: {len(regional_revenue)} regions analyzed")

        # Seasonal insights
        monthly_sales = self.analysis_results['monthly_sales']
        peak_month = monthly_sales.loc[monthly_sales['revenue'].idxmax()]
        print(f"\n📅 SEASONAL TRENDS")
        print(f"   Peak Month: {int(peak_month['year'])}-{int(peak_month['month']):02d} (${peak_month['revenue']:,.2f})")

        # Customer segmentation insights
        if 'customer_segmentation' in self.model_results:
            rfm = self.model_results['customer_segmentation']['customer_features']
            high_value_segment = rfm[rfm['cluster'] == rfm.groupby('cluster')['monetary_total'].mean().idxmax()]

            print(f"\n👥 CUSTOMER SEGMENTATION")
            print(f"   Customer Segments: {rfm['cluster'].nunique()}")
            print(f"   High-Value Segment Size: {len(high_value_segment):,} customers")
            print(f"   High-Value Segment Revenue: ${high_value_segment['monetary_total'].sum():,.2f}")

        # Recommendations
        print(f"\n💡 STRATEGIC RECOMMENDATIONS")
        print("   1. Focus marketing efforts on top-performing categories")
        print("   2. Implement targeted campaigns for high-value customer segments")
        print("   3. Optimize inventory for seasonal demand patterns")
        print("   4. Develop retention programs for at-risk customers")
        print("   5. Expand operations in high-performing regions")

    def create_dashboard(self):
        """Generate interactive dashboards"""
        print("\n" + "=" * 60)
        print("GENERATING INTERACTIVE DASHBOARDS")
        print("=" * 60)

        if self.df is None:
            print("Error: No data available for dashboard generation.")
            return

        # Create dashboards directory
        os.makedirs('visualizations', exist_ok=True)

        # Initialize dashboard with current data
        self.dashboard = ECommerceDashboard()
        self.dashboard.df = self.df  # Use our processed data

        start_time = time.time()

        # Generate all dashboards
        dashboards, kpis = self.dashboard.generate_full_dashboard()

        dashboard_time = time.time() - start_time
        print(f"\nDashboard generation completed in {dashboard_time:.2f} seconds")

        # Display KPIs
        print("\n📊 KEY PERFORMANCE INDICATORS")
        for kpi, value in kpis.items():
            print(f"   {kpi}: {value}")

        return dashboards, kpis

    def export_results(self):
        """Export analysis results to various formats"""
        print("\n" + "=" * 60)
        print("EXPORTING RESULTS")
        print("=" * 60)

        # Create exports directory
        os.makedirs('exports', exist_ok=True)

        export_files = []

        if self.df is not None:
            # Export cleaned dataset
            csv_file = 'exports/cleaned_ecommerce_data.csv'
            self.df.to_csv(csv_file, index=False)
            export_files.append(csv_file)

            # Export Excel summary
            excel_file = 'exports/analysis_summary.xlsx'
            with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
                # Main dataset sample
                self.df.head(1000).to_excel(writer, sheet_name='Sample Data', index=False)

                # Analysis results
                if self.analysis_results:
                    self.analysis_results['category_performance'].to_excel(writer, sheet_name='Category Analysis', index=False)
                    self.analysis_results['regional_analysis'].to_excel(writer, sheet_name='Regional Analysis', index=False)
                    self.analysis_results['monthly_sales'].to_excel(writer, sheet_name='Monthly Sales', index=False)

                    if 'customer_segmentation' in self.model_results:
                        rfm_sample = self.model_results['customer_segmentation']['customer_features'].head(1000)
                        rfm_sample.to_excel(writer, sheet_name='Customer Segments', index=False)

            export_files.append(excel_file)

        print("Exported files:")
        for file in export_files:
            print(f"  ✓ {file}")

        return export_files

    def run_complete_analysis(self, num_records=100000):
        """Run the complete InsightLens analysis pipeline"""
        print("🔍 Starting InsightLens Complete Analysis...")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        total_start_time = time.time()

        try:
            # Step 1: Data Pipeline
            self.run_data_pipeline(num_records)

            # Step 2: Train Models
            self.train_predictive_models()

            # Step 3: Generate Insights
            self.generate_insights()

            # Step 4: Create Dashboards
            self.create_dashboard()

            # Step 5: Export Results
            self.export_results()

            total_time = time.time() - total_start_time

            print("\n" + "=" * 60)
            print("ANALYSIS COMPLETED SUCCESSFULLY! 🎉")
            print("=" * 60)
            print(f"Total execution time: {total_time:.2f} seconds")
            print(f"Data processed: {len(self.df):,} transactions")
            print(f"Models trained: 4 predictive models")
            print(f"Dashboards created: 6 interactive visualizations")

            print("\n📁 OUTPUT FILES:")
            print("  📊 Dashboards: visualizations/*.html")
            print("  🤖 Models: models/trained_models.pkl")
            print("  📈 Data: data/cleaned_ecommerce_data.csv")
            print("  📋 Exports: exports/analysis_summary.xlsx")

            return True

        except Exception as e:
            print(f"\n❌ Analysis failed with error: {str(e)}")
            return False

def main():
    """Main execution function"""
    analyzer = InsightLensAnalyzer()

    # Run complete analysis with sample data
    success = analyzer.run_complete_analysis(num_records=100000)

    if success:
        print("\n✨ InsightLens analysis pipeline completed successfully!")
        print("Open the HTML files in visualizations/ folder to view interactive dashboards.")
    else:
        print("\n❌ Analysis pipeline failed. Please check the error messages above.")

if __name__ == "__main__":
    main()