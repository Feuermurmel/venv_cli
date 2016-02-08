from ._helpers import *


def test_create(workspace):
	"""
	Test whether a virtualenv is successfully created.
	"""
	
	workspace.run(
		'venv --create --no-activate')
	
	workspace.check_venv()


def test_create_via_no_activate(workspace):
	"""
	Test whether --no-activate implies --create.
	"""
	
	workspace.run(
		'venv --no-activate')
	
	workspace.check_venv()


def test_not_recreated(workspace_with_venv):
	"""
	Test whether --create does not recreate a venv.
	"""
	
	workspace_with_venv.create_file('venv/dummy')
	
	workspace_with_venv.run(
		'venv --no-activate')
	
	workspace_with_venv.check_file('venv/dummy')


def test_recreate(workspace_with_venv):
	"""
	Test whether --recreate does recreate a venv.
	"""
	
	workspace_with_venv.create_file('venv/dummy')
	
	workspace_with_venv.run(
		'venv --recreate --no-activate')
	
	workspace_with_venv.check_file('venv/dummy', exists = False)


def test_create_non_default_name(workspace):
	"""
	Test whether a virtualenv is successfully created when a different path is specified.
	"""
	
	workspace.run(
		'venv --create --no-activate venv2')
	
	workspace.check_dir(['venv2'])
	workspace.check_venv('venv2')
