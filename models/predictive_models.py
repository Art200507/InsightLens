import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import mean_squared_error, accuracy_score, classification_report
from sklearn.cluster import KMeans
import torch
import torch.nn as nn
import torch.optim as optim
from datetime import datetime, timedelta
import pickle
import warnings
warnings.filterwarnings('ignore')

class SalesForecastModel:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoders = {}

    def prepare_features(self, df):
        """Prepare features for sales forecasting"""
        # Create time-based features
        df['year'] = df['transaction_date'].dt.year
        df['month'] = df['transaction_date'].dt.month
        df['day'] = df['transaction_date'].dt.day
        df['day_of_week'] = df['transaction_date'].dt.dayofweek
        df['quarter'] = df['transaction_date'].dt.quarter
        df['is_weekend'] = (df['transaction_date'].dt.dayofweek >= 5).astype(int)

        # Encode categorical variables
        categorical_cols = ['product_category', 'region']
        for col in categorical_cols:
            if col not in self.label_encoders:
                self.label_encoders[col] = LabelEncoder()
            df[f'{col}_encoded'] = self.label_encoders[col].fit_transform(df[col])

        # Create lag features
        df_sorted = df.sort_values('transaction_date')
        df_sorted['sales_lag_7'] = df_sorted['total_amount'].shift(7)
        df_sorted['sales_lag_30'] = df_sorted['total_amount'].shift(30)

        # Moving averages
        df_sorted['sales_ma_7'] = df_sorted['total_amount'].rolling(window=7).mean()
        df_sorted['sales_ma_30'] = df_sorted['total_amount'].rolling(window=30).mean()

        return df_sorted.dropna()

    def train(self, df):
        """Train sales forecasting model"""
        print("Training sales forecasting model...")

        # Prepare features
        df_features = self.prepare_features(df.copy())

        feature_cols = ['year', 'month', 'day', 'day_of_week', 'quarter', 'is_weekend',
                       'product_category_encoded', 'region_encoded', 'customer_age',
                       'sales_lag_7', 'sales_lag_30', 'sales_ma_7', 'sales_ma_30']

        X = df_features[feature_cols]
        y = df_features['total_amount']

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        # Train Random Forest model
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.model.fit(X_train_scaled, y_train)

        # Evaluate
        y_pred = self.model.predict(X_test_scaled)
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)

        print(f"Sales Forecasting RMSE: {rmse:.2f}")

        return {
            'model': self.model,
            'rmse': rmse,
            'feature_importance': dict(zip(feature_cols, self.model.feature_importances_))
        }

class CustomerSegmentationModel:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()

    def create_customer_features(self, df):
        """Create customer-level features for segmentation"""
        # Calculate RFM metrics
        current_date = df['transaction_date'].max()

        customer_features = df.groupby('customer_id').agg({
            'transaction_date': lambda x: (current_date - x.max()).days,  # Recency
            'transaction_id': 'count',  # Frequency
            'total_amount': ['sum', 'mean'],  # Monetary
            'product_category': lambda x: x.nunique(),  # Category diversity
            'customer_age': 'first',
            'region': 'first'
        }).reset_index()

        # Flatten column names
        customer_features.columns = ['customer_id', 'recency', 'frequency', 'monetary_total',
                                   'monetary_avg', 'category_diversity', 'age', 'region']

        # Create additional features
        customer_features['avg_days_between_purchases'] = customer_features['recency'] / customer_features['frequency']
        customer_features['total_per_category'] = customer_features['monetary_total'] / customer_features['category_diversity']

        return customer_features

    def train_clustering(self, df, n_clusters=5):
        """Train K-means clustering for customer segmentation"""
        print("Training customer segmentation model...")

        # Create customer features
        customer_features = self.create_customer_features(df)

        # Select features for clustering
        feature_cols = ['recency', 'frequency', 'monetary_total', 'monetary_avg',
                       'category_diversity', 'age', 'avg_days_between_purchases']

        X = customer_features[feature_cols].fillna(0)

        # Scale features
        X_scaled = self.scaler.fit_transform(X)

        # Train K-means
        self.model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        clusters = self.model.fit_predict(X_scaled)

        customer_features['cluster'] = clusters

        # Analyze clusters
        cluster_analysis = customer_features.groupby('cluster').agg({
            'recency': 'mean',
            'frequency': 'mean',
            'monetary_total': 'mean',
            'customer_id': 'count'
        }).round(2)

        print("Cluster Analysis:")
        print(cluster_analysis)

        return {
            'customer_features': customer_features,
            'cluster_analysis': cluster_analysis,
            'model': self.model
        }

