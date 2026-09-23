"""
Master ML Training Script
Smart Food Management System

Executes training for all three Scikit-learn models:
1. Food Recommendation (KNN) -> trained_models/knn_model.pkl
2. Food Demand Prediction (Linear Regression) -> trained_models/demand_model.pkl
3. Food Waste Risk Prediction (Decision Tree) -> trained_models/waste_model.pkl
"""

import sys
import os

# Add parent directory to system path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from models.recommendation_model import FoodRecommendationModel
from models.demand_model import FoodDemandModel
from models.waste_model import FoodWasteModel

def main():
    print("=" * 65)
    print("  SMART FOOD MANAGEMENT SYSTEM - AIML MODEL TRAINING PIPELINE")
    print("=" * 65)

    # 1. Train Recommendation Model (KNN)
    print("\n[Step 1/3] Training Food Recommendation Model (KNN)...")
    try:
        rec_model = FoodRecommendationModel()
        rec_model.train()
        print("  -> KNN Model trained successfully.")
    except Exception as e:
        print(f"  [ERROR] Failed to train KNN model: {e}")

    # 2. Train Demand Prediction Model (Linear Regression)
    print("\n[Step 2/3] Training Food Demand Model (Linear Regression)...")
    try:
        demand_model = FoodDemandModel()
        demand_model.train()
        print("  -> Linear Regression Demand Model trained successfully.")
    except Exception as e:
        print(f"  [ERROR] Failed to train Demand model: {e}")

    # 3. Train Food Waste Risk Model (Decision Tree)
    print("\n[Step 3/3] Training Food Waste Model (Decision Tree Classifier)...")
    try:
        waste_model = FoodWasteModel()
        waste_model.train()
        print("  -> Decision Tree Waste Model trained successfully.")
    except Exception as e:
        print(f"  [ERROR] Failed to train Waste model: {e}")

    print("\n" + "=" * 65)
    print("  ALL AIML MODELS COMPILED & SAVED TO 'trained_models/' DIRECTORY")
    print("=" * 65)

if __name__ == '__main__':
    main()
