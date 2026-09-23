"""
Smart Food Management System Using Artificial Intelligence and Machine Learning
Flask Application Backend & REST APIs
"""

import os
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import check_password_hash

from config import Config
from db import (
    get_db, get_all_food, get_food_by_id, get_user_by_email,
    create_user, place_order, get_orders_by_user, get_admin_dashboard_data
)
from models.recommendation_model import get_recommendation_engine
from models.demand_model import get_demand_engine
from models.waste_model import get_waste_engine

app = Flask(__name__)
app.config.from_object(Config)

# Initialize database on startup
with app.app_context():
    get_db()

# Global template context processor
@app.context_processor
def inject_global_data():
    cart = session.get('cart', {})
    cart_count = sum(item.get('quantity', 1) for item in cart.values())
    user_name = session.get('user_name', None)
    user_role = session.get('user_role', None)
    return dict(cart_count=cart_count, current_user=user_name, current_role=user_role)

# -------------------------------------------------------------
# AUTHENTICATION ROUTES
# -------------------------------------------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()

        user = get_user_by_email(email)
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_email'] = user['email']
            session['user_role'] = user['role']
            flash(f"Welcome back, {user['name']}!", 'success')
            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password. Please try again.', 'danger')
            return render_template('login.html', email=email)

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        role = request.form.get('role', 'user')

        if not name or not email or not password:
            flash('All fields are required.', 'danger')
            return render_template('register.html')

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html')

        existing = get_user_by_email(email)
        if existing:
            flash('An account with this email already exists. Please login.', 'warning')
            return redirect(url_for('login'))

        create_user(name, email, password, role=role)
        flash('Account registered successfully! Please login with your credentials.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out safely.', 'info')
    return redirect(url_for('index'))

# -------------------------------------------------------------
# CORE APPLICATION PAGES
# -------------------------------------------------------------
@app.route('/')
def index():
    featured_items = get_all_food()[:6]
    categories = ['South Indian', 'North Indian', 'Chinese', 'Fast Food', 'Desserts']
    return render_template('index.html', featured_items=featured_items, categories=categories)

@app.route('/menu')
def menu():
    category = request.args.get('category', 'all')
    search = request.args.get('search', '').strip()
    veg_only = request.args.get('vegetarian', '')
    
    items = get_all_food(category=category, search=search, veg_only=veg_only)
    categories = ['All', 'South Indian', 'North Indian', 'Chinese', 'Fast Food', 'Desserts']
    return render_template('menu.html', items=items, active_category=category, search=search, veg_only=veg_only, categories=categories)

@app.route('/food/<int:food_id>')
def food_details(food_id):
    item = get_food_by_id(food_id)
    if not item:
        flash('Food item not found.', 'danger')
        return redirect(url_for('menu'))
    
    # KNN recommendations for similar items
    engine = get_recommendation_engine()
    similar_items = engine.recommend(
        category=item['category'],
        taste=item['taste'],
        vegetarian=item['vegetarian'],
        previous_food=item['name'],
        top_n=3
    )
    return render_template('food_details.html', item=item, similar_items=similar_items)

# -------------------------------------------------------------
# AIML MODULE 1: FOOD RECOMMENDATION (KNN)
# -------------------------------------------------------------
@app.route('/recommend', methods=['GET', 'POST'])
def recommendation():
    engine = get_recommendation_engine()
    categories = ['South Indian', 'North Indian', 'Chinese', 'Fast Food', 'Desserts']
    tastes = ['Mild', 'Medium', 'Spicy']
    
    recommended_items = None
    selected_category = 'North Indian'
    selected_taste = 'Medium'
    selected_veg = 1
    previous_food = ''

    if request.method == 'POST':
        selected_category = request.form.get('category', 'North Indian')
        selected_taste = request.form.get('taste', 'Medium')
        selected_veg = int(request.form.get('vegetarian', 1))
        previous_food = request.form.get('previous_food', '').strip()
        min_rating = float(request.form.get('min_rating', 0.0))

        recommended_items = engine.recommend(
            category=selected_category,
            taste=selected_taste,
            vegetarian=selected_veg,
            min_rating=min_rating,
            previous_food=previous_food,
            top_n=4
        )

    return render_template(
        'recommendation.html',
        categories=categories,
        tastes=tastes,
        recommended_items=recommended_items,
        selected_category=selected_category,
        selected_taste=selected_taste,
        selected_veg=selected_veg,
        previous_food=previous_food
    )

@app.route('/api/recommend', methods=['POST'])
def api_recommend():
    data = request.get_json() or {}
    engine = get_recommendation_engine()
    results = engine.recommend(
        category=data.get('category'),
        taste=data.get('taste', 'Medium'),
        vegetarian=int(data.get('vegetarian', 1)),
        min_rating=float(data.get('min_rating', 0.0)),
        previous_food=data.get('previous_food'),
        top_n=int(data.get('top_n', 4))
    )
    return jsonify({'success': True, 'recommendations': results})

