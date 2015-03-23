from .scanner import Scanner
from .config import Config
import yaml
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("config",
                    help="the config file to use")
parser.add_argument("-r", "--reset", type=str,
                    help="reset is running")
args = parser.parse_args()


config_file = args.config

#Reset is running
if args.reset:
    cf = open(config_file)
    config_yaml = yaml.load(cf)
    cf.close()
    config_yaml['is_running'] = False
    cf = open(config_file, 'w')
    yaml.dump(config_yaml, cf)
    cf.close()


scan = Scanner(config=Config(config_file))
scan.sync_and_scan_institute_folders()
