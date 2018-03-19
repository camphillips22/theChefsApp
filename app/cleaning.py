import pandas as pd
import numpy as np

def read_data(xls_path):
    xls = pd.ExcelFile(xls_path)
    if (xls_path == "../Ga Tech/GA Tech Data Final.xlsx"):
        ingredients = pd.read_excel(xls, 'Ingredients', index_col=None, header=None)
        recipe_type = pd.read_excel(xls,"Recipe Type", index_col=None, header=None)
        occasion = pd.read_excel(xls,"Occasion", index_col=None, header=None)
        course = pd.read_excel(xls,"Course", index_col=None, header=None)
        diet = pd.read_excel(xls, "Diet", index_col=None, header=None, parse_cols=[0,1,3])
        ethnicity = pd.read_excel(xls, "Ethnicity", index_col=None, header=None)
    else:
        ingredients = pd.read_excel(xls, 'Ingredients', index_col=None, header=None, parse_cols=[0,1,2])
        recipe_type = pd.read_excel(xls,"Recipe Type", index_col=None, header=None, parse_cols=[0,1,2])
        occasion = pd.read_excel(xls,"Occasion", index_col=None, header=None)
        course = pd.read_excel(xls,"Course", index_col=None, header=None, parse_cols=[0,1,2])
        diet = pd.read_excel(xls, "Diet", index_col=None, header=None, parse_cols=[0,1,2])
        ethnicity = pd.read_excel(xls, "Ethnicity", index_col=None, header=None, parse_cols=[0,1,2])
    ingredients.columns = ["index","recipe_name","ingredients"]
    recipe_type.columns = ["index","recipe_name","recipe_type"]
    occasion.columns = ["index","recipe_name","occasion"]
    course.columns = ["index","recipe_name","course"]
    diet.columns = ["index","recipe_name","diet"]
    ethnicity.columns = ["index","recipe_name","ethnicity"]
    return ingredients, recipe_type, occasion, course, diet, ethnicity

def row_concat(df1, df2):
    return pd.concat([df1,df2], axis=0)


def load_data():
    ingredients_1, recipe_type_1, occasion_1, course_1, diet_1, ethnicity_1 = read_data("../../Ga Tech/GA Tech Data Final.xlsx")
    ingredients_2, recipe_type_2, occasion_2, course_2, diet_2, ethnicity_2 = read_data("../../Ga Tech/GA Tech Data Final 2.xlsx")

    ingredients = row_concat(ingredients_1, ingredients_2)
    recipe_type = row_concat(recipe_type_1, recipe_type_2)
    occasion = row_concat(occasion_1, occasion_2)
    course = row_concat(course_1, course_2)
    diet = row_concat(diet_1, diet_2)
    ethnicity = row_concat(ethnicity_1, ethnicity_2)

    ingredients.loc[ingredients.ingredients.isnull(),"ingredients"] = ["cheddar cheese","smoked cheddar cheese","croissants","cream","Vegemite"]
    recipe_type.loc[recipe_type.recipe_type.isnull(),"recipe_type"] = "Sandwiches & burgers"
    course.loc[course.course.isnull(),"recipe_type"] = "Breakfast / brunch"
    diet.loc[diet.diet.isnull(), "diet"] = "Vegetarian"
    ethnicity.loc[ethnicity.ethnicity.isnull(), "ethnicity"] = "French"
    index_recipe = ingredients.loc[:,["index","recipe_name"]]
    index_recipe.drop_duplicates(inplace=True)

    diet_dummies = pd.get_dummies(diet,columns=["diet"]).groupby(["index"]).sum()
    recipe_type_dummies = pd.get_dummies(recipe_type, columns=["recipe_type"]).groupby(["index"]).sum()
    course_dummies = pd.get_dummies(course, columns=["course"]).groupby(["index"]).sum()
    ethnicity_dummies = pd.get_dummies(ethnicity, columns=['ethnicity']).groupby(["index"]).sum()
    occasion_dummies = pd.get_dummies(occasion, columns=['occasion']).groupby(["index"]).sum()

    return ingredients, index_recipe, recipe_type_dummies, occasion_dummies, course_dummies, diet_dummies, ethnicity_dummies