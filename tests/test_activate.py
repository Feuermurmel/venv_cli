from .helpers import *


def test_activate(workspace_with_venv):
	workspace_with_venv.run(
		'venv',
		'python -c "print(123)"',
		expect_stdout_contains = '123')


def test_fail_without_create(workspace):
	"""
	Test whether activating fails without an existing virtualenv if --create is not specified.
	"""
	
	workspace.run(
		'venv',
		expect_error = True)
	
	workspace.check_venv(exists = False)
