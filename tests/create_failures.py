from ._helpers import *


def test_create_failure(workspace):
	"""
	Test whether failure to setup a virtualenv does not leave a trace.
	"""
	
	workspace.run('venv --python no-such-python', expect_error = True)
	
	workspace.check_dir()


def test_create_non_existing_path(workspace):
	"""
	Test whether creating a virtualenv at a non-existing path fails.
	"""
	
	workspace.run(
		'venv --no-activate foo/venv',
		expect_error = True,
		expect_stderr_contains = 'does not exist')
	
	workspace.check_dir()


def test_create_path_is_file(workspace):
	"""
	Test whether creating a virtualenv at a path occupied by a file fails.
	"""
	
	workspace.create_file('venv')
	
	workspace.run(
		'venv --no-activate',
		expect_error = True,
		expect_stderr_contains = 'is not a virtualenv')
	
	workspace.check_dir([], ['venv'])


def test_create_path_is_dir(workspace):
	"""
	Test whether creating a virtualenv at a path occupied by a file fails.
	"""
	
	workspace.create_dir('venv')
	workspace.create_file('venv/dummy')
	
	workspace.run(
		'venv --no-activate',
		expect_error = True,
		expect_stderr_contains = 'is not a virtualenv')
	
	workspace.check_dir(['venv'])
	workspace.check_dir([], ['dummy'], path = 'venv')


def test_create_parent_is_file(workspace):
	"""
	Test whether creating a virtualenv at a path occupied by a file fails.
	"""
	
	workspace.create_file('foo')
	
	workspace.run(
		'venv --no-activate foo/venv',
		expect_error = True,
		expect_stderr_contains = 'is not a directory')
	
	workspace.check_dir([], ['foo'])


def test_recreate_failure(workspace_with_venv):
	"""
	Test whether failure to recreate a virtualenv does not leave a trace.
	"""
	
	workspace_with_venv.create_file('venv/dummy')
	
	workspace_with_venv.run('venv --python no-such-python', expect_error = True)
	
	workspace_with_venv.check_dir(['venv'])
	workspace_with_venv.check_file('venv/dummy')
