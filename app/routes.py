from flask import render_template, request
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
        ]
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
        return json.dumps(data)


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

        if data == 'error' or len(data['results']) == 0:
            clusters = Recipe.cluster_on_filters(0.7, *get_filter_args(request))
            data = package_clusters(clusters)

        return json.dumps(data)


@app.route('/search/ingredients', methods=['POST'])
def search_ingredients():
    if request.method == 'POST':
        ings = Ingredient.query.filter(
            Ingredient.name.contains(request.form['q'])
        ).all()
        data = {"results": [{'id': ing.id, "text": ing.name} for ing in ings]}
        return json.dumps(data)
