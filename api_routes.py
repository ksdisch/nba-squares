from flask import Blueprint, jsonify, g, url_for
from db_queries import get_last_n_rows, get_players_by_stat_from_db, get_players_by_award_from_db
from flask import Blueprint, jsonify, request
import os
import psycopg2

# Define database connection parameters. These parameters will be read from the environment variables.
db_params = {
    "host" : os.environ['DB_HOST'],
    "port" : os.environ['DB_PORT'],
    "dbname" : os.environ['DB_NAME'],
    "user" : os.environ['DB_USER'],
    "password" : os.environ['DB_PASS']
}

# Establish a connection to the database using the defined parameters.
conn = psycopg2.connect(**db_params)


api = Blueprint('api', __name__)

# Define the API routes
# curl "http://localhost:5000/api/v1/records/players/10"
@api.route('/records/<string:table>/<int:n>', methods=['GET'])
def api_get_last_n_rows(table, n):
    records = get_last_n_rows(table, n)
    return jsonify(records)

# curl "http://localhost:5000/api/v1/players/1980/pts_per_g/33/['PG','SG', 'SF', 'PF', 'C']/gt"
@api.route('/players', methods=['GET'])
def api_get_players_by_stat_from_db():
    date = request.args.get('date')
    stat = request.args.get('stat')
    value = int(request.args.get('value'))
    positions = request.args.get('positions').split(',')  # Convert positions from comma-separated string to list
    comparison = request.args.get('comparison')
    
    # Use the connection in g.pg_conn
    records = get_players_by_stat_from_db(conn, date, stat, value, positions, comparison)
    # print(jsonify(records).get_data(as_text=True))
    return jsonify(records)



@api.route('/players/awards', methods=['GET'])
def api_get_players_by_award_from_db():
    date = request.args.get('date')
    award = request.args.get('award')
    rank = int(request.args.get('rank'))
    positions = request.args.get('positions').split(',')

    records = get_players_by_award_from_db(conn, date, award, rank, positions)

    return jsonify(records)



# curl "http://localhost:5000/api/v1/players/1980/pts_per_g/33/['PG','SG', 'SF', 'PF', 'C']/gt"


# export DB_HOST="localhost" export DB_PORT=5432 export DB_USER="postgres" export DB_PASS="Bashor47" export DB_NAME="nba-data" 