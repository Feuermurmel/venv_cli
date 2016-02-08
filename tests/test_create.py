from .helpers import *


def test_create():
	"""
	Test whether a virtualenv is successfully created.
	"""
	
	with workspace() as ws:
		ws.run(
			'venv --create --no-activate')
		
		ws.check_venv()


def test_create_via_no_activate():
	"""
	Test whether --no-activate implies --create.
	"""
	
	with workspace() as ws:
		ws.run(
			'venv --no-activate')
		
		ws.check_venv()


def test_not_recreated():
	"""
	Test whether --create does not recreate a venv.
	"""
	
	with workspace_with_venv() as ws:
		ws.create_file('venv/dummy')
		
		ws.run(
			'venv --no-activate')
		
		ws.check_file('venv/dummy')


def test_recreate():
	"""
	Test whether --recreate does recreate a venv.
	"""
	
	with workspace_with_venv() as ws:
		ws.create_file('venv/dummy')
		
		ws.run(
			'venv --recreate --no-activate')
		
		ws.check_file('venv/dummy', exists = False)


def test_create_non_default_name():
	"""
	Test whether a virtualenv is successfully created when a different path is specified.
	"""
	
	with workspace() as ws:
		ws.run(
			'venv --create --no-activate venv2')
		
		ws.check_dir(['venv2'])
		ws.check_venv('venv2')
