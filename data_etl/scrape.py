import time
import requests
from bs4 import BeautifulSoup
import psycopg2
import pprint
import string

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time



# Import the necessary utility functions for working with the database
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db_queries import get_last_n_rows, get_players_by_stat_from_db, get_columns, get_tables, get_player_id_by_name
from db_utils import add_player_record, add_player_yearly_stats_record, log_awards_data, add_roster_record, add_team_record, get_column_names, update_column
from misc_funcs import get_data_type

### REMINDER: #Matt Zunic, Ivica Zubac, Nate Robinson, CJ Miles, Tracy McGrady, Rashard Lewis, LaMarcus Aldrige, Nene, Keith Benson, Daequan Cook, Serge Ibaka, Rudy Hackett stats may be missing from restarting loop after debugging

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

# Function to scrape yearly award data from basketball-reference.com
# The function should take a year as a parameter and return a list of dictionaries containing the player names of each player who finished in the top 10 in voting for that award that year.

def scrape_awards_data(year):
    awards_url = f'https://www.basketball-reference.com/awards/awards_{year}.html'
    awards_dict = {'mvp': [], 'dpoy': [], 'smoy': [], 'mip': [], 'roy': [], 'leading_all_nba': [], 'leading_all_defense': [], 'coy': []}

    chrome_options = Options()
    chrome_options.add_argument("--headless")

    webdriver_service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)

    print("Opening webpage...")
    driver.get(awards_url)
    time.sleep(2)

    print("Webpage opened. Parsing HTML...")
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    for award in awards_dict.keys():
        print(f"Scraping data for {award}...")
        try:
            selenium_table_div = driver.find_element(By.XPATH, f'//*[@id="div_{award}"]')
        except NoSuchElementException:
            print(f"No data found for {award} for the year {year}. Moving to the next award...")
            continue

        if selenium_table_div:
            selenium_table = selenium_table_div.find_element(By.XPATH, f'//*[@id="div_{award}"]/table')
            selenium_rows = selenium_table.find_elements(By.TAG_NAME, 'tr')
            for row in selenium_rows:
                try:
                    if award == 'coy':
                        name_element = row.find_element(By.CSS_SELECTOR,'td[data-stat="coach"]')
                    else:
                        name_element = row.find_element(By.CSS_SELECTOR,'td[data-stat="player"]')
                        name = name_element.text

                    if name:
                        awards_dict[award].append(name)
                except:
                    # Handle the case when the player name element is not found
                    print("Player name element not found. Skipping to the next row...")
                    continue

        else:
            print(f"No data found for {award} for the year {year}. Moving to the next award...")

    driver.quit()

    print("Scraping finished.")
    return awards_dict



# # Iterate over years since 1955 and scrape award data for each year
# for year in range(2022, 2023):
#     awards_dict = scrape_awards_data(year)
#     print(f"Logging award data for {year}...")
#     log_awards_data(conn, year, awards_dict)
#     print(f"Logging finished for {year}.")


# Prepare a list of alphabet letters to loop through for player names
alphabet = list(string.ascii_lowercase)

teams_table_cols = get_column_names(conn, 'teams')
players_table_cols = get_column_names(conn, 'players')
rosters_table_cols = get_column_names(conn, 'rosters')
player_yearly_stats_table_cols = get_column_names(conn, 'player_yearly_stats')
player_awards_table_cols = get_column_names(conn, 'player_awards')

# Skip these for now and add them in after to maintain database integrity
duplicate_names = ['Chris Johnson', 'Cliff Robinson', 'Marcus Williams'] # http://www.insidehoops.com/forum/showthread.php?288724-NBA-players-that-have-the-same-first-and-last-name

def scrape_player_data():
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
                                        city, team_name = team.rsplit(" ", 1)
                                        if city == 'Portland Trail':
                                            city = 'Portland'
                                            team_name = 'Trail Blazers'


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

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# REMINDER**** Start from here when adding the A's:  Kenny Anderson, team SuperSonics, year 2002...

