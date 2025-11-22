import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.neighbors import NearestNeighbors
import pickle
import os

class DonationPredictor:
    """
    ML Model for predicting donation demand and supply patterns
    """
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False

    def train(self, X_train, y_train):
        """Train the model"""
        X_scaled = self.scaler.fit_transform(X_train)
        self.model.fit(X_scaled, y_train)
        self.is_trained = True

    def predict(self, X):
        """Make predictions"""
        if not self.is_trained:
            raise ValueError("Model must be trained first")
        X_scaled = self.scaler.transform(X)
        return self.model.predict(X_scaled)

    def save(self, path):
        """Save model to file"""
        with open(path, 'wb') as f:
            pickle.dump({'model': self.model, 'scaler': self.scaler}, f)

    def load(self, path):
        """Load model from file"""
        if os.path.exists(path):
            with open(path, 'rb') as f:
                data = pickle.load(f)
                self.model = data['model']
                self.scaler = data['scaler']
                self.is_trained = True

class RecommendationEngine:
    """
    Collaborative filtering for donation recommendations
    """
    def __init__(self):
        self.knn = NearestNeighbors(n_neighbors=5, algorithm='ball_tree')
        self.is_fitted = False

    def fit(self, user_donation_matrix):
        """Fit the recommendation model"""
        self.knn.fit(user_donation_matrix)
        self.is_fitted = True

    def recommend(self, user_vector, n_recommendations=5):
        """Get recommendations for a user"""
        if not self.is_fitted:
            raise ValueError("Model must be fitted first")
        distances, indices = self.knn.kneighbors([user_vector], n_neighbors=n_recommendations)
        return indices[0], distances[0]

    def save(self, path):
        """Save model to file"""
        with open(path, 'wb') as f:
            pickle.dump(self.knn, f)

    def load(self, path):
        """Load model from file"""
        if os.path.exists(path):
            with open(path, 'rb') as f:
                self.knn = pickle.load(f)
                self.is_fitted = True

class AnomalyDetector:
    """
    Detect unusual donation patterns
    """
    @staticmethod
    def detect_outliers(data, threshold=2.5):
        """Detect outliers using z-score"""
        mean = np.mean(data)
        std = np.std(data)
        z_scores = np.abs((data - mean) / std)
        return z_scores > threshold

    @staticmethod
    def detect_fraud(donation_data):
        """Detect suspicious donation patterns"""
        flags = []
        
        # Check if quantity is unusually high
        if donation_data['quantity'] > 1000:
            flags.append('unusually_high_quantity')
        
        # Check if same user donating too frequently
        if donation_data['frequency_per_day'] > 10:
            flags.append('high_frequency')
        
        # Check location inconsistencies
        if donation_data['location_variance'] > 100:  # km
            flags.append('location_inconsistency')
        
        return len(flags) > 0, flags
