from ._helpers import *


def test_workspace_check_venv_not_existing(workspace):
	workspace.check_venv(exists = False)
	
	with pytest.raises(AssertionError):
		workspace.check_venv()


def test_workspace_check_venv_existing(workspace_with_venv):
	workspace_with_venv.check_venv()
	
	with pytest.raises(AssertionError):
		workspace_with_venv.check_venv(exists = False)


def test_check_write(workspace):
	workspace.create_file('test', 'foo')
	
	with open(os.path.join(workspace.dir, 'test'), 'rb') as file:
		assert file.read() == b'foo'


def test_check_file_existing(workspace):
	workspace.create_file('test', 'foo')
	
	workspace.check_file('test', 'foo')
	
	with pytest.raises(AssertionError):
		workspace.check_file('test', 'bar')
	
	with pytest.raises(AssertionError):
		workspace.check_file('test', exists = False)


def test_check_file_not_existing(workspace):
	workspace.check_file('test', exists = False)
	
	with pytest.raises(AssertionError):
		workspace.check_file('test')
	
	with pytest.raises(AssertionError):
		workspace.check_file('test', 'bar')


def test_check_dir(workspace):
	os.mkdir(os.path.join(workspace.dir, 'foo'))
	
	with open(os.path.join(workspace.dir, 'bar'), 'w'):
		pass
	
	workspace.check_dir(['foo'], ['bar'])
	
	with pytest.raises(AssertionError):
		workspace.check_dir()


def test_check_dir_subdir(workspace):
	os.makedirs(os.path.join(workspace.dir, 'foo/bar'))
	
	workspace.check_dir(['bar'], path = 'foo')


def test_check_dir_none(workspace):
	workspace.check_dir()
	
	with pytest.raises(AssertionError):
		workspace.check_dir('foo')
