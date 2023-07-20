# Import necessary modules
import psycopg2
from psycopg2 import sql
import os

# Connection parameters - replace with your actual parameters
db_params = {
    "host" : os.environ['DB_HOST'],
    "port" : os.environ['DB_PORT'],
    "dbname" : os.environ['DB_NAME'],
    "user" : os.environ['DB_USER'],
    "password" : os.environ['DB_PASS']
}

# Connect to your postgres DB
# If a connection cannot be made an Exception will be raised here
conn = psycopg2.connect(**db_params)

# conn.cursor will return a cursor object, you can use this cursor to perform queries
cur = conn.cursor()

# Create teams table
teams_table = """
CREATE TABLE teams (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    city VARCHAR(55) NOT NULL,
    UNIQUE (name, city)
);
"""
cur.execute(teams_table)

# Create players table
players_table = """
CREATE TABLE players (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    UNIQUE (first_name, last_name)
);
"""
cur.execute(players_table)



# Create rosters table              (When we specify primary key: (player_id, team_id), we are saying that the combination of the player and team uniquely identifies each record in the rosters table. This makes sense in the context of the NBA because a player cannot play for the same team more than once in the same season.)
rosters_table = """
CREATE TABLE rosters (
    player_id INTEGER REFERENCES players(id),
    team_id INTEGER REFERENCES teams(id),
    year INTEGER NOT NULL,
    PRIMARY KEY (player_id, team_id, year)
);
"""
cur.execute(rosters_table)

# Create player_stats table
player_yearly_stats_table = """
CREATE TABLE player_yearly_stats (
    id SERIAL PRIMARY KEY,
    player_id INTEGER REFERENCES players(id),
    year INTEGER NOT NULL,
    age INTEGER, 
    pos VARCHAR(15),  
    g INTEGER,
    gs INTEGER,
    mp_per_g DECIMAL(4, 2),
    fg_per_g DECIMAL(4, 2),
    fga_per_g DECIMAL(4, 2),
    fg_pct DECIMAL(4, 2),
    fg3_per_g DECIMAL(4, 2),
    fg3a_per_g DECIMAL(4, 2),
    fg3_pct DECIMAL(4, 2),
    fg2_per_g DECIMAL(4, 2),
    fg2a_per_g DECIMAL(4, 2),
    fg2_pct DECIMAL(4, 2),
    efg_pct DECIMAL(4, 2),
    ft_per_g DECIMAL(4, 2),
    fta_per_g DECIMAL(4, 2),
    ft_pct DECIMAL(4, 2),
    orb_per_g DECIMAL(4, 2),
    drb_per_g DECIMAL(4, 2),
    trb_per_g DECIMAL(4, 2),
    ast_per_g DECIMAL(4, 2),
    stl_per_g DECIMAL(4, 2),
    blk_per_g DECIMAL(4, 2),
    tov_per_g DECIMAL(4, 2),
    pf_per_g DECIMAL(4, 2),
    pts_per_g DECIMAL(4, 2)
    
);
"""
cur.execute(player_yearly_stats_table)

# Create players_awards table
players_awards_table = """
DROP TABLE IF EXISTS players_awards;
CREATE TABLE players_awards (
    id SERIAL PRIMARY KEY,
    player_id INTEGER REFERENCES players(id),
    year INTEGER NOT NULL,
    award_name VARCHAR(50) NOT NULL,
    rank INTEGER NOT NULL,
    UNIQUE (player_id, year, award_name)
);
"""
cur.execute(players_awards_table)


# After executing all the commands, we need to commit to the database to make sure the changes are saved
conn.commit()

# Close the cursor and connection
cur.close()
conn.close()