class HighValueCustomerPredictor:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoders = {}

    def create_features(self, df):
        """Create features for high-value customer prediction"""
        # Define high-value customers (top 20% by total spending)
        customer_spending = df.groupby('customer_id')['total_amount'].sum()
        threshold = customer_spending.quantile(0.8)
        high_value_customers = set(customer_spending[customer_spending >= threshold].index)

        # Create customer features
        customer_features = df.groupby('customer_id').agg({
            'total_amount': ['sum', 'mean', 'std'],
            'transaction_id': 'count',
            'product_category': lambda x: x.nunique(),
            'customer_age': 'first',
            'region': 'first',
            'transaction_date': lambda x: (x.max() - x.min()).days
        }).reset_index()

        # Flatten column names
        customer_features.columns = ['customer_id', 'total_spent', 'avg_order_value', 'spending_std',
                                   'transaction_count', 'category_diversity', 'age', 'region',
                                   'customer_lifetime_days']

        # Create target variable
        customer_features['is_high_value'] = customer_features['customer_id'].apply(
            lambda x: 1 if x in high_value_customers else 0
        )

        # Fill NaN values
        customer_features['spending_std'] = customer_features['spending_std'].fillna(0)
        customer_features['customer_lifetime_days'] = customer_features['customer_lifetime_days'].fillna(0)

        # Encode categorical variables
        if 'region' not in self.label_encoders:
            self.label_encoders['region'] = LabelEncoder()
        customer_features['region_encoded'] = self.label_encoders['region'].fit_transform(customer_features['region'])

        return customer_features

    def train(self, df):
        """Train high-value customer prediction model"""
        print("Training high-value customer prediction model...")

        # Create features
        customer_features = self.create_features(df)

        feature_cols = ['total_spent', 'avg_order_value', 'spending_std', 'transaction_count',
                       'category_diversity', 'age', 'region_encoded', 'customer_lifetime_days']

        X = customer_features[feature_cols]
        y = customer_features['is_high_value']

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)

        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        # Train Random Forest classifier
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.model.fit(X_train_scaled, y_train)

        # Evaluate
        y_pred = self.model.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)

        print(f"High-value customer prediction accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred))

        return {
            'model': self.model,
            'accuracy': accuracy,
            'feature_importance': dict(zip(feature_cols, self.model.feature_importances_))
        }

class PyTorchNeuralNetwork(nn.Module):
    def __init__(self, input_size, hidden_size=64):
        super(PyTorchNeuralNetwork, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        self.fc3 = nn.Linear(hidden_size, 1)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.2)

    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.relu(self.fc2(x))
        x = self.dropout(x)
        x = torch.sigmoid(self.fc3(x))
        return x

class PyTorchHighValuePredictor:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()

    def train(self, df):
        """Train PyTorch neural network for high-value customer prediction"""
        print("Training PyTorch neural network...")

        # Prepare data (reuse feature creation from previous model)
        predictor = HighValueCustomerPredictor()
        customer_features = predictor.create_features(df)

        feature_cols = ['total_spent', 'avg_order_value', 'spending_std', 'transaction_count',
                       'category_diversity', 'age', 'customer_lifetime_days']

        X = customer_features[feature_cols].values
        y = customer_features['is_high_value'].values

        # Scale features
        X_scaled = self.scaler.fit_transform(X)

        # Convert to PyTorch tensors
        X_tensor = torch.FloatTensor(X_scaled)
        y_tensor = torch.FloatTensor(y.reshape(-1, 1))

        # Split data
        split_idx = int(0.8 * len(X_tensor))
        X_train, X_test = X_tensor[:split_idx], X_tensor[split_idx:]
        y_train, y_test = y_tensor[:split_idx], y_tensor[split_idx:]

        # Initialize model
        input_size = X_train.shape[1]
        self.model = PyTorchNeuralNetwork(input_size)

        # Training parameters
        criterion = nn.BCELoss()
        optimizer = optim.Adam(self.model.parameters(), lr=0.001)

        # Training loop
        epochs = 100
        for epoch in range(epochs):
            self.model.train()
            optimizer.zero_grad()

            outputs = self.model(X_train)
            loss = criterion(outputs, y_train)

            loss.backward()
            optimizer.step()

            if (epoch + 1) % 20 == 0:
                print(f'Epoch [{epoch+1}/{epochs}], Loss: {loss.item():.4f}')

        # Evaluation
        self.model.eval()
        with torch.no_grad():
            test_outputs = self.model(X_test)
            predicted = (test_outputs > 0.5).float()
            accuracy = (predicted == y_test).float().mean().item()

        print(f"PyTorch model accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")

        return {
            'model': self.model,
            'accuracy': accuracy
        }

class ModelManager:
    def __init__(self):
        self.models = {}

    def train_all_models(self, df):
        """Train all predictive models"""
        print("Training all predictive models...")

        # Sales forecasting
        sales_model = SalesForecastModel()
        sales_results = sales_model.train(df)
        self.models['sales_forecast'] = sales_model

        # Customer segmentation
        segmentation_model = CustomerSegmentationModel()
        segmentation_results = segmentation_model.train_clustering(df)
        self.models['customer_segmentation'] = segmentation_model

        # High-value customer prediction (scikit-learn)
        high_value_model = HighValueCustomerPredictor()
        high_value_results = high_value_model.train(df)
        self.models['high_value_sklearn'] = high_value_model

        # High-value customer prediction (PyTorch)
        pytorch_model = PyTorchHighValuePredictor()
        pytorch_results = pytorch_model.train(df)
        self.models['high_value_pytorch'] = pytorch_model

        return {
            'sales_forecast': sales_results,
            'customer_segmentation': segmentation_results,
            'high_value_sklearn': high_value_results,
            'high_value_pytorch': pytorch_results
        }

    def save_models(self, filepath='models/trained_models.pkl'):
        """Save all trained models"""
        with open(filepath, 'wb') as f:
            pickle.dump(self.models, f)
        print(f"Models saved to {filepath}")

if __name__ == "__main__":
    # Load data
    df = pd.read_csv('data/cleaned_ecommerce_data.csv')
    df['transaction_date'] = pd.to_datetime(df['transaction_date'])

    # Train all models
    model_manager = ModelManager()
    results = model_manager.train_all_models(df)

    # Save models
    model_manager.save_models()

    print("All models trained successfully!")