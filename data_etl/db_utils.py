from db_queries import get_player_id_by_name

def add_team_record(conn, team_data):
    """
    This function is used to insert a new record into the teams table in the basketball database.

    Parameters:
    conn (psycopg2.extensions.connect): The connection object to the database.
    team_data (dict): The data for the new team to be added. It should be a dictionary containing 
    keys that correspond to the columns of the teams table.

    Returns:
    None
    """
    cur = conn.cursor()
    insert_query = """
    INSERT INTO teams (name, city) VALUES (%(name)s, %(city)s)
    ON CONFLICT (name, city) DO UPDATE SET name = %(name)s, city = %(city)s;
    """
    cur.execute(insert_query, team_data)
    conn.commit()
    

# def add_player_record(conn, player_data):
#     """
#     Inserts a new player record into the players table and returns the id of the inserted record.

#     Parameters:
#     conn (psycopg2.extensions.connection): The database connection.
#     player_data (dict): The player data.

#     Returns:
#     int: The id of the inserted record.
#     """
#     cur = conn.cursor()
#     insert_query = """
#     INSERT INTO players (first_name, last_name) VALUES (%(first_name)s, %(last_name)s) 
#     ON CONFLICT (first_name, last_name) DO NOTHING RETURNING id;
#     """
#     cur.execute(insert_query, player_data)
#     conn.commit()

def add_player_record(conn, player_data):
    first_name = player_data['first_name']
    last_name = player_data['last_name']

    # Create a new cursor
    cur = conn.cursor()

    # Check if the player already exists
    cur.execute(f"SELECT 1 FROM players WHERE first_name=%s AND last_name=%s", (first_name, last_name))
    exists = cur.fetchone()

    # If the player doesn't exist, insert a new record
    if not exists:
        cur.execute(f"INSERT INTO players (first_name, last_name) VALUES (%s, %s)", (first_name, last_name))
        conn.commit()

    cur.close()



def add_roster_record(conn, roster_data):
    """
    This function is used to insert a new record into the rosters table in the basketball database.

    Parameters:
    conn (psycopg2.extensions.connect): The connection object to the database.
    roster_data (dict): The data for the new roster to be added. It should be a dictionary containing keys that correspond to the columns of the rosters table.

    Returns:
    None
    """
    cur = conn.cursor()
    insert_query = """INSERT INTO rosters (player_id, team_id, year) VALUES (%(player_id)s, %(team_id)s, %(year)s)
                  ON CONFLICT (player_id, team_id, year) DO NOTHING"""
    cur.execute(insert_query, roster_data)
    conn.commit()

def add_player_yearly_stats_record(conn, stats_data):
    """
    This function is used to insert a new record into the player_yearly_stats table in the basketball database.

    Parameters:
    conn (psycopg2.extensions.connect): The connection object to the database.
    stats_data (dict): The data for the new player yearly stats to be added. It should be a dictionary containing keys that correspond to the columns of the player_yearly_stats table.

    Returns:
    None
    """
    cur = conn.cursor()
    insert_query = """
    INSERT INTO player_yearly_stats (player_id, year, pos, g, gs, mp_per_g, fg_per_g, fg_pct, fg3_per_g, fg3a_per_g, fg3_pct, fg2_per_g, fg2a_per_g, fg2_pct, efg_pct, ft_per_g, fta_per_g, ft_pct, orb_per_g, drb_per_g, trb_per_g, ast_per_g, stl_per_g, blk_per_g, tov_per_g, pf_per_g, pts_per_g)
    VALUES (%(player_id)s, %(year)s, %(pos)s, %(g)s, %(gs)s, %(mp_per_g)s, %(fg_per_g)s, %(fg_pct)s, %(fg3_per_g)s, %(fg3a_per_g)s, %(fg3_pct)s, %(fg2_per_g)s, %(fg2a_per_g)s, %(fg2_pct)s, %(efg_pct)s, %(ft_per_g)s, %(fta_per_g)s, %(ft_pct)s, %(orb_per_g)s, %(drb_per_g)s, %(trb_per_g)s, %(ast_per_g)s, %(stl_per_g)s, %(blk_per_g)s, %(tov_per_g)s, %(pf_per_g)s, %(pts_per_g)s);
    """
    cur.execute(insert_query, stats_data)
    conn.commit()


