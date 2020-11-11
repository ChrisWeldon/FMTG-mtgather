from setuptools import setup

setup(name='mtgather',
      version='0.1',
      description='package for interfacing with MTG mysql server',
      url='http://github.com/ChrisWeldon/FMTG',
      author='Chris Evans',
      author_email='cwevans612@gmail.com',
      license='GNU',
      packages=['mtgather'],
      zip_safe=False,
      test_suite='nose.collector',
      tests_require=['nose'],
)
