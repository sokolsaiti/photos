from setuptools import setup

from conf.settings import BASE_URL

setup(
    name='photos',
    version='0.1',
    packages=[''],
    package_dir={'': 'db'},
    url=BASE_URL,
    license='The Unlicense',
    author='Sokol Saiti',
    author_email='',
    description='Simple web app for publishing and displaying photos.'
)
