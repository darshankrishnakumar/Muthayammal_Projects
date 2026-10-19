import os
import io
import csv
import random
import urllib.parse
from datetime import datetime, timezone, timedelta
from flask import Flask, request, jsonify, Response, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import pymysql
from ml_engine import MLEngine

app = Flask(__name__)
CORS(app)

FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))

@app.route('/')
def serve_index():
    return send_from_directory(FRONTEND_DIR, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    target = os.path.join(FRONTEND_DIR, path)
    if os.path.exists(target) and not os.path.isdir(target):
        return send_from_directory(FRONTEND_DIR, path)
    return jsonify({'error': 'Not found'}), 404


# Database Configuration (supports MySQL with automatic local SQLite fallback)
default_mysql = 'mysql+pymysql://root:password@localhost/stock_management_db'
db_url = os.environ.get('DATABASE_URL', default_mysql)

sqlite_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'stock_management.db')
sqlite_uri = f'sqlite:///{sqlite_path}'

if db_url.startswith('mysql'):
    try:
        parsed = urllib.parse.urlparse(db_url)
        conn = pymysql.connect(
            host=parsed.hostname or 'localhost',
            port=parsed.port or 3306,
            user=parsed.username or 'root',
            password=parsed.password or '',
            database=parsed.path.lstrip('/') or None,
            connect_timeout=1
        )
        conn.close()
        app.config['SQLALCHEMY_DATABASE_URI'] = db_url
        print(f"Connected to MySQL database: {parsed.path.lstrip('/')}")
    except Exception as e:
        print(f"MySQL unavailable ({e}). Falling back to local SQLite: {sqlite_path}")
        app.config['SQLALCHEMY_DATABASE_URI'] = sqlite_uri
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

def now_utc():
    return datetime.now(timezone.utc)

# ─── MODELS ──────────────────────────────────────────────────────────────────

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=now_utc)
    products = db.relationship('Product', backref='category', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'product_count': len(self.products) if self.products else 0
        }

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    sku = db.Column(db.String(50), unique=True, nullable=False)
    price = db.Column(db.Float, nullable=False)
    cost_price = db.Column(db.Float, default=0.0)
    quantity = db.Column(db.Integer, default=0)
    min_stock = db.Column(db.Integer, default=10)
    reorder_point = db.Column(db.Integer, default=15)
    lead_time_days = db.Column(db.Integer, default=3)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    description = db.Column(db.Text)
    barcode = db.Column(db.String(50), unique=True, nullable=True)
    rfid_tag = db.Column(db.String(50), unique=True, nullable=True)
    location_aisle = db.Column(db.String(50), default='Aisle A-01')
    created_at = db.Column(db.DateTime, default=now_utc)
    updated_at = db.Column(db.DateTime, default=now_utc, onupdate=now_utc)

    def to_dict(self):
        rop = self.reorder_point or (self.min_stock + 5)
        status = 'Out of Stock' if self.quantity == 0 else ('Low Stock' if self.quantity <= self.min_stock else 'In Stock')
        return {
            'id': self.id,
            'name': self.name,
            'sku': self.sku,
            'price': self.price,
            'cost_price': self.cost_price or round(self.price * 0.65, 2),
            'quantity': self.quantity,
            'min_stock': self.min_stock,
            'reorder_point': rop,
            'lead_time_days': self.lead_time_days or 3,
            'category': self.category.name if self.category else 'Uncategorized',
            'category_id': self.category_id,
            'description': self.description,
            'barcode': self.barcode or f"8901234{self.id:05d}",
            'rfid_tag': self.rfid_tag or f"EPC-00{self.id:04d}",
            'location_aisle': self.location_aisle or 'Zone 1',
            'status': status,
            'valuation': round(self.quantity * self.price, 2),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Supplier(db.Model):
    __tablename__ = 'suppliers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    contact_person = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(50))
    address = db.Column(db.String(255))
    lead_time_days = db.Column(db.Integer, default=5)
    rating = db.Column(db.Float, default=4.8)
    payment_terms = db.Column(db.String(50), default='Net 30')
    created_at = db.Column(db.DateTime, default=now_utc)
    purchase_orders = db.relationship('PurchaseOrder', backref='supplier', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'contact_person': self.contact_person,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'lead_time_days': self.lead_time_days,
            'rating': self.rating,
            'payment_terms': self.payment_terms,
            'po_count': len(self.purchase_orders) if self.purchase_orders else 0
        }

class PurchaseOrder(db.Model):
    __tablename__ = 'purchase_orders'
    id = db.Column(db.Integer, primary_key=True)
    po_number = db.Column(db.String(50), unique=True, nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False)
    total_amount = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(30), default='ORDERED') # PENDING, ORDERED, IN_TRANSIT, RECEIVED, CANCELLED
    ordered_date = db.Column(db.DateTime, default=now_utc)
    expected_delivery_date = db.Column(db.DateTime)
    received_date = db.Column(db.DateTime, nullable=True)
    notes = db.Column(db.Text)
    items = db.relationship('PurchaseOrderItem', backref='purchase_order', cascade='all, delete-orphan', lazy=True)
    shipment = db.relationship('Shipment', backref='purchase_order', uselist=False, lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'po_number': self.po_number,
            'supplier_id': self.supplier_id,
            'supplier_name': self.supplier.name if self.supplier else 'Unknown',
            'total_amount': self.total_amount,
            'status': self.status,
            'ordered_date': self.ordered_date.isoformat() if self.ordered_date else None,
            'expected_delivery_date': self.expected_delivery_date.isoformat() if self.expected_delivery_date else None,
            'received_date': self.received_date.isoformat() if self.received_date else None,
            'notes': self.notes,
            'item_count': len(self.items) if self.items else 0,
            'items': [item.to_dict() for item in self.items] if self.items else [],
            'has_shipment': bool(self.shipment)
        }

