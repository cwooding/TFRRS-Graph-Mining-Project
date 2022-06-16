import glob
from bs4 import BeautifulSoup
import yaml

import utility.io as io
from utility.helpers import convert_time, get_child_string, get_table_name, remove_white_space


def get_teams(region_files):
    """
    Find Teams in a League HTML Page
    """
    print("Getting all teams.")

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


def get_meets(config, team_files):
    """
    Find meets on a team HTML Page
    """
    print("Getting all meets.")

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
                        if "xc" in meet_link and config['year'] in meet_date:
                            meets[meet_name] = (meet_date, meet_link)
        
        team_page.close()
    
    return meets


def get_results(meet_files, team_pages):
    """
    Get the results from all of the meets
    """
    print("Getting all meet results.")

    results = {}
    for meet_file in meet_files:
        meet_result = []

        meet_page = open(meet_file, "r")
        doc = BeautifulSoup(meet_page, "html.parser")

        for table in doc.find_all('table'):
            table_name = get_table_name(table)

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

                    # If they finished the race and in the teams we are looking for
                    if final_time and team in team_pages:
                        meet_result.append((name, team, final_time))

        results[meet_file] = sorted(meet_result, key=lambda x: x[2])
        meet_page.close()

    return results


def get_championship_results(championship_meet_file):
    """
    Get the results from all of the meets
    """
    individual_result = {}
    team_result = {}

    meet_page = open(championship_meet_file, "r")
    doc = BeautifulSoup(meet_page, "html.parser")

    for table in doc.find_all('table'):
        table_name = get_table_name(table)

        if "Men" in table_name and "Individual" in table_name:
            column_names = [column.string.strip() for column in table.find('thead').find_all('th')]
            name_index = column_names.index('NAME')
            team_index = column_names.index('TEAM')
            time_index = column_names.index('TIME')

            for row in table.find('tbody').find_all('tr'):
                row = row.find_all('td')
                       
                name = remove_white_space(get_child_string(row[name_index]))
                team = remove_white_space(get_child_string(row[team_index]))
                final_time = convert_time(get_child_string(row[time_index]))

                # If they finished the race and in the teams we are looking for
                if final_time:
                    individual_result[name] = (team, final_time)
        elif "Men" in table_name and "Team" in table_name:
            column_names = [column.string.strip() for column in table.find('thead').find_all('th')]
            team_index = column_names.index('Team')
            score_index = column_names.index('Score')

            for row in table.find('tbody').find_all('tr'):
                row = row.find_all('td')
                       
                team = remove_white_space(get_child_string(row[team_index]))
                score = get_child_string(row[score_index])

                team_result[team] = (team, score)

    meet_page.close()

    return individual_result, team_result


def results_to_file(config, results):
    """
    Put meet results in a file that can be read by NetworkX to create a graph
    """
    print("Converting meet results to graph edge list")

    meet_results_filename = io.get_graph_filename(config)
    f = open(meet_results_filename, "w")
    for _, result in results.items():

        if config['edge_between_all']:
            for first in result:
                for second in result:
                    if first[2] < second[2]:
                        first_node = remove_white_space(first[0])
                        second_node = remove_white_space(second[0])
                        time_diff = second[2] - first[2]

                        line = "{} {} {:.1f}\n".format(second_node, first_node, time_diff)
                        f.write(line)
        else:
            for i in range(len(result) - 1):
                first = result[i]
                second = result[i + 1]

                first_node = remove_white_space(first[0])
                second_node = remove_white_space(second[0])
                time_diff = second[2] - first[2]

                line = "{} {} {:.1f}\n".format(second_node, first_node, time_diff)
                f.write(line)
    f.close()


if __name__ == "__main__":
    """
    Scrape all of the data and create appropriate graph
    """
    config = yaml.safe_load(open('config.yml'))

    # Get teams from the conference pages
    conference_dir = io.get_conference_dir(config)
    conference_files = glob.glob(conference_dir)
    teams = get_teams(conference_files)

    # Get all the meets that these teams competed at
    meets_dir = io.get_meets_dir(config)
    meets_files = glob.glob(meets_dir)
    results = get_results(meets_files, teams)

    results_to_file(config, results)