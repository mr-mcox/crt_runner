import pytest
import os
from ..crt_log import CRTLog

@pytest.fixture
def successfully_completed_log_file(request):
	f = open('log_file.txt','w')
	file_contents = """
	We need between 377 and 410 CMs to fill collabs and there are 402 CMs
	Beginning computation of cm collab scores
	Now beginning CM placements
	There are currently 170 collabs to place. 3 cms have been placed so far.
	There are currently 160 collabs to place. 26 cms have been placed so far.
	There are currently 0 collabs to place. 375 cms have been placed so far.
	CMs are all placed
	After filling remaining collabs, 400 cms have been placed so far.
	After 0 swaps attempted there have been 0 swaps made
	There were 4 swaps made
	Collab builder has successfully completed. Please open the output files for the suggested CM placements.
	"""
	f.write(file_contents)
	f.close()
	def delete_log_file():
		os.remove('log_file.txt')
	request.addfinalizer(delete_log_file)
	return open('log_file.txt')


def test_crt_completed_successfully(successfully_completed_log_file):
	l = CRTLog(successfully_completed_log_file)
	assert l.successfully_completed