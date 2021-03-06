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
	
	with workspace(virtualenvs = ['venv']) as ws:
		ws.create_file('venv/dummy')
		
		ws.run(
			'venv --no-activate')
		
		ws.check_file('venv/dummy')


def test_recreate():
	"""
	Test whether --recreate does recreate a venv.
	"""
	
	with workspace(virtualenvs = ['venv']) as ws:
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


def test_usability():
	"""
	Check that installing a project into the virtualenv succeeds. There are many reasons why this could fail so it is a good indicator for subtle things that can go wrong.
	"""
	
	with workspace(virtualenvs = ['venv'], dummy_project = True) as ws:
		ws.run(
			'venv',
			'python setup.py install')
		
		# For good measure.
		ws.run(
			'venv',
			'python setup.py develop')
	