from flask import render_template, request
import json

from app import app
from app import models


@app.route('/')
@app.route('/index')
def index():
    courses = models.Course.query.all()
    ethnicities = models.Ethnicity.query.all()
    types = models.RecipeType.query.all()
    diets = models.Diet.query.all()
    occasions = models.Occasion.query.all()

    return render_template(
        'index.html',
        courses=courses,
        ethnicities=ethnicities,
        occasions=occasions,
        diets=diets,
        types=types,
        ingredients=[],
    )


@app.route('/filter', methods=['POST'])
def filter_recipes():
    if request.method == 'POST':
        return str(request.form)


@app.route('/search/ingredients', methods=['POST'])
def search_ingredients():
    if request.method == 'POST':
        ings = models.Ingredient.query.filter(
            models.Ingredient.name.contains(request.form['q'])
        ).all()
        data = {"results": [{'id': ing.id, "text": ing.name} for ing in ings]}
        return json.dumps(data)
