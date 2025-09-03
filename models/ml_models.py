"""
Machine Learning models for the Auto-Bundler & Dynamic Pricing Agent system.
Provides demand forecasting, price elasticity analysis, and bundle recommendation scoring.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, ElasticNet
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
import joblib
import structlog

logger = structlog.get_logger(__name__)


class DemandForecastingModel:
    """
    Demand forecasting model using time series and feature-based approaches.
    """
    
    def __init__(self, model_type: str = "random_forest"):
        self.model_type = model_type
        self.model = None
        self.scaler = StandardScaler()
        self.feature_columns = []
        self.is_trained = False
        
        # Initialize model based on type
        if model_type == "random_forest":
            self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        elif model_type == "gradient_boosting":
            self.model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        elif model_type == "linear":
            self.model = LinearRegression()
        else:
            raise ValueError(f"Unsupported model type: {model_type}")
    
    def prepare_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Prepare features for demand forecasting"""
        features = data.copy()
        
        # Time-based features
        if 'timestamp' in features.columns:
            features['timestamp'] = pd.to_datetime(features['timestamp'])
            features['day_of_week'] = features['timestamp'].dt.dayofweek
            features['hour'] = features['timestamp'].dt.hour
            features['month'] = features['timestamp'].dt.month
            features['is_weekend'] = (features['day_of_week'] >= 5).astype(int)
        
        # Price features
        if 'current_price' in features.columns:
            features['price_log'] = np.log1p(features['current_price'])
            if 'base_price' in features.columns:
                features['price_ratio'] = features['current_price'] / features['base_price']
        
        # Stock features
        if 'current_stock' in features.columns:
            features['stock_log'] = np.log1p(features['current_stock'])
            if 'min_stock' in features.columns:
                features['stock_ratio'] = features['current_stock'] / features['min_stock']
        
        # Category encoding
        if 'category' in features.columns:
            le = LabelEncoder()
            features['category_encoded'] = le.fit_transform(features['category'])
        
        return features
    
    def train(self, historical_data: pd.DataFrame, target_column: str = 'demand') -> Dict[str, float]:
        """Train the demand forecasting model"""
        try:
            logger.info("Training demand forecasting model")
            
            # Prepare features
            features = self.prepare_features(historical_data)
            
            # Select feature columns (exclude target and non-numeric)
            exclude_cols = [target_column, 'timestamp', 'product_id', 'category']
            self.feature_columns = [col for col in features.columns 
                                  if col not in exclude_cols and features[col].dtype in ['int64', 'float64']]
            
            X = features[self.feature_columns]
            y = features[target_column]
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            # Train model
            self.model.fit(X_scaled, y)
            self.is_trained = True
            
            # Calculate metrics
            y_pred = self.model.predict(X_scaled)
            metrics = {
                'mse': mean_squared_error(y, y_pred),
                'mae': mean_absolute_error(y, y_pred),
                'r2': r2_score(y, y_pred),
                'training_samples': len(X)
            }
            
            logger.info("Demand forecasting model trained", metrics=metrics)
            return metrics
            
        except Exception as e:
            logger.error("Failed to train demand forecasting model", error=str(e))
            raise
    
    def predict(self, data: pd.DataFrame) -> np.ndarray:
        """Predict demand for given data"""
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        try:
            # Prepare features
            features = self.prepare_features(data)
            X = features[self.feature_columns]
            
            # Scale and predict
            X_scaled = self.scaler.transform(X)
            predictions = self.model.predict(X_scaled)
            
            return np.maximum(0, predictions)  # Ensure non-negative predictions
            
        except Exception as e:
            logger.error("Failed to predict demand", error=str(e))
            raise
    
    def save_model(self, filepath: str) -> None:
        """Save the trained model"""
        if not self.is_trained:
            raise ValueError("No trained model to save")
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_columns': self.feature_columns,
            'model_type': self.model_type
        }
        joblib.dump(model_data, filepath)
        logger.info(f"Model saved to {filepath}")
    
    def load_model(self, filepath: str) -> None:
        """Load a trained model"""
        model_data = joblib.load(filepath)
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.feature_columns = model_data['feature_columns']
        self.model_type = model_data['model_type']
        self.is_trained = True
        logger.info(f"Model loaded from {filepath}")


