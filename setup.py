# -*- coding: utf-8 -*-
from distutils.core import setup

import re

REPOSITORY = 'https://github.com/shoeffner/cvloop'
README = ''

with open('cvloop/__init__.py', 'r') as fd:
    VERSION = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        fd.read(), re.MULTILINE).group(1)

with open('README.rst', 'r') as f:
    README = f.read()

README = re.sub(
    r' _(.+): ([^(http)].+)',
    r' _\1: {}/blob/master/\2'.format(REPOSITORY),
    README)

setup(
    name='cvloop',
    version=VERSION,
    description='cvloop allows online video transformation and evaluation with OpenCV. Designed for jupyter notebooks.',  # noqa
    long_description=README,
    author='Sebastian Höffner',
    author_email='info@sebastian-hoeffner.de',
    url=REPOSITORY,
    download_url='{}/tarball/{}'.format(REPOSITORY, VERSION),
    packages=['cvloop'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Topic :: Multimedia :: Video :: Display',
    ],
    license='MIT',
    keywords=[
        'OpenCV', 'cv2', 'video', 'loop', 'jupyter', 'notebook'
    ],
)
