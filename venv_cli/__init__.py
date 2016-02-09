import os, sys, contextlib, argparse, subprocess, shutil, io, tempfile


# TODO: Currently hardcoded. Need to see which shells we want to support and how we want to detect a user's shell.
_shell = 'bash'


class UserError(Exception):
	def __init__(self, msg, *args, exit_code = 1):
		super().__init__(msg.format(*args))
		
		self.exit_code = exit_code


def log(msg, *args):
	print('{}: {}'.format(os.path.basename(sys.argv[0]), msg.format(*args)), file = sys.stderr)


def bash_escape_string(string):
	"""
	Return a version of string which can be used in a bash script without additional escaping.
	"""
	
	return "'{}'".format("'\\''".join(string.split("'")))


def command(*args, use_stdout = False):
	stdout = subprocess.PIPE if use_stdout else None
	process = subprocess.Popen(args, stdout = stdout, close_fds = False)
	
	out, _ = process.communicate()
	
	if process.returncode:
		raise Exception('Error running command: {}'.format(' '.join(args)))
	
	return out


def rm_temp(path):
	try:
		if os.path.exists(path):
			shutil.rmtree(path)
	except OSError as e:
		raise UserError('Removing temporary path {} failed: {}', path, e)


@contextlib.contextmanager
def backed_up_dir(path):
	"""
	If there is a directory at the specified path, it is moved to a backup path when the context is entered. If the context is left normally, the backup is deleted. Otherwise, anything at the specified path is removed and the backup is moved back in place.
	"""
	
	backup_path = path + '~venv_cli_backup'
	delete_path = path + '~venv_cli_delete'
	
	rm_temp(backup_path)
	rm_temp(delete_path)
	
	if os.path.exists(path):
		os.rename(path, backup_path)
	
	try:
		yield
	except:
		if os.path.exists(path):
			os.rename(path, delete_path)
		
		if os.path.exists(backup_path):
			os.rename(backup_path, path)
		
		rm_temp(delete_path)
		
		raise
	else:
		if os.path.exists(backup_path):
			rm_temp(backup_path)


@contextlib.contextmanager
def temporary_script(lines : list):
	# The script close the original file descriptor upon execution. But if execution fails, TemporaryFile should close it.
	with tempfile.TemporaryFile() as file:
		fd = file.fileno()
		name = '/dev/fd/{}'.format(fd)
		writer = io.TextIOWrapper(file)
		
		# Close the original file descriptor, which has been duplicated by bash when this line is executed.
		for i in ['exec {}<&-'.format(fd)] + lines:
			print(i, file = writer)
		
		writer.flush()
		file.seek(0)
		
		# Otherwise, the shell would not be able to access this file descriptor.
		os.set_inheritable(fd, True)
		
		yield name


def exec_shell(rc_lines : list):
	"""
	Replace the current process with a new shell and provide it with an rc file with the specified content.
	
	This function does not return unless a failure occurs.
	"""
	
	bash_executable = shutil.which(_shell)
	
	with temporary_script(rc_lines) as name:
		# TODO: We assume that the only open file descriptors at this time are stdin, stderr, stdout and the rcfile.
		os.execvp(bash_executable, [_shell, '--rcfile', name, '-i'])


class Virtualenv:
	def __init__(self, path):
		self.path = path
	
	def create(self, python : str, prompt : str, setup : bool):
		with backed_up_dir(self.path):
			command('virtualenv', '--python', python, '--prompt', prompt, self.path)
			
			if setup:
				lines = [
					'set -e',
					'. {}/bin/activate'.format(bash_escape_string(self.path)),
					'python setup.py develop']
				
				with temporary_script(lines) as script:
					command('bash', script)
	
	def activate(self):
		lines = [
			'[ -e ~/.bashrc ] && . ~/.bashrc',
			'. {}/bin/activate || exit $?'.format(bash_escape_string(self.path))]
		
		exec_shell(lines)
	
	@property
	def python_version_string(self):
		"""
		Given the path to a virtualenv return the Python version string for the install interpreter. This is what `python --version` returns.
		"""
		
		stdout = command(os.path.join(self.path, 'bin', 'python'), '--version', use_stdout = True)
		
		return stdout.decode().strip()
	
	@property
	def path_exists(self):
		return os.path.exists(self.path)
	
	@property
	def is_virtualenv(self):
		return all(os.path.isfile(os.path.join(self.path, 'bin', i)) for i in ['activate', 'python'])


