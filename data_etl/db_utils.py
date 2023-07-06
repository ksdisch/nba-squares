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
    insert_query = """
    INSERT INTO rosters (player_id, team_id, year) VALUES (%(player_id)s, %(team_id)s, %(year)s);
    """
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

def add_players_awards_record(conn, award_data):
    """
    This function is used to insert a new record into the players_awards table in the basketball database.

    Parameters:
    conn (psycopg2.extensions.connect): The connection object to the database.
    award_data (dict): The data for the new player award to be added. It should be a dictionary containing keys that correspond to the columns of the players_awards table.

    Returns:
    None
    """
    cur = conn.cursor()
    insert_query = """
    INSERT INTO players_awards (player_id, award_type, year)
    VALUES (%(player_id)s, %(award_type)s, %(year)s);
    """
    cur.execute(insert_query, award_data)
    conn.commit()


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

