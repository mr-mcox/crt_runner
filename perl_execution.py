import subprocess

class PerlCommand(object):
	"""Call the perl command"""
	def __init__(self):
		pass
		
	def run_crt(self):
		subprocess.call(['perl',
			self.path_to_crt,
			self.cms_file,
			self.collab_file,
			self.user_settings_file,
			self.output_directory],stdout=self.log_file)