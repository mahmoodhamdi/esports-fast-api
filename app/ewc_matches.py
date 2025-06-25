# app/ewc_matches.py
import sqlite3
import requests
from bs4 import BeautifulSoup
from datetime import datetime as dt
import logging

logger = logging.getLogger(__name__)

BASE_URL = "https://liquipedia.net"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
}

def get_events_ewc():
    url = f"{BASE_URL}/esports/Esports_World_Cup/2025"
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        events_data = []
        events_headers = soup.select_one('div.esports-team-game-list')
        if not events_headers:
            logger.error("Could not find events section")
            return []

        for span in events_headers.select('span > a'):
            name = span.text.strip()
            link = span['href'].strip()
            full_link = link if link.startswith('http') else BASE_URL + link
            events_data.append({"name": name, "link": full_link})

        return events_data
    except Exception as e:
        logger.error(f"Error fetching events data: {e}")
        return []

def get_group_stage_url(main_link, soup=None):
    try:
        if not soup:
            res = requests.get(main_link, headers=HEADERS)
            res.raise_for_status()
            soup = BeautifulSoup(res.text, 'html.parser')

        detailed = soup.find('a', string=lambda x: x and 'click HERE' in x)
        if detailed:
            full_url = BASE_URL + detailed['href']
            if main_link.split('/')[2] in full_url:
                return full_url
    except:
        pass
    return main_link.rstrip('/') + '/Group_Stage'

def scrape_group_stage(game_name, link):
    url = get_group_stage_url(link)
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        group_boxes = soup.select('div.template-box')

        if not group_boxes:
            return {"message": "No matches yet"}

        data = {}
        for group in group_boxes:
            group_name_tag = group.select_one('.brkts-matchlist-title')
            group_name = group_name_tag.text.strip() if group_name_tag else 'Unknown Group'
            matches = []

            for match in group.select('.brkts-matchlist-match'):
                teams = match.select('.brkts-matchlist-opponent')
                if len(teams) == 2:
                    team1 = teams[0].get('aria-label', 'N/A')
                    logo1 = BASE_URL + teams[0].select_one('img')['src'] if teams[0].select_one('img') else 'N/A'
                    team2 = teams[1].get('aria-label', 'N/A')
                    logo2 = BASE_URL + teams[1].select_one('img')['src'] if teams[1].select_one('img') else 'N/A'
                else:
                    team1 = team2 = logo1 = logo2 = 'N/A'

                match_time = match.select_one('span.timer-object')
                time_text = match_time.text.strip() if match_time else 'N/A'

                score_tag = match.select_one('.brkts-matchlist-score')
                score = score_tag.text.strip() if score_tag else 'N/A'

                matches.append({
                    "Team1": {"Name": team1, "Logo": logo1},
                    "Team2": {"Name": team2, "Logo": logo2},
                    "MatchTime": time_text,
                    "Score": score
                })

            data[group_name] = matches
        return data
    except Exception as e:
        logger.error(f"Error scraping group stage for {game_name}: {e}")
        return {"message": f"Error: {e}"}

def parse_match_datetime(match_time: str):
    try:
        if ' - ' in match_time:
            date_str, time_str = match_time.split(' - ')
            date_str = ' '.join(date_str.split()[:3])
            time_str = time_str.split()[0]
            return dt.strptime(f"{date_str} {time_str}", '%B %d, %Y %H:%M')
        else:
            date_str = ' '.join(match_time.split()[:3])
            return dt.strptime(date_str, '%B %d, %Y')
    except:
        return dt.max

def store_matches_in_db():
    try:
        games = get_events_ewc()
        if not games:
            return False, "No events found."

        all_matches = []
        for game in games:
            game_name = game['name']
            game_link = game['link']
            match_data = scrape_group_stage(game_name, game_link)

            if isinstance(match_data, dict) and "message" in match_data:
                continue

            for group_name, matches in match_data.items():
                for match in matches:
                    match_time = match.get("MatchTime", "N/A")
                    try:
                        date_str = ' '.join(match_time.split(' - ')[0].split()[:3])
                        match_date = dt.strptime(date_str, '%B %d, %Y').strftime('%Y-%m-%d')
                    except:
                        match_date = "Unknown"

                    all_matches.append((
                        game_name, match_date, group_name,
                        match['Team1']['Name'], match['Team1']['Logo'],
                        match['Team2']['Name'], match['Team2']['Logo'],
                        match['MatchTime'], match['Score']
                    ))

        conn = sqlite3.connect('news.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM matches')  # clear old data
        cursor.executemany('''
            INSERT INTO matches (
                game, match_date, group_name,
                team1_name, team1_logo,
                team2_name, team2_logo,
                match_time, score
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', all_matches)
        conn.commit()
        conn.close()
        return True, f"{len(all_matches)} matches saved successfully."
    except Exception as e:
        logger.error(f"Error storing matches: {e}")
        return False, str(e)

def get_all_matches_from_db(game=None, group=None, date=None, sort_by="match_date", sort_order="asc", page=1, per_page=50):
    try:
        conn = sqlite3.connect("news.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = "SELECT * FROM matches WHERE 1=1"
        params = []

        if game:
            query += " AND LOWER(game) = LOWER(?)"
            params.append(game)
        if group:
            query += " AND LOWER(group_name) = LOWER(?)"
            params.append(group)
        if date:
            query += " AND match_date = ?"
            params.append(date)

        allowed_sort_columns = {"match_date", "match_time", "game", "group_name"}
        if sort_by not in allowed_sort_columns:
            sort_by = "match_date"
        sort_order = sort_order.lower() if sort_order.lower() in ("asc", "desc") else "asc"

        query += f" ORDER BY {sort_by} {sort_order}"

        offset = (page - 1) * per_page
        query += " LIMIT ? OFFSET ?"
        params.extend([per_page, offset])

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error reading matches from DB: {e}")
        return []
