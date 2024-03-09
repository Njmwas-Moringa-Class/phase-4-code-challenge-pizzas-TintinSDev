#!/usr/bin/env python3

from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)


@app.route('/')
def index():
    return '<h1>Code challenge</h1>'

# Route to get all restaurants
@app.route('/restaurants', methods=['GET'])
def get_restaurants():
    try:
        restaurants = Restaurant.query.all()
        restaurant_list = []
        for restaurant in restaurants:
            restaurant_data = {
                "id": restaurant.id,
                "name": restaurant.name,
                "address": restaurant.address
            }
            restaurant_list.append(restaurant_data)
        return jsonify(restaurant_list), 200
    except Exception as e:
        error_message = {"error": str(e)}
        return make_response(jsonify(error_message), 500)
# Route to get a specific restaurant by ID
@app.route('/restaurants/<int:id>', methods=['GET'])
def get_restaurant(id):
    try:
        restaurant = Restaurant.query.get(id)
        if restaurant:
            # Get the associated pizzas for the restaurant
            restaurant_pizzas = RestaurantPizza.query.filter_by(restaurant_id=id).all()
            pizza_data = []
            for rp in restaurant_pizzas:
                pizza = Pizza.query.get(rp.pizza_id)
                pizza_info = {
                    "id": rp.id,
                    "pizza": {
                        "id": pizza.id,
                        "name": pizza.name,
                        "ingredients": pizza.ingredients
                    },
                    "price": rp.price,
                    "restaurant_id": rp.restaurant_id,
                    "pizza_id": rp.pizza_id
                }
                pizza_data.append(pizza_info)
            
            # Construct JSON response
            restaurant_info = {
                "id": restaurant.id,
                "name": restaurant.name,
                "address": restaurant.address,
                "restaurant_pizzas": pizza_data
            }
            return jsonify(restaurant_info), 200
        else:
            return make_response(jsonify({"error": "Restaurant not found"}), 404)
    except Exception as e:
        error_message = {"error": str(e)}
        return make_response(jsonify(error_message), 500)

# Route to delete a restaurant by ID
@app.route('/restaurants/<int:id>', methods=['DELETE'])
def delete_restaurant(id):
    restaurant = Restaurant.query.get(id)
    if restaurant:
        # Delete associated RestaurantPizzas
        RestaurantPizza.query.filter_by(restaurant_id=id).delete()
        # Delete the restaurant
        db.session.delete(restaurant)
        db.session.commit()
        return '', 204
    else:
        return make_response(jsonify({"error": "Restaurant not found"}), 404)
# Route to get all pizzas
@app.route('/pizzas', methods=['GET'])
def get_pizzas():
    try:
        pizzas = Pizza.query.all()
        pizza_list = []
        for pizza in pizzas:
            pizza_data = {
                "id": pizza.id,
                "name": pizza.name,
                "ingredients": pizza.ingredients
            }
            pizza_list.append(pizza_data)
        return jsonify(pizza_list), 200
    except Exception as e:
        error_message = {"error": str(e)}
        return make_response(jsonify(error_message), 500)

# Route to create a new RestaurantPizza
@app.route('/restaurant_pizzas', methods=['POST'])
def create_restaurant_pizza():
    try:
        # Extract data from the request
        data = request.json
        price = data.get('price')
        pizza_id = data.get('pizza_id')
        restaurant_id = data.get('restaurant_id')
        
        # Check if Pizza and Restaurant exist
        pizza = Pizza.query.get(pizza_id)
        restaurant = Restaurant.query.get(restaurant_id)
        
        if not pizza:
            return make_response(jsonify({"error": "Pizza not found"}), 400)
        if not restaurant:
            return make_response(jsonify({"error": "Restaurant not found"}), 400)
        
        # Create a new RestaurantPizza
        new_restaurant_pizza = RestaurantPizza(price=price, pizza_id=pizza_id, restaurant_id=restaurant_id)
        db.session.add(new_restaurant_pizza)
        db.session.commit()
        
        # Construct JSON response
        response_data = {
            "id": new_restaurant_pizza.id,
            "price": new_restaurant_pizza.price,
            "pizza": {
                "id": pizza.id,
                "name": pizza.name,
                "ingredients": pizza.ingredients
            },
            "pizza_id": pizza_id,
            "restaurant": {
                "id": restaurant.id,
                "name": restaurant.name,
                "address": restaurant.address
            },
            "restaurant_id": restaurant_id
        }
        return jsonify(response_data), 201
    except Exception as e:
        error_message = {"errors": ["Validation errors"]}
        return make_response(jsonify(error_message), 400)

if __name__ == '__main__':
    app.run(port=5555, debug=True)
