from setuptools import setup, find_packages
from io import open

# with open('SpeechAdjuster/README.md', encoding='utf-8') as f:
#     long_description = f.read()

setup(
    name = 'speechadjuster',
    version = 'v1.0.0.dev1',  # Ideally should be same as your GitHub release tag varsion
    description = ' ',
    packages=find_packages(include=['SpeechAdjuster', 'SpeechAdjuster.*']),
    package_data = {
    'SpeechAdjuster': ['config.ini', 'README.md', 'graphics/*.png']
    },
    include_package_data = False,
    author = 'Olympia Simantiraki',
    author_email = 'olina.simantiraki@gmail.com',
    url = 'https://github.com/osimantir/speechadjuster.git',
    download_url = 'https://github.com/osimantir/speechadjuster/archive/v1.0.0.tar.gz',
    keywords = [],
    classifiers = [],
    python_requires='>=3.6',
    install_requires=['numpy>=1.19.5','pandas>=1.1.5', 'pyaudio>=0.2.11', 'Cython>=0.29.22','kivy>=1.10', 'matplotlib>=3.3.4'
      ],
    # long_description=long_description,
    # long_description_content_type='text/markdown',
    entry_points={
        "console_scripts": [
            "speechadjuster = SpeechAdjuster.speechadjuster:main", 
            "results = SpeechAdjuster.results:main"
        ]
    },
)
