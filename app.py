from flask import Flask, render_template, request, redirect, url_for, flash, session
from models import db,User,  Product, Location, ProductMovement

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
app.config['SECRET_KEY'] = 'your-secret-key'
db.init_app(app)


@app.before_request
def create_tables():
    db.create_all()
    # Create a default user if not exists
    if not User.query.filter_by(username='admin').first():
        user = User(username='admin')
        user.set_password('admin123')
        db.session.add(user)
        db.session.commit()

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Logged in successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# Protect all main routes
@app.route('/')
@login_required
def index():
    return render_template('index.html')

# Product CRUD 
@app.route('/products', methods=['GET', 'POST'])
def products():
    if request.method == 'POST':
        product_id = request.form['product_id'].strip()
        name = request.form['name'].strip()
        try:
            quantity = int(request.form['quantity'])
            if quantity < 0:
                raise ValueError
        except:
            flash("Quantity must be a non-negative integer.")
            return redirect(url_for('products'))
        if not product_id or not name:
            flash("All fields are required.")
        elif Product.query.get(product_id):
            flash("Product ID already exists.")
        else:
            db.session.add(Product(product_id=product_id, name=name, quantity=quantity))
            db.session.commit()
            flash("Product added successfully.")
        return redirect(url_for('products'))
    products = Product.query.all()
    return render_template('products.html', products=products)

