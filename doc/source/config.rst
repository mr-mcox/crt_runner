Config
**************

.. automodule:: crt_runner.config
	:special-members: __init__
	:members: 

Format of the yaml configuration file
======================================
The yaml file should include the following items:

* path_to_perl_script
* mandrill_api_key
* from_email
* email_from_name
* institutes
* emails
* cm_file_base_name
* collab_file_base_name
* user_settings_base_name
* warnings
* box_access_token_file
* box_refresh_token_file
* box_client_id
* box_client_secret
* box_sync_modify_dates
* root_box_folder_name
* root_local_folder

The fields expected in each institute section:
----------------------------------------------
Each of these fields should be listed under the institute name:

* ddm_name
* ddm_email
* file_prefix

The fields expected in each emails section:
----------------------------------------------
Each of these fields should be listed under the email type:

* subject
* body


Format of the warnings section:
----------------------------------------------
This should be a list where each field has the following entries:

* crt_warning
* user_friendly_warning

The crt_warning section can have regular expression groups eg (.*) . These captured groups will be substituted for the character X in the associated user_friendly_warning

Example YAML file
----------------------------------------------
.. code-block:: yaml

	path_to_perl_script: '/path/to/script'
	mandrill_api_key: 'API SECRET'
	from_email: 'national@tfa.org'
	from_name: 'National Overloard'
	cm_file_base_name: '_CMs.xls'
	collab_file_base_name: '_collabs.xls'
	user_settings_base_name: '_user_settings.txt'
	box_access_token_file: /path/to/box_access_token.txt
	box_refresh_token_file: /path/to/box_refresh_token.txt
	box_client_id: ae399afe
	box_client_secret: eafegead
	box_sync_modify_dates: /path/to/modify_dates.yaml
	root_box_folder_name: collab_test
	root_local_folder: /path/to/sync_folders
	emails:
		sample_email:
			subject: 'email subject'
			body: 'email body'
	institutes:
		Atlanta:
			ddm_name: 'Nick'
			ddm_email: 'ddm.nick@gmail.com'
			path_to_folder: 'path/to/folder'
			file_prefix: 'ATL'
	warnings:
		-
			crt_warning: 'Sample warning'
			user_friendly_warning: 'Warning to be displayed'
		-
			crt_warning: 'Warning about (.*) CMs'
			user_friendly_warning: 'Display warning about X CMs'
