import subprocess
import os.path
import sys

canary_file = 'placement_reccomendations_and_cm_level_scoring.xls'

initial_command = ['perl',
                   sys.argv[1]]

working_directory = sys.argv[2]

files = [
    'ATL_cms.xls',
    'ATL_collabs.xls',
    'user_settings.txt']

path_to_files = [
    os.path.join(working_directory, filename) for filename in files]

full_args = initial_command + path_to_files + [working_directory]

if not os.path.isfile(os.path.join(working_directory,canary_file)):
	subprocess.call(full_args)