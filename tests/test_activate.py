from .helpers import *


def test_activate():
	with workspace(virtualenvs = ['venv']) as ws:
		ws.run(
			'venv',
			'python -c "print(123)"',
			expect_stdout_contains = '123')


def test_fail_without_create():
	"""
	Test whether activating fails without an existing virtualenv if --create is not specified.
	"""
	
	with workspace() as ws:
		ws.run(
			'venv',
			expect_error = True)
		
		ws.check_venv(exists = False)


def test_pyenv_launcher_not_exported():
	"""
	Check that the dreaded __PYVENV_LAUNCHER__ environment variable is not exported into the shell session when activating the virtualenv.
	"""
	
	with workspace(virtualenvs = ['venv']) as ws:
		ws.run(
			'venv',
			'! [ "$__PYVENV_LAUNCHER__" ]')
