from setuptools import setup, find_packages
setup(
    name='twitter-game-book',
    version='0.0.2-2',
    packages=find_packages(),
    # Register the command line package as a console-script to go in $PATH
    entry_points = {
        'console_scripts': ['runtwgb=twgamebook.command_line:main'],
    },
    install_requires = ['docopt', 'requests'],
    author='DJ Nrrd',
    author_email='djnrrd@gmail.com',
    url='https://github.com/djnrrd/twitter-game-book',
    project_urls={
        'Bug Tracker': 'https://github.com/djnrrd/twitter-game-book/issues',
        'Source Code': 'https://github.com/djnrrd/twitter-game-book/',
    },

    keywords='twitter bot twitterbot games',
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: No Input/Output (Daemon)',
        'Topic :: Games/Entertainment :: Role-Playing'
    ]
)