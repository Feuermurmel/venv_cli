from .helpers import *


def test_workspace_check_venv_not_existing():
	with workspace() as ws:
		ws.check_venv(exists = False)
		
		with pytest.raises(AssertionError):
			ws.check_venv()


def test_workspace_check_venv_existing():
	with workspace(virtualenvs = ['venv']) as ws:
		ws.check_venv()
		
		with pytest.raises(AssertionError):
			ws.check_venv(exists = False)


def test_check_write():
	with workspace() as ws:
		ws.create_file('test', 'foo')
		
		with open(os.path.join(ws.cwd, 'test'), 'rb') as file:
			assert file.read() == b'foo'


def test_check_file_existing():
	with workspace() as ws:
		ws.create_file('test', 'foo')
		
		ws.check_file('test', 'foo')
		
		with pytest.raises(AssertionError):
			ws.check_file('test', 'bar')
		
		with pytest.raises(AssertionError):
			ws.check_file('test', exists = False)


def test_check_file_not_existing():
	with workspace() as ws:
		ws.check_file('test', exists = False)
		
		with pytest.raises(AssertionError):
			ws.check_file('test')
		
		with pytest.raises(AssertionError):
			ws.check_file('test', 'bar')


def test_check_dir():
	with workspace() as ws:
		os.mkdir(os.path.join(ws.cwd, 'foo'))
		
		with open(os.path.join(ws.cwd, 'bar'), 'w'):
			pass
		
		ws.check_dir(['foo'], ['bar'])
		
		with pytest.raises(AssertionError):
			ws.check_dir()


def test_check_dir_subdir():
	with workspace() as ws:
		os.makedirs(os.path.join(ws.cwd, 'foo/bar'))
		
		ws.check_dir(['bar'], path = 'foo')


def test_check_dir_none():
	with workspace() as ws:
		ws.check_dir()
		
		with pytest.raises(AssertionError):
			ws.check_dir('foo')
