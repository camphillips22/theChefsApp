from . import db
from sqlalchemy.orm import relationship


ingredient_association = db.Table(
    'ingredientlink',
    db.Model.metadata,
    db.Column('recipe_id', db.Integer, db.ForeignKey('recipes.id')),
    db.Column('ingredient_id', db.Integer, db.ForeignKey('ingredients.id'))
)

diet_association = db.Table(
    'dietlink',
    db.Model.metadata,
    db.Column('recipe_id', db.Integer, db.ForeignKey('recipes.id')),
    db.Column('diet_id', db.Integer, db.ForeignKey('diets.id'))
)

occasion_association = db.Table(
    'occasionlink',
    db.Model.metadata,
    db.Column('recipe_id', db.Integer, db.ForeignKey('recipes.id')),
    db.Column('occasion_id', db.Integer, db.ForeignKey('occasions.id'))
)

type_association = db.Table(
    'typelink',
    db.Model.metadata,
    db.Column('recipe_id', db.Integer, db.ForeignKey('recipes.id')),
    db.Column('type_id', db.Integer, db.ForeignKey('recipe_types.id'))
)

ethnicity_association = db.Table(
    'ethnicitylink',
    db.Model.metadata,
    db.Column('recipe_id', db.Integer, db.ForeignKey('recipes.id')),
    db.Column('ethnicity_id', db.Integer, db.ForeignKey('ethnicities.id'))
)

course_association = db.Table(
    'courselink',
    db.Model.metadata,
    db.Column('recipe_id', db.Integer, db.ForeignKey('recipes.id')),
    db.Column('course_id', db.Integer, db.ForeignKey('courses.id'))
)


class Recipe(db.Model):
    __tablename__ = 'recipes'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))

    courses = relationship(
        "Course",
        secondary=course_association,
        backref='recipes'
    )

    ingredients = relationship(
        "Ingredient",
        secondary=ingredient_association,
        backref='recipes'
    )

    occasions = relationship(
        "Occasion",
        secondary=occasion_association,
        backref='recipes'
    )

    diets = relationship(
        "Diet",
        secondary=diet_association,
        backref='recipes'
    )

    types = relationship(
        "RecipeType",
        secondary=type_association,
        backref='recipes'
    )

    ethnicities = relationship(
        "Ethnicity",
        secondary=ethnicity_association,
        backref='recipes'
    )

    @classmethod
    def filter_by_table(cls, other_class, filt_list):
        if isinstance(filt_list, str):
            filt_list = (filt_list,)

        assoc_lookup = {
            Ethnicity: cls.ethnicities,
            Course: cls.courses,
            Occasion: cls.occasions,
            Diet: cls.diets,
            RecipeType: cls.types,
            Ingredient: cls.ingredients
        }

        return cls.query.join(
            assoc_lookup[other_class]
        ).filter(
            other_class.name.in_(filt_list)
        ).group_by(
            cls.id
        ).having(
            db.func.count(other_class.id) > (len(filt_list)-1)
        )

    @classmethod
    def filter_by_ingredients(cls, ingredients):
        return cls.filter_by_table(Ingredient, ingredients)

    @classmethod
    def filter_by_courses(cls, courses):
        return cls.filter_by_table(Course, courses)

    @classmethod
    def filter_by_ethnicities(cls, ethnicities):
        return cls.filter_by_table(Ethnicity, ethnicities)

    @classmethod
    def filter_by_diets(cls, diets):
        return cls.filter_by_table(Diet, diets)

    @classmethod
    def filter_by_types(cls, types):
        return cls.filter_by_table(RecipeType, types)

    @classmethod
    def filter_by_occasions(cls, occasions):
        return cls.filter_by_table(Occasion, occasions)

    @classmethod
    def filter_multiple(cls, *args):
        if (len(args) % 2) != 0:
            raise TypeError('filter_multiple() takes multiples of 2 positional \
                            arguments')
        qs = [
            cls.filter_by_table(args[x], args[x+1]).subquery()
            for x in range(0, len(args), 2)
        ]
        query = cls.query
        for q in qs:
            query = query.join(q, q.c.id == cls.id)
        return query

    def __repr__(self):
        return '<Recipe {}, {}>'.format(self.id, self.name)


class Ingredient(db.Model):
    __tablename__ = 'ingredients'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))

    def __repr__(self):
        return '<Ingredient {}, {}>'.format(self.id, self.name)


class Diet(db.Model):
    __tablename__ = 'diets'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))

    def __repr__(self):
        return '<Diet {}, {}>'.format(self.id, self.name)


class RecipeType(db.Model):
    __tablename__ = 'recipe_types'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))

    def __repr__(self):
        return '<RecipeType {}, {}>'.format(self.id, self.name)


class Course(db.Model):
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))

    def __repr__(self):
        return '<Course {}, {}>'.format(self.id, self.name)


class Occasion(db.Model):
    __tablename__ = 'occasions'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))

    def __repr__(self):
        return '<Occasion {}, {}>'.format(self.id, self.name)


class Ethnicity(db.Model):
    __tablename__ = 'ethnicities'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))

    def __repr__(self):
        return '<Ethnicity {}, {}>'.format(self.id, self.name)
