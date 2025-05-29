from flask import Flask, render_template, request, redirect, url_for, flash, jsonify # Added jsonify
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from email_validator import validate_email, EmailNotValidError # For email validation
import datetime # For reservation date/time handling

from database import init_db, db as sqlalchemy_db, User, Reservation, Order, OrderItem, MenuItem # Import all necessary models

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here' # Replace with a real secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/restaurant.db' # Ensure this path is correct
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

init_db(app) # Initialize the database

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' # The route name for the login page

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- Main Routes ---
@app.route('/')
def index(): # Renamed from hello_world to index for clarity
    return render_template('landing_page.html')

# --- Authentication Routes ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not username or not email or not password or not confirm_password:
            flash('All fields are required!', 'danger')
            return redirect(url_for('register'))

        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('register'))

        try:
            v = validate_email(email) # Validate email
            email = v.normalized_email # Use normalized email
        except EmailNotValidError as e:
            flash(str(e), 'danger')
            return redirect(url_for('register'))

        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            if existing_user.username == username:
                flash('Username already exists. Please choose a different one.', 'warning')
            if existing_user.email == email: # Check separately to give specific feedback
                flash('Email address already registered. Please use a different one.', 'warning')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password_hash=hashed_password)
        
        sqlalchemy_db.session.add(new_user)
        sqlalchemy_db.session.commit()

        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash('Both username and password are required!', 'danger')
            return redirect(url_for('login'))

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Login successful!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash('Invalid username or password. Please try again.', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/profile')
@login_required
def profile():
    return f"Hello, {current_user.username}! This is your profile."

# --- Reservation Routes ---
@app.route('/make_reservation', methods=['GET', 'POST'])
@login_required
def make_reservation():
    if request.method == 'POST':
        date_str = request.form.get('reservation_date')
        time_str = request.form.get('reservation_time')
        number_of_guests = request.form.get('number_of_guests')
        special_requests = request.form.get('special_requests', '')

        if not date_str or not time_str or not number_of_guests:
            flash('Please fill in all required fields (Date, Time, Number of Guests).', 'danger')
            return redirect(url_for('make_reservation'))

        try:
            reservation_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
            reservation_time_obj = datetime.datetime.strptime(time_str, '%H:%M').time()
            number_of_guests_int = int(number_of_guests)
        except ValueError:
            flash('Invalid date, time, or number of guests format.', 'danger')
            return redirect(url_for('make_reservation'))

        if number_of_guests_int <= 0:
            flash('Number of guests must be positive.', 'danger')
            return redirect(url_for('make_reservation'))

        combined_datetime = datetime.datetime.combine(reservation_date, reservation_time_obj)

        # Basic validation: Ensure reservation is in the future
        if combined_datetime <= datetime.datetime.now():
            flash('Reservation date and time must be in the future.', 'danger')
            return redirect(url_for('make_reservation'))
        
        # Check for overlapping reservations (simplified: exact time match for now)
        # A more robust check would consider table availability and duration.
        existing_reservation = Reservation.query.filter_by(reservation_time=combined_datetime).first()
        if existing_reservation:
            flash('This time slot is already booked. Please choose a different time.', 'warning')
            return redirect(url_for('make_reservation'))

        new_reservation = Reservation(
            user_id=current_user.id,
            reservation_time=combined_datetime,
            number_of_guests=number_of_guests_int,
            special_requests=special_requests,
            status='Pending' # Default status
        )
        sqlalchemy_db.session.add(new_reservation)
        sqlalchemy_db.session.commit()

        flash('Reservation submitted successfully! It is now pending confirmation.', 'success')
        return redirect(url_for('my_reservations'))

    return render_template('make_reservation.html')

@app.route('/my_reservations')
@login_required
def my_reservations():
    reservations = Reservation.query.filter_by(user_id=current_user.id).order_by(Reservation.reservation_time.desc()).all()
    return render_template('my_reservations.html', reservations=reservations)

# --- Admin Routes ---
@app.route('/admin/reservations')
@login_required # Basic login protection, ideally role-based
def admin_reservations():
    # For now, any logged-in user can access. Add role check later.
    # For now, any logged-in user can access. Add role check later.
    # For example: if not current_user.is_admin: abort(403) # Placeholder for admin check
    reservations = Reservation.query.order_by(Reservation.reservation_time.desc()).all()
    return render_template('admin_reservations.html', reservations=reservations)

@app.route('/admin/reservations/update/<int:reservation_id>', methods=['POST'])
@login_required # Basic login protection, ideally role-based
def admin_update_reservation_status(reservation_id):
    # Placeholder for admin check
    # if not current_user.is_admin: abort(403)
    reservation = Reservation.query.get_or_404(reservation_id)
    new_status = request.form.get('status')

    if new_status not in ['Pending', 'Confirmed', 'Cancelled']: # Valid statuses for reservations
        flash('Invalid status selected for reservation.', 'danger')
        return redirect(url_for('admin_reservations'))

    reservation.status = new_status
    sqlalchemy_db.session.commit()
    flash(f'Reservation ID {reservation.id} status updated to {new_status}.', 'success')
    return redirect(url_for('admin_reservations'))

# --- Order Routes (Phase 2 Implementation) ---

@app.route('/admin/orders') # Route for admin to view all orders
@login_required # Placeholder for admin check
def admin_orders():
    # Placeholder for admin check
    # if not current_user.is_admin: abort(403)
    all_orders = Order.query.order_by(Order.order_date.desc()).all()
    return render_template('orders.html', orders=all_orders)

@app.route('/admin/order/update_status/<int:order_id>', methods=['POST'])
@login_required # Placeholder for admin check
def admin_update_order_status(order_id):
    # Placeholder for admin check
    # if not current_user.is_admin: abort(403)
    order_to_update = Order.query.get_or_404(order_id)
    new_status = request.form.get('status')
    
    valid_statuses = ['Pending', 'Confirmed', 'Preparing', 'Ready for Pickup', 'Completed', 'Cancelled']
    if new_status not in valid_statuses:
        flash(f'Invalid status "{new_status}" selected for order.', 'danger')
        return redirect(url_for('admin_orders'))

    order_to_update.status = new_status
    sqlalchemy_db.session.commit()
    flash(f'Order ID {order_to_update.id} status updated to {new_status}.', 'success')
    return redirect(url_for('admin_orders'))


@app.route('/submit_order', methods=['POST'])
@login_required
def submit_order():
    # Phase 2: Actual Order Processing
    cart_data = request.get_json()

    if not cart_data:
        return jsonify({'status': 'error', 'message': 'No cart data received.'}), 400

    if not current_user.is_authenticated: # Should be caught by @login_required, but good for belt-and-suspenders
        return jsonify({'status': 'error', 'message': 'User not authenticated.'}), 401

    calculated_total_amount = 0
    order_items_to_create = []

    try:
        for item_in_cart in cart_data:
            menu_item_id = item_in_cart.get('menuItemId')
            quantity = item_in_cart.get('quantity')
            customizations_from_cart = item_in_cart.get('customizations', '') # str or dict

            if not menu_item_id or not quantity or quantity <= 0:
                return jsonify({'status': 'error', 'message': f'Invalid item data in cart: {item_in_cart.get("name", "Unknown")}'}), 400

            menu_item_db = MenuItem.query.get(menu_item_id)
            if not menu_item_db:
                return jsonify({'status': 'error', 'message': f'Menu item with ID {menu_item_id} not found.'}), 404
            
            authoritative_price = menu_item_db.price
            calculated_total_amount += authoritative_price * quantity
            
            # Handle customizations: Store as string if it's a dict, or use as is if already string.
            # This assumes OrderItem does not have a structured field for customizations.
            # If OrderItem had e.g., a JSON field, we'd store customizations_from_cart directly.
            customizations_str = ""
            if isinstance(customizations_from_cart, dict):
                customizations_list = []
                if customizations_from_cart.get('bread'):
                    customizations_list.append(f"Bread: {customizations_from_cart['bread']}")
                if customizations_from_cart.get('sauce'):
                    customizations_list.append(f"Sauce: {customizations_from_cart['sauce']}")
                if customizations_from_cart.get('addons'):
                    customizations_list.append(f"Addons: {', '.join(customizations_from_cart['addons'])}")
                customizations_str = "; ".join(customizations_list)
            elif isinstance(customizations_from_cart, str):
                customizations_str = customizations_from_cart

            order_items_to_create.append({
                'menu_item_id': menu_item_db.id,
                'quantity': quantity,
                'price_at_time_of_order': authoritative_price
                # 'customizations_notes': customizations_str # No field for this in OrderItem currently
            })
            # Log customizations if they exist
            if customizations_str:
                print(f"Customizations for item {menu_item_db.name} (Order in progress): {customizations_str}")


        if not order_items_to_create:
             return jsonify({'status': 'error', 'message': 'Cannot create an empty order.'}), 400


        new_order = Order(
            user_id=current_user.id,
            order_date=datetime.datetime.utcnow(),
            status='Confirmed', # Or 'Pending'
            total_amount=calculated_total_amount
        )
        sqlalchemy_db.session.add(new_order)
        sqlalchemy_db.session.flush() # To get new_order.id for OrderItems

        for item_data in order_items_to_create:
            order_item_obj = OrderItem(
                order_id=new_order.id,
                menu_item_id=item_data['menu_item_id'],
                quantity=item_data['quantity'],
                price_at_time_of_order=item_data['price_at_time_of_order']
            )
            sqlalchemy_db.session.add(order_item_obj)
        
        sqlalchemy_db.session.commit()
        return jsonify({'status': 'success', 'order_id': new_order.id, 'message': 'Order placed successfully!'})

    except Exception as e:
        sqlalchemy_db.session.rollback()
        print(f"Error processing order: {e}") # Log the error
        return jsonify({'status': 'error', 'message': 'An internal error occurred. Please try again.'}), 500


@app.route('/order_history')
@login_required
def order_history():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.order_date.desc()).all()
    # The 'items' and 'menu_item' relationships should allow access to OrderItems and MenuItem details in the template
    return render_template('order_history.html', orders=orders) # Will create this template next

@app.route('/order_confirmed/<int:order_id>')
@login_required
def order_confirmed(order_id):
    order = Order.query.get_or_404(order_id)

    # Security Check: Ensure the order belongs to the current user
    # Add admin check here in the future if admins can view any order confirmation
    if order.user_id != current_user.id:
        flash('You are not authorized to view this order.', 'danger')
        return redirect(url_for('index')) # Or an appropriate error page / order_history

    # The order_confimerd.html template is used here.
    # The original placeholder was order_confirmed_placeholder.html
    return render_template('order_confimerd.html', order=order)


if __name__ == '__main__':
    app.run(debug=True)
