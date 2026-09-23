-- ================================================================
-- Smart Food Management System Using Artificial Intelligence and Machine Learning
-- Database: smart_food_management
-- MySQL Schema & Seed Data
-- ================================================================

CREATE DATABASE IF NOT EXISTS smart_food_management CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE smart_food_management;

-- 1. USERS TABLE
DROP TABLE IF EXISTS waste_history;
DROP TABLE IF EXISTS demand_history;
DROP TABLE IF EXISTS food_stock;
DROP TABLE IF EXISTS ratings;
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS food_items;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('user', 'admin') DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 2. FOOD ITEMS TABLE
CREATE TABLE food_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    category VARCHAR(50) NOT NULL,
    taste ENUM('Mild', 'Medium', 'Spicy') DEFAULT 'Medium',
    vegetarian TINYINT(1) DEFAULT 1,
    price DECIMAL(8, 2) NOT NULL,
    rating DECIMAL(3, 2) DEFAULT 4.5,
    description TEXT,
    ingredients TEXT,
    image_url VARCHAR(500),
    is_available TINYINT(1) DEFAULT 1,
    stock_qty INT DEFAULT 50,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 3. ORDERS TABLE
CREATE TABLE orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    status ENUM('Pending', 'Preparing', 'Ready', 'Delivered', 'Cancelled') DEFAULT 'Preparing',
    payment_method VARCHAR(50) DEFAULT 'Online UPI / Card',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 4. ORDER ITEMS TABLE