@app.route('/edit_product/<product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    if request.method == 'POST':
        name = request.form['name'].strip()
        try:
            quantity = int(request.form['quantity'])
            if quantity < 0:
                raise ValueError
        except:
            flash("Quantity must be a non-negative integer.")
            return redirect(url_for('edit_product', product_id=product_id))
        if not name:
            flash("Name is required.")
        else:
            product.name = name
            product.quantity = quantity
            db.session.commit()
            flash("Product updated.")
            return redirect(url_for('products'))
    return render_template('edit_product.html', product=product)

@app.route('/delete_product/<product_id>')
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash("Product deleted.")
    return redirect(url_for('products'))

# Location CRUD 
@app.route('/locations', methods=['GET', 'POST'])
def locations():
    if request.method == 'POST':
        location_id = request.form['location_id'].strip()
        name = request.form['name'].strip()
        if not location_id or not name:
            flash("All fields are required.")
        elif Location.query.get(location_id):
            flash("Location ID already exists.")
        else:
            db.session.add(Location(location_id=location_id, name=name))
            db.session.commit()
            flash("Location added successfully.")
        return redirect(url_for('locations'))
    locations = Location.query.all()
    return render_template('locations.html', locations=locations)

@app.route('/edit_location/<location_id>', methods=['GET', 'POST'])
def edit_location(location_id):
    location = Location.query.get_or_404(location_id)
    if request.method == 'POST':
        name = request.form['name'].strip()
        if not name:
            flash("Name is required.")
        else:
            location.name = name
            db.session.commit()
            flash("Location updated.")
            return redirect(url_for('locations'))
    return render_template('edit_location.html', location=location)

@app.route('/delete_location/<location_id>')
def delete_location(location_id):
    location = Location.query.get_or_404(location_id)
    db.session.delete(location)
    db.session.commit()
    flash("Location deleted.")
    return redirect(url_for('locations'))

# ProductMovement CRUD with business logic 
@app.route('/movements', methods=['GET', 'POST'])
def movements():
    products = Product.query.all()
    locations = Location.query.all()
    if request.method == 'POST':
        product_id = request.form['product_id']
        movement_type = request.form['movement_type']
        qty = request.form.get('qty', '0').strip()
        from_location = request.form.get('from_location') or None
        to_location = request.form.get('to_location') or None

        try:
            qty = int(qty)
            if qty <= 0:
                raise ValueError
        except:
            flash("Quantity must be a positive integer.")
            return redirect(url_for('movements'))

        product = Product.query.get(product_id)
        if not product:
            flash("Invalid product.")
            return redirect(url_for('movements'))

        # 1. Unknown to Hub
        if movement_type == 'unknown_to_hub':
            if not to_location or from_location:
                flash("Only To Location should be filled for Unknown to Hub.")
                return redirect(url_for('movements'))
            if product.quantity < qty:
                flash("Not enough product in main stock.")
                return redirect(url_for('movements'))
            product.quantity -= qty
            db.session.add(ProductMovement(
                product_id=product_id,
                from_location=None,
                to_location=to_location,
                qty=qty,
                movement_type=movement_type
            ))
            db.session.commit()
            flash("Moved from unknown to hub successfully.")
            return redirect(url_for('movements'))

        # 2. Hub to Hub
        elif movement_type == 'hub_to_hub':
            if not from_location or not to_location or from_location == to_location:
                flash("Both From and To locations must be filled and different for Hub to Hub.")
                return redirect(url_for('movements'))
            ever_received = ProductMovement.query.filter_by(
                product_id=product_id,
                to_location=from_location,
                movement_type='unknown_to_hub'
            ).first()
            if not ever_received:
                flash("Invalid: Source hub never received from unknown.")
                return redirect(url_for('movements'))
            in_qty = sum(m.qty for m in ProductMovement.query.filter_by(product_id=product_id, to_location=from_location))
            out_qty = sum(m.qty for m in ProductMovement.query.filter_by(product_id=product_id, from_location=from_location))
            if in_qty - out_qty < qty:
                flash(f"Not enough stock in {from_location}.")
                return redirect(url_for('movements'))
            db.session.add(ProductMovement(
                product_id=product_id,
                from_location=from_location,
                to_location=to_location,
                qty=qty,
                movement_type=movement_type
            ))
            db.session.commit()
            flash("Moved from hub to hub successfully.")
            return redirect(url_for('movements'))

        # 3. Hub to Customer
        elif movement_type == 'hub_to_customer':
            if not from_location or to_location:
                flash("Only From Location should be filled for Hub to Customer.")
                return redirect(url_for('movements'))
            in_qty = sum(m.qty for m in ProductMovement.query.filter_by(product_id=product_id, to_location=from_location))
            out_qty = sum(m.qty for m in ProductMovement.query.filter_by(product_id=product_id, from_location=from_location))
            if in_qty - out_qty < qty:
                flash(f"Not enough stock in {from_location}.")
                return redirect(url_for('movements'))
            db.session.add(ProductMovement(
                product_id=product_id,
                from_location=from_location,
                to_location=None,
                qty=qty,
                movement_type=movement_type
            ))
            db.session.commit()
            flash("Moved from hub to customer successfully.")
            return redirect(url_for('movements'))

        else:
            flash("Invalid movement type.")
            return redirect(url_for('movements'))

    movements = ProductMovement.query.order_by(ProductMovement.timestamp.desc()).all()
    return render_template('movements.html', products=products, locations=locations, movements=movements)

@app.route('/edit_movement/<int:movement_id>', methods=['GET', 'POST'])
def edit_movement(movement_id):
    movement = ProductMovement.query.get_or_404(movement_id)
    products = Product.query.all()
    locations = Location.query.all()
    if request.method == 'POST':
        # For simplicity, do not allow changing movement_type or product
        try:
            qty = int(request.form['qty'])
            if qty <= 0:
                raise ValueError
        except:
            flash("Quantity must be a positive integer.")
            return redirect(url_for('edit_movement', movement_id=movement_id))
        movement.qty = qty
        db.session.commit()
        flash("Movement updated.")
        return redirect(url_for('movements'))
    return render_template('edit_movement.html', movement=movement, products=products, locations=locations)

@app.route('/delete_movement/<int:movement_id>')
def delete_movement(movement_id):
    movement = ProductMovement.query.get_or_404(movement_id)
    db.session.delete(movement)
    db.session.commit()
    flash("Movement deleted.")
    return redirect(url_for('movements'))

# Report 
@app.route('/report')
def report():
    products = Product.query.all()
    locations = Location.query.all()
    balances = {}
    for product in products:
        for location in locations:
            in_qty = sum(m.qty for m in ProductMovement.query.filter_by(
                product_id=product.product_id, to_location=location.location_id))
            out_qty = sum(m.qty for m in ProductMovement.query.filter_by(
                product_id=product.product_id, from_location=location.location_id))
            balances[(product.product_id, location.location_id)] = in_qty - out_qty
    return render_template('report.html', products=products, locations=locations, balances=balances)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
