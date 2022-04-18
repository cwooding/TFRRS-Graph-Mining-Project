import os
import re


def get_child_string(s):
    """
    Get the string that this bs4 object is wrapping.
    Assumes that this tree has a string in the child, otherwise will throw AttributeError
    """
    while s.string is None:
        s = s.findChild() 
    
    return s.string.strip()


def convert_time(final_time):
    """
    Convert time from MM:SS.s format to double representing number of seconds
    """
    if re.match("^\d+:\d+\.\d+$", final_time):
        colon = final_time.index(':')

        minutes = float(final_time[0:colon])
        seconds = float(final_time[colon+1:])
        
        return 60 * minutes + seconds