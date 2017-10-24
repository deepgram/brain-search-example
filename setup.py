"""
Copyright 2017 Deepgram
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
   http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from setuptools import setup, find_packages

PACKAGE='brainsearch'

__author__ = 'jmward'

################################################################################
def get_version():
	""" Gets the current version of the package.
	"""
	version_py = os.path.join(os.path.dirname(__file__), 'deepgram', 'version.py')
	with open(version_py, 'r') as fh:
		for line in fh:
			if line.startswith('__version__'):
				return line.split('=')[-1].strip().replace('"', '')
	raise ValueError('Failed to parse version from: {}'.format(version_py))

################################################################################


setup(
	# Package information
	name=PACKAGE,
	version=get_version(),
	description='A simple utility to search audio files in a directory',
	keywords='deep learning speech recognition',
	classifiers=[
	],

	# Author information
	url='https://github.com/deepgram/brain-search-example',
	author='Jeff Ward',
	author_email='susan@deepgram.com',
	license='Proprietary',

	# What is packaged here.
	packages=find_packages(),

	# What to include.
	package_data={
		'': ['*.txt', '*.rst', '*.md']
	},

	# Dependencies
	install_requires=[
		'deepgram-brain>=0.1.1'
	],

	entry_points={
		'console_scripts' : ['{pkg}={pkg}.__main__:main'.format(pkg=PACKAGE)]
	},
)
