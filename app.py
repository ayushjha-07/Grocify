# -*- coding: utf-8 -*-
"""
Grocify - AI-Powered Grocery & Retail Management Platform
Core Flask backend application.
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from datetime import datetime, timedelta
import random
import json
import math

app = Flask(__name__)
app.secret_key = "grocify_retail_erp_secret_key"

# --- GLOBAL SYSTEM SETTINGS ---
settings = {
    "store_name": "Grocify",
    "tagline": "Smart Grocery & Retail Management Platform",
    "delivery_charge": 30,
    "free_delivery_threshold": 500,
    "default_credit_limit": 10000,
    "whatsapp_enabled": True
}

# --- IN-MEMORY DATABASE ---

# 1. User accounts database
users_db = [
    {"username": "owner", "password": "owner123", "role": "Owner", "name": "Grocify Team", "mobile": "9876501100"},
    {"username": "clerk", "password": "clerk123", "role": "Clerk", "name": "Ramji Prasad", "mobile": "9876501199"},
    {"username": "delivery", "password": "delivery123", "role": "Delivery Boy", "name": "Sanjay Kumar", "mobile": "9876502201"},
    {"username": "customer", "password": "customer123", "role": "Customer", "name": "Ramesh Kumar Mishra", "mobile": "9876501101"}
]

# 2. Product Catalog (60 items with cost_price and supplier)
products_db = [
    {"id": 1, "name": "Ashirvaad Shudh Chakki Atta (5kg)", "category": "Rice & Flour", "price": 260, "cost_price": 200, "stock": 35, "supplier": "ITC Ltd.", "image": "atta"},
    {"id": 2, "name": "India Gate Basmati Rice Rozana (5kg)", "category": "Rice & Flour", "price": 450, "cost_price": 350, "stock": 8, "supplier": "India Gate Ltd.", "image": "rice"},
    {"id": 3, "name": "Tata Salt Iodized (1kg)", "category": "Grocery & Staples", "price": 28, "cost_price": 20, "stock": 120, "supplier": "Tata Consumer Products", "image": "salt"},
    {"id": 4, "name": "Fortune Pure Mustard Oil (1L)", "category": "Oils & Spices", "price": 175, "cost_price": 135, "stock": 45, "supplier": "Adani Wilmar", "image": "mustard_oil"},
    {"id": 5, "name": "MDH Shahi Paneer Masala (100g)", "category": "Oils & Spices", "price": 95, "cost_price": 70, "stock": 50, "supplier": "MDH Spices", "image": "masala"},
    {"id": 6, "name": "Tata Sampann Toor Dal Premium (1kg)", "category": "Pulses & Grains", "price": 160, "cost_price": 120, "stock": 6, "supplier": "Tata Consumer Products", "image": "dal"},
    {"id": 7, "name": "Amul Pasteurised Butter (500g)", "category": "Dairy Products", "price": 275, "cost_price": 210, "stock": 18, "supplier": "GCMMF (Amul)", "image": "butter"},
    {"id": 8, "name": "Amul Taaza Milk Tetra (1L)", "category": "Dairy Products", "price": 68, "cost_price": 52, "stock": 40, "supplier": "GCMMF (Amul)", "image": "milk"},
    {"id": 9, "name": "Britannia Marie Gold Biscuits (250g)", "category": "Snacks & Biscuits", "price": 35, "cost_price": 25, "stock": 80, "supplier": "Britannia Industries", "image": "biscuits"},
    {"id": 10, "name": "Red Label Strong Tea (1kg)", "category": "Tea & Coffee", "price": 410, "cost_price": 315, "stock": 25, "supplier": "Hindustan Unilever", "image": "tea"},
    {"id": 11, "name": "Nescafe Classic Coffee Jar (100g)", "category": "Tea & Coffee", "price": 320, "cost_price": 240, "stock": 5, "supplier": "Nestle India", "image": "coffee"},
    {"id": 12, "name": "Dettol Liquid Handwash Original (200ml)", "category": "Personal Care", "price": 99, "cost_price": 75, "stock": 60, "supplier": "Reckitt Benckiser", "image": "handwash"},
    {"id": 13, "name": "Patanjali Dant Kanti Toothpaste (200g)", "category": "Personal Care", "price": 115, "cost_price": 85, "stock": 55, "supplier": "Patanjali Ayurved", "image": "toothpaste"},
    {"id": 14, "name": "Vim Liquid Dishwash (500ml)", "category": "Household Essentials", "price": 110, "cost_price": 80, "stock": 30, "supplier": "Hindustan Unilever", "image": "vim"},
    {"id": 15, "name": "Surf Excel Easy Wash (1kg)", "category": "Household Essentials", "price": 140, "cost_price": 105, "stock": 22, "supplier": "Hindustan Unilever", "image": "surf"},
    {"id": 16, "name": "Maggi 2-Minute Noodles (12-Pack)", "category": "Snacks & Biscuits", "price": 168, "cost_price": 130, "stock": 4, "supplier": "Nestle India", "image": "maggi"},
    {"id": 17, "name": "Tata Sampann Kabuli Chana (1kg)", "category": "Pulses & Grains", "price": 150, "cost_price": 115, "stock": 32, "supplier": "Tata Consumer Products", "image": "chana"},
    {"id": 18, "name": "Haldiram's Aloo Bhujia (350g)", "category": "Snacks & Biscuits", "price": 110, "cost_price": 85, "stock": 75, "supplier": "Haldiram's Foods", "image": "bhujia"},
    {"id": 19, "name": "Frooti Mango Drink (1.2L)", "category": "Beverages", "price": 70, "cost_price": 50, "stock": 45, "supplier": "Parle Agro", "image": "frooti"},
    {"id": 20, "name": "Thums Up Cold Drink (1.25L)", "category": "Beverages", "price": 75, "cost_price": 55, "stock": 40, "supplier": "Coca-Cola India", "image": "thumsup"},
    {"id": 21, "name": "Sunsilk Black Shine Shampoo (180ml)", "category": "Personal Care", "price": 120, "cost_price": 90, "stock": 35, "supplier": "Hindustan Unilever", "image": "shampoo"},
    {"id": 22, "name": "Lizol Disinfectant Floor Cleaner (500ml)", "category": "Household Essentials", "price": 105, "cost_price": 80, "stock": 28, "supplier": "Reckitt Benckiser", "image": "lizol"},
    {"id": 23, "name": "Amul Pure Cow Ghee (1L)", "category": "Dairy Products", "price": 650, "cost_price": 500, "stock": 15, "supplier": "GCMMF (Amul)", "image": "ghee"},
    {"id": 24, "name": "Tata Tea Gold Leaf Premium (1kg)", "category": "Tea & Coffee", "price": 460, "cost_price": 350, "stock": 20, "supplier": "Tata Consumer Products", "image": "tea"},
    {"id": 25, "name": "Tata Sampann Kabuli Chana Premium (1kg)", "category": "Pulses & Grains", "price": 150, "cost_price": 115, "stock": 32, "supplier": "Tata Consumer Products", "image": "dal"},
    {"id": 26, "name": "India Gate Basmati Rice Premium (5kg)", "category": "Rice & Flour", "price": 450, "cost_price": 350, "stock": 12, "supplier": "India Gate Ltd.", "image": "rice"},
    {"id": 27, "name": "Madhur Pure Sugar (1kg)", "category": "Grocery & Staples", "price": 50, "cost_price": 38, "stock": 150, "supplier": "Renuka Sugars", "image": "salt"},
    {"id": 28, "name": "Rajdhani Besan (1kg)", "category": "Rice & Flour", "price": 90, "cost_price": 68, "stock": 40, "supplier": "Rajdhani Group", "image": "atta"},
    {"id": 29, "name": "Catch Turmeric Powder Haldi (200g)", "category": "Oils & Spices", "price": 60, "cost_price": 45, "stock": 65, "supplier": "DS Group", "image": "masala"},
    {"id": 30, "name": "Tata Sampann Moong Dal Premium (1kg)", "category": "Pulses & Grains", "price": 175, "cost_price": 130, "stock": 25, "supplier": "Tata Consumer Products", "image": "dal"},
    {"id": 31, "name": "Fortune Soya Chunks (200g)", "category": "Pulses & Grains", "price": 45, "cost_price": 32, "stock": 50, "supplier": "Adani Wilmar", "image": "dal"},
    {"id": 32, "name": "Amul Cheese Slices (200g / 10 Slices)", "category": "Dairy Products", "price": 150, "cost_price": 115, "stock": 22, "supplier": "GCMMF (Amul)", "image": "butter"},
    {"id": 33, "name": "Fortune Soya Health Refined Oil (1L)", "category": "Oils & Spices", "price": 140, "cost_price": 105, "stock": 38, "supplier": "Adani Wilmar", "image": "mustard_oil"},
    {"id": 34, "name": "Britannia Good Day Cashew Cookies (200g)", "category": "Snacks & Biscuits", "price": 40, "cost_price": 28, "stock": 95, "supplier": "Britannia Industries", "image": "biscuits"},
    {"id": 35, "name": "Kurkure Masala Munch (90g)", "category": "Snacks & Biscuits", "price": 20, "cost_price": 14, "stock": 110, "supplier": "PepsiCo India", "image": "biscuits"},
    {"id": 36, "name": "Tata Tea Premium (1kg)", "category": "Tea & Coffee", "price": 380, "cost_price": 285, "stock": 30, "supplier": "Tata Consumer Products", "image": "tea"},
    {"id": 37, "name": "Maaza Mango Drink (1.2L)", "category": "Beverages", "price": 75, "cost_price": 52, "stock": 45, "supplier": "Coca-Cola India", "image": "frooti"},
    {"id": 38, "name": "Colgate Strong Teeth Toothpaste (200g)", "category": "Personal Care", "price": 95, "cost_price": 70, "stock": 65, "supplier": "Colgate-Palmolive", "image": "toothpaste"},
    {"id": 39, "name": "Lifebuoy Total Soap Bar (125g)", "category": "Personal Care", "price": 35, "cost_price": 24, "stock": 150, "supplier": "Hindustan Unilever", "image": "handwash"},
    {"id": 40, "name": "Comfort After Wash Fabric Conditioner (250ml)", "category": "Household Essentials", "price": 75, "cost_price": 55, "stock": 35, "supplier": "Hindustan Unilever", "image": "vim"},
    {"id": 41, "name": "Tata Sampann Unpolished Arhar Dal (1kg)", "category": "Pulses & Grains", "price": 180, "cost_price": 140, "stock": 30, "supplier": "Tata Consumer Products", "image": "dal"},
    {"id": 42, "name": "Fortune Premium Kachi Ghani Mustard Oil (1L)", "category": "Oils & Spices", "price": 185, "cost_price": 145, "stock": 25, "supplier": "Adani Wilmar", "image": "mustard_oil"},
    {"id": 43, "name": "Aashirvaad Select Premium Sharbati Atta (5kg)", "category": "Rice & Flour", "price": 290, "cost_price": 220, "stock": 20, "supplier": "ITC Ltd.", "image": "atta"},
    {"id": 44, "name": "Kohinoor Super Silver Basmati Rice (5kg)", "category": "Rice & Flour", "price": 600, "cost_price": 460, "stock": 15, "supplier": "Kohinoor Foods", "image": "rice"},
    {"id": 45, "name": "Amul Gold Milk Tetra Pack (1L)", "category": "Dairy Products", "price": 74, "cost_price": 58, "stock": 35, "supplier": "GCMMF (Amul)", "image": "milk"},
    {"id": 46, "name": "Nestle Everyday Dairy Whitener (1kg)", "category": "Dairy Products", "price": 420, "cost_price": 320, "stock": 12, "supplier": "Nestle India", "image": "milk"},
    {"id": 47, "name": "Society Tea Premium Dust (1kg)", "category": "Tea & Coffee", "price": 430, "cost_price": 330, "stock": 18, "supplier": "Society Tea", "image": "tea"},
    {"id": 48, "name": "Brooke Bond Taj Mahal Tea (1kg)", "category": "Tea & Coffee", "price": 650, "cost_price": 500, "stock": 10, "supplier": "Hindustan Unilever", "image": "tea"},
    {"id": 49, "name": "Tata Salt Lite Low Sodium (1kg)", "category": "Grocery & Staples", "price": 40, "cost_price": 30, "stock": 80, "supplier": "Tata Consumer Products", "image": "salt"},
    {"id": 50, "name": "Dabur Honey Pure Gold (500g)", "category": "Grocery & Staples", "price": 220, "cost_price": 165, "stock": 22, "supplier": "Dabur India", "image": "ghee"},
    {"id": 51, "name": "MDH Deggi Mirch Powder (100g)", "category": "Oils & Spices", "price": 85, "cost_price": 65, "stock": 45, "supplier": "MDH Spices", "image": "masala"},
    {"id": 52, "name": "Everest Garam Masala Premium (100g)", "category": "Oils & Spices", "price": 90, "cost_price": 70, "stock": 50, "supplier": "Everest Spices", "image": "masala"},
    {"id": 53, "name": "MTR Rava Idli Mix (500g)", "category": "Snacks & Biscuits", "price": 120, "cost_price": 90, "stock": 30, "supplier": "MTR Foods", "image": "biscuits"},
    {"id": 54, "name": "Parle-G Gold Biscuits (1kg Pack)", "category": "Snacks & Biscuits", "price": 80, "cost_price": 60, "stock": 100, "supplier": "Parle Products", "image": "biscuits"},
    {"id": 55, "name": "Minute Maid Mixed Fruit Juice (1L)", "category": "Beverages", "price": 99, "cost_price": 75, "stock": 40, "supplier": "Coca-Cola India", "image": "frooti"},
    {"id": 56, "name": "Pepsi Bottle Cold Drink (1.25L)", "category": "Beverages", "price": 75, "cost_price": 55, "stock": 35, "supplier": "PepsiCo India", "image": "thumsup"},
    {"id": 57, "name": "Himalaya Purifying Neem Face Wash (200ml)", "category": "Personal Care", "price": 199, "cost_price": 150, "stock": 25, "supplier": "Himalaya Wellness", "image": "handwash"},
    {"id": 58, "name": "Colgate MaxFresh Gel Toothpaste (150g)", "category": "Personal Care", "price": 110, "cost_price": 80, "stock": 40, "supplier": "Colgate-Palmolive", "image": "toothpaste"},
    {"id": 59, "name": "Surf Excel Matic Front Load Liquid (1L)", "category": "Household Essentials", "price": 220, "cost_price": 170, "stock": 15, "supplier": "Hindustan Unilever", "image": "surf"},
    {"id": 60, "name": "Vim Dishwash Bar Multipack (3x200g)", "category": "Household Essentials", "price": 60, "cost_price": 45, "stock": 50, "supplier": "Hindustan Unilever", "image": "vim"}
]

# 3. Traditional Khata Ledger Account Database
khata_db = [
    {
        "customer_name": "Ramesh Kumar Mishra",
        "mobile": "9876501101",
        "outstanding_amount": 1450,
        "credit_limit": 10000,
        "payment_history": [
            {"date": "2026-05-10", "type": "Purchase", "description": "Atta, Dal & Spices", "amount": 1250},
            {"date": "2026-05-15", "type": "Payment", "description": "Cash Settle Part", "amount": 800},
            {"date": "2026-06-01", "type": "Purchase", "description": "Biscuits & Tea Box", "amount": 1000}
        ]
    },
    {
        "customer_name": "Mahendra Singh (Pradhan Ji)",
        "mobile": "9876501102",
        "outstanding_amount": 3200,
        "credit_limit": 20000,
        "payment_history": [
            {"date": "2026-05-20", "type": "Purchase", "description": "Monthly Staples Basket", "amount": 3200}
        ]
    },
    {
        "customer_name": "Suresh Chandra Prasad",
        "mobile": "9876501103",
        "outstanding_amount": 0,
        "credit_limit": 10000,
        "payment_history": [
            {"date": "2026-04-12", "type": "Purchase", "description": "Dairy & Mustard Oils", "amount": 1500},
            {"date": "2026-04-20", "type": "Payment", "description": "Full Account Settle", "amount": 1500}
        ]
    },
    {
        "customer_name": "Gita Devi",
        "mobile": "9876501104",
        "outstanding_amount": 420,
        "credit_limit": 8000,
        "payment_history": [
            {"date": "2026-06-05", "type": "Purchase", "description": "Personal Care & Vim Bar", "amount": 420}
        ]
    },
    {
        "customer_name": "Rajeshwar Paswan",
        "mobile": "9876501105",
        "outstanding_amount": 1200,
        "credit_limit": 12000,
        "payment_history": [
            {"date": "2026-05-28", "type": "Purchase", "description": "Staples & Grains", "amount": 2200},
            {"date": "2026-06-02", "type": "Payment", "description": "UPI Pay", "amount": 1000}
        ]
    }
]

# 4. Delivery Staff Database
delivery_boys_db = [
    {"id": 1, "name": "Sanjay Kumar", "mobile": "9876502201", "status": "Active"},
    {"id": 2, "name": "Ram Avtar", "mobile": "9876502202", "status": "Active"},
    {"id": 3, "name": "Vijay Yadav", "mobile": "9876502203", "status": "Active"}
]

# 5. Orders Database (linked with delivery boy)
orders_db = [
    {
        "order_id": 1001,
        "customer_name": "Ramesh Kumar Mishra",
        "mobile": "9876501101",
        "address": "Mishra Tola, Near Shiv Temple",
        "village": "Rampur",
        "pincode": "843101",
        "items": "Ashirvaad Atta x1, Fortune Oil x2",
        "total_amount": 610,
        "payment_method": "Khata Credit",
        "status": "Delivered",
        "delivery_boy_id": 1,
        "date": "2026-06-12 11:30"
    },
    {
        "order_id": 1002,
        "customer_name": "Vikram Singh",
        "mobile": "9876501110",
        "address": "House 45, Main Market Road",
        "village": "Laxmipur",
        "pincode": "843102",
        "items": "Red Label Tea x1, Marie Biscuits x4",
        "total_amount": 550,
        "payment_method": "UPI",
        "status": "Out for Delivery",
        "delivery_boy_id": 1,
        "date": "2026-06-13 16:45"
    },
    {
        "order_id": 1003,
        "customer_name": "Gita Devi",
        "mobile": "9876501104",
        "address": "Devi Sthan, Ward 4",
        "village": "Rampur",
        "pincode": "843101",
        "items": "Patanjali Toothpaste x2, Vim Liquid x1",
        "total_amount": 340,
        "payment_method": "Cash on Delivery",
        "status": "Pending",
        "delivery_boy_id": 2,
        "date": "2026-06-14 09:15"
    },
    {
        "order_id": 1004,
        "customer_name": "Sanjay Ojha",
        "mobile": "9876501115",
        "address": "Ojha Gali, Near High School",
        "village": "Fatehpur",
        "pincode": "843105",
        "items": "Fortune Oil x2, Tata Salt x5",
        "total_amount": 490,
        "payment_method": "Razorpay",
        "status": "Pending",
        "delivery_boy_id": None,
        "date": "2026-06-14 14:02"
    }
]

# 6. Audit logs registry
audit_logs_db = [
    {
        "timestamp": "2026-06-14 15:45:00",
        "user": "owner",
        "role": "Owner",
        "action": "System Start",
        "details": "Grocify production-grade marketplace initial setup loaded."
    }
]

# 7. WhatsApp simulation logs
whatsapp_logs_db = [
    {
        "timestamp": "2026-06-14 14:02:10",
        "mobile": "9876501115",
        "message": "Namaste Sanjay Ojha, your order #1004 of ₹490 has been received. Thanks for shopping at Grocify!",
        "status": "Sent"
    }
]

# 8. Preloaded Sales History (30 Days of sales with both revenue and profit)
sales_history = []
base_date = datetime.now() - timedelta(days=30)
for i in range(31):
    log_date = (base_date + timedelta(days=i)).strftime("%Y-%m-%d")
    daily_sales = random.randint(3200, 8500)
    daily_orders = random.randint(8, 22)
    daily_profit = int(daily_sales * random.uniform(0.18, 0.26))  # 18-26% average kirana margins
    sales_history.append({
        "date": log_date,
        "revenue": daily_sales,
        "profit": daily_profit,
        "orders": daily_orders
    })

# --- SYSTEM UTILITY HELPERS ---

def log_audit(action, details):
    """Adds a log entry to the audit database."""
    current_user = get_current_user()
    username = current_user['username'] if current_user else "Guest"
    role = current_user['role'] if current_user else "Guest"
    audit_logs_db.insert(0, {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user": username,
        "role": role,
        "action": action,
        "details": details
    })

def send_whatsapp(mobile, message):
    """Simulates sending a WhatsApp alert message."""
    if settings.get("whatsapp_enabled", True):
        whatsapp_logs_db.insert(0, {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "mobile": mobile,
            "message": message,
            "status": "Sent"
        })

def get_current_user():
    """Gets currently logged-in user profile from session."""
    if 'username' in session:
        return next((u for u in users_db if u['username'] == session['username']), None)
    return None

def calculate_store_stats():
    """Calculates active KPI statistics for store owner console."""
    total_products = len(products_db)
    daily_orders = len([o for o in orders_db if o['date'].startswith(datetime.now().strftime("%Y-%m-%d"))])
    total_khata_credit = sum(k['outstanding_amount'] for k in khata_db)
    monthly_revenue = sum(day['revenue'] for day in sales_history)
    registered_customers = len(khata_db) + len(set(o['mobile'] for o in orders_db))
    low_stock_items = len([p for p in products_db if p['stock'] < 10])
    
    return {
        "total_products": total_products,
        "daily_orders": daily_orders,
        "monthly_revenue": monthly_revenue,
        "registered_customers": registered_customers,
        "low_stock_items": low_stock_items,
        "total_khata_credit": total_khata_credit
    }

def get_ai_forecasting():
    """Generates 30-day moving average inventory forecasting."""
    forecast = []
    for product in products_db:
        cat = product['category'].lower()
        if "rice" in cat or "flour" in cat or "oil" in cat:
            sales_30d = random.randint(25, 60)
        elif "dairy" in cat or "snack" in cat or "staple" in cat:
            sales_30d = random.randint(15, 35)
        else:
            sales_30d = random.randint(5, 20)
            
        daily_rate = round(sales_30d / 30.0, 2)
        projected_demand = math.ceil(daily_rate * 30)
        cover_days = 999 if daily_rate == 0 else round(product['stock'] / daily_rate)
        
        if product['stock'] == 0:
            status = "Critical (Out of Stock)"
            color = "rose"
        elif cover_days <= 7:
            status = "Reorder Immediately"
            color = "rose"
        elif cover_days <= 15:
            status = "Warning (Low Stock Cover)"
            color = "amber"
        else:
            status = "Healthy"
            color = "emerald"
            
        reorder_qty = max(0, projected_demand - product['stock'])
        
        forecast.append({
            "id": product['id'],
            "name": product['name'],
            "stock": product['stock'],
            "daily_rate": daily_rate,
            "projected_demand": projected_demand,
            "cover_days": cover_days,
            "status": status,
            "color": color,
            "reorder_qty": reorder_qty,
            "supplier": product['supplier']
        })
    return forecast

def calculate_pl_analytics():
    """Computes cost of goods sold, profit and category P&L breakdowns."""
    total_rev = sum(day['revenue'] for day in sales_history)
    total_prof = sum(day['profit'] for day in sales_history)
    total_cogs = total_rev - total_prof
    margin = round((total_prof / total_rev) * 100, 2) if total_rev > 0 else 0
    
    category_summary = {}
    categories_list = list(set(p['category'] for p in products_db))
    
    for cat in categories_list:
        weight = 0.15
        if "rice" in cat.lower() or "flour" in cat.lower(): weight = 0.25
        elif "oil" in cat.lower() or "spice" in cat.lower(): weight = 0.20
        elif "dairy" in cat.lower(): weight = 0.12
        
        cat_revenue = int(total_rev * weight)
        cat_profit = int(cat_revenue * random.uniform(0.18, 0.25))
        cat_cogs = cat_revenue - cat_profit
        cat_margin = round((cat_profit / cat_revenue) * 100, 1) if cat_revenue > 0 else 0
        
        category_summary[cat] = {
            "revenue": cat_revenue,
            "cogs": cat_cogs,
            "profit": cat_profit,
            "margin": cat_margin
        }
        
    return {
        "revenue": total_rev,
        "cogs": total_cogs,
        "profit": total_prof,
        "margin": margin,
        "categories": category_summary
    }

# --- MIDDLEWARE & CONTEXT PROCESSORS ---

@app.context_processor
def inject_global_data():
    """Injects user sessions and store configurations in all pages."""
    return {
        "current_user": get_current_user(),
        "settings": settings
    }

# --- CONTROLLERS & ROUTES ---

@app.route('/')
def index():
    """Customer storefront directory."""
    categories = [
        "Grocery & Staples", "Rice & Flour", "Pulses & Grains", 
        "Oils & Spices", "Dairy Products", "Snacks & Biscuits", 
        "Tea & Coffee", "Beverages", "Personal Care", "Household Essentials"
    ]
    
    sorted_products = sorted(products_db, key=lambda p: p['stock'])
    user = get_current_user()
    my_khata = None
    my_orders = []
    
    if user and user['role'] == "Customer":
        my_khata = next((k for k in khata_db if k['mobile'] == user['mobile']), None)
        if not my_khata:
            my_khata = {
                "customer_name": user['name'],
                "mobile": user['mobile'],
                "outstanding_amount": 0,
                "credit_limit": settings["default_credit_limit"],
                "payment_history": []
            }
            khata_db.append(my_khata)
        my_orders = [o for o in orders_db if o['mobile'] == user['mobile']]
        my_orders = sorted(my_orders, key=lambda o: o['order_id'], reverse=True)
        
    return render_template(
        'index.html', 
        products=sorted_products, 
        categories=categories, 
        my_khata=my_khata,
        my_orders=my_orders,
        delivery_charge=settings["delivery_charge"], 
        threshold=settings["free_delivery_threshold"]
    )

# --- AUTHENTICATION CONTROLLERS ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User Login route."""
    if get_current_user():
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Check if username matches username or mobile
        matched_user = next((u for u in users_db if u['username'] == username or u['mobile'] == username), None)
        
        if matched_user:
            if matched_user['password'] == password:
                session['username'] = matched_user['username']
                log_audit("User Login", f"Logged in successfully as {matched_user['role']} ({matched_user['name']})")
                flash(f"Welcome back, {matched_user['name']}!", "success")
                
                if matched_user['role'] in ["Owner", "Clerk"]:
                    return redirect(url_for('admin'))
                elif matched_user['role'] == "Delivery Boy":
                    return redirect(url_for('delivery_dashboard'))
                else:
                    return redirect(url_for('index'))
            else:
                flash("Incorrect Password!", "error")
        else:
            flash("Username or Mobile not found!", "error")
            
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User Registration route."""
    if get_current_user():
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        name = request.form.get('name')
        mobile = request.form.get('mobile')
        role = request.form.get('role', 'Customer')
        
        if any(u['username'] == username for u in users_db):
            flash("Username already exists! Choose another.", "error")
            return redirect(url_for('register'))
            
        new_user = {
            "username": username,
            "password": password,
            "role": role,
            "name": name,
            "mobile": mobile
        }
        users_db.append(new_user)
        
        if role == "Customer":
            existing_khata = next((k for k in khata_db if k['mobile'] == mobile), None)
            if not existing_khata:
                new_khata = {
                    "customer_name": name,
                    "mobile": mobile,
                    "outstanding_amount": 0,
                    "credit_limit": settings["default_credit_limit"],
                    "payment_history": []
                }
                khata_db.append(new_khata)
                
        elif role == "Delivery Boy":
            new_db_id = max(d['id'] for d in delivery_boys_db) + 1 if delivery_boys_db else 1
            delivery_boys_db.append({
                "id": new_db_id,
                "name": name,
                "mobile": mobile,
                "status": "Active"
            })
            
        log_audit("User Registered", f"New user {username} ({role}) registered.")
        flash("Registration successful! You can now log in.", "success")
        return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/logout')
def logout():
    """Logs out active user session."""
    user = get_current_user()
    if user:
        log_audit("User Logout", f"Logged out from session.")
        session.pop('username', None)
        flash("Logged out successfully.", "success")
    return redirect(url_for('index'))

# --- COMMERCE CONTROLLERS ---

@app.route('/checkout', methods=['POST'])
def checkout():
    """Process customer order placement with credit checks and payments."""
    global orders_db, khata_db, products_db
    
    name = request.form.get('customer_name')
    mobile = request.form.get('mobile')
    address = request.form.get('address')
    village = request.form.get('village')
    pincode = request.form.get('pincode')
    payment_method = request.form.get('payment_method')
    
    cart_data_raw = request.form.get('cart_data')
    if not cart_data_raw:
        flash("Your shopping cart is empty!", "error")
        return redirect(url_for('index'))
        
    try:
        cart_items = json.loads(cart_data_raw)
    except:
        flash("Error parsing cart details.", "error")
        return redirect(url_for('index'))
        
    subtotal = 0
    items_summary_list = []
    
    for item in cart_items:
        prod_id = int(item['id'])
        qty = int(item['quantity'])
        
        product = next((p for p in products_db if p['id'] == prod_id), None)
        if product:
            if product['stock'] < qty:
                qty = product['stock']
                if qty == 0:
                    continue
            subtotal += product['price'] * qty
            items_summary_list.append(f"{product['name']} x{qty}")
            
    if subtotal == 0:
        flash("All selected items are currently out of stock!", "error")
        return redirect(url_for('index'))
        
    shipping = 0 if subtotal >= settings["free_delivery_threshold"] else settings["delivery_charge"]
    grand_total = subtotal + shipping
    
    if payment_method == "Khata Credit":
        ledger = next((k for k in khata_db if k['mobile'] == mobile), None)
        limit = ledger['credit_limit'] if ledger else settings["default_credit_limit"]
        outstanding = ledger['outstanding_amount'] if ledger else 0
        
        if outstanding + grand_total > limit:
            flash(f"Purchase Blocked! This order exceeds your credit limit of ₹{limit:,}. Current Dues: ₹{outstanding:,}. Order total: ₹{grand_total:,}.", "error")
            log_audit("Checkout Failed", f"Credit checkout blocked for {name} ({mobile}) due to credit limit.")
            return redirect(url_for('index'))
            
    for item in cart_items:
        prod_id = int(item['id'])
        qty = int(item['quantity'])
        product = next((p for p in products_db if p['id'] == prod_id), None)
        if product:
            product['stock'] = max(0, product['stock'] - qty)
            
    order_id = max(o['order_id'] for o in orders_db) + 1 if orders_db else 1001
    order_date = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    assigned_db = random.choice(delivery_boys_db)['id'] if delivery_boys_db else None
    
    new_order = {
        "order_id": order_id,
        "customer_name": name,
        "mobile": mobile,
        "address": address,
        "village": village,
        "pincode": pincode,
        "items": ", ".join(items_summary_list),
        "total_amount": grand_total,
        "payment_method": payment_method,
        "status": "Pending",
        "delivery_boy_id": assigned_db,
        "date": order_date
    }
    
    orders_db.append(new_order)
    
    if payment_method == "Khata Credit":
        ledger = next((k for k in khata_db if k['mobile'] == mobile), None)
        if ledger:
            ledger['outstanding_amount'] += grand_total
            ledger['payment_history'].append({
                "date": datetime.now().strftime("%Y-%m-%d"),
                "type": "Purchase",
                "description": f"Order #{order_id} credit checkout",
                "amount": grand_total
            })
        else:
            ledger = {
                "customer_name": name,
                "mobile": mobile,
                "outstanding_amount": grand_total,
                "credit_limit": settings["default_credit_limit"],
                "payment_history": [
                    {
                        "date": datetime.now().strftime("%Y-%m-%d"),
                        "type": "Purchase",
                        "description": f"Order #{order_id} credit checkout",
                        "amount": grand_total
                    }
                ]
            }
            khata_db.append(ledger)
            
        send_whatsapp(mobile, f"Khata Alert: Order #{order_id} charged to credit. ₹{grand_total:,} added. Outstanding: ₹{ledger['outstanding_amount']:,}. - Grocify")
        
    today_date = datetime.now().strftime("%Y-%m-%d")
    today_sales = next((day for day in sales_history if day['date'] == today_date), None)
    today_profit = int(grand_total * random.uniform(0.18, 0.25))
    if today_sales:
        today_sales['revenue'] += grand_total
        today_sales['profit'] += today_profit
        today_sales['orders'] += 1
    else:
        sales_history.append({
            "date": today_date,
            "revenue": grand_total,
            "profit": today_profit,
            "orders": 1
        })
        
    log_audit("Order Placed", f"Order #{order_id} placed successfully via {payment_method}. Amount: ₹{grand_total:,}")
    send_whatsapp(mobile, f"Namaste {name}, your order #{order_id} of ₹{grand_total:,} has been received. Thanks for trusting Grocify!")
    
    flash(f"Order #{order_id} placed successfully! Thank you for trusting Grocify.", "success")
    return redirect(url_for('index'))

@app.route('/order/<int:order_id>/invoice')
def print_invoice(order_id):
    """Renders a printable invoice page."""
    order = next((o for o in orders_db if o['order_id'] == order_id), None)
    if not order:
        flash("Order not found!", "error")
        return redirect(url_for('index'))
        
    invoice_items = []
    raw_items = order['items'].split(', ')
    subtotal = 0
    
    for raw_item in raw_items:
        if ' x' in raw_item:
            parts = raw_item.rsplit(' x', 1)
            item_name = parts[0]
            try:
                qty = int(parts[1])
            except:
                qty = 1
        else:
            item_name = raw_item
            qty = 1
            
        prod = next((p for p in products_db if item_name in p['name']), None)
        unit_price = prod['price'] if prod else 100
        line_total = unit_price * qty
        subtotal += line_total
        
        invoice_items.append({
            "name": item_name,
            "qty": qty,
            "unit_price": unit_price,
            "total": line_total
        })
        
    shipping = order['total_amount'] - subtotal
    
    return render_template(
        'invoice.html', 
        order=order, 
        items=invoice_items, 
        subtotal=subtotal, 
        shipping=shipping
    )

# --- ADMIN CONSOLE ROUTES ---

@app.route('/admin')
def admin():
    """Admin dashboard console."""
    user = get_current_user()
    if not user or user['role'] not in ["Owner", "Clerk"]:
        flash("Unauthorized access! Admin console requires Owner or Clerk credentials.", "error")
        return redirect(url_for('login'))
        
    stats = calculate_store_stats()
    categories = [
        "Grocery & Staples", "Rice & Flour", "Pulses & Grains", 
        "Oils & Spices", "Dairy Products", "Snacks & Biscuits", 
        "Tea & Coffee", "Beverages", "Personal Care", "Household Essentials"
    ]
    
    forecasting_data = get_ai_forecasting()
    pl_data = calculate_pl_analytics()
    sales_json = json.dumps(sales_history)
    
    return render_template(
        'admin.html',
        products=products_db,
        khata=khata_db,
        orders=orders_db,
        delivery_boys=delivery_boys_db,
        stats=stats,
        categories=categories,
        forecast=forecasting_data,
        pl=pl_data,
        whatsapp_logs=whatsapp_logs_db,
        audit_logs=audit_logs_db,
        sales_json=sales_json,
        users=users_db
    )

@app.route('/admin/update_user_role', methods=['POST'])
def update_user_role():
    """Allows Owner to change roles of registered users."""
    user = get_current_user()
    if not user or user['role'] != "Owner":
        flash("Permission Denied! Only the Store Owner can assign user roles.", "error")
        return redirect(url_for('admin', tab='users'))
        
    username = request.form.get('username')
    new_role = request.form.get('role')
    
    if username == user['username']:
        flash("You cannot change your own role!", "error")
        return redirect(url_for('admin', tab='users'))
        
    target_user = next((u for u in users_db if u['username'] == username), None)
    if not target_user:
        flash("User not found!", "error")
        return redirect(url_for('admin', tab='users'))
        
    old_role = target_user['role']
    target_user['role'] = new_role
    
    # If the user is promoted to Delivery Boy and isn't in delivery_boys_db, add them
    if new_role == "Delivery Boy":
        exists = any(d['mobile'] == target_user['mobile'] for d in delivery_boys_db)
        if not exists:
            new_id = max(d['id'] for d in delivery_boys_db) + 1 if delivery_boys_db else 1
            delivery_boys_db.append({
                "id": new_id,
                "name": target_user['name'],
                "mobile": target_user['mobile'],
                "status": "Active"
            })
            
    # Write audit log
    log_audit("User Role Updated", f"Changed role of user '{username}' from {old_role} to {new_role}.")
    flash(f"Role for user '{target_user['name']}' updated to {new_role} successfully!", "success")
    return redirect(url_for('admin', tab='users'))


@app.route('/product/<int:product_id>')
def product_details(product_id):
    """Product details page with rich specification and reviews."""
    product = next((p for p in products_db if p['id'] == product_id), None)
    if not product:
        flash("Product not found!", "error")
        return redirect(url_for('index'))
        
    # Get related products (same category, max 4, excluding current)
    related = [p for p in products_db if p['category'] == product['category'] and p['id'] != product['id']][:4]
    if len(related) < 4:
        # Pad with other products if not enough in same category
        pad = [p for p in products_db if p['id'] != product['id'] and p not in related][:4 - len(related)]
        related.extend(pad)
        
    # Mock reviews
    mock_reviews_pool = [
        {"name": "Ramesh Kumar Mishra", "rating": 5, "date": "2026-06-10", "comment": "Excellent quality! Packaging was original and fresh. Highly recommended.", "verified": True, "helpful": 12},
        {"name": "Gita Devi", "rating": 5, "date": "2026-06-08", "comment": "Bahut accha product hai. Price is very reasonable compared to local city market.", "verified": True, "helpful": 8},
        {"name": "Mahendra Singh", "rating": 4, "date": "2026-06-01", "comment": "Good quality and authentic taste. Delivery boy Sanjay brought it on time.", "verified": True, "helpful": 5},
        {"name": "Suresh Chandra", "rating": 5, "date": "2026-05-28", "comment": "Standard packaging. Clean and fresh. Grocify Team always delivers the best.", "verified": True, "helpful": 15}
    ]
    
    # Deterministic mock sample based on product ID to avoid page reload randomness
    rand_idx = (product_id * 7) % len(mock_reviews_pool)
    reviews = [
        mock_reviews_pool[rand_idx],
        mock_reviews_pool[(rand_idx + 1) % len(mock_reviews_pool)],
        mock_reviews_pool[(rand_idx + 2) % len(mock_reviews_pool)]
    ]
    
    # Mock specifications and nutrition based on category
    specs = {
        "Brand": product['supplier'] if 'supplier' in product else "Grocify Fresh",
        "Manufacturer": product['supplier'] if 'supplier' in product else "Grocify",
        "Shelf Life": "6 Months" if product['category'] in ["Rice & Flour", "Pulses & Grains", "Oils & Spices", "Grocery & Staples"] else "12 Months",
        "Storage": "Store in dry place, away from sunlight" if product['category'] not in ["Dairy Products"] else "Refrigerate after opening",
        "Country of Origin": "India"
    }
    
    # Mock nutrition table
    nutrition = [
        {"item": "Energy", "value": "364 kcal"},
        {"item": "Carbohydrates", "value": "73 g"},
        {"item": "Protein", "value": "10 g"},
        {"item": "Fat", "value": "1.5 g"},
        {"item": "Dietary Fiber", "value": "11 g"}
    ]
    
    # Weight/Size options
    if "1kg" in product['name'].lower() or "1l" in product['name'].lower():
        weight_options = ["500g / 500ml", "1kg / 1L", "2kg / 2L"]
    elif "5kg" in product['name'].lower():
        weight_options = ["1kg", "5kg", "10kg"]
    elif "100g" in product['name'].lower():
        weight_options = ["50g", "100g", "250g"]
    else:
        weight_options = ["Standard Pack", "Family Pack"]
        
    return render_template(
        'product_details.html',
        product=product,
        related=related,
        reviews=reviews,
        specs=specs,
        nutrition=nutrition,
        weight_options=weight_options
    )


@app.route('/cart')
def cart_page():
    """Shopping Cart and Checkout Page."""
    user = get_current_user()
    customer_name = ""
    mobile = ""
    address = ""
    village = ""
    pincode = ""
    if user:
        customer_name = user['name']
        mobile = user['mobile']
        # Fetch previous order details to load default address fields
        prior_order = next((o for o in reversed(orders_db) if o['mobile'] == mobile), None)
        if prior_order:
            address = prior_order.get('address', '')
            village = prior_order.get('village', '')
            pincode = prior_order.get('pincode', '')
            
    # Recommended products: Frequently Bought Together (max 4 items)
    frequent_items = sorted(products_db, key=lambda x: x['price'], reverse=True)[:6]
    
    return render_template(
        'cart.html',
        customer_name=customer_name,
        mobile=mobile,
        address=address,
        village=village,
        pincode=pincode,
        frequent_items=frequent_items,
        settings=settings
    )


@app.route('/dashboard')
@app.route('/profile')
def customer_dashboard():
    """Customer profile management dashboard."""
    user = get_current_user()
    if not user:
        flash("Please log in to view your customer dashboard.", "error")
        return redirect(url_for('login'))
        
    # Redirect administrators and delivery boys to their respective dashboards
    if user['role'] in ["Owner", "Clerk"]:
        return redirect(url_for('admin'))
    elif user['role'] == "Delivery Boy":
        return redirect(url_for('delivery_dashboard'))
        
    # Get user order history
    my_orders = [o for o in orders_db if o['mobile'] == user['mobile']]
    my_orders = sorted(my_orders, key=lambda o: o['order_id'], reverse=True)
    
    # Get khata ledger dues and limit
    ledger = next((k for k in khata_db if k['mobile'] == user['mobile']), None)
    dues = ledger['outstanding_amount'] if ledger else 0
    limit = ledger['credit_limit'] if ledger else settings["default_credit_limit"]
    
    # Mock wishlist items (pick 3 products from catalog)
    wishlist_items = products_db[:3]
    
    # Calculation stats
    total_orders = len(my_orders)
    reward_points = total_orders * 150 + 200
    money_saved = total_orders * 45
    
    # Mock notifications queue
    notifications = [
        {"icon": "package", "title": "Order Shipped!", "desc": "Your order #1002 has been handed over to Sanjay (Delivery Boy).", "time": "2 hours ago", "unread": True},
        {"icon": "tag", "title": "Bazar Offer Available", "desc": "Use code SAVE100 to get ₹100 flat discount on orders above ₹500.", "time": "1 day ago", "unread": False},
        {"icon": "credit-card", "title": "Khata Credit Charged", "desc": "₹650 charged to your credit ledger for order #1001.", "time": "3 days ago", "unread": False}
    ]
    
    return render_template(
        'dashboard.html',
        user=user,
        orders=my_orders,
        dues=dues,
        limit=limit,
        wishlist_items=wishlist_items,
        total_orders=total_orders,
        reward_points=reward_points,
        money_saved=money_saved,
        notifications=notifications,
        settings=settings
    )


@app.route('/inventory')
@app.route('/admin/inventory_manager')
def inventory_manager():
    """Enterprise-grade Inventory Management page for Grocify."""
    user = get_current_user()
    if not user:
        flash("Please log in to access the Grocify Inventory Management panel.", "error")
        return redirect(url_for('login'))
        
    if user['role'] not in ["Owner", "Clerk"]:
        flash("Access Denied! Enterprise dashboard requires Clerk or Owner clearance.", "error")
        return redirect(url_for('login'))
        
    # Calculate stats
    total_val = sum(p['price'] * p['stock'] for p in products_db)
    products_in_stock = len([p for p in products_db if p['stock'] > 0])
    low_stock_items = len([p for p in products_db if 0 < p['stock'] < 10])
    out_of_stock_items = len([p for p in products_db if p['stock'] == 0])
    
    # Mock warehouses
    warehouses = [
        {"name": "Rampur Main Warehouse", "capacity": "85%", "temp": "22°C", "products": 450, "utilization": 85},
        {"name": "Mishra Tola Cold Storage", "capacity": "60%", "temp": "4°C", "products": 120, "utilization": 60},
        {"name": "Town Transit Hub", "capacity": "40%", "temp": "26°C", "products": 85, "utilization": 40}
    ]
    
    # Mock stock movements
    movements = [
        {"type": "Stock Added", "desc": "Restocked 50 units of Amul Milk (1L) from supplier Ganga Dairy.", "time": "1 hour ago", "icon": "plus-circle", "color": "text-[#16A34A]"},
        {"type": "Sale Out", "desc": "12 units of Maggi Noodles sold under order #1004.", "time": "3 hours ago", "icon": "arrow-down-right", "color": "text-[#2563EB]"},
        {"type": "Transfer", "desc": "Transferred 20 units of Mustard Oil to Town Transit Hub.", "time": "Yesterday", "icon": "git-pull-request", "color": "text-[#F97316]"},
        {"type": "Adjustment", "desc": "Reduced 2 units of Surf Excel due to packaging damage.", "time": "2 days ago", "icon": "sliders", "color": "text-slate-500"}
    ]
    
    # Mock supplier parameters
    suppliers = [
        {"name": "Ganga Dairy Cooperative", "phone": "+91 98765 09901", "products": "Milk, Butter, Ghee", "balance": 4500, "lead_time": "1.5 Days"},
        {"name": "Rampur Krishi Mandi", "phone": "+91 98765 09902", "products": "Rice, Wheat, Dal", "balance": 12000, "lead_time": "2.0 Days"},
        {"name": "Hindustan Unilever Distributor", "phone": "+91 98765 09903", "products": "Soaps, Detergents, Toothpaste", "balance": 8500, "lead_time": "3.5 Days"}
    ]

    return render_template(
        'inventory_manager.html',
        products=products_db,
        warehouses=warehouses,
        movements=movements,
        suppliers=suppliers,
        total_val=total_val,
        products_in_stock=products_in_stock,
        low_stock_items=low_stock_items,
        out_of_stock_items=out_of_stock_items,
        categories=categories,
        users=users_db,
        settings=settings
    )


@app.route('/delivery_dashboard')
def delivery_dashboard():
    """Specialized delivery staff mobile workspace."""
    user = get_current_user()
    if not user or user['role'] != "Delivery Boy":
        flash("Access Denied! Specialized console requires Delivery Boy authentication.", "error")
        return redirect(url_for('login'))
        
    staff = next((d for d in delivery_boys_db if d['mobile'] == user['mobile']), None)
    staff_id = staff['id'] if staff else None
    
    my_deliveries = [o for o in orders_db if o['delivery_boy_id'] == staff_id]
    my_deliveries = sorted(my_deliveries, key=lambda o: o['order_id'], reverse=True)
    
    return render_template('delivery_dashboard.html', deliveries=my_deliveries, staff=staff)

@app.route('/admin/add_product', methods=['POST'])
def add_product():
    """Adds a new product to catalog."""
    user = get_current_user()
    if not user or user['role'] not in ["Owner", "Clerk"]:
        return jsonify({"error": "Unauthorized"}), 403
        
    global products_db
    new_id = max(p['id'] for p in products_db) + 1 if products_db else 1
    
    name = request.form.get('name')
    category = request.form.get('category')
    price = int(request.form.get('price', 0))
    cost_price = int(request.form.get('cost_price', 0))
    stock = int(request.form.get('stock', 0))
    supplier = request.form.get('supplier')
    
    image_code = "staples"
    cat_lower = category.lower()
    if "rice" in cat_lower or "flour" in cat_lower: image_code = "rice"
    elif "oil" in cat_lower or "spice" in cat_lower: image_code = "mustard_oil"
    elif "dairy" in cat_lower: image_code = "milk"
    elif "snack" in cat_lower or "biscuit" in cat_lower: image_code = "biscuits"
    elif "tea" in cat_lower or "coffee" in cat_lower: image_code = "tea"
    elif "beverage" in cat_lower: image_code = "frooti"
    elif "care" in cat_lower: image_code = "handwash"
    elif "house" in cat_lower: image_code = "vim"
    
    new_prod = {
        "id": new_id,
        "name": name,
        "category": category,
        "price": price,
        "cost_price": cost_price,
        "stock": stock,
        "supplier": supplier,
        "image": image_code
    }
    products_db.append(new_prod)
    log_audit("Product Added", f"Added item '{name}' to inventory. ID: #{new_id}, Cost: ₹{cost_price}, Price: ₹{price}")
    flash(f"Product '{name}' added successfully!", "success")
    return redirect(url_for('admin', tab='inventory'))

@app.route('/admin/edit_product/<int:prod_id>', methods=['POST'])
def edit_product(prod_id):
    """Updates product specifications."""
    user = get_current_user()
    if not user or user['role'] not in ["Owner", "Clerk"]:
        return jsonify({"error": "Unauthorized"}), 403
        
    global products_db
    for p in products_db:
        if p['id'] == prod_id:
            p['name'] = request.form.get('name')
            p['category'] = request.form.get('category')
            p['price'] = int(request.form.get('price', 0))
            p['cost_price'] = int(request.form.get('cost_price', 0))
            p['stock'] = int(request.form.get('stock', 0))
            p['supplier'] = request.form.get('supplier')
            log_audit("Product Edited", f"Updated product ID: #{prod_id} details. Stock: {p['stock']}, Cost: ₹{p['cost_price']}, Price: ₹{p['price']}")
            break
    flash("Product details updated successfully!", "success")
    return redirect(url_for('admin', tab='inventory'))

@app.route('/admin/delete_product/<int:prod_id>', methods=['POST'])
def delete_product(prod_id):
    """Removes a product from catalog (Owner-only action)."""
    user = get_current_user()
    if not user or user['role'] != "Owner":
        flash("Permission Denied! Only the Store Owner can delete catalog products.", "error")
        return redirect(url_for('admin', tab='inventory'))
        
    global products_db
    product = next((p for p in products_db if p['id'] == prod_id), None)
    if product:
        products_db = [p for p in products_db if p['id'] != prod_id]
        log_audit("Product Deleted", f"Removed product '{product['name']}' (ID: #{prod_id}) from catalog.")
        flash("Product removed successfully from inventory.", "success")
    return redirect(url_for('admin', tab='inventory'))

@app.route('/admin/update_delivery/<int:order_id>', methods=['POST'])
def update_delivery(order_id):
    """Updates delivery dispatch statuses and boy assignments."""
    global orders_db
    order = next((o for o in orders_db if o['order_id'] == order_id), None)
    if not order:
        flash("Order not found!", "error")
        return redirect(url_for('admin', tab='deliveries'))
        
    assigned_db_val = request.form.get('delivery_boy_id')
    assigned_db_id = int(assigned_db_val) if assigned_db_val else None
    new_status = request.form.get('status')
    
    order['delivery_boy_id'] = assigned_db_id
    old_status = order['status']
    order['status'] = new_status
    
    db_name = "Unassigned"
    if assigned_db_id:
        db_boy = next((d for d in delivery_boys_db if d['id'] == assigned_db_id), None)
        if db_boy:
            db_name = db_boy['name']
            
    log_audit("Delivery Status Updated", f"Order #{order_id} status changed from '{old_status}' to '{new_status}'. Assigned: {db_name}")
    
    if new_status == "Out for Delivery":
        send_whatsapp(order['mobile'], f"Namaste {order['customer_name']}, your order #{order_id} is Out for Delivery with our agent {db_name}. - Grocify")
    elif new_status == "Delivered":
        send_whatsapp(order['mobile'], f"Namaste {order['customer_name']}, your order #{order_id} has been delivered successfully. Thank you! - Grocify")
        
    flash(f"Order #{order_id} updated successfully.", "success")
    
    user = get_current_user()
    if user and user['role'] == "Delivery Boy":
        return redirect(url_for('delivery_dashboard'))
    return redirect(url_for('admin', tab='deliveries'))

@app.route('/admin/update_khata/<string:mobile>', methods=['POST'])
def update_khata(mobile):
    """Updates ledger balance and edits individual credit limits."""
    global khata_db
    ledger = next((k for k in khata_db if k['mobile'] == mobile), None)
    if not ledger:
        flash("Khata account not found!", "error")
        return redirect(url_for('admin', tab='ledger'))
        
    action_type = request.form.get('action_type')
    
    if action_type == "Update Limit":
        new_limit = int(request.form.get('credit_limit', settings["default_credit_limit"]))
        old_limit = ledger['credit_limit']
        ledger['credit_limit'] = new_limit
        log_audit("Khata Limit Updated", f"Credit limit for {ledger['customer_name']} updated from ₹{old_limit:,} to ₹{new_limit:,}")
        send_whatsapp(mobile, f"Khata Notice: Your family credit limit has been adjusted to ₹{new_limit:,}. - Grocify")
        flash(f"Credit limit for {ledger['customer_name']} updated successfully to ₹{new_limit:,}.", "success")
    else:
        description = request.form.get('description')
        amount = int(request.form.get('amount', 0))
        
        if amount <= 0:
            flash("Please enter a valid amount!", "error")
            return redirect(url_for('admin', tab='ledger'))
            
        if action_type == "Purchase":
            ledger['outstanding_amount'] += amount
            ledger['payment_history'].append({
                "date": datetime.now().strftime("%Y-%m-%d"),
                "type": "Purchase",
                "description": description,
                "amount": amount
            })
            log_audit("Khata Credit Charged", f"Manually charged ₹{amount:,} to {ledger['customer_name']}'s account. Memo: {description}")
            send_whatsapp(mobile, f"Khata Alert: ₹{amount:,} charged. Outstanding Balance: ₹{ledger['outstanding_amount']:,}. - Grocify")
            flash(f"Recorded credit purchase of ₹{amount} for {ledger['customer_name']}.", "success")
        else:
            ledger['outstanding_amount'] = max(ledger['outstanding_amount'] - amount, 0)
            ledger['payment_history'].append({
                "date": datetime.now().strftime("%Y-%m-%d"),
                "type": "Payment",
                "description": description,
                "amount": amount
            })
            log_audit("Khata Payment Receipt", f"Recorded payment of ₹{amount:,} from {ledger['customer_name']}. Memo: {description}")
            send_whatsapp(mobile, f"Khata Receipt: We have received payment of ₹{amount:,}. Outstanding Balance: ₹{ledger['outstanding_amount']:,}. - Grocify")
            flash(f"Recorded payment receipt of ₹{amount} from {ledger['customer_name']}.", "success")
            
    return redirect(url_for('admin', tab='ledger'))

@app.route('/admin/update_settings', methods=['POST'])
def update_settings():
    """Updates system global configurations."""
    user = get_current_user()
    if not user or user['role'] != "Owner":
        flash("Access Denied! Settings changes are Owner-only actions.", "error")
        return redirect(url_for('admin', tab='settings'))
        
    global settings
    settings["store_name"] = request.form.get('store_name')
    settings["tagline"] = request.form.get('tagline')
    settings["delivery_charge"] = int(request.form.get('delivery_charge', 30))
    settings["free_delivery_threshold"] = int(request.form.get('free_delivery_threshold', 500))
    settings["default_credit_limit"] = int(request.form.get('default_credit_limit', 10000))
    settings["whatsapp_enabled"] = 'whatsapp_enabled' in request.form
    
    log_audit("Settings Configured", f"Shop settings updated. Name: {settings['store_name']}, Base Limit: ₹{settings['default_credit_limit']:,}")
    flash("System settings saved successfully!", "success")
    return redirect(url_for('admin', tab='settings'))

# --- BACKUP & RESTORE MODULES ---

@app.route('/admin/backup', methods=['GET'])
def backup_database():
    """Generates JSON download files of the full ERP database state."""
    user = get_current_user()
    if not user or user['role'] not in ["Owner", "Clerk"]:
        return "Unauthorized Access", 403
        
    db_state = {
        "settings": settings,
        "products": products_db,
        "khata": khata_db,
        "delivery_boys": delivery_boys_db,
        "orders": orders_db,
        "users": users_db,
        "audit_logs": audit_logs_db,
        "whatsapp_logs": whatsapp_logs_db,
        "sales_history": sales_history
    }
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    response_data = json.dumps(db_state, indent=2)
    
    from flask import Response
    return Response(
        response_data,
        mimetype="application/json",
        headers={"Content-disposition": f"attachment; filename=grocify_backup_{timestamp}.json"}
    )

@app.route('/admin/restore', methods=['POST'])
def restore_database():
    """Uploads and overrides current in-memory data with json backups."""
    user = get_current_user()
    if not user or user['role'] != "Owner":
        flash("Permission Denied! Database restoring is Owner-only.", "error")
        return redirect(url_for('admin', tab='settings'))
        
    global settings, products_db, khata_db, delivery_boys_db, orders_db, users_db, audit_logs_db, whatsapp_logs_db, sales_history
    
    file = request.files.get('backup_file')
    if not file:
        flash("No file selected for restoration!", "error")
        return redirect(url_for('admin', tab='settings'))
        
    try:
        data = json.load(file)
        
        if "products" in data: products_db = data["products"]
        if "khata" in data: khata_db = data["khata"]
        if "delivery_boys" in data: delivery_boys_db = data["delivery_boys"]
        if "orders" in data: orders_db = data["orders"]
        if "users" in data: users_db = data["users"]
        if "settings" in data: settings.update(data["settings"])
        if "sales_history" in data: sales_history = data["sales_history"]
        if "audit_logs" in data: audit_logs_db = data["audit_logs"]
        if "whatsapp_logs" in data: whatsapp_logs_db = data["whatsapp_logs"]
        
        log_audit("Database Restored", "Full backup import executed.")
        flash("Database restored successfully!", "success")
    except Exception as e:
        flash(f"Error parsing backup file: {str(e)}", "error")
        
    return redirect(url_for('admin', tab='settings'))

@app.route('/admin/reset', methods=['POST'])
def reset_system():
    """Resets databases back to factory defaults."""
    user = get_current_user()
    if not user or user['role'] != "Owner":
        flash("Permission Denied! System resets require Owner credentials.", "error")
        return redirect(url_for('admin', tab='settings'))
        
    global products_db, khata_db, orders_db, sales_history, whatsapp_logs_db, audit_logs_db, settings, delivery_boys_db, users_db
    
    settings = {
        "store_name": "Grocify",
        "tagline": "Smart Grocery & Retail Management Platform",
        "delivery_charge": 30,
        "free_delivery_threshold": 500,
        "default_credit_limit": 10000,
        "whatsapp_enabled": True
    }
    
    users_db = [
        {"username": "owner", "password": "owner123", "role": "Owner", "name": "Grocify Team", "mobile": "9876501100"},
        {"username": "clerk", "password": "clerk123", "role": "Clerk", "name": "Ramji Prasad", "mobile": "9876501199"},
        {"username": "delivery", "password": "delivery123", "role": "Delivery Boy", "name": "Sanjay Kumar", "mobile": "9876502201"},
        {"username": "customer", "password": "customer123", "role": "Customer", "name": "Ramesh Kumar Mishra", "mobile": "9876501101"}
    ]
    
    delivery_boys_db = [
        {"id": 1, "name": "Sanjay Kumar", "mobile": "9876502201", "status": "Active"},
        {"id": 2, "name": "Ram Avtar", "mobile": "9876502202", "status": "Active"},
        {"id": 3, "name": "Vijay Yadav", "mobile": "9876502203", "status": "Active"}
    ]
    
    products_db = [
        {"id": 1, "name": "Ashirvaad Shudh Chakki Atta (5kg)", "category": "Rice & Flour", "price": 260, "cost_price": 200, "stock": 35, "supplier": "ITC Ltd.", "image": "atta"},
        {"id": 2, "name": "India Gate Basmati Rice Rozana (5kg)", "category": "Rice & Flour", "price": 450, "cost_price": 350, "stock": 8, "supplier": "India Gate Ltd.", "image": "rice"},
        {"id": 3, "name": "Tata Salt Iodized (1kg)", "category": "Grocery & Staples", "price": 28, "cost_price": 20, "stock": 120, "supplier": "Tata Consumer Products", "image": "salt"},
        {"id": 4, "name": "Fortune Pure Mustard Oil (1L)", "category": "Oils & Spices", "price": 175, "cost_price": 135, "stock": 45, "supplier": "Adani Wilmar", "image": "mustard_oil"},
        {"id": 5, "name": "MDH Shahi Paneer Masala (100g)", "category": "Oils & Spices", "price": 95, "cost_price": 70, "stock": 50, "supplier": "MDH Spices", "image": "masala"},
        {"id": 6, "name": "Tata Sampann Toor Dal Premium (1kg)", "category": "Pulses & Grains", "price": 160, "cost_price": 120, "stock": 6, "supplier": "Tata Consumer Products", "image": "dal"},
        {"id": 7, "name": "Amul Pasteurised Butter (500g)", "category": "Dairy Products", "price": 275, "cost_price": 210, "stock": 18, "supplier": "GCMMF (Amul)", "image": "butter"},
        {"id": 8, "name": "Amul Taaza Milk Tetra (1L)", "category": "Dairy Products", "price": 68, "cost_price": 52, "stock": 40, "supplier": "GCMMF (Amul)", "image": "milk"},
        {"id": 9, "name": "Britannia Marie Gold Biscuits (250g)", "category": "Snacks & Biscuits", "price": 35, "cost_price": 25, "stock": 80, "supplier": "Britannia Industries", "image": "biscuits"},
        {"id": 10, "name": "Red Label Strong Tea (1kg)", "category": "Tea & Coffee", "price": 410, "cost_price": 315, "stock": 25, "supplier": "Hindustan Unilever", "image": "tea"},
        {"id": 11, "name": "Nescafe Classic Coffee Jar (100g)", "category": "Tea & Coffee", "price": 320, "cost_price": 240, "stock": 5, "supplier": "Nestle India", "image": "coffee"},
        {"id": 12, "name": "Dettol Liquid Handwash Original (200ml)", "category": "Personal Care", "price": 99, "cost_price": 75, "stock": 60, "supplier": "Reckitt Benckiser", "image": "handwash"},
        {"id": 13, "name": "Patanjali Dant Kanti Toothpaste (200g)", "category": "Personal Care", "price": 115, "cost_price": 85, "stock": 55, "supplier": "Patanjali Ayurved", "image": "toothpaste"},
        {"id": 14, "name": "Vim Liquid Dishwash (500ml)", "category": "Household Essentials", "price": 110, "cost_price": 80, "stock": 30, "supplier": "Hindustan Unilever", "image": "vim"},
        {"id": 15, "name": "Surf Excel Easy Wash (1kg)", "category": "Household Essentials", "price": 140, "cost_price": 105, "stock": 22, "supplier": "Hindustan Unilever", "image": "surf"},
        {"id": 16, "name": "Maggi 2-Minute Noodles (12-Pack)", "category": "Snacks & Biscuits", "price": 168, "cost_price": 130, "stock": 4, "supplier": "Nestle India", "image": "maggi"},
        {"id": 17, "name": "Tata Sampann Kabuli Chana (1kg)", "category": "Pulses & Grains", "price": 150, "cost_price": 115, "stock": 32, "supplier": "Tata Consumer Products", "image": "chana"},
        {"id": 18, "name": "Haldiram's Aloo Bhujia (350g)", "category": "Snacks & Biscuits", "price": 110, "cost_price": 85, "stock": 75, "supplier": "Haldiram's Foods", "image": "bhujia"},
        {"id": 19, "name": "Frooti Mango Drink (1.2L)", "category": "Beverages", "price": 70, "cost_price": 50, "stock": 45, "supplier": "Parle Agro", "image": "frooti"},
        {"id": 20, "name": "Thums Up Cold Drink (1.25L)", "category": "Beverages", "price": 75, "cost_price": 55, "stock": 40, "supplier": "Coca-Cola India", "image": "thumsup"},
        {"id": 21, "name": "Sunsilk Black Shine Shampoo (180ml)", "category": "Personal Care", "price": 120, "cost_price": 90, "stock": 35, "supplier": "Hindustan Unilever", "image": "shampoo"},
        {"id": 22, "name": "Lizol Disinfectant Floor Cleaner (500ml)", "category": "Household Essentials", "price": 105, "cost_price": 80, "stock": 28, "supplier": "Reckitt Benckiser", "image": "lizol"},
        {"id": 23, "name": "Amul Pure Cow Ghee (1L)", "category": "Dairy Products", "price": 650, "cost_price": 500, "stock": 15, "supplier": "GCMMF (Amul)", "image": "ghee"},
        {"id": 24, "name": "Tata Tea Gold Leaf Premium (1kg)", "category": "Tea & Coffee", "price": 460, "cost_price": 350, "stock": 20, "supplier": "Tata Consumer Products", "image": "tea"},
        {"id": 25, "name": "Tata Sampann Kabuli Chana Premium (1kg)", "category": "Pulses & Grains", "price": 150, "cost_price": 115, "stock": 32, "supplier": "Tata Consumer Products", "image": "dal"},
        {"id": 26, "name": "India Gate Basmati Rice Premium (5kg)", "category": "Rice & Flour", "price": 450, "cost_price": 350, "stock": 12, "supplier": "India Gate Ltd.", "image": "rice"},
        {"id": 27, "name": "Madhur Pure Sugar (1kg)", "category": "Grocery & Staples", "price": 50, "cost_price": 38, "stock": 150, "supplier": "Renuka Sugars", "image": "salt"},
        {"id": 28, "name": "Rajdhani Besan (1kg)", "category": "Rice & Flour", "price": 90, "cost_price": 68, "stock": 40, "supplier": "Rajdhani Group", "image": "atta"},
        {"id": 29, "name": "Catch Turmeric Powder Haldi (200g)", "category": "Oils & Spices", "price": 60, "cost_price": 45, "stock": 65, "supplier": "DS Group", "image": "masala"},
        {"id": 30, "name": "Tata Sampann Moong Dal Premium (1kg)", "category": "Pulses & Grains", "price": 175, "cost_price": 130, "stock": 25, "supplier": "Tata Consumer Products", "image": "dal"},
        {"id": 31, "name": "Fortune Soya Chunks (200g)", "category": "Pulses & Grains", "price": 45, "cost_price": 32, "stock": 50, "supplier": "Adani Wilmar", "image": "dal"},
        {"id": 32, "name": "Amul Cheese Slices (200g / 10 Slices)", "category": "Dairy Products", "price": 150, "cost_price": 115, "stock": 22, "supplier": "GCMMF (Amul)", "image": "butter"},
        {"id": 33, "name": "Fortune Soya Health Refined Oil (1L)", "category": "Oils & Spices", "price": 140, "cost_price": 105, "stock": 38, "supplier": "Adani Wilmar", "image": "mustard_oil"},
        {"id": 34, "name": "Britannia Good Day Cashew Cookies (200g)", "category": "Snacks & Biscuits", "price": 40, "cost_price": 28, "stock": 95, "supplier": "Britannia Industries", "image": "biscuits"},
        {"id": 35, "name": "Kurkure Masala Munch (90g)", "category": "Snacks & Biscuits", "price": 20, "cost_price": 14, "stock": 110, "supplier": "PepsiCo India", "image": "biscuits"},
        {"id": 36, "name": "Tata Tea Premium (1kg)", "category": "Tea & Coffee", "price": 380, "cost_price": 285, "stock": 30, "supplier": "Tata Consumer Products", "image": "tea"},
        {"id": 37, "name": "Maaza Mango Drink (1.2L)", "category": "Beverages", "price": 75, "cost_price": 52, "stock": 45, "supplier": "Coca-Cola India", "image": "frooti"},
        {"id": 38, "name": "Colgate Strong Teeth Toothpaste (200g)", "category": "Personal Care", "price": 95, "cost_price": 70, "stock": 65, "supplier": "Colgate-Palmolive", "image": "toothpaste"},
        {"id": 39, "name": "Lifebuoy Total Soap Bar (125g)", "category": "Personal Care", "price": 35, "cost_price": 24, "stock": 150, "supplier": "Hindustan Unilever", "image": "handwash"},
        {"id": 40, "name": "Comfort After Wash Fabric Conditioner (250ml)", "category": "Household Essentials", "price": 75, "cost_price": 55, "stock": 35, "supplier": "Hindustan Unilever", "image": "vim"},
        {"id": 41, "name": "Tata Sampann Unpolished Arhar Dal (1kg)", "category": "Pulses & Grains", "price": 180, "cost_price": 140, "stock": 30, "supplier": "Tata Consumer Products", "image": "dal"},
        {"id": 42, "name": "Fortune Premium Kachi Ghani Mustard Oil (1L)", "category": "Oils & Spices", "price": 185, "cost_price": 145, "stock": 25, "supplier": "Adani Wilmar", "image": "mustard_oil"},
        {"id": 43, "name": "Aashirvaad Select Premium Sharbati Atta (5kg)", "category": "Rice & Flour", "price": 290, "cost_price": 220, "stock": 20, "supplier": "ITC Ltd.", "image": "atta"},
        {"id": 44, "name": "Kohinoor Super Silver Basmati Rice (5kg)", "category": "Rice & Flour", "price": 600, "cost_price": 460, "stock": 15, "supplier": "Kohinoor Foods", "image": "rice"},
        {"id": 45, "name": "Amul Gold Milk Tetra Pack (1L)", "category": "Dairy Products", "price": 74, "cost_price": 58, "stock": 35, "supplier": "GCMMF (Amul)", "image": "milk"},
        {"id": 46, "name": "Nestle Everyday Dairy Whitener (1kg)", "category": "Dairy Products", "price": 420, "cost_price": 320, "stock": 12, "supplier": "Nestle India", "image": "milk"},
        {"id": 47, "name": "Society Tea Premium Dust (1kg)", "category": "Tea & Coffee", "price": 430, "cost_price": 330, "stock": 18, "supplier": "Society Tea", "image": "tea"},
        {"id": 48, "name": "Brooke Bond Taj Mahal Tea (1kg)", "category": "Tea & Coffee", "price": 650, "cost_price": 500, "stock": 10, "supplier": "Hindustan Unilever", "image": "tea"},
        {"id": 49, "name": "Tata Salt Lite Low Sodium (1kg)", "category": "Grocery & Staples", "price": 40, "cost_price": 30, "stock": 80, "supplier": "Tata Consumer Products", "image": "salt"},
        {"id": 50, "name": "Dabur Honey Pure Gold (500g)", "category": "Grocery & Staples", "price": 220, "cost_price": 165, "stock": 22, "supplier": "Dabur India", "image": "ghee"},
        {"id": 51, "name": "MDH Deggi Mirch Powder (100g)", "category": "Oils & Spices", "price": 85, "cost_price": 65, "stock": 45, "supplier": "MDH Spices", "image": "masala"},
        {"id": 52, "name": "Everest Garam Masala Premium (100g)", "category": "Oils & Spices", "price": 90, "cost_price": 70, "stock": 50, "supplier": "Everest Spices", "image": "masala"},
        {"id": 53, "name": "MTR Rava Idli Mix (500g)", "category": "Snacks & Biscuits", "price": 120, "cost_price": 90, "stock": 30, "supplier": "MTR Foods", "image": "biscuits"},
        {"id": 54, "name": "Parle-G Gold Biscuits (1kg Pack)", "category": "Snacks & Biscuits", "price": 80, "cost_price": 60, "stock": 100, "supplier": "Parle Products", "image": "biscuits"},
        {"id": 55, "name": "Minute Maid Mixed Fruit Juice (1L)", "category": "Beverages", "price": 99, "cost_price": 75, "stock": 40, "supplier": "Coca-Cola India", "image": "frooti"},
        {"id": 56, "name": "Pepsi Bottle Cold Drink (1.25L)", "category": "Beverages", "price": 75, "cost_price": 55, "stock": 35, "supplier": "PepsiCo India", "image": "thumsup"},
        {"id": 57, "name": "Himalaya Purifying Neem Face Wash (200ml)", "category": "Personal Care", "price": 199, "cost_price": 150, "stock": 25, "supplier": "Himalaya Wellness", "image": "handwash"},
        {"id": 58, "name": "Colgate MaxFresh Gel Toothpaste (150g)", "category": "Personal Care", "price": 110, "cost_price": 80, "stock": 40, "supplier": "Colgate-Palmolive", "image": "toothpaste"},
        {"id": 59, "name": "Surf Excel Matic Front Load Liquid (1L)", "category": "Household Essentials", "price": 220, "cost_price": 170, "stock": 15, "supplier": "Hindustan Unilever", "image": "surf"},
        {"id": 60, "name": "Vim Dishwash Bar Multipack (3x200g)", "category": "Household Essentials", "price": 60, "cost_price": 45, "stock": 50, "supplier": "Hindustan Unilever", "image": "vim"}
    ]
    
    khata_db = [
        {
            "customer_name": "Ramesh Kumar Mishra",
            "mobile": "9876501101",
            "outstanding_amount": 1450,
            "credit_limit": 10000,
            "payment_history": [
                {"date": "2026-05-10", "type": "Purchase", "description": "Atta, Dal & Spices", "amount": 1250},
                {"date": "2026-05-15", "type": "Payment", "description": "Cash Settle Part", "amount": 800},
                {"date": "2026-06-01", "type": "Purchase", "description": "Biscuits & Tea Box", "amount": 1000}
            ]
        },
        {
            "customer_name": "Mahendra Singh (Pradhan Ji)",
            "mobile": "9876501102",
            "outstanding_amount": 3200,
            "credit_limit": 20000,
            "payment_history": [
                {"date": "2026-05-20", "type": "Purchase", "description": "Monthly Staples Basket", "amount": 3200}
            ]
        },
        {
            "customer_name": "Suresh Chandra Prasad",
            "mobile": "9876501103",
            "outstanding_amount": 0,
            "credit_limit": 10000,
            "payment_history": [
                {"date": "2026-04-12", "type": "Purchase", "description": "Dairy & Mustard Oils", "amount": 1500},
                {"date": "2026-04-20", "type": "Payment", "description": "Full Account Settle", "amount": 1500}
            ]
        },
        {
            "customer_name": "Gita Devi",
            "mobile": "9876501104",
            "outstanding_amount": 420,
            "credit_limit": 8000,
            "payment_history": [
                {"date": "2026-06-05", "type": "Purchase", "description": "Personal Care & Vim Bar", "amount": 420}
            ]
        },
        {
            "customer_name": "Rajeshwar Paswan",
            "mobile": "9876501105",
            "outstanding_amount": 1200,
            "credit_limit": 12000,
            "payment_history": [
                {"date": "2026-05-28", "type": "Purchase", "description": "Staples & Grains", "amount": 2200},
                {"date": "2026-06-02", "type": "Payment", "description": "UPI Pay", "amount": 1000}
            ]
        }
    ]
    
    orders_db = [
        {
            "order_id": 1001,
            "customer_name": "Ramesh Kumar Mishra",
            "mobile": "9876501101",
            "address": "Mishra Tola, Near Shiv Temple",
            "village": "Rampur",
            "pincode": "843101",
            "items": "Ashirvaad Atta x1, Fortune Oil x2",
            "total_amount": 610,
            "payment_method": "Khata Credit",
            "status": "Delivered",
            "delivery_boy_id": 1,
            "date": "2026-06-12 11:30"
        },
        {
            "order_id": 1002,
            "customer_name": "Vikram Singh",
            "mobile": "9876501110",
            "address": "House 45, Main Market Road",
            "village": "Laxmipur",
            "pincode": "843102",
            "items": "Red Label Tea x1, Marie Biscuits x4",
            "total_amount": 550,
            "payment_method": "UPI",
            "status": "Out for Delivery",
            "delivery_boy_id": 1,
            "date": "2026-06-13 16:45"
        },
        {
            "order_id": 1003,
            "customer_name": "Gita Devi",
            "mobile": "9876501104",
            "address": "Devi Sthan, Ward 4",
            "village": "Rampur",
            "pincode": "843101",
            "items": "Patanjali Toothpaste x2, Vim Liquid x1",
            "total_amount": 340,
            "payment_method": "Cash on Delivery",
            "status": "Pending",
            "delivery_boy_id": 2,
            "date": "2026-06-14 09:15"
        },
        {
            "order_id": 1004,
            "customer_name": "Sanjay Ojha",
            "mobile": "9876501115",
            "address": "Ojha Gali, Near High School",
            "village": "Fatehpur",
            "pincode": "843105",
            "items": "Fortune Oil x2, Tata Salt x5",
            "total_amount": 490,
            "payment_method": "Razorpay",
            "status": "Pending",
            "delivery_boy_id": None,
            "date": "2026-06-14 14:02"
        }
    ]
    
    whatsapp_logs_db.clear()
    audit_logs_db.clear()
    
    sales_history.clear()
    for i in range(31):
        log_date = (base_date + timedelta(days=i)).strftime("%Y-%m-%d")
        daily_sales = random.randint(3200, 8500)
        daily_orders = random.randint(8, 22)
        daily_profit = int(daily_sales * random.uniform(0.18, 0.26))
        sales_history.append({
            "date": log_date,
            "revenue": daily_sales,
            "profit": daily_profit,
            "orders": daily_orders
        })
        
    log_audit("System Reset", "ERP platform reset back to default preset profiles.")
    flash("System databases successfully reset to factory defaults!", "success")
    return redirect(url_for('admin', tab='settings'))

if __name__ == '__main__':
    print("Grocify is starting up...")
    print("Local URL: http://127.0.0.1:5001")
    app.run(debug=True, host='127.0.0.1', port=5001)
