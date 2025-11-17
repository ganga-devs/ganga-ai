# Installation of dependencies
To create the python environment do
```[bash]
pyenv virtualenv 3.11 ganga-ai
pyenv activate ganga-ai
pip install -r requirements.txt
```

# Running the code
To run the code do
```[bash]
$ ipython
$ %load_ext ganga_ai
$ %%assist <your query>
$ %%login
$ %%logout
```
