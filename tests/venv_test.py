from ._helpers import *


def test_test_nothing(workspace):
	"""
	Test without a venv.
	"""
	
	workspace.run(
		'venv --test',
		expect_error = True,
		expect_stderr_contains = 'does not exist')


def test_test_directory(workspace):
	"""
	Test with an empty directory.
	"""
	
	workspace.create_dir('venv')
	
	workspace.run(
		'venv --test',
		expect_error = True,
		expect_stderr_contains = 'is not a virtualenv')


def test_test_venv(workspace_with_venv):
	"""
	Test with an empty directory.
	"""
	
	workspace_with_venv.run(
		'venv --test',
		expect_stderr_contains = 'is a virtualenv running')


def test_test_venv_different_name(workspace):
	"""
	Test with an empty directory.
	"""
	
	workspace.run('venv --no-activate venv2')
	
	workspace.run(
		'venv --test venv2',
		expect_stderr_contains = 'is a virtualenv running')
