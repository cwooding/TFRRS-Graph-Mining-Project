import os

from pyrsistent import optional


def create_dirs(dir):
    """
    Create the directories if they dont exist
    """
    if not os.path.exists(dir):
        os.makedirs(dir)


def get_meets_dir(config, filename="*"):
    """
    Return the meets directory
    """
    meets_dir = os.path.join(config['file']['data_dir'], config['file']['division_dir'], "meets")
    
    create_dirs(meets_dir)
    
    return os.path.join(meets_dir, filename)


def get_regions_dir(config):
    """
    Return the regions directory
    """
    regions_dir = os.path.join(config['file']['data_dir'], config['file']['division_dir'], "regions")
    
    create_dirs(regions_dir)
    
    return os.path.join(regions_dir, "*")


def get_teams_dir(config, filename="*"):
    """
    Return the teams directory
    """
    teams_dir = os.path.join(config['file']['data_dir'], config['file']['division_dir'], "teams")
    
    create_dirs(teams_dir)

    return os.path.join(teams_dir, filename)


def get_team_filename(config, team):
    """
    """
    filename = "{}.html".format(''.join(filter(str.isalnum, team)))

    return get_teams_dir(config, filename)


def get_meet_filename(config, meet):
    """
    """
    filename = "{}.html".format(''.join(filter(str.isalnum, meet)))

    return get_meets_dir(config, filename)


def get_graph_filename(config):
    """
    """
    dir = os.path.join(config['file']['data_dir'], config['file']['division_dir'])

    create_dirs(dir)

    return os.path.join(dir, config['file']['graph_filename'])