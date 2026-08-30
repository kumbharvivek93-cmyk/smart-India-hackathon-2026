from extensions import db
from datetime import datetime ,timedelta


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(30),
        nullable=False
    )

    email = db.Column(
        db.String(100),
        nullable=False,
        unique=True
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )

    role = db.Column(
        db.String(20),
        nullable=False
    )

    is_active = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )
class Farmer(db.Model):
    __tablename__ = "farmers"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15))
    village = db.Column(db.String(100))
    taluka = db.Column(db.String(100))
    district = db.Column(db.String(100))
    state = db.Column(db.String(100))
    pincode = db.Column(db.String(10))

    farm_size = db.Column(db.Float)
    farm_size_unit = db.Column(db.String(20))

    fpo_member = db.Column(
        db.Boolean,
        default=False,
        nullable=False
    )

    fpo_name = db.Column(
        db.String(150),
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

class Crop(db.Model):
    __tablename__ = "crops"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        nullable=False,
        unique=True
    )

    category = db.Column(
        db.String(50)
    )

    unit = db.Column(
        db.String(20)
    )

    description = db.Column(
        db.Text
    )

class FarmerCrop(db.Model):
    __tablename__ = "farmer_crops"

    id = db.Column(db.Integer, primary_key=True)

    farmer_id = db.Column(
        db.Integer,
        db.ForeignKey("farmers.id"),
        nullable=False
    )

    crop_id = db.Column(
        db.Integer,
        db.ForeignKey("crops.id"),
        nullable=False
    )

    variety = db.Column(db.String(100))

    area = db.Column(db.Float)
    area_unit = db.Column(db.String(20))

    sowing_date = db.Column(db.Date)

    expected_harvest_date = db.Column(db.Date)

    expected_quantity = db.Column(db.Float)

class MarketPrice(db.Model):
    __tablename__ = "market_prices"

    id = db.Column(db.Integer, primary_key=True)

    crop_id = db.Column(
        db.Integer,
        db.ForeignKey("crops.id"),
        nullable=False
    )

    market_name = db.Column(db.String(150), nullable=False)
    district = db.Column(db.String(100))
    state = db.Column(db.String(100))

    price_min = db.Column(db.Float)
    price_max = db.Column(db.Float)
    modal_price = db.Column(db.Float)

    arrival_quantity = db.Column(db.Float)
    arrival_unit = db.Column(db.String(20))

    date = db.Column(db.Date, nullable=False)

    source = db.Column(db.String(100))

    crop = db.relationship(
        "Crop",
        backref="market_prices"
    )

class Buyer(db.Model):
    __tablename__ = "buyers"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    company_name = db.Column(db.String(150), nullable=False)
    contact_person = db.Column(db.String(100))
    phone = db.Column(db.String(15))
    email = db.Column(db.String(100))
    address = db.Column(db.String(255))
    village_city = db.Column(db.String(100))
    district = db.Column(db.String(100))
    state = db.Column(db.String(100))

    business_type = db.Column(db.String(100))

    is_verified = db.Column(
        db.Boolean,
        default=False,
        nullable=False
    )

    verification_date = db.Column(db.DateTime)

    rating = db.Column(
        db.Float,
        default=0.0,
        nullable=False
    )

    total_transactions = db.Column(
        db.Integer,
        default=0,
        nullable=False
    )

    user = db.relationship(
        "User",
        backref="buyer_profile"
    )