# -------------------------------------------------------------
# AIML MODULE 2: FOOD DEMAND PREDICTION (LINEAR REGRESSION)
# -------------------------------------------------------------
@app.route('/predict-demand', methods=['GET', 'POST'])
def demand_prediction():
    engine = get_demand_engine()
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    categories = ['South Indian', 'North Indian', 'Chinese', 'Fast Food', 'Desserts']

    prediction_result = None
    selected_day = 'Friday'
    selected_category = 'North Indian'
    prev_orders = 85
    prev_demand = 90

    if request.method == 'POST':
        selected_day = request.form.get('day', 'Friday')
        selected_category = request.form.get('food_category', 'North Indian')
        try:
            prev_orders = float(request.form.get('previous_orders', 80))
            prev_demand = float(request.form.get('previous_demand', 85))
        except ValueError:
            prev_orders, prev_demand = 80, 85

        prediction_result = engine.predict(
            day=selected_day,
            food_category=selected_category,
            previous_orders=prev_orders,
            previous_demand=prev_demand
        )

        # Log into demand history
        try:
            db = get_db()
            db.execute(
                "INSERT INTO demand_history (food_category, day_of_week, orders_count, predicted_demand) VALUES (?, ?, ?, ?)",
                (selected_category, selected_day, int(prev_orders), prediction_result['predicted_demand'])
            )
        except Exception as e:
            print(f"[WARN] Could not record demand history: {e}")

    return render_template(
        'demand_prediction.html',
        days=days,
        categories=categories,
        prediction=prediction_result,
        selected_day=selected_day,
        selected_category=selected_category,
        prev_orders=int(prev_orders),
        prev_demand=int(prev_demand)
    )

@app.route('/api/predict-demand', methods=['POST'])
def api_predict_demand():
    data = request.get_json() or {}
    engine = get_demand_engine()
    res = engine.predict(
        day=data.get('day', 'Friday'),
        food_category=data.get('food_category', 'North Indian'),
        previous_orders=float(data.get('previous_orders', 80)),
        previous_demand=float(data.get('previous_demand', 85))
    )
    return jsonify({'success': True, 'result': res})

# -------------------------------------------------------------
# AIML MODULE 3: FOOD WASTE PREDICTION (DECISION TREE)
# -------------------------------------------------------------
@app.route('/predict-waste', methods=['GET', 'POST'])
def waste_prediction():
    engine = get_waste_engine()
    prediction_result = None

    qty_prepared = 150
    expected_orders = 90
    current_stock = 45
    expiry_hours = 6
    previous_wastage = 20

    if request.method == 'POST':
        try:
            qty_prepared = float(request.form.get('quantity_prepared', 100))
            expected_orders = float(request.form.get('expected_orders', 90))
            current_stock = float(request.form.get('current_stock', 15))
            expiry_hours = float(request.form.get('expiry_hours', 18))
            previous_wastage = float(request.form.get('previous_wastage', 5))
        except ValueError:
            pass

        prediction_result = engine.predict(
            quantity_prepared=qty_prepared,
            expected_orders=expected_orders,
            current_stock=current_stock,
            expiry_hours=expiry_hours,
            previous_wastage=previous_wastage
        )

        # Log into waste history
        try:
            db = get_db()
            food_item_id = int(request.form.get('food_id', 1))
            db.execute(
                "INSERT INTO waste_history (food_id, quantity_prepared, quantity_wasted, waste_risk, mitigation_action) VALUES (?, ?, ?, ?, ?)",
                (food_item_id, int(qty_prepared), int(previous_wastage), prediction_result['risk_level'].replace(' Waste Risk', ''), prediction_result['action'])
            )
        except Exception as e:
            print(f"[WARN] Could not record waste history: {e}")

    food_items = get_all_food()
    return render_template(
        'waste_prediction.html',
        prediction=prediction_result,
        food_items=food_items,
        qty_prepared=int(qty_prepared),
        expected_orders=int(expected_orders),
        current_stock=int(current_stock),
        expiry_hours=int(expiry_hours),
        previous_wastage=int(previous_wastage)
    )

@app.route('/api/predict-waste', methods=['POST'])
def api_predict_waste():
    data = request.get_json() or {}
    engine = get_waste_engine()
    res = engine.predict(
        quantity_prepared=float(data.get('quantity_prepared', 100)),
        expected_orders=float(data.get('expected_orders', 90)),
        current_stock=float(data.get('current_stock', 15)),
        expiry_hours=float(data.get('expiry_hours', 18)),
        previous_wastage=float(data.get('previous_wastage', 5))
    )
    return jsonify({'success': True, 'result': res})