class PurchaseOrderItem(db.Model):
    __tablename__ = 'purchase_order_items'
    id = db.Column(db.Integer, primary_key=True)
    po_id = db.Column(db.Integer, db.ForeignKey('purchase_orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity_ordered = db.Column(db.Integer, nullable=False)
    unit_cost = db.Column(db.Float, nullable=False)
    total_cost = db.Column(db.Float, nullable=False)
    product = db.relationship('Product')

    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'product_name': self.product.name if self.product else 'Unknown',
            'sku': self.product.sku if self.product else 'N/A',
            'quantity_ordered': self.quantity_ordered,
            'unit_cost': self.unit_cost,
            'total_cost': self.total_cost
        }

class Shipment(db.Model):
    __tablename__ = 'shipments'
    id = db.Column(db.Integer, primary_key=True)
    tracking_number = db.Column(db.String(80), unique=True, nullable=False)
    po_id = db.Column(db.Integer, db.ForeignKey('purchase_orders.id'), nullable=True)
    carrier = db.Column(db.String(80), default='DHL Freight / BlueDart')
    origin = db.Column(db.String(100), default='Central Logistics Hub')
    destination = db.Column(db.String(100), default='Main Organization Warehouse')
    current_location = db.Column(db.String(100), default='Regional Sort Facility')
    status = db.Column(db.String(30), default='IN_TRANSIT') # PICKED_UP, IN_TRANSIT, OUT_FOR_DELIVERY, DELIVERED
    estimated_delivery = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=now_utc)
    updated_at = db.Column(db.DateTime, default=now_utc, onupdate=now_utc)

    def to_dict(self):
        return {
            'id': self.id,
            'tracking_number': self.tracking_number,
            'po_id': self.po_id,
            'po_number': self.purchase_order.po_number if self.purchase_order else 'Manual Cargo',
            'carrier': self.carrier,
            'origin': self.origin,
            'destination': self.destination,
            'current_location': self.current_location,
            'status': self.status,
            'estimated_delivery': self.estimated_delivery.isoformat() if self.estimated_delivery else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Sale(db.Model):
    __tablename__ = 'sales'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity_sold = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    sale_date = db.Column(db.DateTime, default=now_utc)
    customer_name = db.Column(db.String(100), default='Walk-in Retail')
    payment_method = db.Column(db.String(50), default='UPI / Card')
    product = db.relationship('Product', backref='sales')

    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'product_name': self.product.name if self.product else 'Unknown Product',
            'sku': self.product.sku if self.product else 'N/A',
            'quantity_sold': self.quantity_sold,
            'unit_price': self.unit_price,
            'total_amount': self.total_amount,
            'sale_date': self.sale_date.isoformat() if self.sale_date else None,
            'customer_name': self.customer_name,
            'payment_method': self.payment_method
        }

class StockMovement(db.Model):
    __tablename__ = 'stock_movements'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    movement_type = db.Column(db.String(20), nullable=False)  # IN, OUT, AUDIT_ADJUSTMENT
    quantity = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.String(200))
    device_source = db.Column(db.String(100), default='ERP Terminal')
    created_at = db.Column(db.DateTime, default=now_utc)
    product = db.relationship('Product', backref='movements')

    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'product_name': self.product.name if self.product else 'Unknown Product',
            'sku': self.product.sku if self.product else 'N/A',
            'movement_type': self.movement_type,
            'quantity': self.quantity,
            'reason': self.reason,
            'device_source': self.device_source,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class IoTDevice(db.Model):
    __tablename__ = 'iot_devices'
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.String(50), unique=True, nullable=False)
    device_name = db.Column(db.String(100), nullable=False)
    device_type = db.Column(db.String(50), nullable=False) # BARCODE_SCANNER, RFID_GATEWAY, WEIGHT_SCALE, SENSOR_HUB
    status = db.Column(db.String(20), default='ONLINE') # ONLINE, OFFLINE, BUSY
    battery_level = db.Column(db.Integer, default=95)
    ip_address = db.Column(db.String(50), default='192.168.1.150')
    location_area = db.Column(db.String(100), default='Dock 1 / Inbound Gate')
    last_ping = db.Column(db.DateTime, default=now_utc)

    def to_dict(self):
        return {
            'id': self.id,
            'device_id': self.device_id,
            'device_name': self.device_name,
            'device_type': self.device_type,
            'status': self.status,
            'battery_level': self.battery_level,
            'ip_address': self.ip_address,
            'location_area': self.location_area,
            'last_ping': self.last_ping.isoformat() if self.last_ping else None
        }

