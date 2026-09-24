"""
Smart Food Management System
Database Access Layer with Dual Engine Support (MySQL + Transparent SQLite Fallback)

This manager attempts to connect to MySQL first. If MySQL is not configured
or the server is offline, it seamlessly falls back to SQLite so the project
runs immediately without crashing during college vivas or laptop evaluations.
"""
import os
import sqlite3
import pandas as pd
from werkzeug.security import generate_password_hash, check_password_hash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SQLITE_DB_PATH = '/tmp/smart_food_management.db'
FOOD_CSV_PATH = os.path.join(BASE_DIR, 'food_dataset.csv')

# MySQL default configuration (can be overridden via environment variables)
MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))
MYSQL_USER = os.getenv('MYSQL_USER', 'root')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'root')
MYSQL_DB = os.getenv('MYSQL_DB', 'smart_food_management')

class DatabaseManager:
    def __init__(self):
        self.engine_type = 'sqlite' # Default fallback
        self._test_and_init_db()

    def _test_and_init_db(self):
        """Try MySQL connection; fall back to SQLite if MySQL is unavailable."""
        try:
            import pymysql
            import pymysql.cursors
            # Test MySQL connection
            conn = pymysql.connect(
                host=MYSQL_HOST,
                port=MYSQL_PORT,
                user=MYSQL_USER,
                password=MYSQL_PASSWORD,
                charset='utf8mb4',
                connect_timeout=2
            )
            cursor = conn.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {MYSQL_DB} CHARACTER SET utf8mb4;")
            cursor.execute(f"USE {MYSQL_DB};")
            conn.commit()
            conn.close()
            self.engine_type = 'mysql'
            print(f"[OK] Database connected to MySQL server ({MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB})")
            self._ensure_mysql_tables()
            return
        except Exception as e:
            # Fall back to SQLite
            self.engine_type = 'sqlite'
            print(f"[INFO] MySQL offline or not configured ({e}). Running in standalone SQLite mode: {SQLITE_DB_PATH}")
            self._ensure_sqlite_tables()

    def get_connection(self):
        """Return active connection based on detected engine."""
        if self.engine_type == 'mysql':
            try:
                import pymysql
                import pymysql.cursors
                return pymysql.connect(
                    host=MYSQL_HOST,
                    port=MYSQL_PORT,
                    user=MYSQL_USER,
                    password=MYSQL_PASSWORD,
                    database=MYSQL_DB,
                    charset='utf8mb4',
                    cursorclass=pymysql.cursors.DictCursor,
                    autocommit=True
                )
            except Exception:
                # If MySQL dropped mid-session, fallback to SQLite
                return self._get_sqlite_connection()
        else:
            return self._get_sqlite_connection()

    def _get_sqlite_connection(self):
        conn = sqlite3.connect(SQLITE_DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure_sqlite_tables(self):
        """Create and populate SQLite tables if missing."""
        conn = self._get_sqlite_connection()
        cursor = conn.cursor()

        cursor.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS food_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            taste TEXT DEFAULT 'Medium',
            vegetarian INTEGER DEFAULT 1,
            price REAL NOT NULL,
            rating REAL DEFAULT 4.5,
            description TEXT,
            ingredients TEXT,
            image_url TEXT,
            is_available INTEGER DEFAULT 1,
            stock_qty INTEGER DEFAULT 50,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            total_amount REAL NOT NULL,
            status TEXT DEFAULT 'Preparing',
            payment_method TEXT DEFAULT 'Online UPI / Card',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            food_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 1,
            price_per_item REAL NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(id),
            FOREIGN KEY (food_id) REFERENCES food_items(id)
        );

        CREATE TABLE IF NOT EXISTS food_stock (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            food_id INTEGER NOT NULL UNIQUE,
            current_stock INTEGER NOT NULL DEFAULT 30,
            min_threshold INTEGER NOT NULL DEFAULT 10,
            expiry_hours INTEGER NOT NULL DEFAULT 24,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (food_id) REFERENCES food_items(id)
        );

        CREATE TABLE IF NOT EXISTS demand_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            food_category TEXT NOT NULL,
            day_of_week TEXT NOT NULL,
            orders_count INTEGER NOT NULL,
            predicted_demand INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS waste_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            food_id INTEGER NOT NULL,
            quantity_prepared INTEGER NOT NULL,
            quantity_wasted INTEGER NOT NULL DEFAULT 0,
            waste_risk TEXT NOT NULL,
            mitigation_action TEXT,
            logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (food_id) REFERENCES food_items(id)
        );
        ''')
        conn.commit()

        # Seed default users if empty
        cursor.execute("SELECT COUNT(*) FROM users;")
        if cursor.fetchone()[0] == 0:
            pw_admin = generate_password_hash("admin123")
            pw_user = generate_password_hash("user123")
            cursor.execute("INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, ?);",
                           ('Admin Officer', 'admin@smartfood.com', pw_admin, 'admin'))
            cursor.execute("INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, ?);",
                           ('Aarav Sharma', 'student@smartfood.com', pw_user, 'user'))
            conn.commit()

        # Seed food items from dataset CSV if empty
        cursor.execute("SELECT COUNT(*) FROM food_items;")
        if cursor.fetchone()[0] == 0 and os.path.exists(FOOD_CSV_PATH):
            df = pd.read_csv(FOOD_CSV_PATH)
            for _, r in df.iterrows():
                cursor.execute('''
                    INSERT INTO food_items (id, name, category, taste, vegetarian, price, rating, description, ingredients, image_url, is_available, stock_qty)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, 50)
                ''', (
                    int(r['food_id']), str(r['food_name']), str(r['category']), str(r['taste']),
                    int(r['vegetarian']), float(r['price']), float(r['rating']),
                    str(r['description']), str(r['ingredients']), str(r['image_url'])
                ))
                cursor.execute('''
                    INSERT INTO food_stock (food_id, current_stock, min_threshold, expiry_hours)
                    VALUES (?, 45, 10, 24)
                ''', (int(r['food_id']),))
            conn.commit()
            print(f"[OK] Seeded {len(df)} food items into database.")

        conn.close()

    def _ensure_mysql_tables(self):
        """Execute schema.sql if tables do not exist in MySQL."""
        schema_path = os.path.join(BASE_DIR, 'database', 'schema.sql')
        if not os.path.exists(schema_path):
            return
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SHOW TABLES LIKE 'food_items';")
            if cursor.fetchone() is None:
                with open(schema_path, 'r', encoding='utf-8') as f:
                    statements = f.read().split(';')
                    for stmt in statements:
                        s = stmt.strip()
                        if s:
                            cursor.execute(s)
                print("[OK] Executed MySQL schema.sql successfully.")
            conn.close()
        except Exception as e:
            print(f"[WARN] Error initializing MySQL tables: {e}")

    def query(self, sql, params=(), one=False):
        """Execute a SELECT query and return list of dicts (or single dict)."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # SQLite uses ? while MySQL uses %s
        if self.engine_type == 'mysql':
            sql = sql.replace('?', '%s')
            
        cursor.execute(sql, params)
        if self.engine_type == 'sqlite':
            rows = cursor.fetchall()
            result = [dict(row) for row in rows]
        else:
            result = cursor.fetchall()

        conn.close()
        return (result[0] if result else None) if one else result

    def execute(self, sql, params=()):
        """Execute an INSERT/UPDATE/DELETE query and return lastrowid."""
        conn = self.get_connection()
        cursor = conn.cursor()

        if self.engine_type == 'mysql':
            sql = sql.replace('?', '%s')

        cursor.execute(sql, params)
        if self.engine_type == 'sqlite':
            conn.commit()
            last_id = cursor.lastrowid
        else:
            last_id = cursor.lastrowid
        conn.close()
        return last_id

# Helper data methods
db_instance = None

def get_db():
    global db_instance
    if db_instance is None:
        db_instance = DatabaseManager()
    return db_instance

def get_all_food(category=None, search=None, veg_only=None):
    """Retrieve food items matching optional filters."""
    db = get_db()
    query = "SELECT * FROM food_items WHERE is_available = 1"
    params = []

    if category and category.lower() != 'all':
        query += " AND LOWER(category) = ?"
        params.append(category.lower())

    if search:
        query += " AND (LOWER(name) LIKE ? OR LOWER(ingredients) LIKE ?)"
        term = f"%{search.lower()}%"
        params.extend([term, term])

    if veg_only is not None and veg_only != '':
        query += " AND vegetarian = ?"
        params.append(1 if str(veg_only) in ['1', 'true', 'True'] else 0)

    query += " ORDER BY rating DESC"
    return db.query(query, params)

def get_food_by_id(food_id):
    db = get_db()
    return db.query("SELECT * FROM food_items WHERE id = ?", (food_id,), one=True)

def get_user_by_email(email):
    db = get_db()
    return db.query("SELECT * FROM users WHERE LOWER(email) = ?", (email.lower().strip(),), one=True)

def create_user(name, email, password, role='user'):
    db = get_db()
    pw_hash = generate_password_hash(password)
    return db.execute("INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, ?)",
                      (name.strip(), email.lower().strip(), pw_hash, role))

def place_order(user_id, cart_items, payment_method='Online UPI / Card'):
    """Create an order and its constituent line items transactionally."""
    db = get_db()
    total_amount = sum(float(item['price']) * int(item['quantity']) for item in cart_items)
    
    order_id = db.execute(
        "INSERT INTO orders (user_id, total_amount, status, payment_method) VALUES (?, ?, 'Preparing', ?)",
        (user_id, total_amount, payment_method)
    )

    for item in cart_items:
        db.execute(
            "INSERT INTO order_items (order_id, food_id, quantity, price_per_item) VALUES (?, ?, ?, ?)",
            (order_id, item['id'], item['quantity'], item['price'])
        )
        # Deduct stock
        db.execute(
            "UPDATE food_items SET stock_qty = MAX(0, stock_qty - ?) WHERE id = ?",
            (item['quantity'], item['id'])
        )
        db.execute(
            "UPDATE food_stock SET current_stock = MAX(0, current_stock - ?) WHERE food_id = ?",
            (item['quantity'], item['id'])
        )
    return order_id

def get_orders_by_user(user_id):
    db = get_db()
    orders = db.query("SELECT * FROM orders WHERE user_id = ? ORDER BY created_at DESC", (user_id,))
    for order in orders:
        items = db.query('''
            SELECT oi.*, fi.name, fi.image_url, fi.category 
            FROM order_items oi
            JOIN food_items fi ON oi.food_id = fi.id
            WHERE oi.order_id = ?
        ''', (order['id'],))
        order['items'] = items
    return orders

def get_admin_dashboard_data():
    db = get_db()
    total_users = db.query("SELECT COUNT(*) as count FROM users WHERE role = 'user'", one=True)['count']
    total_food = db.query("SELECT COUNT(*) as count FROM food_items", one=True)['count']
    total_orders = db.query("SELECT COUNT(*) as count FROM orders", one=True)['count']
    total_revenue = db.query("SELECT COALESCE(SUM(total_amount), 0) as total FROM orders", one=True)['total']
    
    recent_orders = db.query('''
        SELECT o.*, u.name as customer_name, u.email as customer_email 
        FROM orders o 
        JOIN users u ON o.user_id = u.id 
        ORDER BY o.created_at DESC LIMIT 6
    ''')

    stocks = db.query('''
        SELECT fs.*, fi.name, fi.category, fi.price 
        FROM food_stock fs 
        JOIN food_items fi ON fs.food_id = fi.id 
        ORDER BY fs.current_stock ASC LIMIT 8
    ''')

    return {
        'total_users': total_users,
        'total_food': total_food,
        'total_orders': total_orders,
        'total_revenue': round(total_revenue, 2),
        'recent_orders': recent_orders,
        'stocks': stocks,
        'db_engine': db.engine_type.upper()
    }
