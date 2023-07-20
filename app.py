from flask import Flask, render_template, g, current_app, request, jsonify
from flask_bootstrap import Bootstrap
from flask_nav import Nav
from flask_nav.elements import Navbar, Subgroup, View, Link, Text, Separator
from db_queries import get_players_by_stat_from_db, get_last_n_rows, get_columns, get_teams_and_cities
from square_data import get_players_for_teams
from dominate.tags import img
from square_data import get_players_for_square
import os
import psycopg2
from psycopg2 import pool
from datetime import date
import random

def create_app():
    app = Flask(__name__)

    app.db_pool = psycopg2.pool.SimpleConnectionPool(1, 10,
        host=os.environ['DB_HOST'],
        port=os.environ['DB_PORT'],
        dbname=os.environ['DB_NAME'],
        user=os.environ['DB_USER'],
        password=os.environ['DB_PASS'])
    
    Bootstrap(app)
    nav = Nav(app)

    nav.register_element('my_nav', Navbar(
        'thenav',
        View('Home Page', 'index'),
        View('Reference', 'reference')))

    @app.before_request
    def before_request():
        # Assign a connection to g.pg_conn for each request
        g.pg_conn = current_app.db_pool.getconn()
    
    # Create a custom Jinja filter
    def enumerate_filter(sequence, start=0):
        return enumerate(sequence, start)
    
    # Register the filter with the Jinja environment
    app.jinja_env.filters['enumerate'] = enumerate_filter

    from api_routes import api
    app.register_blueprint(api, url_prefix='/api/v1')

    @app.route('/')
    @app.route('/')
    def index(): 
        teams_cities_dict = get_teams_and_cities(g.pg_conn)
        x_teams = random.sample(list(teams_cities_dict.keys()), 3)
        y_teams = random.sample(list(teams_cities_dict.keys()), 3)
        players_by_square = {}

        for y_team in y_teams:
            for x_team in x_teams:
                square_key = f"{y_team}_{x_team}"
                players_by_square[square_key] = get_players_for_square(g.pg_conn, team1=x_team, team2=y_team)

        return render_template('index.html', title='NBA Grid Game', x_teams=x_teams, y_teams=y_teams, players_by_square=players_by_square)

        







    @app.route('/reference', methods=['GET', 'POST'])
    def reference():
        data = []
        position_choices = ['PG', 'SG', 'SF', 'PF', 'C']
        default_position_choices = ['PG', 'SG', 'SF', 'PF', 'C']
        default_year = date.today().year - 1
        headers = get_columns(g.pg_conn, 'player_avg_view')
        stat_choices = headers
        current_year = date.today().year
        selected_values = {
            'year': default_year,
            'stat': 'pts_per_g',
            'value': '33',
            'positions': default_position_choices,
            'comparison': 'gt',
        }
        if request.method == 'POST':
            year = int(request.form.get('year', default_year))
            stat = request.form.get('stat', 'pts_per_g')
            value = request.form.get('value', '33')
            positions = request.form.getlist('positions')
            if not positions:  # if positions list is empty
                positions = default_position_choices
            comparison = request.form.get('comparison', 'gt')

            records = get_players_by_stat_from_db(g.pg_conn, year, stat, value, positions, comparison)
            data = jsonify(records).get_json()
            # Update selected values to reflect what user has submitted
            selected_values = {
                'year': year,
                'stat': stat,
                'value': value,
                'positions': positions,
                'comparison': comparison,
            }
        return render_template('reference.html', title='NBA Grid Game', data=data, headers=headers, position_choices=position_choices, stat_choices=stat_choices, current_year=current_year, selected_values=selected_values)

    @app.teardown_appcontext
    def close_conn(error):
        # At the end of the request, put the connection back in the pool
        if hasattr(g, 'pg_conn'):
            current_app.db_pool.putconn(g.pg_conn)
            
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)



    
