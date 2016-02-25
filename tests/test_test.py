import shutil
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
	
	with workspace(virtualenvs = ['venv']) as ws:
		ws.run(
			'venv --test',
			expect_stderr_contains = 'is a virtualenv running')


def test_test_venv_different_name():
	"""
	Test with an empty directory.
	"""
	
	with workspace(virtualenvs = ['venv2']) as ws:
		ws.run(
			'venv --test venv2',
			expect_stderr_contains = 'is a virtualenv running')


def test_test_old_python_version():
	"""
	Test whether the version string can be extracted from different Python versions.
	"""
	
	def filter_versions(names):
		return [i for i in names if shutil.which(i) is not None]
	
	old_behavior_versions = filter_versions(['python2.6', 'python2.7', 'python3.0', 'python3.1', 'python3.2', 'python3.3'])
	new_behavior_versions = filter_versions(['python3.4', 'python3.5', 'python3.6', 'python3.7', 'python3.8', 'python3.9'])
	
	if not old_behavior_versions and not new_behavior_versions:
		pytest.skip('A python version <= 3.3 and another >= 3.4 is necessary.')
	
	for i in old_behavior_versions[0], new_behavior_versions[0]:
		with workspace() as ws:
			ws.run('venv -c -p {}'.format(i))
			
			res = ws.run('venv --test')
			
			assert 'is a virtualenv running' in res.stderr
			
			# Check that we didn't get an empty version string. This is brittle and should probably be replaced by something more robust.
			assert 'is a virtualenv running .' not in res.stderr
