from .helpers import *


def test_test_nothing():
	"""
	Test without a venv.
	"""
	
	with workspace() as ws:
		ws.run(
			'venv --test',
			expect_error = True,
			expect_stderr_contains = 'does not exist')


def test_test_directory():
	"""
	Test with an empty directory.
	"""
	
	with workspace() as ws:
		ws.create_dir('venv')
		
		ws.run(
			'venv --test',
			expect_error = True,
			expect_stderr_contains = 'is not a virtualenv')


def test_test_venv():
	"""
	Test with an empty directory.
	"""
	
	with workspace_with_venv() as ws:
		ws.run(
			'venv --test',
			expect_stderr_contains = 'is a virtualenv running')


def test_test_venv_different_name():
	"""
	Test with an empty directory.
	"""
	
	with workspace() as ws:
		ws.run('venv --no-activate venv2')
		
		ws.run(
			'venv --test venv2',
			expect_stderr_contains = 'is a virtualenv running')