# ─── API ROUTES ──────────────────────────────────────────────────────────────

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'running',
        'service': 'Enterprise Stock Management System (SMS) API',
        'version': '2.0-Enterprise',
        'database': 'SQLite' if 'sqlite' in app.config['SQLALCHEMY_DATABASE_URI'] else 'MySQL'
    })

# 1. Dashboard Executive Summary
@app.route('/api/dashboard', methods=['GET'])
def dashboard():
    products = Product.query.all()
    total_products = len(products)
    low_stock_products = [p for p in products if p.quantity <= p.min_stock]
    out_of_stock = [p for p in products if p.quantity == 0]
    
    total_valuation = sum(p.quantity * p.price for p in products)
    total_cost_valuation = sum(p.quantity * (p.cost_price or p.price * 0.65) for p in products)
    
    total_sales_result = db.session.query(db.func.sum(Sale.total_amount)).scalar()
    total_sales = float(total_sales_result or 0)
    
    total_categories = Category.query.count()
    total_suppliers = Supplier.query.count()
    active_shipments = Shipment.query.filter(Shipment.status.in_(['PICKED_UP', 'IN_TRANSIT', 'OUT_FOR_DELIVERY'])).count()
    pending_pos = PurchaseOrder.query.filter(PurchaseOrder.status.in_(['ORDERED', 'PENDING', 'IN_TRANSIT'])).count()

    # Sales last 7 days
    weekly_sales = []
    now = now_utc()
    for i in range(6, -1, -1):
        day = now - timedelta(days=i)
        start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        end = day.replace(hour=23, minute=59, second=59, microsecond=999999)
        amount = db.session.query(db.func.sum(Sale.total_amount)).filter(
            Sale.sale_date.between(start, end)
        ).scalar() or 0
        weekly_sales.append({'date': start.strftime('%a'), 'amount': round(float(amount), 2)})

    return jsonify({
        'total_products': total_products,
        'low_stock_count': len(low_stock_products),
        'out_of_stock_count': len(out_of_stock),
        'total_valuation': round(total_valuation, 2),
        'total_cost_valuation': round(total_cost_valuation, 2),
        'gross_margin_potential': round(total_valuation - total_cost_valuation, 2),
        'total_sales': round(total_sales, 2),
        'total_categories': total_categories,
        'total_suppliers': total_suppliers,
        'active_shipments': active_shipments,
        'pending_pos': pending_pos,
        'weekly_sales': weekly_sales,
        'low_stock_items': [p.to_dict() for p in low_stock_products[:5]]
    })

# 2. Product Catalog CRUD
@app.route('/api/products', methods=['GET'])
def get_products():
    search = request.args.get('search', '').strip()
    category_id = request.args.get('category_id')
    status_filter = request.args.get('status')
    
    query = Product.query
    if search:
        query = query.filter((Product.name.ilike(f'%{search}%')) | (Product.sku.ilike(f'%{search}%')) | (Product.barcode.ilike(f'%{search}%')))
    if category_id:
        query = query.filter(Product.category_id == category_id)
        
    products = query.order_by(Product.name.asc()).all()
    
    if status_filter == 'Low Stock':
        products = [p for p in products if p.quantity <= p.min_stock and p.quantity > 0]
    elif status_filter == 'Out of Stock':
        products = [p for p in products if p.quantity == 0]
        
    return jsonify([p.to_dict() for p in products])

@app.route('/api/products/<int:pid>', methods=['GET'])
def get_product(pid):
    p = Product.query.get_or_404(pid)
    return jsonify(p.to_dict())

@app.route('/api/products', methods=['POST'])
def add_product():
    data = request.json or {}
    if not data.get('name') or not data.get('sku') or data.get('price') is None:
        return jsonify({'error': 'Name, SKU, and Price are mandatory'}), 400
        
    product = Product(
        name=data['name'],
        sku=data['sku'].upper(),
        price=float(data['price']),
        cost_price=float(data.get('cost_price', float(data['price']) * 0.65)),
        quantity=int(data.get('quantity', 0)),
        min_stock=int(data.get('min_stock', 10)),
        reorder_point=int(data.get('reorder_point', int(data.get('min_stock', 10)) + 5)),
        lead_time_days=int(data.get('lead_time_days', 3)),
        category_id=data.get('category_id'),
        description=data.get('description', ''),
        barcode=data.get('barcode'),
        rfid_tag=data.get('rfid_tag'),
        location_aisle=data.get('location_aisle', 'Aisle A-01')
    )
    db.session.add(product)
    db.session.flush()

    if product.quantity > 0:
        mv = StockMovement(
            product_id=product.id,
            movement_type='IN',
            quantity=product.quantity,
            reason='Initial catalog intake / inward stock',
            device_source='Admin UI'
        )
        db.session.add(mv)

    db.session.commit()
    return jsonify(product.to_dict()), 201

