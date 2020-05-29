from setuptools import setup
import sys,os

setup(
	name = 'iotr-configure',
	version = '0.0.2',
	description = 'Configure the IOT router',
	license='GPL v3',
	author = 'Kevin Bertrand',
	packages = ['src'],
	package_data={'src': ['description.txt']
		},
	install_requires=['future'],
	entry_points = {
		'console_scripts': [
			'hello=src.app:main']
		},
	classifiers = ['Operating System :: OS Independent',
		'Programming Language :: Python :: 2.7',
		'Programming Language :: Python :: 3.6',
		'Operating System :: MacOS :: MacOS X',
		'Operating System :: Microsoft :: Windows',
		'Operating System :: POSIX',
		'License :: OSI Approved :: GNU General Public License v3 (GPLv3)'],
)
