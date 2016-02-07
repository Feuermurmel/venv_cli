import setuptools


setuptools.setup(
	name = 'venv_cli',
	version = '0.1',
	packages = setuptools.find_packages(),
	package_data = { '': ['*.*'] },
	install_requires = [],
	entry_points = dict(
		console_scripts = [
			'venv = venv_cli:script_main']))