class Lot(db.Model):
    __tablename__ = "lots"

    id = db.Column(db.Integer, primary_key=True)

    farmer_id = db.Column(
        db.Integer,
        db.ForeignKey("farmers.id"),
        nullable=False
    )

    crop_id = db.Column(
        db.Integer,
        db.ForeignKey("crops.id"),
        nullable=False
    )

    lot_number = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )

    variety = db.Column(db.String(100))

    quantity = db.Column(
        db.Float,
        nullable=False
    )

    unit = db.Column(
        db.String(20),
        nullable=False
    )

    harvest_date = db.Column(db.Date)

    quality_grade = db.Column(db.String(20))

    quality_score = db.Column(db.Float)

    moisture = db.Column(db.Float)

    foreign_matter = db.Column(db.Float)

    damage_percentage = db.Column(db.Float)

    expected_price = db.Column(db.Float)

    location = db.Column(db.String(255))

    description = db.Column(db.Text)

    image = db.Column(db.String(255))

    status = db.Column(
        db.String(30),
        default="available",
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    farmer = db.relationship(
        "Farmer",
        backref="lots"
    )

    crop = db.relationship(
        "Crop",
        backref="lots"
    )

class BuyerRequirement(db.Model):
    __tablename__ = "buyer_requirements"

    id = db.Column(db.Integer, primary_key=True)

    buyer_id = db.Column(
        db.Integer,
        db.ForeignKey("buyers.id"),
        nullable=False
    )

    crop_id = db.Column(
        db.Integer,
        db.ForeignKey("crops.id"),
        nullable=False
    )

    required_quantity = db.Column(
        db.Float,
        nullable=False
    )

    unit = db.Column(
        db.String(20),
        nullable=False
    )

    min_quality_grade = db.Column(
        db.String(20)
    )

    max_price = db.Column(
        db.Float
    )

    delivery_location = db.Column(
        db.String(255)
    )

    required_by = db.Column(
        db.Date
    )

    description = db.Column(
        db.Text
    )

    status = db.Column(
        db.String(30),
        default="open",
        nullable=False
    )

    buyer = db.relationship(
        "Buyer",
        backref="requirements"
    )

    crop = db.relationship(
        "Crop",
        backref="buyer_requirements"
    )

class Offer(db.Model):
    __tablename__ = "offers"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    lot_id = db.Column(
        db.Integer,
        db.ForeignKey("lots.id"),
        nullable=False
    )

    buyer_id = db.Column(
        db.Integer,
        db.ForeignKey("buyers.id"),
        nullable=False
    )

    farmer_id = db.Column(
        db.Integer,
        db.ForeignKey("farmers.id"),
        nullable=False
    )

    offered_price = db.Column(
        db.Float,
        nullable=False
    )

    quantity = db.Column(
        db.Float,
        nullable=False
    )

    message = db.Column(
        db.Text
    )

    status = db.Column(
        db.String(30),
        default="pending",
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    expires_at = db.Column(
        db.DateTime
    )

    # Relationships
    lot = db.relationship(
        "Lot",
        backref="offers"
    )

    buyer = db.relationship(
        "Buyer",
        backref="offers"
    )

    farmer = db.relationship(
        "Farmer",
        backref="received_offers"
    )	

class Transaction(db.Model):
    __tablename__ = "transactions"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    transaction_number = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )

    offer_id = db.Column(
        db.Integer,
        db.ForeignKey("offers.id"),
        nullable=False
    )

    farmer_id = db.Column(
        db.Integer,
        db.ForeignKey("farmers.id"),
        nullable=False
    )

    buyer_id = db.Column(
        db.Integer,
        db.ForeignKey("buyers.id"),
        nullable=False
    )

    lot_id = db.Column(
        db.Integer,
        db.ForeignKey("lots.id"),
        nullable=False
    )

    quantity = db.Column(
        db.Float,
        nullable=False
    )

    price_per_unit = db.Column(
        db.Float,
        nullable=False
    )

    total_amount = db.Column(
        db.Float,
        nullable=False
    )

    transaction_date = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    delivery_status = db.Column(
        db.String(30),
        default="pending",
        nullable=False
    )

    transaction_status = db.Column(
        db.String(30),
        default="pending",
        nullable=False
    )

    # Relationships
    offer = db.relationship(
        "Offer",
        backref="transaction"
    )

    farmer = db.relationship(
        "Farmer",
        backref="transactions"
    )

    buyer = db.relationship(
        "Buyer",
        backref="transactions"
    )

    lot = db.relationship(
        "Lot",
        backref="transactions"
    )
class TransportProvider(db.Model):
    __tablename__ = "transport_providers"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    provider_name = db.Column(
        db.String(150),
        nullable=False
    )

    phone = db.Column(
        db.String(15),
        nullable=False
    )

    vehicle_type = db.Column(
        db.String(50),
        nullable=False
    )

    vehicle_number = db.Column(
        db.String(30),
        unique=True,
        nullable=False
    )

    capacity = db.Column(
        db.Float,
        nullable=False
    )

    cost_per_km = db.Column(
        db.Float,
        nullable=False
    )

    rating = db.Column(
        db.Float,
        default=0.0,
        nullable=False
    )

    is_available = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

class TransportRequest(db.Model):
    __tablename__ = "transport_requests"

    id = db.Column(db.Integer, primary_key=True)

    transaction_id = db.Column(
        db.Integer,
        db.ForeignKey("transactions.id"),
        nullable=False
    )

    provider_id = db.Column(
        db.Integer,
        db.ForeignKey("transport_providers.id"),
        nullable=False
    )

    pickup_location = db.Column(
        db.String(255),
        nullable=False
    )

    delivery_location = db.Column(
        db.String(255),
        nullable=False
    )

    distance_km = db.Column(db.Float)

    estimated_cost = db.Column(db.Float)

    request_date = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    status = db.Column(
        db.String(30),
        default="requested",
        nullable=False
    )

    transaction = db.relationship(
        "Transaction",
        backref="transport_requests"
    )

    provider = db.relationship(
        "TransportProvider",
        backref="transport_requests"
    )

class StorageFacility(db.Model):
    __tablename__ = "storage_facilities"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(
        db.String(150),
        nullable=False
    )

    location = db.Column(
        db.String(255),
        nullable=False
    )

    district = db.Column(
        db.String(100),
        nullable=False
    )

    storage_type = db.Column(
        db.String(50),
        nullable=False
    )

    total_capacity = db.Column(
        db.Float,
        nullable=False
    )

    available_capacity = db.Column(
        db.Float,
        nullable=False
    )

    cost_per_quintal_day = db.Column(
        db.Float,
        nullable=False
    )

    phone = db.Column(
        db.String(15)
    )

    rating = db.Column(
        db.Float,
        default=0.0,
        nullable=False
    )

class Payment(db.Model):
    __tablename__ = "payments"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    transaction_id = db.Column(
        db.Integer,
        db.ForeignKey("transactions.id"),
        nullable=False
    )

    amount = db.Column(
        db.Float,
        nullable=False
    )

    payment_method = db.Column(
        db.String(50)
    )

    transaction_reference = db.Column(
        db.String(100),
        unique=True
    )

    payment_date = db.Column(
        db.DateTime
    )

    status = db.Column(
        db.String(30),
        default="pending",
        nullable=False
    )

    notes = db.Column(
        db.Text
    )

    transaction = db.relationship(
        "Transaction",
        backref="payments"
    )

class Dispute(db.Model):
    __tablename__ = "disputes"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    transaction_id = db.Column(
        db.Integer,
        db.ForeignKey("transactions.id"),
        nullable=False
    )

    raised_by = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    category = db.Column(
        db.String(50),
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=False
    )

    status = db.Column(
        db.String(30),
        default="open",
        nullable=False
    )

    resolution = db.Column(
        db.Text
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    resolved_at = db.Column(
        db.DateTime
    )

    # Relationships
    transaction = db.relationship(
        "Transaction",
        backref="disputes"
    )

    user = db.relationship(
        "User",
        backref="disputes"
    )
class Rating(db.Model):
    __tablename__ = "ratings"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    transaction_id = db.Column(
        db.Integer,
        db.ForeignKey("transactions.id"),
        nullable=False
    )

    farmer_id = db.Column(
        db.Integer,
        db.ForeignKey("farmers.id"),
        nullable=False
    )

    buyer_id = db.Column(
        db.Integer,
        db.ForeignKey("buyers.id"),
        nullable=False
    )

    rating = db.Column(
        db.Integer,
        nullable=False
    )

    review = db.Column(
        db.Text
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # Relationships
    transaction = db.relationship(
        "Transaction",
        backref="ratings"
    )

    farmer = db.relationship(
        "Farmer",
        backref="ratings"
    )

    buyer = db.relationship(
        "Buyer",
        backref="ratings"
    )

class PricePrediction(db.Model):
    __tablename__ = "price_predictions"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    crop_id = db.Column(
        db.Integer,
        db.ForeignKey("crops.id"),
        nullable=False
    )

    market_name = db.Column(
        db.String(150),
        nullable=False
    )

    current_price = db.Column(
        db.Float,
        nullable=False
    )

    predicted_price = db.Column(
        db.Float,
        nullable=False
    )

    prediction_days = db.Column(
        db.Integer,
        nullable=False
    )

    trend = db.Column(
        db.String(30)
    )

    recommendation = db.Column(
        db.String(255)
    )

    confidence = db.Column(
        db.Float
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    crop = db.relationship(
        "Crop",
        backref="price_predictions"
    )
