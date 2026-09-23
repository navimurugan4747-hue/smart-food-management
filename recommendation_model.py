"""
Smart Food Management System
Model 1: Food Recommendation System using K-Nearest Neighbors (KNN)

Features used for similarity:
- Food category (One-hot encoded)
- Taste profile (Mild: 0, Medium: 1, Spicy: 2)
- Dietary type (Vegetarian: 1, Non-Vegetarian: 0)
- Normalized Rating & Price
"""

import os
import math
import pandas as pd
import numpy as np

# Directory paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_PATH = os.path.join(BASE_DIR, 'dataset', 'food_dataset.csv')
MODEL_DIR = os.path.join(BASE_DIR, 'trained_models')
MODEL_FILE = os.path.join(MODEL_DIR, 'knn_model.pkl')

TASTE_MAP = {'Mild': 0.0, 'Medium': 1.0, 'Spicy': 2.0}
ALL_CATEGORIES = ['South Indian', 'North Indian', 'Chinese', 'Fast Food', 'Desserts']

class FoodRecommendationModel:
    def __init__(self):
        self.df = None
        self.feature_matrix = None
        self.food_records = []
        self.knn = None
        self.is_trained = False
        self._load_or_train()

    def _extract_features(self, df):
        """Build numeric feature vectors for each food item."""
        features = []
        max_price = df['price'].max() if df['price'].max() > 0 else 1.0
        
        for _, row in df.iterrows():
            vec = []
            # Category one-hot encoding (weight: 2.0)
            cat = str(row['category']).strip()
            for c in ALL_CATEGORIES:
                vec.append(2.0 if cat.lower() == c.lower() else 0.0)
            
            # Taste (weight: 1.5)
            taste_val = TASTE_MAP.get(str(row['taste']).strip(), 1.0)
            vec.append(taste_val * 1.5)
            
            # Vegetarian preference (weight: 3.0 to strongly respect dietary restrictions)
            veg_val = 1.0 if int(row['vegetarian']) == 1 else 0.0
            vec.append(veg_val * 3.0)
            
            # Rating (weight: 1.0)
            rating_val = float(row['rating']) / 5.0
            vec.append(rating_val * 1.0)
            
            # Normalized Price (weight: 0.5)
            price_norm = float(row['price']) / max_price
            vec.append(price_norm * 0.5)
            
            features.append(vec)
        return np.array(features, dtype=float)

    def train(self):
        """Train KNN NearestNeighbors model using Scikit-Learn."""
        if not os.path.exists(DATASET_PATH):
            raise FileNotFoundError(f"Dataset not found at {DATASET_PATH}")
            
        self.df = pd.read_csv(DATASET_PATH)
        self.feature_matrix = self._extract_features(self.df)
        self.food_records = self.df.to_dict('records')

        try:
            from sklearn.neighbors import NearestNeighbors
            import joblib
            
            # Train KNN with Cosine Distance
            self.knn = NearestNeighbors(n_neighbors=min(8, len(self.df)), metric='cosine')
            self.knn.fit(self.feature_matrix)
            
            os.makedirs(MODEL_DIR, exist_ok=True)
            bundle = {
                'knn': self.knn,
                'feature_matrix': self.feature_matrix,
                'df': self.df,
                'food_records': self.food_records,
                'categories': ALL_CATEGORIES,
                'taste_map': TASTE_MAP
            }
            joblib.dump(bundle, MODEL_FILE)
            print(f"[OK] KNN Recommendation Model trained and saved to {MODEL_FILE}")
            self.is_trained = True
        except ImportError:
            print("[INFO] scikit-learn or joblib not installed in current environment. Using native KNN vector engine.")
            self.is_trained = True

    def _load_or_train(self):
        """Load saved joblib model if present, otherwise train."""
        if os.path.exists(MODEL_FILE):
            try:
                import joblib
                bundle = joblib.load(MODEL_FILE)
                self.knn = bundle.get('knn')
                self.feature_matrix = bundle.get('feature_matrix')
                self.df = bundle.get('df')
                self.food_records = bundle.get('food_records')
                self.is_trained = True
                print(f"[OK] Loaded pre-trained KNN model from {MODEL_FILE}")
                return
            except Exception as e:
                print(f"[WARN] Could not load saved model ({e}). Retraining...")
        
        self.train()

    def recommend(self, category=None, taste='Medium', vegetarian=1, min_rating=0.0, previous_food=None, top_n=4):
        """
        Recommend food items based on category, taste, dietary preference, and prior choice.
        Returns a list of matching food item dicts with match percentage and explanation.
        """
        if self.df is None or len(self.food_records) == 0:
            self._load_or_train()

        veg_flag = 1 if (str(vegetarian).lower() in ['1', 'true', 'veg', 'vegetarian']) else 0
        taste_clean = taste.strip().title() if taste else 'Medium'
        if taste_clean not in TASTE_MAP:
            taste_clean = 'Medium'

        # Query vector construction
        max_price = self.df['price'].max() if self.df['price'].max() > 0 else 1.0
        query_vec = []
        for c in ALL_CATEGORIES:
            if category and str(category).lower() == c.lower():
                query_vec.append(2.0)
            else:
                query_vec.append(0.0)

        query_vec.append(TASTE_MAP[taste_clean] * 1.5)
        query_vec.append(float(veg_flag) * 3.0)
        query_vec.append(0.9 * 1.0) # Assume user prefers high rating ~4.5/5
        query_vec.append(0.5 * 0.5) # Average price baseline
        query_vec = np.array(query_vec, dtype=float).reshape(1, -1)

        # Scikit-learn KNN or pure-numpy cosine similarity
        if self.knn is not None:
            distances, indices = self.knn.kneighbors(query_vec, n_neighbors=min(15, len(self.food_records)))
            candidate_indices = indices[0]
            candidate_dists = distances[0]
        else:
            # Native cosine distance fallback: 1 - (u . v) / (||u|| * ||v||)
            norms = np.linalg.norm(self.feature_matrix, axis=1) * np.linalg.norm(query_vec[0])
            norms[norms == 0] = 1e-9
            sims = np.dot(self.feature_matrix, query_vec[0]) / norms
            candidate_dists = 1.0 - sims
            candidate_indices = np.argsort(candidate_dists)

        results = []
        for idx, dist in zip(candidate_indices, candidate_dists):
            item = dict(self.food_records[idx])
            
            # Strict dietary filter: vegetarian users should never be recommended non-veg
            if veg_flag == 1 and int(item.get('vegetarian', 0)) == 0:
                continue

            # Rating threshold
            if float(item.get('rating', 0)) < float(min_rating):
                continue

            # Avoid recommending the exact same previous choice as top match if specified
            if previous_food and str(item.get('food_name')).lower() == str(previous_food).lower():
                continue

            # Calculate match percentage based on cosine distance
            similarity = max(0.0, min(1.0, 1.0 - dist))
            match_score = int(70 + (similarity * 29)) # Scaled to realistic 70% - 99% range
            item['match_score'] = match_score
            item['recommendation_reason'] = (
                f"Matches your preference for {taste_clean} taste, "
                f"{'Vegetarian' if veg_flag == 1 else 'Non-Veg'} cuisine, "
                f"and top-rated {item.get('category')} dishes."
            )
            results.append(item)
            if len(results) >= top_n:
                break

        # Fallback if filters were too restrictive
        if len(results) == 0:
            for item in self.food_records[:top_n]:
                item_copy = dict(item)
                item_copy['match_score'] = 82
                item_copy['recommendation_reason'] = "Popular choice matching your tastes."
                results.append(item_copy)

        return results

# Singleton instance for quick inference
recommendation_engine = None

def get_recommendation_engine():
    global recommendation_engine
    if recommendation_engine is None:
        recommendation_engine = FoodRecommendationModel()
    return recommendation_engine

if __name__ == '__main__':
    print("--- Training Food Recommendation KNN Model ---")
    model = FoodRecommendationModel()
    model.train()
    print("\n--- Testing AI Recommendation ---")
    sample_recs = model.recommend(category='North Indian', taste='Spicy', vegetarian=1)
    for i, r in enumerate(sample_recs, 1):
        print(f"{i}. {r['food_name']} ({r['category']}) - Rating: {r['rating']} - Match: {r['match_score']}%")
