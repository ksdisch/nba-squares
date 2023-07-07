# app.py
from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_nav import Nav
from flask_nav.elements import *
from dominate.tags import img


###############################################
#      Define navbar with logo                #
###############################################
logo = img(src='/Users/kyledisch/Desktop/MY_PROJECTS/nba-squares/static/imgs/bball.jpeg', height="50", width="50", style="margin-top:-15px")
#here we define our menu items
topbar = Navbar(logo,
                View('News', 'get_news'),
                View('Live', 'get_live'),
                View('Programme', 'get_programme'),
                View('Classement', 'get_classement'),
                View('Contact', 'get_contact'),
                )

# registers the "top" menubar
nav = Nav()
nav.register_element('top', topbar)


app = Flask(__name__)
Bootstrap(app)

@app.route('/')
def home():
    return render_template('index.html', title='Squares Game, NBA Edition')

if __name__ == '__main__':
    app.run(debug=True)
# end of app.py

# /Users/kyledisch/Desktop/MY_PROJECTS/nba-squares/static/imgs