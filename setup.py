# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name='cakephp-instaweb',
    version='0.1',
    description='Instantly serves a CakePHP application',
    author='Chris Lamb',
    author_email='chris@chris-lamb.co.uk',
    license='MIT',
    url='http://chris-lamb.co.uk/projects/cakephp-instaweb/',
    py_modules=['cakephp_instaweb'],
    packages=[''],
    install_requires=['Twisted'],
    entry_points={
        'console_scripts': (
            'cakephp-instaweb = cakephp_instaweb:main',
        )
    },
)