@app.route('/api/products/<int:pid>', methods=['PUT'])
def update_product(pid):
    product = Product.query.get_or_404(pid)
    data = request.json or {}
    old_qty = product.quantity

    for field in ['name', 'sku', 'price', 'cost_price', 'quantity', 'min_stock', 
                  'reorder_point', 'lead_time_days', 'category_id', 'description', 
                  'barcode', 'rfid_tag', 'location_aisle']:
        if field in data:
            val = data[field]
            if field in ['price', 'cost_price']: val = float(val)
            elif field in ['quantity', 'min_stock', 'reorder_point', 'lead_time_days']: val = int(val)
            setattr(product, field, val)

    if 'quantity' in data and data['quantity'] != old_qty:
        diff = data['quantity'] - old_qty
        mv = StockMovement(
            product_id=pid,
            movement_type='IN' if diff > 0 else 'OUT',
            quantity=abs(diff),
            reason=data.get('reason', 'Manual inventory count adjustment'),
            device_source='ERP Interface'
        )
        db.session.add(mv)

    db.session.commit()
    return jsonify(product.to_dict())

@app.route('/api/products/<int:pid>', methods=['DELETE'])
def delete_product(pid):
    product = Product.query.get_or_404(pid)
    db.session.delete(product)
    db.session.commit()
    return jsonify({'message': f'Product {product.name} deleted successfully'})

# 3. Categories
@app.route('/api/categories', methods=['GET'])
def get_categories():
    return jsonify([c.to_dict() for c in Category.query.all()])

@app.route('/api/categories', methods=['POST'])
def add_category():
    data = request.json or {}
    if not data.get('name'):
        return jsonify({'error': 'Category name required'}), 400
    cat = Category(name=data['name'], description=data.get('description', ''))
    db.session.add(cat)
    db.session.commit()
    return jsonify(cat.to_dict()), 201

# 4. Point of Sale & Sales Transactions
@app.route('/api/sales', methods=['GET'])
def get_sales():
    limit = int(request.args.get('limit', 100))
    sales = Sale.query.order_by(Sale.sale_date.desc()).limit(limit).all()
    return jsonify([s.to_dict() for s in sales])

@app.route('/api/sales', methods=['POST'])
def record_sale():
    data = request.json or {}
    product_id = data.get('product_id')
    qty_sold = int(data.get('quantity_sold', 1))

    if not product_id or qty_sold <= 0:
        return jsonify({'error': 'Invalid product or quantity'}), 400

    product = Product.query.get_or_404(product_id)
    if product.quantity < qty_sold:
        return jsonify({'error': f'Insufficient stock. Only {product.quantity} units available.'}), 400

    sale = Sale(
        product_id=product.id,
        quantity_sold=qty_sold,
        unit_price=product.price,
        total_amount=round(product.price * qty_sold, 2),
        customer_name=data.get('customer_name', 'Walk-in Retail'),
        payment_method=data.get('payment_method', 'UPI / Electronic')
    )
    product.quantity -= qty_sold

    mv = StockMovement(
        product_id=product.id,
        movement_type='OUT',
        quantity=qty_sold,
        reason=f"Sale transaction ({data.get('customer_name', 'Walk-in')})",
        device_source=data.get('device_source', 'POS Terminal')
    )
    db.session.add(sale)
    db.session.add(mv)
    db.session.commit()
    return jsonify(sale.to_dict()), 201

# 5. Stock Movements & Audit Ledger
@app.route('/api/movements', methods=['GET'])
def get_movements():
    m_type = request.args.get('type')
    query = StockMovement.query
    if m_type:
        query = query.filter(StockMovement.movement_type == m_type)
    mvs = query.order_by(StockMovement.created_at.desc()).limit(100).all()
    return jsonify([m.to_dict() for m in mvs])

# 6. Suppliers & Procurement
@app.route('/api/suppliers', methods=['GET'])
def get_suppliers():
    return jsonify([s.to_dict() for s in Supplier.query.all()])

@app.route('/api/suppliers', methods=['POST'])
def add_supplier():
    data = request.json or {}
    if not data.get('name'):
        return jsonify({'error': 'Supplier name is required'}), 400
    s = Supplier(
        name=data['name'],
        contact_person=data.get('contact_person', ''),
        email=data.get('email', ''),
        phone=data.get('phone', ''),
        address=data.get('address', ''),
        lead_time_days=int(data.get('lead_time_days', 5)),
        rating=float(data.get('rating', 4.5)),
        payment_terms=data.get('payment_terms', 'Net 30')
    )
    db.session.add(s)
    db.session.commit()
    return jsonify(s.to_dict()), 201

# 7. Purchase Orders & Automated Reorder
@app.route('/api/purchases', methods=['GET'])
def get_purchases():
    pos = PurchaseOrder.query.order_by(PurchaseOrder.ordered_date.desc()).all()
    return jsonify([p.to_dict() for p in pos])

