import os, subprocess, sys, contextlib, pkgutil, tempfile, pytest


class RunResult:
	def __init__(self, returncode : int, stdout : str, stderr : str):
		self.returncode = returncode
		self.stdout = stdout
		self.stderr = stderr


class Workspace:
	"""
	Allows executing commands and checking conditions in a temporary directory.
	"""
	
	def __init__(self, dir):
		self.cwd = os.path.join(dir, 'cwd')
		self.home = os.path.join(dir, 'home')
		
		os.mkdir(self.cwd)
		os.mkdir(self.home)
	
	def _run_commands(self, lines):
		environ = dict(os.environ)
		environ['HOME'] = os.path.abspath(self.home)
		
		process = subprocess.Popen(
			['bash'],
			cwd = self.cwd,
			stdin = subprocess.PIPE,
			stdout = subprocess.PIPE,
			stderr = subprocess.PIPE,
			env = environ)
		
		input = ''.join(i + '\n' for i in lines).encode()
		out, err = process.communicate(input)
		
		sys.stdout.buffer.write(out)
		sys.stderr.buffer.write(err)
		
		# We expect all output to be valid UTF-8, mainly because all output should be ASCII.
		return RunResult(process.returncode, out.decode(), err.decode())
	
	def run(self, *lines, expect_error = False, expect_stdout_contains = '', expect_stderr_contains = ''):
		"""
		Runs the specified commands by piping them into a non-interactive bash process.
		"""
		
		def iter_lines():
			yield 'set -e'
			
			for i in lines:
				yield i
				
				# Enable errexit whenever a new shell session might have been started.
				if i.split()[0] == 'venv':
					yield 'set -e'
		
		result = self._run_commands(list(iter_lines()))
		
		if expect_error:
			assert result.returncode
		else:
			assert not result.returncode
		
		assert expect_stdout_contains in result.stdout
		assert expect_stderr_contains in result.stderr
		
		return result
	
	def check_venv(self, path = 'venv', *, exists = True):
		if exists:
			self.run(
				'. {}/bin/activate'.format(path),
				'[ "$VIRTUAL_ENV" ]')
		else:
			self.run(
				'! [ -e venv ]')
	
	def create_file(self, path, content : str = ''):
		with open(os.path.join(self.cwd, path), 'w', encoding = 'utf-8') as file:
			file.write(content)
	
	def create_dir(self, path):
		os.makedirs(os.path.join(self.cwd, path), exist_ok = True)
	
	def check_file(self, path, content = None, *, exists = True):
		file_path = os.path.join(self.cwd, path)
		
		if exists:
			assert os.path.isfile(file_path)
			
			if content is not None:
				with open(file_path, 'r', encoding = 'utf-8') as file:
					assert file.read() == content
		else:
			if content is not None:
				raise ValueError('content must be None if exists is set to False.')
			
			assert not os.path.exists(file_path)
	
	def check_dir(self, dirs = [], files = [], *, path = '.', exclude_hidden = True):
		"""
		Check that a set of directories exists and that only those directories exist.
		"""
		
		found_dirs = set()
		found_files = set()
		
		for i in os.listdir(os.path.join(self.cwd, path)):
			if not (i.startswith('.') and exclude_hidden):
				item_path = os.path.join(self.cwd, path, i)
				
				if os.path.isdir(item_path):
					found_dirs.add(i)
				elif os.path.isfile(item_path):
					found_files.add(i)
		
		if dirs is not None:
			assert found_dirs == set(dirs)
		
		if files is not None:
			assert found_files == set(files)


@contextlib.contextmanager
def workspace(*, virtualenvs = [], dummy_project = False):
	with tempfile.TemporaryDirectory() as temp_dir:
		ws = Workspace(temp_dir)
		
		if dummy_project:
			for i in 'setup.py', 'venv_cli_dummy.py':
				data = pkgutil.get_data(__name__, os.path.join('example_project', i)).decode()
				
				ws.create_file(i, data)
		
		for i in virtualenvs:
			ws.run('venv --no-activate {}'.format(i))
		
		yield ws
