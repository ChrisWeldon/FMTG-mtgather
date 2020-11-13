from setuptools import setup

def parse_requirements(filename):
    """ load requirements from a pip requirements file """
    lineiter = (line.strip() for line in open(filename))
    return [line for line in lineiter if line and not line.startswith("#")]

# parse_requirements() returns generator of pip.req.InstallRequirement objects
install_reqs = parse_requirements("requirements.txt")

install_reqs = [
  'beautifulsoup4==4.9.3',
  'bs4==0.0.1',
  'certifi==2020.6.20',
  'chardet==3.0.4',
  'fake-useragent==0.1.11',
  'idna==2.10',
  'importlib-metadata==2.0.0',
  'Mako==1.1.3',
  'Markdown==3.3.3',
  'MarkupSafe==1.1.1',
  'mysql-connector==2.2.9',
  'mysql-connector-python==8.0.22',
  'nose==1.3.7',
  'numpy==1.19.4',
  'pandas==1.1.4',
  'pdoc3==0.9.1',
  'protobuf==3.13.0',
  'python-dateutil==2.8.1',
  'pytz==2020.4',
  'requests==2.24.0',
  'six==1.15.0',
  'soupsieve==2.0.1',
  'urllib3==1.25.11',
  'zipp==3.4.0']

setup(name='mtgather',
      version='0.1',
      description='package for interfacing with MTG mysql server',
      url='http://github.com/ChrisWeldon/FMTG',
      author='Chris Evans',
      author_email='cwevans612@gmail.com',
      license='GNU',
      packages=['mtgather'],
      zip_safe=False,
      install_requirements = install_reqs,
      test_suite='nose.collector',
      include_package_data=True,
      tests_require=['nose'],
)
