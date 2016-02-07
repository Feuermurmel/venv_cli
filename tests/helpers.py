import os, subprocess, sys, pytest


class Workspace:
	"""
	Allows executing commands and checking conditions in a temporary directory.
	"""
	
	def __init__(self, dir):
		self.dir = dir
		
	def run(self, *lines, expect_error = False, expect_stdout_contains = '', expect_stderr_contains = ''):
		"""
		Runs the specified commands by piping them into a non-interactive bash process.
		"""
		
		process = subprocess.Popen(
			['bash', '--norc'],
			cwd = self.dir,
			stdin = subprocess.PIPE,
			stdout = subprocess.PIPE,
			stderr = subprocess.PIPE)
		
		input = ''.join(i + '\n' for i in ('set -e',) + lines).encode()
		
		out, err = process.communicate(input)
		
		sys.stdout.buffer.write(out)
		sys.stderr.buffer.write(err)
		
		if expect_error:
			assert process.returncode
		else:
			assert not process.returncode
		
		assert expect_stdout_contains in out.decode()
		assert expect_stderr_contains in err.decode()
	
	def check_venv(self, path = 'venv', *, exists = True):
		if exists:
			self.run(
				'. {}/bin/activate'.format(path),
				'[ "$VIRTUAL_ENV" ]')
		else:
			self.run(
				'! [ -e venv ]')
	
	def create_file(self, path, content : str = ''):
		with open(os.path.join(self.dir, path), 'w', encoding = 'utf-8') as file:
			file.write(content)
	
	def check_file(self, path, content = None, *, exists = True):
		file_path = os.path.join(self.dir, path)
		
		if exists:
			assert os.path.isfile(file_path)
			
			if content is not None:
				with open(file_path, 'r', encoding = 'utf-8') as file:
					assert file.read() == content
		else:
			if content is not None:
				raise ValueError('content must be None if exists is set to False.')
			
			assert not os.path.exists(file_path)


@pytest.fixture()
def workspace(tmpdir_factory):
	temp_dir = tmpdir_factory.mktemp('cwd')
	
	return Workspace(str(temp_dir))


@pytest.fixture()
def workspace_with_venv(workspace):
	workspace.run('venv --create --no-activate')
	
	return workspace


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
