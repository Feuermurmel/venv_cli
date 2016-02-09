from .helpers import *


def test_create_setup():
	"""
	Check that a python project installed into the virtualenv is usable.
	"""
	
	with workspace(dummy_project = True) as ws:
		ws.run(
			'venv --setup',
			'venv_cli_dummy',
			expect_stdout_contains = 'Yay.')


def test_recreate_setup():
	"""
	Check that recreating and setting up of a python project succeeds.
	"""
	
	with workspace(virtualenvs = ['venv'], dummy_project = True) as ws:
		ws.run('venv --setup')


def test_setup_failure():
	"""
	Test whether failure to setup a virtualenv does not leave a trace.
	"""
	
	with workspace(virtualenvs = ['venv']) as ws:
		ws.create_file('venv/dummy')
		
		ws.run('venv --setup', expect_error = True)
		
		ws.check_dir(['venv'])
		ws.check_file('venv/dummy')
