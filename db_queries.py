import psycopg2
import os
import pprint
from collections import OrderedDict
import psycopg2.extras

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


# File for functions that query the database.



# Function that returns the tables of a database. The function takes the following parameters: the connection object.
def get_tables(conn):
    try:
        cursor = conn.cursor()
        # Get all of the tables in a database
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
        tables = cursor.fetchall()
        tables_list = [table[0] for table in tables]
        return tables_list
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error while getting tables of PostgreSQL database", error)
        # Close the cursor
        cursor.close()
        raise
    finally:
        # Close the cursor
        if (conn):
            cursor.close()

# Function that returns the columns of a table/view. The function takes the following parameters: the connection object, the table name, and a boolean that determines whether to query tables or views.
def get_columns(conn, table):
    try:
        with conn.cursor() as cursor:
            # Get all of the columns in a table or view
            cursor.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table}' and table_schema not in ('information_schema', 'pg_catalog');")
            columns = cursor.fetchall()

        # Format the results as a list of strings
        return [column[0] for column in columns]

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error while getting columns of PostgreSQL table/view", error)
        raise



# Function for retrieving the last n rows of a given table. 
def get_last_n_rows(table, n):
    try:
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        query = "SELECT * FROM " + table + " ORDER BY id DESC LIMIT " + str(n)
        cursor.execute(query)
        records = cursor.fetchall()
        return records
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error while getting last n rows of PostgreSQL database", error)
        # Close the cursor
        cursor.close()
        raise
    finally:
        # Close the cursor
        if (conn):
            cursor.close()


# player_yearly_stats_columns = get_columns(conn, 'player_yearly_stats')
# print(player_yearly_stats_columns)



# ----------------- INDIVIDUAL TABLE QUERIES ----------------- #

# ----------------- PLAYER_YEARLY_STATS TABLE ----------------- #

# Function to retrieve the full rows for players that have averaged either less than, equal to, or greater than a certain value of a given stat. 
# The user can choose whether or not to specify position(s) The default will be all positions, if they choose to specify, it needs to be a list  made up the following choices: 'PG', 'SG', 'SF', 'PF', 'C'
# The function should take the following parameters: conn, date, stat, value, position, comparison.
# The function should return the rows of the players that meet the criteria.
def get_players_by_stat_from_db(conn, year, stat, value, positions, comparison):
    if comparison == 'lte':
        op = '<='
    elif comparison == 'gte':
        op = '>='
    else:
        op = '='


    try:
        with conn.cursor() as cur:
            query = f"""
                SELECT * 
                FROM player_avg_view
                WHERE year >= %s AND pos IN %s AND {stat} {op} %s
                ORDER BY {stat} DESC
            """
            cur.execute(query, (year, tuple(positions), value))
            records = cur.fetchall()

            # Inspect the order of column headers
            column_headers = [desc[0] for desc in cur.description]
            print(f'Column headers: {column_headers}')

            # Inspect a row of data
            if records:  # Make sure there is at least one record
                print(f'A row of data: {records[0]}')

            # Create a list of ordered dictionaries
            records_dict_list = [OrderedDict(zip(column_headers, row)) for row in records]

            return records_dict_list
    except Exception as e:
        print("Error in get_players_by_stat_from_db: ", str(e))
        return []
    








# ----------------- PLAYERS TABLE ----------------- #

# Function that returns the player_id of a player given their name. The function takes the following parameters: the connection object, the player's name.
def get_player_id_by_name(conn, name):
    try:
        with conn.cursor() as cursor:
            # Get the player_id of a player given their name
            try:
                first_name, last_name = name.split(' ', 1) # Splitting by the first space character
            except ValueError:
                first_name = name
                last_name = ''
            cursor.execute("SELECT id FROM players WHERE first_name = %s AND last_name = %s", (first_name, last_name))

            player_id = cursor.fetchone()[0]

        # Format the results as a list of strings
        return player_id

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error while getting player_id of player", error)
        raise





# ----------------- PLAYERS_AWARDS TABLE ----------------- #
# Function to retrieve the full rows for players that received votes for a given award in a given year.
# The function should take the following parameters: conn, year, award_names, max_rank.
# The function should return the rows of the players that meet the criteria.
def get_players_by_award_from_db(conn, year, award_names, max_rank):
    try:
        with conn.cursor() as cur:
            query = f"""
                SELECT * 
                FROM players_awards
                WHERE year = %s AND award_name IN %s AND rank <= %s
                ORDER BY award_name, rank
            """
            cur.execute(query, (year, tuple(award_names), max_rank))
            records = cur.fetchall()

            # Inspect the order of column headers
            column_headers = [desc[0] for desc in cur.description]
            print(f'Column headers: {column_headers}')

            # Inspect a row of data
            if records:  # Make sure there is at least one record
                print(f'A row of data: {records[0]}')

            # Create a list of ordered dictionaries
            records_dict_list = [OrderedDict(zip(column_headers, row)) for row in records]

            return records_dict_list
    except Exception as e:
        print("Error in get_players_by_award_from_db: ", str(e))
        return []
    
    




# ----------------- ROSTERS TABLE ----------------- #



# ----------------- TEAMS TABLE ----------------- #
def get_teams_and_cities(conn):
    """
    This function is used to retrieve all values from the name and city columns of the teams table in the basketball database.

    Parameters:
    conn (psycopg2.extensions.connect): The connection object to the database.

    Returns:
    city_team_dict (dict): A dictionary with cities as keys and team names as values.

    Example:
    city_team_dict = {
        'Atlanta': 'Hawks',
        'Boston': 'Celtics'
    }
    """
    try:
        with conn.cursor() as cur:
            query = """
                SELECT city, name
                FROM teams
            """
            cur.execute(query)
            records = cur.fetchall()

            # Convert records into the desired dictionary format
            city_team_dict = {city: name for city, name in records}

            return city_team_dict

    except Exception as e:
        print("Error in get_teams_and_cities: ", str(e))
        return {}
