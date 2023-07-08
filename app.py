# app.py
from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_nav import Nav
from flask_nav.elements import Navbar, Subgroup, View, Link, Text, Separator
from dominate.tags import img


app = Flask(__name__)

Bootstrap(app)
nav = Nav(app)

nav.register_element('my_nav', Navbar(
    'thenav',
    View('Home Page', 'index')))

@app.route('/')
def index(): # Home page
    return render_template('index.html', title='NBA Grid Game')

if __name__ == '__main__':
    app.run(debug=True)
# end of app.py

# /Users/kyledisch/Desktop/MY_PROJECTS/nba-squares/static/imgs