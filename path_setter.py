import os
import re

def find_path(directory):
    match = re.search(str(directory), os.getcwd())
    if not match:
        raise IOError(str(directory) + ' is not in current working ' +
                      'directory of ' + os.getcwd())
    return os.getcwd()[:match.span()[0]] + directory
