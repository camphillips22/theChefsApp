# theChefsApp
Group Project for CSE6242

# Installation

To install packages, run:
```bash
pip install -r requirements.txt
```
Note that it is assumed that you have Python 2.7+ (not 3.X), as well as Pandas and Numpy. If not, please install these first.

# Running Server
```bash
python run.py
```

# Running Development Server
Running the development server allows you to change files and the server will
recognize the changes and restart. To run the development server, run

```bash
export DEBUG=True
python run.py
```

# Creating a Local Copy of the Database
Run 
```python
python init_db.py
```
Be patient as it will take a while. It should update on it's progress.

# Running the Clustering Algorithm
You can test the clustering by starting a flask shell by running.
```bash
export FLASK_APP=run.py
flask shell
```
The shell will provide a few pre-imported classes including the flask database
and all of the current models.

Clustering and filtering can be performed by calling the function
`Recipe.cluster_on_filters(clust_fact, *args)` where `clust_fact` is the cluster
sensitivity of the DBSCAN algorithm and `*args` are alternating arguments of
`db.Model` and name of entry. An few examples of this are shown below.

```python
Recipe.cluster_on_filters(0.7, Course, 'Main course', Diet, 'Vegan')
Recipe.cluster_on_filters(0.7, Ethnicity, 'American')
```


Grouping and filtering can be performed by calling
`Recipe.group_on_filters(*args)` where `*args` are the name of entry; 

``` python
Recipe.group_on_filters(Ethnicity)
Recipe.group_on_filters(Diet, Ethnicity)
```