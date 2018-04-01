from flask import render_template, request
import json

from app import app
from app.models import (Recipe, Ingredient, Course, Ethnicity, RecipeType,
                        Diet, Occasion)


@app.route('/')
@app.route('/index')
def index():
    courses = Course.query.all()
    ethnicities = Ethnicity.query.all()
    types = RecipeType.query.all()
    diets = Diet.query.all()
    occasions = Occasion.query.all()

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
        result = Recipe.filter_multiple(
            Course, [int(id) for id in request.form.getlist('course')],
            Ethnicity, [int(id) for id in request.form.getlist('ethnicity')],
            Occasion, [int(id) for id in request.form.getlist('occasion')],
            RecipeType, [int(id) for id in request.form.getlist('type')],
            Diet, [int(id) for id in request.form.getlist('diet')],
            Ingredient, [int(id) for id in request.form.getlist('ingredient')]
        ).limit(5000).all()
        data = {"results": [{"id": rec.id, "name": rec.name} for rec in result]}
        return json.dumps(data)


@app.route('/search/ingredients', methods=['POST'])
def search_ingredients():
    if request.method == 'POST':
        ings = models.Ingredient.query.filter(
            models.Ingredient.name.contains(request.form['q'])
        ).all()
        data = {"results": [{'id': ing.id, "text": ing.name} for ing in ings]}
        return json.dumps(data)
