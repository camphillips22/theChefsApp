from app import app, db
from app.models import (Recipe, Ingredient, Diet, RecipeType, Course, Occasion,
                        Ethnicity)


@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'Recipe': Recipe,
        'Ingredient': Ingredient,
        'Diet': Diet,
        'RecipeType': RecipeType,
        'Course': Course,
        'Occasion': Occasion,
        'Ethnicity': Ethnicity,
    }


if __name__ == "__main__":
    import webbrowser
    webbrowser.open("http://127.0.0.1:5000")
    app.run()
