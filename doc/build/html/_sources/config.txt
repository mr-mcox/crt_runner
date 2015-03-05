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

The fields expected in each institute section:
----------------------------------------------
Each of these fields should be listed under the institute name:

* ddm_name
* ddm_email
* path_to_folder
* file_prefix

The fields expected in each emails section:
----------------------------------------------
Each of these fields should be listed under the email type:

* subject
* body