class PriceElasticityModel:
    """
    Price elasticity analysis model to understand price sensitivity.
    """
    
    def __init__(self):
        self.model = ElasticNet(alpha=0.1, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
    
    def calculate_elasticity(self, price_data: pd.DataFrame) -> Dict[str, float]:
        """Calculate price elasticity for products"""
        elasticities = {}
        
        try:
            for product_id in price_data['product_id'].unique():
                product_data = price_data[price_data['product_id'] == product_id].copy()
                
                if len(product_data) < 5:  # Need minimum data points
                    continue
                
                # Calculate percentage changes
                product_data = product_data.sort_values('timestamp')
                product_data['price_pct_change'] = product_data['price'].pct_change()
                product_data['demand_pct_change'] = product_data['demand'].pct_change()
                
                # Remove invalid data
                valid_data = product_data.dropna()
                
                if len(valid_data) < 3:
                    continue
                
                # Calculate elasticity (% change in demand / % change in price)
                price_changes = valid_data['price_pct_change']
                demand_changes = valid_data['demand_pct_change']
                
                # Filter out extreme changes
                valid_mask = (np.abs(price_changes) < 0.5) & (np.abs(demand_changes) < 2.0)
                price_changes = price_changes[valid_mask]
                demand_changes = demand_changes[valid_mask]
                
                if len(price_changes) > 0:
                    elasticity = np.mean(demand_changes / price_changes.replace(0, np.nan))
                    if not np.isnan(elasticity) and np.isfinite(elasticity):
                        elasticities[product_id] = float(elasticity)
            
            logger.info(f"Calculated elasticity for {len(elasticities)} products")
            return elasticities
            
        except Exception as e:
            logger.error("Failed to calculate price elasticity", error=str(e))
            return {}


class BundleRecommendationModel:
    """
    Bundle recommendation scoring model using collaborative filtering approaches.
    """
    
    def __init__(self):
        self.item_similarity = {}
        self.association_rules = []
        self.is_trained = False
    
    def train(self, transaction_data: pd.DataFrame) -> Dict[str, Any]:
        """Train bundle recommendation model"""
        try:
            logger.info("Training bundle recommendation model")
            
            # Calculate item co-occurrence matrix
            transactions = transaction_data.groupby('transaction_id')['product_id'].apply(list).tolist()
            
            # Build item-item similarity matrix
            all_items = set()
            for transaction in transactions:
                all_items.update(transaction)
            
            all_items = list(all_items)
            item_counts = {item: 0 for item in all_items}
            co_occurrence = {item: {other: 0 for other in all_items} for item in all_items}
            
            # Count occurrences and co-occurrences
            for transaction in transactions:
                for item in transaction:
                    item_counts[item] += 1
                    for other_item in transaction:
                        if item != other_item:
                            co_occurrence[item][other_item] += 1
            
            # Calculate similarities (Jaccard similarity)
            for item1 in all_items:
                self.item_similarity[item1] = {}
                for item2 in all_items:
                    if item1 != item2:
                        intersection = co_occurrence[item1][item2]
                        union = item_counts[item1] + item_counts[item2] - intersection
                        similarity = intersection / union if union > 0 else 0
                        self.item_similarity[item1][item2] = similarity
            
            self.is_trained = True
            
            metrics = {
                'total_items': len(all_items),
                'total_transactions': len(transactions),
                'avg_transaction_size': np.mean([len(t) for t in transactions])
            }
            
            logger.info("Bundle recommendation model trained", metrics=metrics)
            return metrics
            
        except Exception as e:
            logger.error("Failed to train bundle recommendation model", error=str(e))
            raise
    
    def get_recommendations(self, item_id: str, n_recommendations: int = 5) -> List[Tuple[str, float]]:
        """Get bundle recommendations for an item"""
        if not self.is_trained:
            raise ValueError("Model must be trained before making recommendations")
        
        if item_id not in self.item_similarity:
            return []
        
        similarities = self.item_similarity[item_id]
        sorted_items = sorted(similarities.items(), key=lambda x: x[1], reverse=True)
        
        return sorted_items[:n_recommendations]
    
    def score_bundle(self, items: List[str]) -> float:
        """Score a bundle based on item relationships"""
        if not self.is_trained or len(items) < 2:
            return 0.0
        
        total_similarity = 0.0
        pair_count = 0
        
        for i, item1 in enumerate(items):
            for item2 in items[i+1:]:
                if item1 in self.item_similarity and item2 in self.item_similarity[item1]:
                    total_similarity += self.item_similarity[item1][item2]
                    pair_count += 1
        
        return total_similarity / pair_count if pair_count > 0 else 0.0


class MLModelManager:
    """
    Manager class for all ML models in the system.
    """
    
    def __init__(self, settings: Any):
        self.settings = settings
        self.demand_model = DemandForecastingModel()
        self.elasticity_model = PriceElasticityModel()
        self.bundle_model = BundleRecommendationModel()
        
        self.models_dir = "models/trained_models"
        self._ensure_models_dir()
    
    def _ensure_models_dir(self):
        """Ensure models directory exists"""
        import os
        os.makedirs(self.models_dir, exist_ok=True)
    
    def train_all_models(self, data: Dict[str, pd.DataFrame]) -> Dict[str, Dict[str, Any]]:
        """Train all ML models with provided data"""
        results = {}
        
        try:
            # Train demand forecasting model
            if 'demand_data' in data:
                results['demand_forecasting'] = self.demand_model.train(data['demand_data'])
                self.demand_model.save_model(f"{self.models_dir}/demand_model.joblib")
            
            # Train bundle recommendation model
            if 'transaction_data' in data:
                results['bundle_recommendation'] = self.bundle_model.train(data['transaction_data'])
            
            logger.info("All models trained successfully", results=results)
            return results
            
        except Exception as e:
            logger.error("Failed to train models", error=str(e))
            raise
    
    def get_demand_forecast(self, product_data: pd.DataFrame, days_ahead: int = 7) -> pd.DataFrame:
        """Get demand forecast for products"""
        try:
            # Generate future dates
            base_date = datetime.now()
            future_data = []
            
            for _, product in product_data.iterrows():
                for day in range(1, days_ahead + 1):
                    future_date = base_date + timedelta(days=day)
                    future_record = product.copy()
                    future_record['timestamp'] = future_date
                    future_data.append(future_record)
            
            future_df = pd.DataFrame(future_data)
            
            # Predict demand
            if self.demand_model.is_trained:
                predictions = self.demand_model.predict(future_df)
                future_df['predicted_demand'] = predictions
            else:
                # Fallback to simple heuristics
                future_df['predicted_demand'] = future_df['current_stock'] * 0.1  # 10% of stock
            
            return future_df
            
        except Exception as e:
            logger.error("Failed to generate demand forecast", error=str(e))
            return pd.DataFrame()
    
    def get_price_elasticity(self, product_id: str, price_history: pd.DataFrame) -> float:
        """Get price elasticity for a specific product"""
        try:
            elasticities = self.elasticity_model.calculate_elasticity(price_history)
            return elasticities.get(product_id, -1.0)  # Default moderately elastic
            
        except Exception as e:
            logger.error(f"Failed to get price elasticity for {product_id}", error=str(e))
            return -1.0
    
    def score_bundle_recommendation(self, items: List[str]) -> float:
        """Score a bundle recommendation"""
        try:
            if self.bundle_model.is_trained:
                return self.bundle_model.score_bundle(items)
            else:
                # Fallback scoring based on simple heuristics
                return 0.5 if len(items) >= 2 else 0.0
                
        except Exception as e:
            logger.error("Failed to score bundle", error=str(e))
            return 0.0
    
    def generate_sample_data(self) -> Dict[str, pd.DataFrame]:
        """Generate sample data for model training (for demo purposes)"""
        np.random.seed(42)
        
        # Sample demand data
        products = ['PROD001', 'PROD002', 'PROD003', 'PROD004', 'PROD005']
        categories = ['audio', 'mobile_accessories', 'computer_accessories']
        
        demand_data = []
        transaction_data = []
        
        base_date = datetime.now() - timedelta(days=90)
        
        for day in range(90):
            current_date = base_date + timedelta(days=day)
            
            for product in products:
                # Generate demand data
                base_demand = np.random.poisson(10)
                price_effect = np.random.uniform(0.8, 1.2)
                seasonal_effect = 1 + 0.1 * np.sin(2 * np.pi * day / 30)  # Monthly seasonality
                
                demand = max(0, int(base_demand * price_effect * seasonal_effect))
                
                demand_data.append({
                    'timestamp': current_date,
                    'product_id': product,
                    'category': np.random.choice(categories),
                    'current_price': 50 + np.random.uniform(-10, 10),
                    'base_price': 50,
                    'current_stock': np.random.randint(10, 200),
                    'min_stock': 10,
                    'demand': demand
                })
                
                # Generate transaction data
                for _ in range(demand // 3):  # Some transactions have multiple items
                    transaction_id = f"TXN_{day}_{product}_{np.random.randint(1000)}"
                    transaction_data.append({
                        'transaction_id': transaction_id,
                        'product_id': product,
                        'timestamp': current_date
                    })
                    
                    # Sometimes add related products to transaction
                    if np.random.random() < 0.3:
                        related_product = np.random.choice([p for p in products if p != product])
                        transaction_data.append({
                            'transaction_id': transaction_id,
                            'product_id': related_product,
                            'timestamp': current_date
                        })
        
        return {
            'demand_data': pd.DataFrame(demand_data),
            'transaction_data': pd.DataFrame(transaction_data)
        }