@app.route('/api/purchases', methods=['POST'])
def create_purchase_order():
    data = request.json or {}
    supplier_id = data.get('supplier_id')
    items_data = data.get('items', [])

    if not supplier_id or not items_data:
        return jsonify({'error': 'Supplier and at least 1 line item required'}), 400

    supplier = Supplier.query.get_or_404(supplier_id)
    po_count = PurchaseOrder.query.count() + 1
    po_num = f"PO-{datetime.now().strftime('%Y%m')}-{po_count:04d}"

    expected_days = supplier.lead_time_days or 5
    expected_delivery = now_utc() + timedelta(days=expected_days)

    po = PurchaseOrder(
        po_number=po_num,
        supplier_id=supplier.id,
        status='ORDERED',
        expected_delivery_date=expected_delivery,
        notes=data.get('notes', 'Automated ROP replenishment')
    )
    db.session.add(po)
    db.session.flush()

    total_amount = 0.0
    for itm in items_data:
        product = Product.query.get(itm['product_id'])
        if not product: continue
        qty = int(itm.get('quantity_ordered', 20))
        cost = float(itm.get('unit_cost', product.cost_price or (product.price * 0.65)))
        line_total = round(qty * cost, 2)
        total_amount += line_total

        po_item = PurchaseOrderItem(
            po_id=po.id,
            product_id=product.id,
            quantity_ordered=qty,
            unit_cost=cost,
            total_cost=line_total
        )
        db.session.add(po_item)

    po.total_amount = round(total_amount, 2)

    # Automatically generate tracking shipment
    shipment = Shipment(
        tracking_number=f"TRK-{random.randint(10000000, 99999999)}",
        po_id=po.id,
        carrier="BlueDart Logistics / Cargo Express",
        origin=supplier.address or "Supplier Fulfillment Yard",
        destination="Central Warehouse Dock 3",
        current_location="Origin Sorting Hub",
        status="IN_TRANSIT",
        estimated_delivery=expected_delivery
    )
    db.session.add(shipment)

    db.session.commit()
    return jsonify(po.to_dict()), 201

@app.route('/api/purchases/<int:poid>/receive', methods=['PUT'])
def receive_purchase_order(poid):
    po = PurchaseOrder.query.get_or_404(poid)
    if po.status == 'RECEIVED':
        return jsonify({'message': 'PO has already been received'}), 400

    po.status = 'RECEIVED'
    po.received_date = now_utc()

    for item in po.items:
        product = item.product
        if product:
            product.quantity += item.quantity_ordered
            mv = StockMovement(
                product_id=product.id,
                movement_type='IN',
                quantity=item.quantity_ordered,
                reason=f"Received PO #{po.po_number} from {po.supplier.name}",
                device_source='Inward Dock Scanner'
            )
            db.session.add(mv)

    if po.shipment:
        po.shipment.status = 'DELIVERED'
        po.shipment.current_location = 'Central Warehouse Received'

    db.session.commit()
    return jsonify(po.to_dict())

# 8. Large Shipment Tracking
@app.route('/api/shipments', methods=['GET'])
def get_shipments():
    shipments = Shipment.query.order_by(Shipment.updated_at.desc()).all()
    return jsonify([s.to_dict() for s in shipments])

@app.route('/api/shipments/<int:sid>/status', methods=['PUT'])
def update_shipment_status(sid):
    s = Shipment.query.get_or_404(sid)
    data = request.json or {}
    if 'status' in data: s.status = data['status']
    if 'current_location' in data: s.current_location = data['current_location']
    s.updated_at = now_utc()
    db.session.commit()
    return jsonify(s.to_dict())

# 9. Hardware & IoT Telemetry
@app.route('/api/hardware/devices', methods=['GET'])
def get_hardware_devices():
    devices = IoTDevice.query.all()
    return jsonify([d.to_dict() for d in devices])

@app.route('/api/hardware/scan', methods=['POST'])
def process_hardware_scan():
    data = request.json or {}
    code = data.get('code', '').strip()
    action = data.get('action', 'LOOKUP') # LOOKUP, INWARD, SALE
    device_id = data.get('device_id', 'DEV-SCAN-01')

    if not code:
        return jsonify({'error': 'Scan code/tag required'}), 400

    product = Product.query.filter(
        (Product.barcode == code) | (Product.rfid_tag == code) | (Product.sku.ilike(code))
    ).first()

    if not product:
        return jsonify({'found': False, 'message': f'Unregistered barcode/RFID: {code}'}), 404

    result = {'found': True, 'product': product.to_dict(), 'action': action}

    if action == 'SALE':
        if product.quantity > 0:
            product.quantity -= 1
            sale = Sale(
                product_id=product.id,
                quantity_sold=1,
                unit_price=product.price,
                total_amount=product.price,
                customer_name='Automated RFID/Barcode Checkout',
                payment_method='Smart Cart Auto-Debit'
            )
            mv = StockMovement(
                product_id=product.id,
                movement_type='OUT',
                quantity=1,
                reason=f"Smart Checkout scan ({code})",
                device_source=device_id
            )
            db.session.add(sale)
            db.session.add(mv)
            db.session.commit()
            result['message'] = f"Successfully checked out 1x {product.name}"
        else:
            result['message'] = "Cannot checkout: item out of stock"
    elif action == 'INWARD':
        product.quantity += int(data.get('quantity', 10))
        mv = StockMovement(
            product_id=product.id,
            movement_type='IN',
            quantity=int(data.get('quantity', 10)),
            reason=f"Inward RFID/Barcode Scan Intake ({code})",
            device_source=device_id
        )
        db.session.add(mv)
        db.session.commit()
        result['message'] = f"Restocked +{data.get('quantity', 10)} units for {product.name}"
    else:
        result['message'] = f"Recognized {product.name} (Qty: {product.quantity})"

    return jsonify(result)

