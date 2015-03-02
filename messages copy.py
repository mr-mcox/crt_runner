import mandrill
mandrill_client = mandrill.Mandrill('ejBA1qPIlAU6c6UA-0mdwg')
message = { 
 'auto_html': None,
 'auto_text': None,
 'bcc_address': None,
 'from_email': 'programtracker@teachforamerica.org',
 'from_name': 'ProgramTracker@',
 'global_merge_vars': None,
 'google_analytics_campaign': None,
 'google_analytics_domains': None,
 'headers': {'Reply-To': 'nicholas.smrdel@teachforamerica.org'},
 'html': '<p>Example HTML content</p>',
 'images': None,
 'important': False,
 'inline_css': None,
 'merge': True,
 'merge_language': 'mailchimp',
 'merge_vars': [{'rcpt': 'matthew.cox@teachforamerica.org',
				 'vars': [{'content': 'merge2 content', 'name': 'merge2'}]}],
 'metadata': {'website': 'www.teachforamerica.org'},
 'preserve_recipients': None,
 'recipient_metadata': [{'rcpt': 'recipient.email@example.com',
						 'values': {'user_id': 123456}}],
 'return_path_domain': None,
 'signing_domain': None,
 'subject': 'Matthew Cox is a Great Teacher',
 'tags': ['password-resets'],
 'text': 'Here is an example email',
 'to': [{'email': 'nicholas.throckmorton@teachforamerica.org',
		 'name': 'Nick Throckmorton',
		 'type': 'to'},{'email': 'matthew.cox@teachforamerica.org',
		 'name': 'Matthew Cox',
		 'type': 'to'}],
 'track_clicks': None,
 'track_opens': None,
 'tracking_domain': None,
 'url_strip_qs': None,
 'view_content_link': None}
result = mandrill_client.messages.send(message=message, async=False, ip_pool='Main Pool')
