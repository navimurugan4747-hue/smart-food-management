"""
Unit & Integration Test Suite
Smart Food Management System
Verifies datasets, database access, and all 3 ML models.
"""

import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from models.recommendation_model import FoodRecommendationModel
from models.demand_model import FoodDemandModel
from models.waste_model import FoodWasteModel
from database.db import get_db, get_all_food

def test_datasets():
    print("[TEST 1/5] Checking Datasets...")
    datasets = ['food_dataset.csv', 'demand_dataset.csv', 'waste_dataset.csv']
    for ds in datasets:
        path = os.path.join(BASE_DIR, 'dataset', ds)
        assert os.path.exists(path), f"Missing dataset: {ds}"
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            assert len(lines) > 20, f"Dataset {ds} has too few rows ({len(lines)})"
    print("  -> All 3 datasets exist and contain rich sample data.")

def test_recommendation_model():
    print("\n[TEST 2/5] Testing Model 1: KNN Food Recommendation...")
    model = FoodRecommendationModel()
    recs = model.recommend(category='North Indian', taste='Spicy', vegetarian=1, top_n=3)
    assert len(recs) > 0, "No recommendations returned"
    for r in recs:
        assert r['vegetarian'] == 1, "Dietary violation: Non-veg dish returned for vegetarian request"
        assert 'match_score' in r, "Match score missing"
        assert r['match_score'] >= 50, "Unrealistic match score"
    print(f"  -> Returned {len(recs)} valid recommendations. Top match: {recs[0]['food_name']} ({recs[0]['match_score']}%)")

def test_demand_model():
    print("\n[TEST 2/5] Testing Model 2: Linear Regression Demand Prediction...")
    model = FoodDemandModel()
    res = model.predict(day='Saturday', food_category='Fast Food', previous_orders=110, previous_demand=120)
    assert res['predicted_demand'] > 0, "Predicted demand must be positive"
    assert res['suggested_preparation'] >= res['predicted_demand'], "Preparation quantity must include buffer"
    assert len(res['chart_labels']) == 7, "Chart data must contain 7 days"
    print(f"  -> Predicted demand: {res['predicted_demand']} units, Prep: {res['suggested_preparation']} units (Buffer: +{res['buffer_units']})")

def test_waste_model():
    print("\n[TEST 4/5] Testing Model 3: Decision Tree Waste Risk Prediction...")
    model = FoodWasteModel()
    # High risk case: high prep, low expected orders, high stock, short expiry
    high_risk = model.predict(quantity_prepared=180, expected_orders=70, current_stock=60, expiry_hours=3, previous_wastage=30)
    assert high_risk['risk_class'] == 'high', f"Expected 'high' risk, got {high_risk['risk_class']}"
    assert 'High' in high_risk['probabilities'], "Probabilities dictionary missing 'High' key"

    # Low risk case: low prep, high expected orders, long expiry
    low_risk = model.predict(quantity_prepared=60, expected_orders=80, current_stock=5, expiry_hours=36, previous_wastage=1)
    assert low_risk['risk_class'] == 'low', f"Expected 'low' risk, got {low_risk['risk_class']}"
    print(f"  -> High risk classified correctly: {high_risk['risk_level']} (High prob: {high_risk['probabilities']['High']}%)")
    print(f"  -> Low risk classified correctly: {low_risk['risk_level']} (Low prob: {low_risk['probabilities']['Low']}%)")

def test_database():
    print("\n[TEST 5/5] Testing Database Layer & Seed Integrity...")
    db = get_db()
    items = get_all_food()
    assert len(items) > 10, f"Expected at least 10 food items in database, found {len(items)}"
    user = db.query("SELECT * FROM users WHERE email = ?", ('admin@smartfood.com',), one=True)
    assert user is not None, "Default admin user missing"
    assert user['role'] == 'admin', "Admin role mismatch"
    print(f"  -> Database operational in {db.engine_type.upper()} mode with {len(items)} food items loaded.")

if __name__ == '__main__':
    print("=" * 60)
    print("  RUNNING SMART FOOD MANAGEMENT SYSTEM AUTOMATED TESTS")
    print("=" * 60)
    test_datasets()
    test_recommendation_model()
    test_demand_model()
    test_waste_model()
    test_database()
    print("\n" + "=" * 60)
    print("  ALL 5 TEST SUITES PASSED SUCCESSFULLY! (100% OPERATIONAL)")
    print("=" * 60)