# REMINDER***** START FROM De'Aaron Fox to add the rest of the F's

# Loop through each letter of the alphabet
for letter in alphabet[6:]:
    print(f"Processing letter {letter}...")
    player_list_url = f'https://www.basketball-reference.com/players/{letter}/'
    time.sleep(4)
    response = requests.get(player_list_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    players_table = soup.find('table', {'id': 'players'})
    rows = players_table.find_all('tr')

    # Iterate through each row in the table. Each row corresponds to a player.
    for row in rows:
        th = row.find('th', {'scope': 'row'})

        if th is not None:
            a = th.find('a')

            if a is not None:
                player_name = a.text
                print(f"Processing player: {player_name}...")
                name_parts = player_name.split()
                first_name = name_parts[0]
                last_name = " ".join(name_parts[1:])
                
                cur = conn.cursor()
                player_id_query = "SELECT id FROM players WHERE first_name = %s AND last_name = %s"
                params = (first_name, last_name)
                cur.execute(player_id_query, params)
                result = cur.fetchone()

                if result is not None:
                    player_id = result[0]

                    player_url = f'https://www.basketball-reference.com{a["href"]}'
                    time.sleep(4)
                    print(f"Fetching data for {player_name} from {player_url}...")
                    response = requests.get(player_url, headers=headers)
                    player_soup = BeautifulSoup(response.text, 'html.parser')

                    per_game_table = player_soup.find('table', {'id': 'per_game'})
                    rows = per_game_table.find_all('tr')[1:]

                    for row in rows:
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
                        age_td = row.find('td', {'data-stat': 'age'})
                        if age_td is not None and age_td.text != '':
                            age = int(age_td.text)
                            print(f'AGE: {age}')
                            update_column(conn, 'player_yearly_stats', 'age', age, player_id, year)

                        team_id_td = row.find('td', {'data-stat': 'team_id'})
                        if team_id_td is not None:
                            a = team_id_td.find('a')
                            if a is not None:
                                team_url = f'https://www.basketball-reference.com{a["href"]}'
                                time.sleep(4)
                                print(f"Fetching team data from {team_url}...")
                                response = requests.get(team_url, headers=headers)
                                team_soup = BeautifulSoup(response.text, 'html.parser')
                                team_info_div = team_soup.find('div', {'data-template': 'Partials/Teams/Summary'})
                                if team_info_div:
                                    span_tags = team_info_div.find_all('span')
                                    if span_tags:
                                        team = span_tags[1].text
                                        city, team_name = team.rsplit(" ", 1)
                                        if city == 'Portland Trail':
                                            city = 'Portland'
                                            team_name = 'Trail Blazers'
                                        
                                        print(f'CITY: {city}')
                                        print(f'TEAM NAME: {team_name}')
                                        team_query = "SELECT id FROM teams WHERE (name = %s AND city = %s) OR (prev_name_1 = %s AND prev_city_1 = %s)"
                                        params = (team_name, city, team_name, city)
                                        cur.execute(team_query, params)
                                        result = cur.fetchone()

                                        if result is not None:
                                            team_id = result[0]

                                            print(f"Adding roster record for player {player_name}, team {team_name}, year {year}...")
                                            roster_data = {'player_id': player_id, 'team_id': team_id, 'year': year}
                                            add_roster_record(conn, roster_data)
                                        else:
                                            print(f"Team {team_name} not found in database. Skipping...")
                                            continue
                                    else:
                                        print(f"No span tags found in team_info_div. Skipping...")
                                        continue
                                else:
                                    print(f"No team_info_div found. Skipping...")
                                    continue
                            else:
                                print(f"No a tag found in team_id_td. Skipping...")
                                continue
                        else:
                            print(f"No team_id_td found. Skipping...")
                            continue
                else:   
                    print(f"Player {player_name} not found in database. Skipping...")
                    continue
            else:
                print(f"No a tag found in th. Skipping...")
                continue
        else:
            print(f"No th found in row. Skipping...")
            continue

    print(f"Finished processing letter {letter}.")

print("Data scraping complete.")


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



