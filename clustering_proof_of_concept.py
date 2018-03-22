from scipy.spatial import distance
from itertools import combinations
from sklearn.cluster import AgglomerativeClustering, DBSCAN
import numpy as np
import pandas as pd 
import time
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, MetaData, Table, and_
from sqlalchemy.dialects import sqlite
import sqlite3


#SET VARS TO RUN TESTS
NUM_CLUSTERS = 80 #Agglomerative clustering only
NUM_RECIPES = 50000 #Applied after filters. Puts an upper limit on the number of recipes
#Set NUM_RECIPES to 1,000,000 to turn off this cap
CLUSTER_SENSITIVITY = 0.7 #Ranges from 0 to 1. Higher values form more clusters.

#Filter the dataset by exact matches for these criteria
#Set FILTER_FEATURE/2 value to None to remove these filters
FILTER_FEATURE = 'ethnicity'
FILTER_VALUE = 'American'

FILTER_FEATURE_2 = None#'diet'
FILTER_VALUE_2 = 'Vegetarian'

#Select specific recipe ids to return.
RECIPE_IDS = []

tStart = time.time()

#SQL data load
#adapted from http://www.radioactiverussian.com/2015/08/sqlalchemy-connecting-to-pre-existing-databases-table-joins/
engine = create_engine('sqlite:///chefs.db')
con = engine.raw_connection()

tbl_meta_Recipes = MetaData(engine)
tbl_Recipes = Table('recipe_index', tbl_meta_Recipes, autoload=True)

tbl_meta_Recipe_Ingredients = MetaData(engine)
tbl_Recipe_Ingredients = Table('recipe_ingredients', tbl_meta_Recipe_Ingredients, autoload=True)

tbl_meta_Ingredients = MetaData(engine)
tbl_Ingredients = Table('ingredients', tbl_meta_Ingredients, autoload=True)

tbl_meta_Diets = MetaData(engine)
tbl_Diets = Table('diet', tbl_meta_Diets, autoload=True)

tbl_meta_Recipe_Types = MetaData(engine)
tbl_Recipe_Types = Table('recipeType', tbl_meta_Recipe_Types, autoload=True)

tbl_meta_Courses = MetaData(engine)
tbl_Courses = Table('course', tbl_meta_Courses, autoload=True)

tbl_meta_Occasions = MetaData(engine)
tbl_Occasions = Table('occasion', tbl_meta_Occasions, autoload=True)

tbl_meta_Ethnicities = MetaData(engine)
tbl_Ethnicities = Table('ethnicity', tbl_meta_Ethnicities, autoload=True)

Session = sessionmaker(bind=engine)
session = Session()

#get table to filter on from filter vars at top
filter_table_dict = {\
	'ethnicity': (tbl_Ethnicities, tbl_Ethnicities.columns.ethnicity),\
	'diet':(tbl_Diets, tbl_Diets.columns.diet),\
	'recipeType':(tbl_Recipe_Types, tbl_Recipe_Types.columns.recipe_type),\
	'course':(tbl_Courses,tbl_Courses.columns.course),\
	'occasion':(tbl_Occasions, tbl_Occasions.columns.occasion)}

#to easily get a NUM_RECIPES subset of recipes
recipe_sub_query = session.query(\
	tbl_Recipes.columns.id, tbl_Recipes.columns.recipe_name)\
.limit(NUM_RECIPES).subquery()

#this version joins all tables to return all features for a recipe. 
#too slow for now
'''
results = session.query(\
	recipe_sub_query)\
	.join(tbl_Recipe_Ingredients, \
		recipe_sub_query.columns.id == tbl_Recipe_Ingredients.columns.id)\
	.join(tbl_Ingredients, \
		tbl_Recipe_Ingredients.columns.ingredient_id \
		== tbl_Ingredients.columns.id)\
	.outerjoin(tbl_Diets, \
		recipe_sub_query.columns.id \
		== tbl_Diets.columns.id)\
	.outerjoin(tbl_Recipe_Types, \
		recipe_sub_query.columns.id \
		== tbl_Recipe_Types.columns.id)\
	.outerjoin(tbl_Courses, \
		recipe_sub_query.columns.id \
		== tbl_Courses.columns.id)\
	.outerjoin(tbl_Ethnicities, \
		recipe_sub_query.columns.id \
		== tbl_Ethnicities.columns.id)\
	.outerjoin(tbl_Occasions, \
		recipe_sub_query.columns.id \
		== tbl_Occasions.columns.id)
'''

results = session.query(\
	recipe_sub_query)\
	.join(tbl_Recipe_Ingredients, \
		recipe_sub_query.columns.id == tbl_Recipe_Ingredients.columns.id)\
	.join(tbl_Ingredients, \
		tbl_Recipe_Ingredients.columns.ingredient_id \
		== tbl_Ingredients.columns.id)

if FILTER_FEATURE is not None and FILTER_FEATURE_2 is not None:

	results = results\
	.join(filter_table_dict[FILTER_FEATURE][0] , \
		recipe_sub_query.columns.id \
		== filter_table_dict[FILTER_FEATURE][0].columns.id)\
	.join(filter_table_dict[FILTER_FEATURE_2][0] , \
		recipe_sub_query.columns.id \
		== filter_table_dict[FILTER_FEATURE_2][0].columns.id)\
	.filter(and_(filter_table_dict[FILTER_FEATURE][1] 
		== FILTER_VALUE, filter_table_dict[FILTER_FEATURE_2][1] 
		== FILTER_VALUE_2))

