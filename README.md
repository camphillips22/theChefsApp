# theChefsApp
Group Project for CSE6242

# Installation

To install packages, run:
```
pip install -r requirements.txt
```
Note that it is assumed that you have Python 2.7+ (not 3.X), as well as Pandas and Numpy. If not, please install these first.

# Running Server
```
python run.py
```

# Running Development Server
Running the development server allows you to change files and the server will
recognize the changes and restart. To run the development server, run

```
export DEBUG=True
python run.py
```

# Creating a Local Copy of the Database
Run the data_modeling iPython notebook. This will generate chefs.db.

# Running the Clustering Script
Make sure you have a local copy of the database first. Open
clustering_proof_of_concept.py and review the filters at the top of the script.
You can set the number of recipes returned, as well as the category filters to
apply. Comments in the script describe the variables' function. Then, run the
file and see output in the console.
