from dataclasses import dataclass
import string
from typing import List, Dict, Union
from flask import Flask, request, jsonify
import re

# ==== Type Definitions, feel free to add or modify ===========================
@dataclass
class CookbookEntry:
	name: str

@dataclass
class RequiredItem():
	name: str
	quantity: int

@dataclass
class Recipe(CookbookEntry):
	required_items: List[RequiredItem]

@dataclass
class Ingredient(CookbookEntry):
	cook_time: int


# =============================================================================
# ==== HTTP Endpoint Stubs ====================================================
# =============================================================================
app = Flask(__name__)

# Store your recipes here!
cookbook = {}

# Task 1 helper (don't touch)
@app.route("/parse", methods=['POST'])
def parse():
	data = request.get_json()
	recipe_name = data.get('input', '')
	parsed_name = parse_handwriting(recipe_name)
	if parsed_name is None:
		return 'Invalid recipe name', 400
	return jsonify({'msg': parsed_name}), 200

# [TASK 1] ====================================================================
# Takes in a recipeName and returns it in a form that
def parse_handwriting(recipeName: str) -> Union[str | None]:
	recipeName = re.sub(r'[-_]+', ' ', recipeName)
	recipeName = ''.join(c for c in recipeName if (c.isalpha() or c == ' '))
	recipeName = string.capwords(recipeName)
	if recipeName is "":
		recipeName = None
	return recipeName


# [TASK 2] ====================================================================
# Endpoint that adds a CookbookEntry to your magical cookbook
@app.route('/entry', methods=['POST'])
def create_entry():
	data = request.get_json()
	entry_type = data.get('type', '')
	entry_name = data.get('name', '')
	if entry_name in cookbook:
		return "entry names must be unique", 400

	if entry_type == 'ingredient':
		cookTime = int(data.get('cookTime', ''))
		if cookTime < 0:
			return jsonify({'message': "cookTime can only be greater than or equal to 0"}), 400
		ingredient = Ingredient(entry_name, cookTime)
		cookbook[entry_name] = ingredient
		return jsonify({}), 200
	elif entry_type == 'recipe':
		data = request.get_json()
		reqItems = data.get('requiredItems', [])
		names = []
		for item in reqItems:
			if (item['name'] in names):
				return 'Recipe requiredItems can only have one element per name.', 400
			names.append(item['name'])
		recipe = Recipe(entry_name, reqItems)
		cookbook[entry_name] = recipe
		return jsonify({}), 200
	else:
		return 'type can only be "recipe" or "ingredient"', 400


# [TASK 3] ====================================================================
# Endpoint that returns a summary of a recipe that corresponds to a query name
@app.route('/summary', methods=['GET'])
def summary():
	totalIngredients = {}
	cookTime = 0
	invalid = False

	def rec(name, quantity):
		nonlocal cookTime
		nonlocal totalIngredients
		nonlocal invalid
		if name not in cookbook or invalid:
			invalid = True
			return

		if isinstance(cookbook[name], Ingredient):
			cookTime += cookbook[name].cook_time * quantity
			if name in totalIngredients:
				totalIngredients[name] += quantity
			else:
				totalIngredients[name] = quantity
		elif isinstance(cookbook[name], Recipe):
			for e_sub in cookbook[name].required_items:
				rec(e_sub['name'], quantity * e_sub['quantity'])

	name = request.args.get('name')
	if name not in cookbook:
		return "", 400
	if isinstance(cookbook[name], Ingredient):
		return "", 400

	rec(name, 1)

	if invalid:
		return "", 400

	return jsonify({
		"name": name,
		"cookTime": cookTime,
		"ingredients": [ {"name": k, "quantity": v} for k, v in totalIngredients.items() ]
	}), 200



# =============================================================================
# ==== DO NOT TOUCH ===========================================================
# =============================================================================

if __name__ == '__main__':
	app.run(debug=True, port=8080)

