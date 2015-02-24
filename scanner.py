from .perl_execution import PerlCommand
import os.path


class Scanner(object):

    """Scan folders to determine whether CRT should be run"""

    def __init__(self):
        """
        
        .. todo:: Canary file should be replaced with more sophisticated run condtions
        """
        self.canary_file = 'placement_reccomendations_and_cm_level_scoring.xls'
        self.perl_command = PerlCommand()

    def scan_folder(self, folder):
        """Run CRT command if canary file missing from identified folder

        :param folder: Path to the folder to scan for the canary file
        :type folder: str
        """
        canary_file = self.canary_file
        if not os.path.isfile(os.path.join(folder, canary_file)):
            self.perl_command.run_crt()
