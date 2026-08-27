import sqlite3

# -------------------------
# DATABASE CONNECTION
# -------------------------

DATABASE = "sih_farmers.db"

connection = sqlite3.connect(DATABASE)

cursor = connection.cursor()


# -------------------------
# 1. USERS TABLE
# -------------------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL,
    is_active INTEGER DEFAULT 1,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
)
""")


# -------------------------
# 2. FARMERS TABLE
# -------------------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS farmers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    full_name TEXT NOT NULL,
    phone TEXT,
    village TEXT,
    taluka TEXT,
    district TEXT,
    state TEXT,
    pincode TEXT,
    farm_size REAL,
    fpo_member INTEGER DEFAULT 0,
    fpo_name TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id)
        REFERENCES users(id)
)
""")


# -------------------------
# 3. CROPS TABLE
# -------------------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS crops (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    category TEXT,
    unit TEXT,
    description TEXT
)
""")


# -------------------------
# 4. FARMER CROPS TABLE
# -------------------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS farmer_crops (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    farmer_id INTEGER NOT NULL,
    crop_id INTEGER NOT NULL,
    variety TEXT,
    area REAL,
    sowing_date TEXT,
    expected_harvest_date TEXT,
    expected_quantity REAL,

    FOREIGN KEY (farmer_id)
        REFERENCES farmers(id),

    FOREIGN KEY (crop_id)
        REFERENCES crops(id)
)
""")


# -------------------------
# 5. MARKETS TABLE
# -------------------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS markets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    district TEXT,
    state TEXT,
    address TEXT,
    latitude REAL,
    longitude REAL
)
""")


# -------------------------
# 6. MARKET PRICES TABLE
# -------------------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS market_prices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    crop_id INTEGER NOT NULL,
    market_id INTEGER NOT NULL,
    price_min REAL,
    price_max REAL,
    modal_price REAL,
    arrival_quantity REAL,
    arrival_unit TEXT,
    price_date TEXT NOT NULL,
    source TEXT,

    FOREIGN KEY (crop_id)
        REFERENCES crops(id),

    FOREIGN KEY (market_id)
        REFERENCES markets(id)
)
""")


# -------------------------
# 7. BUYERS TABLE
# -------------------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS buyers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    company_name TEXT NOT NULL,
    contact_person TEXT,
    phone TEXT,
    email TEXT,
    address TEXT,
    district TEXT,
    state TEXT,
    business_type TEXT,
    is_verified INTEGER DEFAULT 0,
    rating REAL DEFAULT 0,
    total_transactions INTEGER DEFAULT 0,

    FOREIGN KEY (user_id)
        REFERENCES users(id)
)
""")


# -------------------------
# 8. LOTS TABLE
# -------------------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS lots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    farmer_id INTEGER NOT NULL,
    crop_id INTEGER NOT NULL,
    lot_number TEXT NOT NULL UNIQUE,
    variety TEXT,
    quantity REAL NOT NULL,
    unit TEXT NOT NULL,
    harvest_date TEXT,
    quality_grade TEXT,
    quality_score REAL,
    moisture REAL,
    foreign_matter REAL,
    damage_percentage REAL,
    expected_price REAL,
    location TEXT,
    description TEXT,
    image TEXT,
    status TEXT DEFAULT 'available',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (farmer_id)
        REFERENCES farmers(id),

    FOREIGN KEY (crop_id)
        REFERENCES crops(id)
)
""")


# -------------------------
# 9. BUYER REQUIREMENTS TABLE
# -------------------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS buyer_requirements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    buyer_id INTEGER NOT NULL,
    crop_id INTEGER NOT NULL,
    required_quantity REAL NOT NULL,
    unit TEXT NOT NULL,
    min_quality_grade TEXT,
    max_price REAL,
    delivery_location TEXT,
    required_by TEXT,
    description TEXT,
    status TEXT DEFAULT 'open',

    FOREIGN KEY (buyer_id)
        REFERENCES buyers(id),

    FOREIGN KEY (crop_id)
        REFERENCES crops(id)
)
""")


# -------------------------
# 10. OFFERS TABLE
# -------------------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS offers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lot_id INTEGER NOT NULL,
    buyer_id INTEGER NOT NULL,
    farmer_id INTEGER NOT NULL,
    offered_price REAL NOT NULL,
    quantity REAL NOT NULL,
    message TEXT,
    status TEXT DEFAULT 'pending',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    expires_at TEXT,

    FOREIGN KEY (lot_id)
        REFERENCES lots(id),

    FOREIGN KEY (buyer_id)
        REFERENCES buyers(id),

    FOREIGN KEY (farmer_id)
        REFERENCES farmers(id)
)
""")


