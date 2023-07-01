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
    city VARCHAR(55) NOT NULL
);
"""
cur.execute(teams_table)

# Create players table
players_table = """
CREATE TABLE players (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL
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
    pos VARCHAR(15),   
    g INTEGER,
    gs INTEGER,
    mp DECIMAL(4, 2),
    fg DECIMAL(4, 2),
    fg_pct DECIMAL(4, 2),
    three_pt DECIMAL(4, 2),
    three_pt_att DECIMAL(4, 2),
    three_pt_pct DECIMAL(4, 2),
    two_pt DECIMAL(4, 2),
    two_pt_att DECIMAL(4, 2),
    two_pt_pct DECIMAL(4, 2),
    efg_pct DECIMAL(4, 2),
    ft DECIMAL(4, 2),
    fta DECIMAL(4, 2),
    ft_pct DECIMAL(4, 2),
    orb DECIMAL(4, 2),
    drb DECIMAL(4, 2),
    trb DECIMAL(4, 2),
    ast DECIMAL(4, 2),
    stl DECIMAL(4, 2),
    blk DECIMAL(4, 2),
    tov DECIMAL(4, 2),
    pf DECIMAL(4, 2),
    pts DECIMAL(4, 2)
    
);
"""
cur.execute(player_yearly_stats_table)

# Create players_awards table
players_awards_table = """
CREATE TABLE players_awards (
    id SERIAL PRIMARY KEY,
    player_id INTEGER REFERENCES players(id),
    award_type VARCHAR(50) NOT NULL,
    year INTEGER NOT NULL
);
"""
cur.execute(players_awards_table)


# After executing all the commands, we need to commit to the database to make sure the changes are saved
conn.commit()

# Close the cursor and connection
cur.close()
conn.close()