@app.route('/api/hardware/telemetry', methods=['POST'])
def smart_scale_telemetry():
    data = request.json or {}
    sku = data.get('sku')
    measured_weight = float(data.get('weight_kg', 0.0))
    unit_weight = float(data.get('unit_weight_kg', 0.25))

    product = Product.query.filter_by(sku=sku).first()
    if not product:
        return jsonify({'error': 'Product not found'}), 404

    calculated_qty = int(round(measured_weight / unit_weight)) if unit_weight > 0 else 0
    discrepancy = calculated_qty - product.quantity

    return jsonify({
        'product': product.name,
        'system_qty': product.quantity,
        'calculated_qty_from_weight': calculated_qty,
        'weight_kg': measured_weight,
        'discrepancy': discrepancy,
        'status': 'MATCH' if discrepancy == 0 else ('SURPLUS' if discrepancy > 0 else 'DEFICIT')
    })

# 10. AI Demand Forecasting & ROP Optimization (PyTorch Bi-LSTM + RF + GBM Ensemble)
@app.route('/api/forecast', methods=['GET'])
def get_forecast():
    sku = request.args.get('sku')
    engine = MLEngine.get_instance()
    forecast_res = engine.forecast_7day(sku=sku)

    products = Product.query.all()
    reorder_alerts = []
    for p in products:
        opt = engine.compute_inventory_optimization(p, p.quantity, p.lead_time_days, p.cost_price)
        rop = opt['reorder_point']
        if p.quantity <= rop:
            reorder_alerts.append({
                'id': p.id,
                'name': p.name,
                'sku': p.sku,
                'category': p.category.name if p.category else 'General',
                'current_stock': p.quantity,
                'min_stock': p.min_stock,
                'reorder_point': rop,
                'lead_time_days': p.lead_time_days or 3,
                'safety_stock': opt['safety_stock'],
                'economic_order_quantity': opt['economic_order_quantity'],
                'suggested_reorder': opt['suggested_reorder'],
                'urgency': opt['urgency'],
                'stockout_risk_percentage': opt['stockout_risk_percentage']
            })

    forecast_res['reorder_alerts'] = reorder_alerts
    forecast_res['models_evaluated'] = engine.get_model_benchmarks()
    return jsonify(forecast_res)

@app.route('/api/forecast/models', methods=['GET'])
def get_forecast_models():
    engine = MLEngine.get_instance()
    return jsonify({
        'models': engine.get_model_benchmarks(),
        'active_model': 'PyTorch Bi-Directional Multi-Layer LSTM Forecaster (Ensemble Hybrid)',
        'features': engine.feature_cols,
        'dataset_sample_size': 5840
    })

@app.route('/api/forecast/product/<sku>', methods=['GET'])
def get_product_forecast(sku):
    product = Product.query.filter_by(sku=sku).first()
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    engine = MLEngine.get_instance()
    forecast_res = engine.forecast_7day(sku=sku)
    opt = engine.compute_inventory_optimization(product, product.quantity, product.lead_time_days, product.cost_price)
    return jsonify({
        'product': product.to_dict(),
        'forecast': forecast_res,
        'inventory_optimization': opt
    })

# 11. Reports & CSV Export Engine
@app.route('/api/reports/summary', methods=['GET'])
def get_reports_summary():
    products = Product.query.all()
    sales = Sale.query.all()
    
    total_revenue = sum(s.total_amount for s in sales)
    total_units_sold = sum(s.quantity_sold for s in sales)
    total_val = sum(p.quantity * p.price for p in products)
    
    # Category revenue breakdown
    cat_sales = {}
    for s in sales:
        cname = s.product.category.name if (s.product and s.product.category) else 'General'
        cat_sales[cname] = round(cat_sales.get(cname, 0) + s.total_amount, 2)
        
    return jsonify({
        'total_revenue': round(total_revenue, 2),
        'total_units_sold': total_units_sold,
        'total_inventory_valuation': round(total_val, 2),
        'sales_by_category': cat_sales,
        'total_transactions': len(sales)
    })

