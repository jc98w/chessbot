A Chess program

Has built in bot that can read from a database and pick the move with the highest winning percentage.
Connects to MongoDB via pymongo.

Getting pymongo and pymongo.server_api to import properly:

1. Create a python virtual environment for the project that will store the extra libraries necessary.
   1. "source venv/bin/activate" for linux or "venv\Scripts\activate for windows"
   2. pip install 'pymongo[srv]'
2. Set venv/bin/python (linux) or 'venv\Scripts\python' (windows) as the interpreter for the project.

Pass valid username and password as commandline args for project
