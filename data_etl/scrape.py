import time
import requests
from bs4 import BeautifulSoup
import string
import os
import psycopg2

# Import the necessary utility functions for working with the database
from db_utils import add_player_record, add_player_yearly_stats_record, add_players_awards_record, add_roster_record, add_team_record, get_column_names
from misc_funcs import get_data_type


### REMINDER: LaMarcus Aldrige, Nene, Keith Benson, Daequan Cook, Serge Ibaka, Rudy Hackett stats may be missing from restarting loop after debugging

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

# Prepare a list of alphabet letters to loop through for player names
alphabet = list(string.ascii_lowercase)

teams_table_cols = get_column_names(conn, 'teams')
players_table_cols = get_column_names(conn, 'players')
rosters_table_cols = get_column_names(conn, 'rosters')
player_yearly_stats_table_cols = get_column_names(conn, 'player_yearly_stats')
player_awards_table_cols = get_column_names(conn, 'player_awards')

# Skip these for now and add them in after to maintain database integrity
duplicate_names = ['Chris Johnson', 'Cliff Robinson', 'Marcus Williams'] # http://www.insidehoops.com/forum/showthread.php?288724-NBA-players-that-have-the-same-first-and-last-name

# Loop through each letter of the alphabet
for letter in alphabet:
    # Define the url that contains player data for players whose last name starts with the current letter.
    player_list_url = f'https://www.basketball-reference.com/players/{letter}/'

    # Implement rate limiting by pausing execution for 4.5 seconds for each iteration.
    time.sleep(2)
    # Send a GET request to the url and parse the response text with BeautifulSoup.
    response = requests.get(player_list_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    # TODO: Scrape a list of links for the players on each letter's page

    # Find the table on the webpage that contains player data and extract all rows from it.
    players_table = soup.find('table', {'id': 'players'})
    rows = players_table.find_all('tr')

    # Iterate through each row in the table. Each row corresponds to a player.
    for row in rows:
        # Within each row, find the 'th' tag which corresponds to the player name.
        th = row.find('th', {'scope': 'row'})
        
        # If a 'th' tag was found, find the 'a' tag within it which contains the player's name.
        if th is not None:
            # Find the 'a' tag within the 'th' tag
            a = th.find('a')
            
            
            # If an 'a' tag was found, extract the player's name from it.
            if a is not None:
                player_name = a.text
                name_parts = player_name.split()
                first_name = name_parts[0]
                last_name = " ".join(name_parts[1:])
                # Check if the player already exists in the database. If yes, skip to the next player. If no, add the player to the database.
                cur = conn.cursor()
                player_exists_query = "SELECT 1 FROM players WHERE first_name = %s AND last_name = %s"
                params = (first_name, last_name)
                cur.execute(player_exists_query, params)
                player_exists = cur.fetchone()
                # If player already exists, skip to next player
                if player_exists:
                    print(f"Player {first_name} {last_name} already exists, moving to the next player...")
                    continue
                # If player is one with duplicate names, skip for now.
                elif player_name in duplicate_names:
                    print(f"There have been multiple players with the name {first_name} {last_name} in NBA history, skipping for now. Remember to go back and add these player's stats in manually...")
                    continue
                else:
                    # STORE NEW PLAYER RECORD
                    add_player_record(conn=conn, player_data={'first_name': first_name, 'last_name': last_name})

                # After adding the player to the database, retrieve the player's id.
                player_id_query = "SELECT MAX(id) FROM players WHERE first_name = %s AND last_name = %s"
                params = (first_name, last_name)
                cur.execute(player_id_query, params)
                # Fetch the result
                result = cur.fetchone()
                # Since fetchone() returns a tuple, you can access the player_id as follows:
                player_id = result[0]

                print(f"The player_id of the most recently added player is: {player_id}")
                
                # Send a GET request to the player's page and parse the response text with BeautifulSoup.
                player_url = f'https://www.basketball-reference.com{a["href"]}'
                time.sleep(2)
                response = requests.get(player_url)
                player_soup = BeautifulSoup(response.text, 'html.parser')

                # Find the table on the player's page that contains the player's per game stats.
                per_game_table = player_soup.find('table', {'id': 'per_game'})

                # Extract all rows from the table. Each row corresponds to a season.
                rows = per_game_table.find_all('tr')[1:]

                print(f"Scraping Per Game table for {player_name}")

                # Iterate through each row in the table.
                for row in rows:
                    # time.sleep(4.5) # Rate limiting pause
                    # Implement rate limiting by pausing execution for 4.5 seconds for each iteration.
                    season = row.find('th')
                    if season is not None and season.text != '':
                        season_text = season.text
                        if season_text[0] == '1' or season_text[0] == '2':
                            try:
                                year = int(season.text[:4])
                                if year < 1979:
                                    continue
                            except ValueError:
                                continue
                        else:
                            continue
                    else: 
                        continue

                    # Extract the player's age from the row.                    
                    age = row.find('td', {'data-stat': 'age'})
                    
                    # Extract the player's age from the row.
                    tds = row.find_all('td')

                    print(f'\n{player_name} {year} per game statistics...')
                    
                    # Prepare a dictionary to store the player's stats data.                    
                    player_yearly_stats_data = {'player_id': player_id, 'year': year, 'age': age}
                    player_yearly_stats_data.setdefault('fg3_per_g', None)
                    player_yearly_stats_data.setdefault('fg3a_per_g', None)
                    player_yearly_stats_data.setdefault('fg3_pct', None)

                    for td in tds:
                        # If the td has an 'a' tag inside of it, get the text of that
                        a = td.find('a')
                        cell_column = td.get('data-stat')
                        if cell_column == 'team_id' and a is not None:
                            team_url = f'https://www.basketball-reference.com{a["href"]}'
                            time.sleep(2)
                            response = requests.get(team_url)
                            team_soup = BeautifulSoup(response.text, 'html.parser')
                            team_info_div = team_soup.find('div', {'data-template': 'Partials/Teams/Summary'})
                            if team_info_div:
                                span_tags = team_info_div.find_all('span')
                                if span_tags:
                                    team = span_tags[1].text
                                    city, team_name = team.split(" ", 1)

                                    print(f'\nCITY: {city}')
                                    print(f'TEAM NAME: {team_name}')

                                    team_data = {'name': team_name, 'city': city}
                                    add_team_record(conn, team_data)

                        if a is not None:
                            cell_value = a.text
                        else:
                            # Otherwise, just get the text of the td
                            cell_value = td.text
                        print(f'{cell_column}: {cell_value}\n')

                        if cell_column != 'team_id' and cell_column != 'lg_id':
                            # Update this part
                            if get_data_type(cell_value) == 'float':
                                player_yearly_stats_data[cell_column] = float(cell_value) if cell_value != '' else None
                            elif get_data_type(cell_value) == 'int':
                                player_yearly_stats_data[cell_column] = int(cell_value) if cell_value != '' else None
                            else: 
                                player_yearly_stats_data[cell_column] = cell_value if cell_value != '' else None

                    print(player_yearly_stats_data)
                    if player_yearly_stats_data['year'] != 'Care':
                        add_player_yearly_stats_record(conn, player_yearly_stats_data)


def scrape_url(url):
    response = requests.get(url)
    if response.status_code == 200:
        webpage = response.text
        soup = BeautifulSoup(webpage, 'html.parser')
        return soup
    else:
        print(f'Failed to scrape {url}')
        return None

def get_player_links(soup):
    player_links = []
    for link in soup.find_all('a'):
        player_links.append(link.get('href'))
    return player_links

# you can add more functions to extract more specific data from the webpage