CREATE TABLE order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    food_id INT NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    price_per_item DECIMAL(8, 2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (food_id) REFERENCES food_items(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 5. RATINGS & REVIEWS TABLE
CREATE TABLE ratings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    food_id INT NOT NULL,
    rating DECIMAL(2, 1) NOT NULL,
    review TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (food_id) REFERENCES food_items(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 6. FOOD STOCK TABLE
CREATE TABLE food_stock (
    id INT AUTO_INCREMENT PRIMARY KEY,
    food_id INT NOT NULL UNIQUE,
    current_stock INT NOT NULL DEFAULT 30,
    min_threshold INT NOT NULL DEFAULT 10,
    expiry_hours INT NOT NULL DEFAULT 24,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (food_id) REFERENCES food_items(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 7. DEMAND HISTORY TABLE (For ML training & analytics tracking)
CREATE TABLE demand_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    food_category VARCHAR(50) NOT NULL,
    day_of_week VARCHAR(20) NOT NULL,
    orders_count INT NOT NULL,
    predicted_demand INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 8. WASTE HISTORY TABLE (For Waste Prediction Tracking)
CREATE TABLE waste_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    food_id INT NOT NULL,
    quantity_prepared INT NOT NULL,
    quantity_wasted INT NOT NULL DEFAULT 0,
    waste_risk ENUM('Low', 'Medium', 'High') NOT NULL,
    mitigation_action VARCHAR(255),
    logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (food_id) REFERENCES food_items(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ================================================================
-- INITIAL SEED DATA
-- Default Passwords:
-- Admin: admin123 (sha256 hash or werkzeug hash)
-- User:  user123
-- ================================================================

INSERT INTO users (id, name, email, password_hash, role) VALUES
(1, 'Admin Officer', 'admin@smartfood.com', 'pbkdf2:sha256:600000$8c3d9a10$86b77dfd2b568770c0c279cbe878051772fe2ce837e2a9ce1e22be582f3ef808', 'admin'),
(2, 'Aarav Sharma', 'student@smartfood.com', 'pbkdf2:sha256:600000$8c3d9a10$86b77dfd2b568770c0c279cbe878051772fe2ce837e2a9ce1e22be582f3ef808', 'user');

INSERT INTO food_items (id, name, category, taste, vegetarian, price, rating, description, ingredients, image_url, is_available, stock_qty) VALUES
(1, 'Classic Masala Dosa', 'South Indian', 'Medium', 1, 120.00, 4.6, 'Crispy fermented crepe made from rice and lentils stuffed with spiced potato mash served with coconut chutney and sambar.', 'Rice batter, Potato, Mustard seeds, Curry leaves, Turmeric, Chutney', 'https://images.unsplash.com/photo-1589301760014-d929f3979dbc?w=500&auto=format&fit=crop&q=80', 1, 45),
(2, 'Steamed Idli Sambar Combo', 'South Indian', 'Mild', 1, 80.00, 4.5, 'Soft and fluffy steamed rice cakes served with aromatic vegetable sambar and fresh coconut chutney.', 'Rice, Urad dal, Sambar lentils, Drumsticks, Coconut, Curry leaves', 'https://images.unsplash.com/photo-1589301760014-d929f3979dbc?w=500&auto=format&fit=crop&q=80', 1, 60),
(3, 'Crispy Medu Vada', 'South Indian', 'Medium', 1, 90.00, 4.4, 'Golden fried lentil doughnuts with a crunchy exterior and fluffy interior paired with spicy tomato chutney.', 'Urad dal, Green chilies, Ginger, Black pepper, Curry leaves, Onion', 'https://images.unsplash.com/photo-1626777552726-4a6b54c97e46?w=500&auto=format&fit=crop&q=80', 1, 40),
(4, 'Hyderabadi Chicken Biryani', 'South Indian', 'Spicy', 0, 260.00, 4.8, 'Authentic dum-cooked fragrant basmati rice layered with tender spiced chicken pieces and aromatic saffron.', 'Basmati rice, Chicken, Biryani spices, Mint, Saffron, Fried onions, Yogurt', 'https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=500&auto=format&fit=crop&q=80', 1, 35),
(5, 'Paneer Butter Masala', 'North Indian', 'Mild', 1, 230.00, 4.7, 'Rich and creamy tomato gravy loaded with butter, soft cottage cheese cubes, and crushed kasuri methi.', 'Cottage cheese (Paneer), Tomato puree, Cashew paste, Fresh cream, Butter, Kasuri methi', 'https://images.unsplash.com/photo-1631452180519-c014fe946bc7?w=500&auto=format&fit=crop&q=80', 1, 50),
(6, 'Butter Chicken (Murgh Makhani)', 'North Indian', 'Medium', 0, 290.00, 4.9, 'Tender char-grilled tandoori chicken cooked in a velvety mild tomato-cashew satin gravy with cream.', 'Chicken, Yogurt, Tandoori masala, Tomatoes, Butter, Cream, Cardamom', 'https://images.unsplash.com/photo-1603894584373-5ac82b2ae398?w=500&auto=format&fit=crop&q=80', 1, 40),
(7, 'Slow-Cooked Dal Makhani', 'North Indian', 'Mild', 1, 190.00, 4.8, 'Overnight slow-cooked black lentils and kidney beans enriched with fresh cream and clarified butter.', 'Whole black urad, Kidney beans, Cream, Butter, Ginger-garlic, Kashmiri chili', 'https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=500&auto=format&fit=crop&q=80', 1, 55),
(8, 'Veg Hakka Noodles', 'Chinese', 'Mild', 1, 160.00, 4.3, 'Wok-tossed noodles with crunchy julienned cabbage, carrots, bell peppers, and scallions in light soy sauce.', 'Noodles, Cabbage, Carrot, Bell peppers, Soy sauce, White pepper, Scallions', 'https://images.unsplash.com/photo-1569718212165-3a8278d5f624?w=500&auto=format&fit=crop&q=80', 1, 45),
(9, 'Schezwan Chicken Fried Rice', 'Chinese', 'Spicy', 0, 220.00, 4.6, 'Fragrant long-grain rice stir-fried in a fiery house-made Schezwan sauce with shredded chicken and eggs.', 'Basmati rice, Chicken, Schezwan chili paste, Eggs, Garlic, Spring onion', 'https://images.unsplash.com/photo-1603133872878-684f208fb84b?w=500&auto=format&fit=crop&q=80', 1, 30),
(10, 'Deluxe Veggie Burger', 'Fast Food', 'Medium', 1, 130.00, 4.3, 'Crispy vegetable patty topped with melted cheddar slice, crunchy lettuce, sliced pickles, and spicy mayo.', 'Sesame bun, Herb potato-corn patty, Cheddar cheese, Lettuce, Pickles, Chipotle mayo', 'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=500&auto=format&fit=crop&q=80', 1, 50),
(11, 'Farmhouse Veggie Supreme Pizza', 'Fast Food', 'Medium', 1, 299.00, 4.6, 'Hand-stretched pizza topped with mozzarella, black olives, bell peppers, sweet corn, and button mushrooms.', 'Pizza dough, San Marzano sauce, Mozzarella, Olives, Bell peppers, Corn, Mushrooms', 'https://images.unsplash.com/photo-1513104890138-7c749659a591?w=500&auto=format&fit=crop&q=80', 1, 25),
(12, 'Hot Gulab Jamun with Rabri', 'Desserts', 'Mild', 1, 100.00, 4.9, 'Deep-fried condensed milk dumplings soaked in cardamom-infused rose sugar syrup, topped with rich rabri.', 'Khoa, Flour, Cardamom, Sugar syrup, Rose water, Saffron rabri, Pistachios', 'https://images.unsplash.com/photo-1589119908995-c6837fa14d48?w=500&auto=format&fit=crop&q=80', 1, 60),
(13, 'Royal Rasmalai', 'Desserts', 'Mild', 1, 120.00, 4.8, 'Soft flattened paneer discs poached in sweetened milk flavored with saffron and crushed green cardamom.', 'Chhena cottage cheese, Condensed milk, Saffron, Cardamom, Almond slivers', 'https://images.unsplash.com/photo-1589119908995-c6837fa14d48?w=500&auto=format&fit=crop&q=80', 1, 45);

INSERT INTO food_stock (food_id, current_stock, min_threshold, expiry_hours) VALUES
(1, 45, 15, 24),
(2, 60, 20, 18),
(3, 40, 10, 20),
(4, 35, 10, 12),
(5, 50, 15, 36),
(6, 40, 12, 24),
(7, 55, 15, 30),
(8, 45, 10, 24),
(9, 30, 10, 18),
(10, 50, 15, 48),
(11, 25, 8, 24),
(12, 60, 15, 72),
(13, 45, 10, 36);

-- Sample initial orders for demo history
INSERT INTO orders (id, user_id, total_amount, status, payment_method) VALUES
(101, 2, 490.00, 'Delivered', 'UPI Payment'),
(102, 2, 350.00, 'Preparing', 'Cash on Counter');

INSERT INTO order_items (order_id, food_id, quantity, price_per_item) VALUES
(101, 5, 1, 230.00),
(101, 4, 1, 260.00),
(102, 1, 2, 120.00),
(102, 12, 1, 100.00);

INSERT INTO demand_history (food_category, day_of_week, orders_count, predicted_demand) VALUES
('North Indian', 'Friday', 98, 95),
('South Indian', 'Friday', 75, 72),
('Fast Food', 'Saturday', 122, 120),
('Chinese', 'Sunday', 102, 105);

INSERT INTO waste_history (food_id, quantity_prepared, quantity_wasted, waste_risk, mitigation_action) VALUES
(4, 80, 5, 'Low', 'Sold out before dinner service close'),
(1, 100, 18, 'Medium', 'Offered 20% student discount after 9 PM');