def parse_args():
	parser = argparse.ArgumentParser(description = 'Create, setup and/or activate a virtualenv within a newly started shell.')
	
	parser.add_argument('-c', '--create', action = 'store_true', help = 'Create virtualenv, unless one already exists at the specified path, before activating it.')
	parser.add_argument('-r', '--recreate', action = 'store_true', help = 'Remove an already existing virtualenv before creating a new one. This implies --create.')
	parser.add_argument('-s', '--setup', action = 'store_true', help = 'Run `python setup.py develop\' after creating the virtualenv. This implies --recreate.')
	parser.add_argument('-n', '--no-activate', dest = 'activate', action = 'store_false', help = 'Do not activate the virtualenv. Implies --create.')
	parser.add_argument('-p', '--python', type = str, default = None, help = 'The Python interpreter to use. Defaults to `python\'. Specifying this implies --recreate.')
	parser.add_argument('-t', '--test', action = 'store_true', help = 'Test whether the specified path is a virtualenv and print a message. If the specified path is not a virtualenv, the exit status will be set to 1. This option conflicts with --create, --recreate, --setup and --no-activate.')
	
	parser.add_argument('virtualenv', nargs = '?', type = Virtualenv, default = Virtualenv('venv'), help = 'Path to the virtualenv to operate on. Defaults to `venv\'')
	
	args = parser.parse_args()
	
	if args.setup:
		# --setup and --python imply --recreate
		args.recreate = True
	
	if args.python:
		# --python implies --recreate
		args.recreate = True
	else:
		args.python = 'python'
	
	if args.recreate:
		# --recreate implies --recreate
		args.create = True
	
	if not args.activate and not args.test:
		# Not specifying --activate or --test implies --create 
		args.create = True
	
	if args.create and args.test:
		parser.error('--test cannot be specified if any of --create, --recreate, --setup, --python or --no-activate are specified.')
	
	if args.test:
		if not args.activate:
			parser.error('--no-activate cannot be specified if --test is specified.')
		
		args.activate = False
	
	return args


def main(create : bool, recreate : bool, setup : bool, activate : bool, python : str, virtualenv : Virtualenv, test : bool):
	if test:
		if virtualenv.is_virtualenv:
			log('{} is a virtualenv running {}.', virtualenv.path, virtualenv.python_version_string)
		elif virtualenv.path_exists:
			raise UserError('{} is not a virtualenv.', virtualenv.path)
		else:
			raise UserError('{} does not exist.', virtualenv.path)
	else:
		parent_dir = os.path.dirname(os.path.abspath(virtualenv.path))
		prompt = '({}) '.format(os.path.basename(parent_dir))
		
		if not os.path.exists(parent_dir):
			raise UserError('Parent {} does not exist.', os.path.dirname(virtualenv.path))
		elif not os.path.isdir(parent_dir):
			raise UserError('Parent {} is not a directory.', os.path.dirname(virtualenv.path))
		
		if create:
			if not virtualenv.is_virtualenv or recreate:
				if virtualenv.path_exists and not virtualenv.is_virtualenv:
					raise UserError('{} is not a virtualenv.', virtualenv.path)
				
				virtualenv.create(python, prompt, setup)
		
		if activate:
			if not virtualenv.path_exists:
				raise UserError('{} does not exist.', virtualenv.path)
			elif not virtualenv.is_virtualenv:
				raise UserError('{} is not a virtualenv.', virtualenv.path)
			
			log('Activating virtualenv {} running {}.', virtualenv.path, virtualenv.python_version_string)
			
			virtualenv.activate()


def script_main():
	try:
		main(**vars(parse_args()))
	except UserError as e:
		log('Error: {}', e)
		sys.exit(e.exit_code)
	except KeyboardInterrupt:
		log('Operation interrupted.')
		sys.exit(2)
