import mandrill
mandrill_client = mandrill.Mandrill('ejBA1qPIlAU6c6UA-0mdwg')
message = { 
 'from_email': 'programtracker@teachforamerica.org',
 'from_name': 'ProgramTracker@',
 'global_merge_vars': None,
 'headers': {'Collab Builder Error'},
 'images': None,
 'important': False,
 'inline_css': None,
 'merge': True,
 'merge_language': 'mailchimp',
 'subject': 'Collab Builder Error',
 'tags': ['password-resets'],
 'text': 'We have noticed your collab builder has run into a oommon error. Your collab builder appears to hang when the last message is improving worst score iterations.',
 'to': [{'email': 'nicholas.smrdel@teachforamerica.org',
		 'name': 'Nick Smrdel',
		 'type': 'to'}],
 'track_clicks': None,
 'track_opens': None,
 'tracking_domain': None,
 'url_strip_qs': None,
 'view_content_link': None}
result = mandrill_client.messages.send(message=message, async=False, ip_pool='Main Pool')