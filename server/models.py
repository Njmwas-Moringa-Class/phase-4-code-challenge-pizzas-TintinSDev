from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData, ForeignKey
from sqlalchemy.orm import validates, relationship
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)


class Restaurant(db.Model, SerializerMixin):
    __tablename__ = 'restaurants'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    address = db.Column(db.String)

    # add relationship
    pizzas = relationship("RestaurantPizza", back_populates="restaurant")

    # add serialization rules
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address
        }

    def __repr__(self):
        return f'<Restaurant {self.name}>'


class Pizza(db.Model, SerializerMixin):
    __tablename__ = 'pizzas'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    ingredients = db.Column(db.String)

    # add relationship
    restaurants = relationship("RestaurantPizza", back_populates="pizza")
    # add serialization rules
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'ingredients': self.ingredients
        }
    def __repr__(self):
        return f'<Pizza {self.name}, {self.ingredients}>'


class RestaurantPizza(db.Model, SerializerMixin):
    __tablename__ = 'restaurant_pizzas'

    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, nullable=False)

    # add relationships
    restaurant_id = db.Column(db.Integer, ForeignKey('restaurants.id'))
    restaurant = relationship("Restaurant", back_populates="pizzas")
    
    pizza_id = db.Column(db.Integer, ForeignKey('pizzas.id'))
    pizza = relationship("Pizza", back_populates="restaurants")
    # add serialization rules
    def serialize(self):
        return {
            'id': self.id,
            'restaurant': self.restaurant.serialize(),
            'pizza': self.pizza.serialize(),
            'price': self.price
        }
    # add validation
    @validates('price')
    def validate_price(self, key, price):
        if not isinstance(price, int) or price < 1 or price > 30:
            raise ValueError("Price must be an integer between 1 and 30.")
        return price
    def __repr__(self):
        return f'<RestaurantPizza ${self.price}, {self.restaurant.name}, {self.pizza.name}>'