elif FILTER_FEATURE is not None:

	results = results\
	.join(filter_table_dict[FILTER_FEATURE][0] , \
		recipe_sub_query.columns.id \
		== filter_table_dict[FILTER_FEATURE][0].columns.id)\
	.filter(filter_table_dict[FILTER_FEATURE][1] 
		== FILTER_VALUE)

elif FILTER_FEATURE_2 is not None:

	results = results\
	.join(filter_table_dict[FILTER_FEATURE_2][0] , \
		recipe_sub_query.columns.id \
		== filter_table_dict[FILTER_FEATURE_2][0].columns.id)\
	.filter(filter_table_dict[FILTER_FEATURE_2][1] 
		== FILTER_VALUE_2)

if RECIPE_IDS is not None and len(RECIPE_IDS) > 0:
	
	results = results.filter(tbl_Recipes.columns.id.in_(RECIPE_IDS))

#for all table join
'''
results = results.with_entities(\
		recipe_sub_query.columns.id,\
		recipe_sub_query.columns.recipe_name,\
		tbl_Recipe_Ingredients.columns.ingredient_id,\
		tbl_Ingredients.columns.ingredient, \
		tbl_Ethnicities.columns.ethnicity,\
		tbl_Diets.columns.diet,\
		tbl_Recipe_Types.columns.recipe_type,\
		tbl_Courses.columns.course,\
		tbl_Occasions.columns.occasion)
'''

results = results.with_entities(\
		recipe_sub_query.columns.id,\
		recipe_sub_query.columns.recipe_name,\
		tbl_Recipe_Ingredients.columns.ingredient_id,\
		tbl_Ingredients.columns.ingredient)

print str(results.statement.compile(dialect=sqlite.dialect()))


#for all table joins
'''
raw_data = pd.DataFrame(results.all(), columns=["Id", "Recipe",
	"Ingredient_Id","Ingredient", "Ethnicity", "Diet", "Occasion",
	"Course", "Recipe_type"])
'''	

raw_data = pd.DataFrame(results.all(), columns=["Id", "Recipe",
	"Ingredient_Id","Ingredient"])

#not sure why the cast is not working
#, dtype={"Id":np.int32})
session.close()

tDataLoaded = time.time()
print "Data load took: " + str(tDataLoaded-tStart) + " secs"

#CSV DATA LOAD
'''
raw_data = pd.read_csv("clustering_test_data.csv")
	#dtype={"Id":np.int32})
'''

# adapted from https://stackoverflow.com/questions/17841149/pandas-groupby-how-to-get-a-union-of-strings
def set_func(x):
	return set(x)

#for all table joins
'''
df_sample = raw_data.groupby('Id').agg({
                        'Recipe' : 'first', 
                        'Ingredient' : set_func,
                        'Ethnicity' : set_func,
                        'Diet' : set_func,
                        'Occasion' : set_func,
                        'Course' : set_func,
                        'Recipe_type' : set_func})
'''    

df_sample = raw_data.groupby('Id').agg({
                        'Recipe' : 'first', 
                        'Ingredient_Id': set_func,
                        'Ingredient' : set_func})

tDataGrouped = time.time()
print "Data grouping took: " + str(tDataGrouped-tDataLoaded) + " secs"

#BUILD DISTANCE/SIMILARITY MATRIX
#adapted from https://stackoverflow.com/questions/30140104/clustering-categorical-data-using-jaccard-similarity
def jaccard(set1, set2):
    intersection_len = len(set1.intersection(set2))
    if intersection_len <= 0:
    	return 1.
    return 1.-(1.*intersection_len /\
    	(len(set1) + len(set2) - intersection_len))

jaccard_generator = (jaccard(row1, row2) for row1, row2\
	in combinations(df_sample["Ingredient"], r=2))

distance_matrix = distance.squareform(\
	np.fromiter(jaccard_generator, dtype=np.float64))

hist, _ = np.histogram(a=distance_matrix, bins=10, range=(0.,1.))
hist_print = [(1.*x) / (1.*NUM_RECIPES * NUM_RECIPES) for x in hist]

tSimilarityCalculated = time.time()
print "Similarity Calculation took: " \
+ str(tSimilarityCalculated - tDataGrouped) + " secs"
print "Distribution of similarities: "
print hist

#CLUSTERING
'''
model = AgglomerativeClustering(n_clusters = NUM_CLUSTERS,\
								linkage="average",\
                                #connectivity=normal_matrix,\
                                affinity="precomputed")
'''
model = DBSCAN(metric="precomputed", eps=CLUSTER_SENSITIVITY, n_jobs=-1)

model.fit(distance_matrix)

df_sample["cluster"] = model.labels_

df_clusters = df_sample.groupby("cluster")

tClustering = time.time()
print "Clustering took: " + str(tClustering-tSimilarityCalculated) + " secs"

print df_clusters.count()

for key, item in df_clusters:
	if key >-1:
		print df_clusters.get_group(key), "\n\n"
