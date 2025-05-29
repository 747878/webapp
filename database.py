from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin # Import UserMixin
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model): # Inherit from UserMixin
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(Text, nullable=False, unique=True)
    password_hash = Column(Text, nullable=False)
    email = Column(Text, nullable=False, unique=True)
    orders = relationship("Order", back_populates="user")
    reservations = relationship("Reservation", back_populates="user")

class MenuItem(db.Model):
    __tablename__ = 'menu_items'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    category = Column(Text)
    image_url = Column(Text)
    order_items = relationship("OrderItem", back_populates="menu_item")

class Order(db.Model):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    order_date = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(Text, default='Pending')
    total_amount = Column(Float, nullable=False)
    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('orders.id'))
    menu_item_id = Column(Integer, ForeignKey('menu_items.id'))
    quantity = Column(Integer, nullable=False)
    price_at_time_of_order = Column(Float, nullable=False)
    order = relationship("Order", back_populates="items")
    menu_item = relationship("MenuItem", back_populates="order_items")

class Reservation(db.Model):
    __tablename__ = 'reservations'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    reservation_time = Column(DateTime, nullable=False)
    number_of_guests = Column(Integer, nullable=False)
    special_requests = Column(Text)
    user = relationship("User", back_populates="reservations")

def init_db(app):
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///restaurant.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    with app.app_context():
        db.create_all()
