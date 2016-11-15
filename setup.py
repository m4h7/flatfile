from setuptools import setup

setup(name='flatfile',
      version='1.0',
      description='Simple structured binary flatfile reader/writer',
      license='MIT',
      packages=['flatfile'],
      setup_requires=['pytest-runner'],
      tests_require=['pytest'],
      zip_safe=False)
