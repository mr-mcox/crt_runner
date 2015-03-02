def test_sendemail():
	l = CRTLog(successfully_completed_log_file)
	assert l.successfully_completed
	