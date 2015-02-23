from .perl_execution import PerlCommand
import os.path

class Scanner(object):
	"""Scan folders to determine whether CRT should be run"""
	def __init__(self):
		pass

	def scan_folder(self,folder):
		canary_file = 'placement_reccomendations_and_cm_level_scoring.xls'
		if not os.path.isfile(os.path.join(folder,canary_file)):
			pc = PerlCommand()
			pc.run_crt()
			