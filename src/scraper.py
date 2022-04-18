import glob
import os
from time import sleep
from bs4 import BeautifulSoup
import requests
import yaml

import utility.io as io
from utility.helpers import convert_time, get_child_string


def get_teams(region_files):
    """
    Find Teams in a League HTML Page
    """
    team_pages = dict()
    for region_file in region_files:
        region_page = open(region_file, "r")
        doc = BeautifulSoup(region_page, "html.parser")

        for table in doc.find_all('table'):
            if table.parent.find('h3').string == "TEAMS":
                for entry in table.find_all('a'):
                    link = entry.get('href')
                    if "_m_" in link:
                        team_name = entry.string
                        team_pages[team_name] = link
        
        region_page.close()

    return team_pages


def get_meets(team_files, year):
    """
    Find meets on a team HTML Page
    """
    meets = {}
    for team_file in team_files:
        team_page = open(team_file, "r")
        doc = BeautifulSoup(team_page, "html.parser")

        for table in doc.find_all('table'):
            if table.parent.find('h3').string == "LATEST RESULTS":
                for row in table.find_all('tr'):
                    data = row.find_all('td')
                    if data:
                        meet_date = get_child_string(data[0])

                        link = data[1].find('a')
                        meet_name = link.string.strip()
                        meet_link = link.get('href').strip()

                        # Issue where downloaded html doesnt have https in html
                        if "https:" not in meet_link:
                            meet_link = "https:" + meet_link

                        # Save XC meets from this year
                        if "xc" in meet_link and year in meet_date:
                            meets[meet_name] = (meet_date, meet_link)
        
        team_page.close()
    
    return meets


def get_results(meet_files, team_pages):
    """
    Get the results from all of the meets
    """
    results = {}

    for meet_file in meet_files:
        meet_result = []

        meet_page = open(meet_file, "r")
        doc = BeautifulSoup(meet_page, "html.parser")

        for table in doc.find_all('table'):
            table_name = next(table.parent.find("h3").children)

            if "Men" in table_name and "Individual" in table_name:
                column_names = [column.string.strip() for column in table.find('thead').find_all('th')]
                name_index = column_names.index('NAME')
                team_index = column_names.index('TEAM')
                time_index = column_names.index('TIME')

                for row in table.find('tbody').find_all('tr'):
                    row = row.find_all('td')
                        
                    name = get_child_string(row[name_index])
                    team = get_child_string(row[team_index])
                    final_time = convert_time(get_child_string(row[time_index]))

                    # If they finished the race and in the teams we are looking
                    if final_time and team in team_pages:
                        meet_result.append((name, team, final_time))

        results[meet_file] = sorted(meet_result, key=lambda x: x[2])
        meet_page.close()

    return results


def results_to_file(results, edge_between_all):
    """
    """
    meet_results_filename = io.get_graph_filename(config)
    f = open(meet_results_filename, "w")
    for _, result in results.items():

        if edge_between_all:
            for first in result:
                for second in result:
                    if first[2] < second[2]:
                        first_node = first[0].replace(' ', '')
                        second_node = second[0].replace(' ', '')
                        time_diff = second[2] - first[2]

                        line = "{} {} {:.1f}\n".format(second_node, first_node, time_diff)
                        f.write(line)
        else:
            for i in range(len(result) - 1):
                first = result[i]
                second = result[i + 1]

                first_node = first[0].replace(' ', '')
                second_node = second[0].replace(' ', '')
                time_diff = second[2] - first[2]

                line = "{} {} {:.1f}\n".format(second_node, first_node, time_diff)
                f.write(line)
    f.close()


def get_and_save_all_pages(config):
    """
    """
    # Use Downloaded Region HTMLs
    region_files = glob.glob(io.get_regions_dir(config))

    teams = get_teams(region_files)
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
    
    year = config['year']
    meets = get_meets(team_files, year)
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
    Scrape all of the data and create appropriate graph
    """
    config = yaml.safe_load(open('config.yml'))

    edge_between_all = config["edge_between_all"]

    # Save HTML Pages where necessary
    get_and_save_all_pages(config)

    regions_dir = io.get_regions_dir(config)
    regions_files = glob.glob(regions_dir)
    teams = get_teams(regions_files)

    meets_dir = io.get_meets_dir(config)
    meets_files = glob.glob(meets_dir)
    results = get_results(meets_files, teams)

    results_to_file(results, edge_between_all)