# Function that logs award data to the database
# The function should take a year and a dictionary of award data as parameters and log the award data to the database.
# The table that the data is being logged into has the following columns: id, player_id, year, award_name, rank (rank is determined by the order in which the players are listed on the webpage)
def log_awards_data(conn, year, awards_dict):
    """
    This function is used to insert a new record into the players_awards table in the basketball database.

    Parameters:
    conn (psycopg2.extensions.connect): The connection object to the database.
    year (int): The year of the awards.
    awards_dict (dict): The data for the new awards to be added. It should be a dictionary containing keys that correspond to the award names and values that are lists of player names.

    Returns:
    None

    Example:
    awards_dict = {
        'MVP': ['LeBron James', 'Kevin Durant', 'Kobe Bryant'],
        'DPOY': ['Dwight Howard', 'LeBron James', 'Kevin Durant']
    }
    """

    for key, value in awards_dict.items():
        award = key
        receiving_votes_list = value
        for i in range(len(receiving_votes_list)):
            rank = i + 1
            cur = conn.cursor()
            player_name = receiving_votes_list[i]
            # Check if the player already exists
            try:
                first_name, last_name = player_name.split(' ', 1) # Splitting by the first space character
            except ValueError:
                first_name = player_name
                last_name = ''
            cur.execute("SELECT 1 FROM players WHERE first_name = %s AND last_name = %s", (first_name, last_name))
            exists = cur.fetchone()

            # If the player doesn't exist, insert a new record
            if not exists:
                cur.execute("INSERT INTO players (first_name, last_name) VALUES (%s, %s)", (first_name, last_name))

                conn.commit()

            # Get the player_id of the player
            player_id = get_player_id_by_name(conn, player_name)
            award_data = {
                'player_id': player_id,
                'year': year,
                'award_name': award,
                'rank': rank
            }

            # Check if the award already exists for the player for that year
            cur.execute(f"SELECT 1 FROM players_awards WHERE player_id = {player_id} AND year = {year} AND award_name = '{award}'")
            exists = cur.fetchone()

            # If the award doesn't exist, insert a new record
            if not exists:
                insert_query = """
                INSERT INTO players_awards (player_id, year, award_name, rank) VALUES (%(player_id)s, %(year)s, %(award_name)s, %(rank)s);
                """
                cur.execute(insert_query, award_data)
                conn.commit()
            cur.close()





def get_column_names(conn, table_name):
    """
    This function is used to fetch the column names of a given table in the connected database.

    Parameters:
    conn (psycopg2.extensions.connect): The connection object to the database.
    table_name (str): The name of the table to get the column names from.

    Returns:
    list: A list of column names of the given table.
    """
    cur = conn.cursor()
    query = f"""
    SELECT column_name
    FROM information_schema.columns
    WHERE table_name   = '{table_name}'
    ORDER BY ordinal_position;
    """
    cur.execute(query)
    column_names = [row[0] for row in cur.fetchall()]
    return column_names

# Function that updates a column in a table in the database based on the player_id and year
# The function should take the following parameters: conn, table_name, column_name, value, player_id, year
# The function should return None
def update_column(conn, table_name, column_name, value, player_id, year):
    """
    This function is used to update a column of a given table in the connected database.

    Parameters:
    conn (psycopg2.extensions.connect): The connection object to the database.
    table_name (str): The name of the table to update the column in.
    column_name (str): The name of the column to update.
    value (str): The value to update the column with.
    player_id (int): The player_id of the player to update the column for.
    year (int): The year to update the column for.

    Returns:
    None
    """
    cur = conn.cursor()
    query = f"""
    UPDATE {table_name}
    SET {column_name} = %s
    WHERE player_id = %s AND year = %s;
    """
    cur.execute(query, (value, player_id, year))
    conn.commit()
    cur.close()


