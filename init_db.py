import pandas as pd

from app import models, db


def get_or_create(session, model, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return False, instance
    else:
        instance = model(**kwargs)
        try:
            session.add(instance)
            session.commit()
            return True, instance
        except Exception as e:
            session.rollback()
            raise e


def read_recipe_sheet(fname, sheet_name):
    with pd.ExcelFile(fname) as xls:
        print('reading sheet "{}" from "{}"'.format(sheet_name, fname))
        data = pd.read_excel(xls, sheet_name, index_col=None, header=None,
                               usecols=[0, 1, 2])

    data.columns = ["id", "recipe_name", 'value']
    return data


def read_data():
    fnames = ['./GA Tech Data Final 2.xlsx', './GA Tech Data Final.xlsx']
    sheets = ['Ingredients', 'Occasion', 'Ethnicity', 'Recipe Type', 'Diet',
              'Course']
    dat = {
        sheet.lower(): pd.concat(
            [read_recipe_sheet(fname, sheet) for fname in fnames],
            axis=0
            )
        for sheet in sheets
    }
    return dat


def clean_data(data):
    data['ingredients'].loc[data['ingredients'].value.isnull(), "value"] = ','.join(["cheddar cheese","smoked cheddar cheese","croissants","cream","Vegemite"])

    data['recipe type'].loc[data['recipe type'].value.isnull(), 'value'] = ["Sandwiches & burgers"]

    data['course'].loc[data['course'].value.isnull(), "value"] = ["Breakfast / brunch"]
    data['diet'].loc[data['diet'].value.isnull(), 'value'] = 'Vegetarian'
    data['ethnicity'].loc[data['ethnicity'].value.isnull(), 'value'] = ['French']

    data['diet'].drop("recipe_name", axis=1, inplace=True)
    data['recipe type'].drop("recipe_name", axis=1, inplace=True)
    data['occasion'].drop("recipe_name", axis=1, inplace=True)
    data['course'].drop("recipe_name", axis=1, inplace=True)
    data['ethnicity'].drop("recipe_name", axis=1, inplace=True)
    data['ingredients'].drop("recipe_name", axis=1, inplace=True)

    return data


def extract_recipes(data):
    recipe_index = data['ingredients'].loc[:,["id","recipe_name"]]
    recipe_index.drop_duplicates(subset='id', inplace=True)
    recipe_index.reset_index(inplace=True)
    recipe_index.drop(['index'], axis=1, inplace=True)
    return recipe_index


def populate_mapping(df, model, association_table):
    uniques = pd.DataFrame(df.value.unique(), columns=['value'])
    uniques['id'] = uniques.index
    objs = [
        model(id=row.id, name=row.value)
        for idx, row in uniques.iterrows()
    ]
    try:
        db.session.bulk_save_objects(objs)
        db.session.commit()
    except Exception:
        db.session.rollback()
        pass

    df.columns = ['recipe_id', 'value']
    recipe_map = df.merge(
        uniques,
        left_on='value',
        right_on='value'
    )[['recipe_id', 'id']]

    recipe_map.columns = association_table.columns.keys()

    print('writing recipe map')
    recipe_map.to_sql(
        association_table.name,
        db.session.connection(),
        index=False,
        if_exists='replace'
    )
    db.session.commit()


def populate_database():
    data = read_data()

    recipes = extract_recipes(data)

    data = clean_data(data)

    db.create_all()

    print('adding recipes to database')
    recs = [
        models.Recipe(id=row.id, name=row.recipe_name)
        for id, row in recipes.iterrows()
    ]
    db.session.bulk_save_objects(recs)
    db.session.commit()

    print('adding ingredients to database')
    populate_mapping(
        data['ingredients'],
        models.Ingredient,
        models.ingredient_association
    )

    print('adding recipe type to database')
    populate_mapping(
        data['recipe type'],
        models.RecipeType,
        models.type_association
    )

    print('adding courses to database')
    populate_mapping(
        data['course'],
        models.Course,
        models.course_association
    )

    print('adding diets to database')
    populate_mapping(
        data['diet'],
        models.Diet,
        models.diet_association
    )

    print('adding occasions to database')
    populate_mapping(
        data['occasion'],
        models.Occasion,
        models.occasion_association
    )

    print('adding ethnicities to database')
    populate_mapping(
        data['ethnicity'],
        models.Ethnicity,
        models.ethnicity_association
    )


if __name__ == "__main__":
    populate_database()
