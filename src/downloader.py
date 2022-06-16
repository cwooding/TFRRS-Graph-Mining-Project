import glob
import os
from time import sleep
import requests
import yaml

import utility.io as io
from scraper import get_teams, get_meets


def download_all_pages(config):
    """
    Grab and save all html pages that are not downloaded yet to the configured folder
    """
    print("Getting and saving pages that are not downloaded yet.")

    conference_files = glob.glob(io.get_conference_dir(config))

    teams = get_teams(conference_files)
    for team, team_url in teams.items():
        filename = io.get_team_filename(config, team) 
        if not os.path.exists(filename):
            print(f"Saving team {team} at {filename}")

            html = requests.get(team_url).text
            with open(filename, "w", encoding="utf-8") as f:
                f.write(html)

            sleep(config['scraper_wait_time'])
        else:
            print(f"Alread saved team {team} at {filename}")
    
    team_files = glob.glob(io.get_teams_dir(config))
    
    meets = get_meets(config, team_files)
    for meet, (_, meet_url) in meets.items():
        filename = io.get_meet_filename(config, meet)
        if not os.path.exists(filename):
            print(f"Saving meet {meet} at {filename}")

            html = requests.get(meet_url).text
            with open(filename, "w", encoding="utf-8") as f:
                f.write(html)

            sleep(config['scraper_wait_time'])
        else:
            print(f"Already saved meet {meet} at {filename}")


if __name__ == "__main__":
    """
    Dowload respective team and meets pages necessary
    """
    config = yaml.safe_load(open('config.yml'))

    download_all_pages(config)