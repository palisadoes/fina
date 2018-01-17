# fina
The *fina* repostitory attempts to determine whether there is a correlation between the BMI of a professional swimmer and their performance.

# Data
The data used and created by *fina* each have a different stories.
## Data Created by *fina* Scripts
Data from disparate, publicly available sources on the web is used to create: 
1. **Swimmer profiles** of names, height, weight, and birthdate, 
2. **Statistics** of swimmer performance per event that also includes their BMI, speed per Kg and overall time.
3. **Graphs** of swimmer performance that compare various combinations of speed, BMI and efficiency (speed / Kg) by gender and swimming stroke over short and long courses, measured in both meters and yards.

##Original Data Sources
The original sources of data used to create thes profiles and statistics include:
1. **HTML** web scrapes of all the athlete profiles found on fina.org.
2. **LENEX** data of multiple meets found on the web.
3. **XML** files created by converting meet entry lists "*Entry List by NOC*" PDF files.
4. **CSV** files of the results of the Rio 2016 Olympic games created manually from the meet's PDF results file.

These file formats were chosen to make the aggregation of information easier by the repository's python programming scripts.

# File Layout
The repository's data is located in an easy to navigate directory tree.

| Subdirectory|Contains| 
| ------------- |-------------| 
| *bin/*| Data manipulation scripts|
| *data/analysis*| The final swimmer database  file (CSV) |
|  *data/athletes/entry-lists*| Meet entry lists containing athlete height, weight and birthdate information |
| *data/athletes/fina.org*| Athlete data found on the fina.org profile pages. |
| *data/athletes/graphs*| Graphs used for analysis|
| *data/athletes/profiles*| Athlete data converted to a standardized format to help with the creation of the database.|
|*data/meets/LENEX*| Meet LENEX data.|
|*data/meets/olympics*| Rio 2016 meet data manually created from the PDF results book.|

Many of the files mentioned are used by the scripts in the creation of the final database and charts.

# Scripts

| Subdirectory|Contains| 
| ------------- |-------------| 
| *bin/make_database.py*| Creates the final database|
| *bin/make_graphs.py*| Creates graphs from the database|
| *bin/make_profiles.py*| Creates graphs from the database|

## Script Usage
The scripts are used in the following ways to use and create the data:

###make_profiles.py
Used to create the single unified athlete profile file.

    bin/make_profiles.py [-h] -f FINA_DIRECTORY -l LISTING_DIRECTORY -p PROFILE_DIRECTORY
    
    bin/make_profiles.py -f data/athletes/fina.org -l data/athletes/entry-lists -p data/athletes/profiles

###make_database.py
Used to create the single unified athlete event database file.

     make_database.py [-h] -l LENEX_DIRECTORY -o OLYMPIC_DIRECTORY -p PROFILE_DIRECTORY -d DATABASE_FILE
     
      bin/make_database.py -l data/meets/LENEX -o data/meets/olympics -p data/athletes/profiles -d data/analysis/all-meet-data.csv 

###make_graphs.py
Used to create the single unified athlete event database file.




 