# -------------------------
# 11. TRANSACTIONS TABLE
# -------------------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_number TEXT NOT NULL UNIQUE,
    offer_id INTEGER NOT NULL,
    farmer_id INTEGER NOT NULL,
    buyer_id INTEGER NOT NULL,
    lot_id INTEGER NOT NULL,
    quantity REAL NOT NULL,
    price_per_unit REAL NOT NULL,
    total_amount REAL NOT NULL,
    transaction_date TEXT DEFAULT CURRENT_TIMESTAMP,
    delivery_status TEXT DEFAULT 'pending',
    transaction_status TEXT DEFAULT 'pending',

    FOREIGN KEY (offer_id)
        REFERENCES offers(id),

    FOREIGN KEY (farmer_id)
        REFERENCES farmers(id),

    FOREIGN KEY (buyer_id)
        REFERENCES buyers(id),

    FOREIGN KEY (lot_id)
        REFERENCES lots(id)
)
""")


# -------------------------
# 12. TRANSPORT PROVIDERS
# -------------------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS transport_providers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone TEXT,
    vehicle_type TEXT,
    vehicle_number TEXT,
    capacity REAL,
    price_per_km REAL,
    rating REAL DEFAULT 0,
    is_verified INTEGER DEFAULT 0
)
""")


# -------------------------
# 13. TRANSPORT REQUESTS
# -------------------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS transport_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_id INTEGER NOT NULL,
    provider_id INTEGER,
    pickup_location TEXT,
    delivery_location TEXT,
    distance REAL,
    transport_cost REAL,
    pickup_date TEXT,
    status TEXT DEFAULT 'requested',

    FOREIGN KEY (transaction_id)
        REFERENCES transactions(id),

    FOREIGN KEY (provider_id)
        REFERENCES transport_providers(id)
)
""")


# -------------------------
# 14. PAYMENTS TABLE
# -------------------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_id INTEGER NOT NULL,
    amount REAL NOT NULL,
    payment_method TEXT,
    payment_status TEXT DEFAULT 'pending',
    payment_date TEXT,
    reference_number TEXT,

    FOREIGN KEY (transaction_id)
        REFERENCES transactions(id)
)
""")


# -------------------------
# 15. RATINGS TABLE
# -------------------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS ratings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_id INTEGER NOT NULL,
    farmer_id INTEGER NOT NULL,
    buyer_id INTEGER NOT NULL,
    rating REAL NOT NULL,
    review TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (transaction_id)
        REFERENCES transactions(id),

    FOREIGN KEY (farmer_id)
        REFERENCES farmers(id),

    FOREIGN KEY (buyer_id)
        REFERENCES buyers(id)
)
""")


# -------------------------
# 16. DISPUTES TABLE
# -------------------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS disputes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_id INTEGER NOT NULL,
    raised_by TEXT NOT NULL,
    reason TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'open',
    resolution TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    resolved_at TEXT,

    FOREIGN KEY (transaction_id)
        REFERENCES transactions(id)
)
""")


# -------------------------
# 17. PRICE PREDICTIONS TABLE
# -------------------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS price_predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    crop_id INTEGER NOT NULL,
    market_id INTEGER NOT NULL,
    predicted_price REAL NOT NULL,
    prediction_date TEXT NOT NULL,
    target_date TEXT NOT NULL,
    confidence REAL,
    model_name TEXT,

    FOREIGN KEY (crop_id)
        REFERENCES crops(id),

    FOREIGN KEY (market_id)
        REFERENCES markets(id)
)
""")


# -------------------------
# SAVE CHANGES
# -------------------------

connection.commit()

print("SIH database created successfully!")
print("All tables created successfully!")


# -------------------------
# CLOSE CONNECTION
# -------------------------

connection.close()