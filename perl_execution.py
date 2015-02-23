import subprocess
from .messenger import Messenger
from .crt_log import CRTLog

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

	def run_crt_with_notifications(self):
		self.run_crt()
		log = CRTLog(self.log_file)
		if log.successfully_completed:
			m = Messenger()
			m.send_email('CRT Successfully completed!')