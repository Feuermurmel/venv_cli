from .helpers import *


def test_create_failure():
	"""
	Test whether failure to setup a virtualenv does not leave a trace.
	"""
	
	with workspace() as ws:
		ws.run('venv --python no-such-python', expect_error = True)
		
		ws.check_dir()


def test_create_non_existing_path():
	"""
	Test whether creating a virtualenv at a non-existing path fails.
	"""
	
	with workspace() as ws:
		ws.run(
			'venv --no-activate foo/venv',
			expect_error = True,
			expect_stderr_contains = 'does not exist')
		
		ws.check_dir()


def test_create_path_is_file():
	"""
	Test whether creating a virtualenv at a path occupied by a file fails.
	"""
	
	with workspace() as ws:
		ws.create_file('venv')
		
		ws.run(
			'venv --no-activate',
			expect_error = True,
			expect_stderr_contains = 'is not a virtualenv')
		
		ws.check_dir([], ['venv'])


def test_create_path_is_dir():
	"""
	Test whether creating a virtualenv at a path occupied by a file fails.
	"""
	
	with workspace() as ws:
		ws.create_dir('venv')
		ws.create_file('venv/dummy')
		
		ws.run(
			'venv --no-activate',
			expect_error = True,
			expect_stderr_contains = 'is not a virtualenv')
		
		ws.check_dir(['venv'])
		ws.check_dir([], ['dummy'], path = 'venv')


def test_create_parent_is_file():
	"""
	Test whether creating a virtualenv at a path occupied by a file fails.
	"""
	
	with workspace() as ws:
		ws.create_file('foo')
		
		ws.run(
			'venv --no-activate foo/venv',
			expect_error = True,
			expect_stderr_contains = 'is not a directory')
		
		ws.check_dir([], ['foo'])


def test_recreate_failure():
	"""
	Test whether failure to recreate a virtualenv does not leave a trace.
	"""
	
	with workspace(virtualenvs = ['venv']) as ws:
		ws.create_file('venv/dummy')
		
		ws.run('venv --python no-such-python', expect_error = True)
		
		ws.check_dir(['venv'])
		ws.check_file('venv/dummy')
