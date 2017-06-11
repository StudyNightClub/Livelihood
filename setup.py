# encoding: utf-8

from setuptools import setup

setup(name='livelihood_database',
      version='2.0.0',
      description='Create and import livelihood database.',
      url='https://github.com/StudyNightClub/livelihood-database',
      author='Lucas Wang',
      author_email='',
      license='MIT',
      packages=['livelihood_database'],
      install_requires=[
          'requests==2.17.3',
      ],
      zip_safe=False)
