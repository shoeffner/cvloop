from distutils.core import setup

VERSION = '0.1.0'

setup(
  name = 'cvloop',
  version = VERSION,
  description = 'cvloop allows online video transformation and evaluation with OpenCV. Designed for jupyter notebooks.',
  author = 'Sebastian Höffner',
  author_email = 'info@sebastian-hoeffner.de',
  url = 'https://github.com/shoeffner/cvloop',
  download_url = 'https://github.com/shoeffner/cvloop/tarball/{}'.format(VERSION),
  packages = ['cvloop'],
  classifiers = [
      'Development Status :: 3 - Alpha',
      'Intended Audience :: Education',
      'Intended Audience :: Science/Research',
      'License :: OSI Approved :: MIT License',
      'Natural Language :: English',
      'Programming Language :: Python',
      'Programming Language :: Python :: 3.5',
      'Programming Language :: Python :: 3.6',
      'Topic :: Multimedia :: Video :: Display',
  ],
  keywords = [
      'OpenCV', 'cv2', 'video', 'loop', 'jupyter', 'notebook'
  ],
)