@app.route('/api/reports/export', methods=['GET'])
def export_report_csv():
    rtype = request.args.get('type', 'products')
    output = io.StringIO()
    writer = csv.writer(output)

    if rtype == 'sales':
        writer.writerow(['Sale ID', 'Date', 'Product', 'SKU', 'Qty Sold', 'Unit Price', 'Total Amount', 'Customer', 'Payment'])
        sales = Sale.query.order_by(Sale.sale_date.desc()).all()
        for s in sales:
            writer.writerow([
                s.id,
                s.sale_date.strftime('%Y-%m-%d %H:%M') if s.sale_date else '',
                s.product.name if s.product else '',
                s.product.sku if s.product else '',
                s.quantity_sold,
                s.unit_price,
                s.total_amount,
                s.customer_name,
                s.payment_method
            ])
        filename = f"sales_report_{datetime.now().strftime('%Y%m%d')}.csv"
    elif rtype == 'movements':
        writer.writerow(['Movement ID', 'Date', 'Product', 'SKU', 'Type', 'Quantity', 'Reason', 'Device'])
        mvs = StockMovement.query.order_by(StockMovement.created_at.desc()).all()
        for m in mvs:
            writer.writerow([
                m.id,
                m.created_at.strftime('%Y-%m-%d %H:%M') if m.created_at else '',
                m.product.name if m.product else '',
                m.product.sku if m.product else '',
                m.movement_type,
                m.quantity,
                m.reason,
                m.device_source
            ])
        filename = f"stock_movements_{datetime.now().strftime('%Y%m%d')}.csv"
    else: # products
        writer.writerow(['Product ID', 'Name', 'SKU', 'Category', 'Price', 'Cost Price', 'Quantity', 'Min Stock', 'ROP', 'Valuation', 'Barcode', 'Location'])
        products = Product.query.order_by(Product.name.asc()).all()
        for p in products:
            writer.writerow([
                p.id,
                p.name,
                p.sku,
                p.category.name if p.category else 'Uncategorized',
                p.price,
                p.cost_price,
                p.quantity,
                p.min_stock,
                p.reorder_point,
                round(p.quantity * p.price, 2),
                p.barcode,
                p.location_aisle
            ])
        filename = f"inventory_catalog_{datetime.now().strftime('%Y%m%d')}.csv"

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename={filename}"}
    )

# 12. Physical Inventory Audit Reconciliation
@app.route('/api/audit/reconcile', methods=['POST'])
def audit_reconcile():
    data = request.json or {}
    product_id = data.get('product_id')
    counted_qty = int(data.get('counted_quantity', 0))
    auditor = data.get('auditor', 'Staff Stock Auditor')

    product = Product.query.get_or_404(product_id)
    variance = counted_qty - product.quantity

    if variance != 0:
        mv = StockMovement(
            product_id=product.id,
            movement_type='AUDIT_ADJUSTMENT',
            quantity=variance,
            reason=f"Physical Stock Count by {auditor} (Variance: {variance:+d})",
            device_source='Handheld Inventory Audit PDA'
        )
        db.session.add(mv)
        product.quantity = counted_qty
        db.session.commit()

    return jsonify({
        'product_id': product.id,
        'product_name': product.name,
        'new_quantity': product.quantity,
        'variance': variance,
        'financial_shrinkage': round(variance * product.cost_price, 2) if variance < 0 else 0
    })

# ─── SEED DATA ───────────────────────────────────────────────────────────────

