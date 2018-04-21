from flask import render_template, request, jsonify
import json

from app import app
from app.models import (Recipe, Ingredient, Course, Ethnicity, RecipeType,
                        Diet, Occasion)


def package_clusters(clusters):
    return {
        "results": [
            {
                'id': str(group),
                'name': '',
                'recipe_id': row.name,
                'recipe_name':row.rname
            } for group in clusters.groups.keys()
            for idx, row in clusters.get_group(group).iterrows()
        ]
    }

def package_group_recs(groups):
    return {
        "results": [
            {
                "id": row.name,
                "name": row.gname,
                "recipes": [
                    {"id": id, "name": name}
                    for id, name in zip(row.rid, row.rname)
                ]
            } for idx, row in groups.iterrows()
        ],
        "recipe_count": int(groups.size)
    }

def package_groups(groups):
    return {
        "results": [
            {
                'gid': row[0],
                'gname': row[1],
                'count': row[2]
            } for row in groups
        ]
    }


def get_filter_args(req):
    return Course, [int(id) for id in req.form.getlist('course')], \
        Ethnicity, [int(id) for id in req.form.getlist('ethnicity')], \
        Occasion, [int(id) for id in req.form.getlist('occasion')], \
        RecipeType, [int(id) for id in req.form.getlist('type')], \
        Diet, [int(id) for id in req.form.getlist('diet')], \
        Ingredient, [int(id) for id in req.form.getlist('ingredient')]


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
        return jsonify(data)


@app.route('/cluster_filter', methods=['POST'])
def filter_with_cluster():
    if request.method == 'POST':
        if request.form['grouping'] == 'similarity':
            clusters = Recipe.cluster_on_filters(0.7, *get_filter_args(request))
            data = package_clusters(clusters)

        elif request.form['grouping'] == 'occasion':
            clusters = Recipe.group_on_filters(Occasion, *get_filter_args(request))
            data = package_group_recs(clusters)

        elif request.form['grouping'] == 'ethnicity':
            clusters = Recipe.group_on_filters(Ethnicity, *get_filter_args(request))
            data = package_group_recs(clusters)

        elif request.form['grouping'] == 'course':
            clusters = Recipe.group_on_filters(Course, *get_filter_args(request))
            data = package_group_recs(clusters)

        elif request.form['grouping'] == 'diet':
            clusters = Recipe.group_on_filters(Diet, *get_filter_args(request))
            data = package_group_recs(clusters)

        elif request.form['grouping'] == 'type':
            clusters = Recipe.group_on_filters(RecipeType, *get_filter_args(request))
            data = package_group_recs(clusters)
        else:
            data = 'error'

        if data == 'error' or data['recipe_count'] < 20:
            clusters = Recipe.cluster_on_filters(0.7, *get_filter_args(request))
            data = package_clusters(clusters)

        return jsonify(data)


@app.route('/search/ingredients', methods=['POST'])
def search_ingredients():
    if request.method == 'POST':
        ings = Ingredient.query.filter(
            Ingredient.name.contains(request.form['q'])
        ).all()
        data = {"results": [{'id': ing.id, "text": ing.name} for ing in ings]}
        return jsonify(data)


@app.route('/get_recipe_info', methods=['POST'])
def get_recipe_info():
    if request.method == 'POST':
        recs = Recipe.query.filter(Recipe.id == int(request.form['recipe_id'])).all()
        data = {'results': [
            {
                'id': r.id,
                'name': r.name,
                'courses': [c.name for c in r.courses],
                'ingredients': [i.name for i in r.ingredients],
                'occasions': [o.name for o in r.occasions],
                'diets': [d.name for d in r.diets],
                'recipe_types': [t.name for t in r.types],
                'ethnicities': [e.name for e in r.ethnicities],
            } for r in recs]
        }
        return jsonify(data)

