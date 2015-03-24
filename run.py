from .scanner import Scanner
from .config import Config
import yaml
import argparse
import logging

parser = argparse.ArgumentParser()
parser.add_argument("config",
                    help="the config file to use")
parser.add_argument("-r", "--reset",
                    help="reset is running", action="store_true")
parser.add_argument("-d", "--debug",
                    help="run in debug mode", action="store_true")
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

config = Config(config_file)

#Reset is running
if args.debug:
    logging.basicConfig(filename=config.crt_runner_log, level=logging.DEBUG)
else:
	logging.basicConfig(filename=config.crt_runner_log, level=logging.ERROR)


scan = Scanner(config=config)
scan.sync_and_scan_institute_folders()
