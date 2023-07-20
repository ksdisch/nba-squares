# Dictionary that maps the comparison operators to their corresponding SQL operators
sql_ops = {
    'eq': '=',
    'lte': '<=',
    'gte': '>=',
    'gt': '>',
    'lt': '<'
}

def get_players_for_square(conn, team1=None, team2=None, x_stat=None, x_comp=None, x_value=None, y_accolade=None):
    """
    This function returns the players that fit the criteria for the given square.

    Parameters:
    conn (psycopg2.extensions.connect): The connection object to the database.
    team1 (str): The name of the first team.
    team2 (str): The name of the second team.
    x_stat (str): The statistic to be used for the x-axis.
    x_comp (str): The comparison operator to be used for the x-axis.
    x_value (int): The value to be used for the x-axis.
    y_accolade (str): The accolade to be used for the y-axis.

    Returns:
    players (list): A list of tuples containing the first and last names of the players that fit the criteria for the given square.

    Example:
    get_players_for_square(conn, team1='Los Angeles Lakers', team2='Boston Celtics')
    get_players_for_square(conn, team1='Los Angeles Lakers', x_stat='pts_per_g', x_comp='gt', x_value=33)
    get_players_for_square(conn, team1='Los Angeles Lakers', y_accolade='MVP')
    get_players_for_square(conn, x_stat='pts_per_g', x_comp='gt', x_value=33, y_accolade='MVP')

    """
    query = ""
    params = ()

    # 2-team intersection
    if team1 and team2:
        query = """
        SELECT DISTINCT p.first_name, p.last_name
        FROM players p
        JOIN rosters r1 ON p.id = r1.player_id
        JOIN rosters r2 ON p.id = r2.player_id
        JOIN teams t1 ON r1.team_id = t1.id
        JOIN teams t2 ON r2.team_id = t2.id
        WHERE t1.name = %s AND t2.name = %s
        """
        params = (team1, team2)

    # Team and x_stat intersection
    elif x_stat and x_comp and x_value and team1:
        x_comp = sql_ops[x_comp]
        query = """
        SELECT DISTINCT p.first_name, p.last_name
        FROM players p
        JOIN player_avg_view v ON p.id = v.player_id
        JOIN rosters r ON p.id = r.player_id
        JOIN teams t ON r.team_id = t.id
        WHERE t.name = %s AND v.year = r.year AND v.{x_stat} {x_comp} %s
        """.format(x_stat=x_stat, x_comp=x_comp)
        params = (team1, x_value)

    # Team and y_accolade intersection
    elif team1 and y_accolade:
        query = """
        SELECT DISTINCT p.first_name, p.last_name
        FROM players p
        JOIN players_awards a ON p.id = a.player_id
        JOIN rosters r ON p.id = r.player_id
        JOIN teams t ON r.team_id = t.id
        WHERE t.name = %s AND a.award_name = %s AND a.year = r.year
        """
        params = (team1, y_accolade)

    # x_stat and y_accolade intersection
    elif x_stat and x_comp and x_value and y_accolade:
        x_comp = sql_ops[x_comp]
        query = """
        SELECT DISTINCT p.first_name, p.last_name
        FROM players p
        JOIN player_avg_view v ON p.id = v.player_id
        JOIN players_awards a ON p.id = a.player_id
        WHERE v.year = a.year AND v.{x_stat} {x_comp} %s AND a.award_name = %s
        """.format(x_stat=x_stat, x_comp=x_comp)
        params = (x_value, y_accolade)

    cur = conn.cursor()
    cur.execute(query, params)
    players = cur.fetchall()
    cur.close()

    return players

        
    


    


def get_players_for_teams(conn, team1, team2):
    """ 
    This function returns the players that have played for both teams.

    Parameters:
    conn (psycopg2.extensions.connect): The connection object to the database.
    team1 (str): The name of the first team.
    team2 (str): The name of the second team.

    Returns:
    players (list): A list of tuples containing the first and last names of the players that have played for both teams.

    Example:
    get_players_for_teams(conn, 'Los Angeles Lakers', 'Boston Celtics')

    """
    query = """
    SELECT p.first_name, p.last_name
    FROM players p
    JOIN rosters r1 ON p.id = r1.player_id
    JOIN rosters r2 ON p.id = r2.player_id
    JOIN teams t1 ON r1.team_id = t1.id
    JOIN teams t2 ON r2.team_id = t2.id
    WHERE t1.name = %s AND t2.name = %s
    """
    cur = conn.cursor()
    cur.execute(query, (team1, team2))
    players = cur.fetchall()
    cur.close()
    return players

# def get_players_for_team_accolade_square()
    



# def get_players_for_team_stat_square()