# -------------------------------------------------------------
# CART & CHECKOUT MANAGEMENT
# -------------------------------------------------------------
@app.route('/cart')
def view_cart():
    cart = session.get('cart', {})
    cart_items = list(cart.values())
    total_amount = sum(float(i['price']) * int(i['quantity']) for i in cart_items)
    return render_template('cart.html', cart_items=cart_items, total_amount=total_amount)

@app.route('/cart/add/<int:food_id>', methods=['POST'])
def add_to_cart(food_id):
    item = get_food_by_id(food_id)
    if not item:
        return jsonify({'success': False, 'message': 'Item not found'}), 404

    cart = session.get('cart', {})
    str_id = str(food_id)
    if str_id in cart:
        cart[str_id]['quantity'] += 1
    else:
        cart[str_id] = {
            'id': item['id'],
            'name': item['name'],
            'price': float(item['price']),
            'image_url': item['image_url'],
            'category': item['category'],
            'quantity': 1
        }
    session['cart'] = cart
    session.modified = True

    cart_count = sum(i['quantity'] for i in cart.values())
    
    if request.is_json:
        return jsonify({'success': True, 'message': f"Added '{item['name']}' to cart!", 'cart_count': cart_count})
    
    flash(f"Added '{item['name']}' to your tray!", 'success')
    return redirect(request.referrer or url_for('menu'))

@app.route('/cart/update/<int:food_id>', methods=['POST'])
def update_cart(food_id):
    cart = session.get('cart', {})
    str_id = str(food_id)
    action = request.form.get('action', 'increase')

    if str_id in cart:
        if action == 'increase':
            cart[str_id]['quantity'] += 1
        elif action == 'decrease':
            cart[str_id]['quantity'] -= 1
            if cart[str_id]['quantity'] <= 0:
                del cart[str_id]
        elif action == 'remove':
            del cart[str_id]

    session['cart'] = cart
    session.modified = True
    return redirect(url_for('view_cart'))

@app.route('/checkout', methods=['POST'])
def checkout():
    user_id = session.get('user_id')
    if not user_id:
        flash('Please login to finalize your meal order.', 'warning')
        return redirect(url_for('login'))

    cart = session.get('cart', {})
    if not cart:
        flash('Your tray is empty.', 'warning')
        return redirect(url_for('menu'))

    payment_method = request.form.get('payment_method', 'Online UPI / Card')
    order_id = place_order(user_id, list(cart.values()), payment_method=payment_method)
    
    # Clear cart after ordering
    session['cart'] = {}
    session.modified = True

    flash(f'Order #{order_id} placed successfully! The smart kitchen has begun preparation.', 'success')
    return redirect(url_for('user_dashboard'))

# -------------------------------------------------------------
# USER & ADMIN DASHBOARDS
# -------------------------------------------------------------
@app.route('/user-dashboard')
def user_dashboard():
    user_id = session.get('user_id')
    if not user_id:
        flash('Please login to access your personal dashboard.', 'warning')
        return redirect(url_for('login'))

    orders = get_orders_by_user(user_id)
    user_name = session.get('user_name', 'Student User')

    # Get tailored recommendations for user
    engine = get_recommendation_engine()
    ai_recs = engine.recommend(category='North Indian', taste='Medium', vegetarian=1, top_n=3)

    return render_template('user_dashboard.html', user_name=user_name, orders=orders, ai_recs=ai_recs)

@app.route('/admin-dashboard')
def admin_dashboard():
    user_role = session.get('user_role')
    # Allow viewing or prompt to login as admin
    if user_role != 'admin':
        flash('Viewing Admin Dashboard in preview mode. For full write privileges, log in as Admin.', 'info')

    stats = get_admin_dashboard_data()
    
    # Run dynamic models for top predictions summary
    demand_engine = get_demand_engine()
    sample_demand = demand_engine.predict(day='Saturday', food_category='Fast Food', previous_orders=110, previous_demand=115)

    waste_engine = get_waste_engine()
    sample_waste = waste_engine.predict(quantity_prepared=150, expected_orders=95, current_stock=35, expiry_hours=6, previous_wastage=15)

    return render_template(
        'admin_dashboard.html',
        stats=stats,
        sample_demand=sample_demand,
        sample_waste=sample_waste
    )

if __name__ == '__main__':
    print("=" * 65)
    print("  SMART FOOD MANAGEMENT SYSTEM USING AIML")
    print("  Server running on http://127.0.0.1:5000")
    print("=" * 65)
    app.run(host='127.0.0.1', port=5000, debug=True)
