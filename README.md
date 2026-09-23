# Smart Food Management System Using Artificial Intelligence and Machine Learning

![Python](https://img.shields.io/badge/Python-3.9%20%7C%203.10%20%7C%203.11-blue?logo=python)
![Flask](https://img.shields.io/badge/Backend-Flask%203.0-lightgrey?logo=flask)
![Scikit-Learn](https://img.shields.io/badge/ML-Scikit--Learn-orange?logo=scikit-learn)
![MySQL](https://img.shields.io/badge/Database-MySQL%20%2B%20SQLite%20Fallback-blue?logo=mysql)
![Bootstrap](https://img.shields.io/badge/UI-Bootstrap%205-purple?logo=bootstrap)

An end-to-end college-level **AIML Mini Project** designed to optimize campus cafeterias and restaurant kitchens by preventing food waste, accurately forecasting meal preparation demands, and delivering personalized food recommendations to diners.

---

## 📌 Project Overview

Traditional cafeteria and commercial food operations suffer from two major flaws:
1. **Unpredictable Demand:** Cooking too much results in severe food wastage; cooking too little causes stockouts and lost revenue.
2. **Generic Menus:** Diners spend excess time searching for dishes matching their specific taste profiles and dietary restrictions.

This project solves both problems through three working **Machine Learning Models** integrated directly into a responsive **Python Flask** web application with a **MySQL** database.

---

## 🧠 AIML Models Integrated

### 1. Model 1 – Food Recommendation System
* **Algorithm:** **K-Nearest Neighbors (KNN)** using Cosine Distance
* **Inputs:** Food Category, Taste Preference (*Mild, Medium, Spicy*), Dietary Restriction (*Vegetarian / Non-Vegetarian*), Previous Favorite Dish, Minimum Rating.
* **Output:** Ranked list of recommended dishes with real-time match compatibility scores (e.g. 96% Match) and reason summaries.
* **Mathematical Concept:** Cosine similarity across multi-dimensional feature vectors:
  $$\text{Cosine Similarity}(u, v) = \frac{u \cdot v}{\|u\|_2 \|v\|_2}$$

### 2. Model 2 – Food Demand Prediction
* **Algorithm:** **Multivariate Linear Regression**
* **Inputs:** Day of the Week, Food Category, Previous Daily Orders Count, Previous Recorded Demand.
* **Output:** Predicted meal demand portions, suggested kitchen preparation quantity with a calibrated safety buffer (+12%), and a 7-day category projection curve rendered via **Chart.js**.
* **Mathematical Concept:** Ordinary Least Squares (OLS):
  $$\hat{y} = \theta_0 + \theta_1 \cdot \text{day} + \theta_2 \cdot \text{weekend} + \theta_3 \cdot \text{orders} + \theta_4 \cdot \text{demand} + \sum \theta_c \cdot \text{cat}_c$$

### 3. Model 3 – Food Waste Risk Prediction
* **Algorithm:** **Decision Tree Classifier**
* **Inputs:** Quantity Prepared, Expected Orders, Current Existing Stock, Remaining Shelf Life (Hours), Historical Wastage.
* **Output:** Risk Classification (**Low Waste Risk**, **Medium Waste Risk**, **High Waste Risk**), probability breakdown, and automated mitigation actions (e.g., Happy-Hour clearance discounts, freezing surplus, or dispatching alerts to local charity food banks).
* **Mathematical Concept:** Recursive binary splitting using the **Gini Impurity Index**:
  $$\text{Gini}(D) = 1 - \sum_{i=1}^{C} p_i^2$$

---

## 🏗️ Project Architecture & Directory Structure

```
Smart-Food-Management/
│
├── app.py                     # Main Flask web application & REST API routes
├── config.py                  # Database & application configuration
├── train_all.py               # Master pipeline to train & persist all 3 ML models
├── test_models.py             # Unit tests verifying ML inference & database
├── requirements.txt           # Python dependencies
├── README.md                  # Complete documentation & viva reference
│
├── dataset/
│   ├── food_dataset.csv       # Food menu items with taste, category, veg/non-veg, ratings
│   ├── demand_dataset.csv     # Historical demand records across days & categories
│   └── waste_dataset.csv      # Batch preparation, shelf-life, and waste risk training data
│
├── models/
│   ├── recommendation_model.py # KNN recommendation pipeline & inference engine
│   ├── demand_model.py         # Linear Regression demand predictor & chart generator
│   └── waste_model.py          # Decision Tree waste classifier & mitigation generator
│
├── trained_models/            # Directory where trained Joblib models (.pkl) are stored
│   ├── knn_model.pkl
│   ├── demand_model.pkl
│   └── waste_model.pkl
│
├── database/
│   ├── schema.sql             # MySQL database creation script with relational schema & seeds
│   └── db.py                  # Database abstraction (MySQL + auto-seeding SQLite fallback)
│
├── templates/                 # Jinja2 HTML5 responsive UI templates
│   ├── base.html              # Core navigation, branding, toasts & footer
│   ├── index.html             # Homepage with Hero, Search, Categories & AI CTA
│   ├── login.html             # User/Admin login with 1-click demo autofill
│   ├── register.html          # Registration with role selection
│   ├── menu.html              # Filterable food catalog with veg/non-veg badges
│   ├── food_details.html      # Ingredient inspection & similar AI dishes
│   ├── recommendation.html    # Interactive KNN recommendation portal
│   ├── demand_prediction.html # Linear Regression forecast cockpit with Chart.js
│   ├── waste_prediction.html  # Decision Tree waste risk evaluator
│   ├── user_dashboard.html    # Order tracking & personalized suggestions
│   ├── admin_dashboard.html   # Management metrics, live feed & inventory alerts
│   └── cart.html              # Meal tray with AJAX cart updates & checkout
│
└── static/
    ├── css/
    │   └── style.css          # Food-themed custom styling, card animations, veg badges
    └── js/
        └── script.js          # AJAX cart handling, toast alerts, credential helpers
```

---

## ⚙️ Installation & Setup Guide

### 1. Prerequisites
- **Python 3.9+** (Available from [python.org](https://www.python.org/downloads/))
- **MySQL Server** (Optional: e.g., MySQL Community Server or XAMPP)
  > **Note:** If MySQL is not running on your computer, the system will **automatically fall back to SQLite** (`database/smart_food_management.db`) and auto-seed tables. It will run without errors or manual configuration.

---

### 2. Step-by-Step Instructions

#### Step 1: Open Terminal in Project Folder
```bash
cd Smart-Food-Management
```

#### Step 2: Create and Activate Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

#### Step 3: Install Required Dependencies
```bash
pip install -r requirements.txt
```

#### Step 4: (Optional) Setup MySQL Database
If you wish to use MySQL:
1. Start your MySQL Server (via XAMPP or MySQL Command Line).
2. Open MySQL client and execute:
   ```bash
   mysql -u root -p < database/schema.sql
   ```
3. Set your environment variables (or leave default `root`/`root`):
   ```bash
   set MYSQL_HOST=localhost
   set MYSQL_USER=root
   set MYSQL_PASSWORD=your_password
   set MYSQL_DB=smart_food_management
   ```
*If you skip Step 4, the application seamlessly auto-generates the database in SQLite!*

#### Step 5: Train Machine Learning Models
Train all 3 Scikit-learn models with one command:
```bash
python train_all.py
```
This reads datasets from `dataset/`, trains the models, and writes the persistence files (`knn_model.pkl`, `demand_model.pkl`, `waste_model.pkl`) to `trained_models/`.

#### Step 6: Launch the Flask Web Application
```bash
python app.py
```
Open your web browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 🔑 Demo Login Credentials

| Role | Email Address | Password | Privileges |
| :--- | :--- | :--- | :--- |
| **Student / Diner** | `student@smartfood.com` | `user123` | View menu, get recommendations, place orders, view personal dashboard |
| **Kitchen Admin** | `admin@smartfood.com` | `admin123` | Kitchen dashboard, demand forecasting, waste risk management, stock alerts |

*(Tip: On the Login page, click the **"Student User"** or **"Admin Officer"** buttons to autofill credentials instantly!)*

---

## 🧪 Demonstration Walkthrough (For College Presentation)

When presenting to evaluators or professors, show this flow:

1. **Food Menu & Ordering (`/menu`):**
   - Point out the **Veg/Non-Veg badges** (green dot vs. red dot).
   - Filter by cuisines (South Indian, North Indian, Chinese, Fast Food, Desserts).
   - Add items to the meal tray and place an order.

2. **Model 1: Food Recommendation (`/recommend`):**
   - Select: *Category: North Indian*, *Taste: Spicy*, *Diet: Vegetarian*.
   - Click **“GET AI RECOMMENDATIONS”**.
   - Show the live **KNN cosine match scores** and explanation badges.

3. **Model 2: Demand Prediction (`/demand-prediction`):**
   - Enter: *Day: Friday*, *Category: North Indian*, *Previous Orders: 90*, *Previous Demand: 95*.
   - Click **“Predict Food Demand”**.
   - Explain the **Predicted Demand**, the **+12% preparation buffer**, and show the dynamic **Chart.js** 7-day trend curve.

4. **Model 3: Waste Risk Prediction (`/predict-waste`):**
   - Enter: *Quantity Prepared: 180*, *Expected Orders: 85*, *Current Stock: 50*, *Expiry: 4 hours*.
   - Click **“Predict Waste Risk”**.
   - Observe the **High Waste Risk** banner, the probability breakdown, and the suggested actions (e.g. 40% clearance discount or food donation protocol).

5. **Kitchen Admin Cockpit (`/admin-dashboard`):**
   - Show the live KPI cards (total diners, menu items, revenue, orders).
   - Show real-time low stock replenishment alerts and recent customer orders.

---

## 🎓 College Viva / Examination Q&A Guide

### Q1: Why did you choose KNN for the recommendation module instead of Collaborative Filtering?
> **Answer:** In campus cafeterias, users frequently order as guests or have new accounts (the **Cold Start problem**). KNN using content features (category, taste, dietary restrictions, rating) allows us to recommend highly relevant items immediately based on user preference vectors without requiring extensive past interaction history.

### Q2: What distance metric does your KNN model use?
> **Answer:** It uses **Cosine Distance** on normalized feature vectors. Cosine distance measures the angular orientation rather than magnitude, ensuring that taste and cuisine similarity are evaluated proportionally.

### Q3: Why is Linear Regression appropriate for Food Demand Prediction?
> **Answer:** Daily demand in cafeterias is strongly linear with respect to historical daily order averages, recent day demand, and day-of-week multipliers (e.g., higher volume on weekends and Fridays). Linear regression is computationally efficient, interpretable, and provides reliable continuous predictions for batch preparation.

### Q4: How does the Decision Tree classify Food Waste Risk?
> **Answer:** The Decision Tree evaluates feature splits using the **Gini Impurity criterion**. It determines critical cutoff thresholds such as the surplus ratio $\frac{\text{Quantity Prepared} + \text{Stock} - \text{Expected Orders}}{\text{Expected Orders}}$ and remaining expiry hours. If the surplus ratio exceeds 40% and expiry is under 6 hours, it traverses to the **High Risk** terminal leaf node.

### Q5: How is the database structured?
> **Answer:** It contains 8 relational tables (`users`, `food_items`, `orders`, `order_items`, `ratings`, `food_stock`, `demand_history`, `waste_history`) with foreign key constraints and cascade rules. The application supports dual-engine connectivity: it connects to MySQL as primary and gracefully falls back to an embedded SQLite database if MySQL is unavailable.

---

## 📜 License & Academic Integrity
Developed as an academic **Artificial Intelligence and Machine Learning (AIML)** mini project. Free to use and modify for learning, college project submissions, and portfolio presentations.
