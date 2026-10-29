-- ============================================================================
-- E-Commerce Website Project Database Schema (PostgreSQL / MySQL Compatible)
-- Tables: users, categories, products, carts, orders, order_items
-- ============================================================================

-- 1. User Table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'customer', -- 'customer' or 'admin'
    is_blocked BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Category Table
CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT
);

-- 3. Product Table
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    price DECIMAL(10, 2) NOT NULL CHECK (price >= 0),
    description TEXT NOT NULL,
    category_id INTEGER NOT NULL REFERENCES categories(id) ON DELETE RESTRICT,
    image_url TEXT,
    rating DECIMAL(3, 2) DEFAULT 4.50,
    reviews_count INTEGER DEFAULT 0,
    stock INTEGER NOT NULL DEFAULT 25 CHECK (stock >= 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Cart Table
CREATE TABLE IF NOT EXISTS carts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    quantity INTEGER NOT NULL DEFAULT 1 CHECK (quantity > 0),
    UNIQUE (user_id, product_id)
);

-- 5. Order Table
CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    total_amount DECIMAL(10, 2) NOT NULL CHECK (total_amount >= 0),
    status VARCHAR(30) NOT NULL DEFAULT 'Pending', -- 'Pending', 'Shipped', 'Delivered'
    payment_method VARCHAR(50) NOT NULL DEFAULT 'Stripe', -- 'Stripe', 'Razorpay', 'COD'
    payment_status VARCHAR(30) NOT NULL DEFAULT 'Paid',
    shipping_address TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. Order Items Table
CREATE TABLE IF NOT EXISTS order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE RESTRICT,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price DECIMAL(10, 2) NOT NULL CHECK (unit_price >= 0)
);

-- Indexes for performance
CREATE INDEX idx_products_category ON products(category_id);
CREATE INDEX idx_carts_user ON carts(user_id);
CREATE INDEX idx_orders_user ON orders(user_id);
CREATE INDEX idx_order_items_order ON order_items(order_id);

-- Seed Initial Categories
INSERT INTO categories (name, description) VALUES
('Audio & Headphones', 'Studio-grade headphones, earbuds, and spatial audio gear'),
('Wearables & Smartwatches', 'Smartwatches, fitness trackers, and health monitors'),
('Peripherals & Workspaces', 'Mechanical keyboards, mice, and desk accessories'),
('Bags & Everyday Carry', 'Minimalist leather backpacks, laptop sleeves, and travel gear')
ON CONFLICT (name) DO NOTHING;