def run_seed():
    with app.app_context():
        db.create_all()
        if Category.query.count() == 0:
            cats = [
                Category(name='Electronics & Peripherals', description='Handheld scanners, POS and smart hubs'),
                Category(name='Hardware & Equipment', description='Printers, thermal scales and terminals'),
                Category(name='Consumables & Packaging', description='BPA-free receipt rolls and packaging labels'),
                Category(name='Industrial & Safety Wear', description='High-visibility vests, gloves and gear')
            ]
            db.session.add_all(cats)
            db.session.flush()

            products = [
                Product(name='Wireless Barcode Scanner', sku='SKU-001', price=2450.00, cost_price=1600.00, quantity=45, min_stock=15, reorder_point=25, lead_time_days=3, category_id=cats[0].id, description='2.4GHz Handheld Laser Scanner with USB cradle', barcode='8901001001', rfid_tag='EPC-0001', location_aisle='Aisle A-01'),
                Product(name='Thermal Receipt Printer', sku='SKU-002', price=4200.00, cost_price=2800.00, quantity=8, min_stock=10, reorder_point=15, lead_time_days=4, category_id=cats[1].id, description='80mm High Speed Thermal POS Printer', barcode='8901001002', rfid_tag='EPC-0002', location_aisle='Aisle A-02'),
                Product(name='IoT RFID Gateway Hub', sku='SKU-003', price=8900.00, cost_price=5800.00, quantity=5, min_stock=12, reorder_point=18, lead_time_days=7, category_id=cats[0].id, description='Smart Warehouse EPC Gen2 UHF Gateway', barcode='8901001003', rfid_tag='EPC-0003', location_aisle='Aisle B-01'),
                Product(name='Digital Weighing Scale', sku='SKU-004', price=3100.00, cost_price=2100.00, quantity=22, min_stock=8, reorder_point=12, lead_time_days=3, category_id=cats[1].id, description='Precision digital bench scale 30kg with RS232', barcode='8901001004', rfid_tag='EPC-0004', location_aisle='Aisle B-02'),
                Product(name='Thermal Paper Roll (50pk)', sku='SKU-005', price=450.00, cost_price=270.00, quantity=120, min_stock=30, reorder_point=45, lead_time_days=2, category_id=cats[2].id, description='BPA-free thermal paper rolls 80x80mm', barcode='8901001005', rfid_tag='EPC-0005', location_aisle='Aisle C-01'),
                Product(name='Handheld POS Terminal', sku='SKU-006', price=12500.00, cost_price=8500.00, quantity=14, min_stock=5, reorder_point=8, lead_time_days=5, category_id=cats[1].id, description='Android 11 POS terminal with NFC reader', barcode='8901001006', rfid_tag='EPC-0006', location_aisle='Aisle B-03'),
                Product(name='Warehouse Staff Vest', sku='SKU-007', price=650.00, cost_price=380.00, quantity=35, min_stock=10, reorder_point=15, lead_time_days=2, category_id=cats[3].id, description='Hi-vis reflective safety vest with pockets', barcode='8901001007', rfid_tag='EPC-0007', location_aisle='Aisle D-01'),
                Product(name='Bluetooth Label Maker', sku='SKU-008', price=3400.00, cost_price=2200.00, quantity=4, min_stock=6, reorder_point=10, lead_time_days=4, category_id=cats[0].id, description='Portable wireless barcode & shipping label printer', barcode='8901001008', rfid_tag='EPC-0008', location_aisle='Aisle A-03')
            ]
            db.session.add_all(products)
            db.session.flush()

            suppliers = [
                Supplier(name='Apex Hardware Wholesalers', contact_person='Vikram Malhotra', email='supply@apexhardware.com', phone='+91 98765 43210', address='Plot 45, Industrial Zone, Chennai', lead_time_days=3, rating=4.9),
                Supplier(name='TechLogix IoT Solutions', contact_person='Pooja Sundaram', email='orders@techlogix.in', phone='+91 91234 56789', address='Tech Park Phase 2, Bangalore', lead_time_days=6, rating=4.7),
                Supplier(name='National Consumables & Paper', contact_person='Ramesh Babu', email='sales@natconsumables.com', phone='+91 94440 12345', address='SIPCOT Complex, Ranipet', lead_time_days=2, rating=4.8)
            ]
            db.session.add_all(suppliers)
            db.session.flush()

            for p in products:
                db.session.add(StockMovement(
                    product_id=p.id,
                    movement_type='IN',
                    quantity=p.quantity,
                    reason='Initial warehouse stock inventory intake',
                    device_source='Warehouse Main Gate'
                ))

            sales = [
                Sale(product_id=products[0].id, quantity_sold=3, unit_price=products[0].price, total_amount=3*products[0].price, customer_name='Apollo Logistics', payment_method='Net Banking'),
                Sale(product_id=products[4].id, quantity_sold=10, unit_price=products[4].price, total_amount=10*products[4].price, customer_name='City Retail Mart', payment_method='UPI'),
                Sale(product_id=products[1].id, quantity_sold=2, unit_price=products[1].price, total_amount=2*products[1].price, customer_name='Green Grocery Chains', payment_method='Credit Card')
            ]
            db.session.add_all(sales)

            po = PurchaseOrder(
                po_number='PO-202610-0001',
                supplier_id=suppliers[0].id,
                total_amount=56000.0,
                status='IN_TRANSIT',
                ordered_date=now_utc() - timedelta(days=2),
                expected_delivery_date=now_utc() + timedelta(days=1),
                notes='Urgent replenishment for Thermal Printers and Scanners'
            )
            db.session.add(po)
            db.session.flush()

            po_items = [
                PurchaseOrderItem(po_id=po.id, product_id=products[1].id, quantity_ordered=15, unit_cost=2800.0, total_cost=42000.0),
                PurchaseOrderItem(po_id=po.id, product_id=products[7].id, quantity_ordered=5, unit_cost=2200.0, total_cost=11000.0)
            ]
            db.session.add_all(po_items)

            shipment = Shipment(
                tracking_number='TRK-84920491',
                po_id=po.id,
                carrier='BlueDart Cargo Express',
                origin='Apex Industrial Yard, Chennai',
                destination='Central Warehouse Receiving Dock',
                current_location='Inter-State Transit Sorting Yard',
                status='IN_TRANSIT',
                estimated_delivery=now_utc() + timedelta(days=1)
            )
            db.session.add(shipment)

            devices = [
                IoTDevice(device_id='SCANNER-W01', device_name='Dock 1 Handheld Barcode Laser', device_type='BARCODE_SCANNER', status='ONLINE', battery_level=92, location_area='Receiving Dock 1'),
                IoTDevice(device_id='RFID-GATE-01', device_name='Portal RFID Archway Gate', device_type='RFID_GATEWAY', status='ONLINE', battery_level=100, location_area='Main Inbound Door'),
                IoTDevice(device_id='SCALE-BENCH-02', device_name='Smart Weighing Shelf #4', device_type='WEIGHT_SCALE', status='ONLINE', battery_level=88, location_area='Aisle B Pick Zone'),
                IoTDevice(device_id='POS-TERMINAL-01', device_name='Front Desk Smart Checkout', device_type='POS_TERMINAL', status='ONLINE', battery_level=97, location_area='Retail Checkout counter')
            ]
            db.session.add_all(devices)

            db.session.commit()
            print("✅ Stock Management Database seeded with enterprise entities.")

@app.route('/api/seed', methods=['GET', 'POST'])
def seed_data():
    run_seed()
    return jsonify({'message': 'Seed data initialized/verified successfully'})

if __name__ == '__main__':
    with app.app_context():
        run_seed()
    port = int(os.environ.get('PORT', 5019))
    print(f"🚀 Stock Management Backend API listening on http://localhost:{port}")
    app.run(debug=True, host='0.0.0.0', port=port)
