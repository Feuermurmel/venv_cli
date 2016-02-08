from ._helpers import *

# def test_create_activate(command_context):
# 	command_context.run(
# 		'venv',
# 		'')
# 	
# 	command_context.bash(['. venv/bin/activate'])



def test_fail_without_create(workspace):
	"""
	Test whether activating fails without an existing virtualenv if --create is not specified.
	"""
	
	workspace.run(
		'venv',
		expect_error = True)
	
	workspace.check_venv(exists = False)
