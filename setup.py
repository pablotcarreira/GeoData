from setuptools import setup

setup(name='geodata',
      version='0.1.2',
      description='OGR/GDAL High level abstraction.',
      license='BSD',
      packages=['geodata', 'geodata.tests'],
      package_data={'geodata.tests': ['data/*', 'out/*']},
      # install_requires=['pytest', 'boto3', 'peewee'],
      python_requires='>=3.6',
      # setup_requires=['pytest-runner'],
      tests_require=['pytest'],
      zip_safe=False)
