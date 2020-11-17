from setuptools import setup

def parse_requirements(filename):
    """ load requirements from a pip requirements file """
    lineiter = (line.strip() for line in open(filename))
    return [line for line in lineiter if line and not line.startswith("#")]

# parse_requirements() returns generator of pip.req.InstallRequirement objects
install_reqs = parse_requirements("requirements.txt")

setup(name='mtgather',
      version='0.2',
      description='A package for interfacing with MTG mysql server',
      url='http://github.com/ChrisWeldon/FMTG',
      author='Chris Evans',
      author_email='cwevans612@gmail.com',
      license='GNU',
      packages=['mtgather'],
      zip_safe=False,
      scripts=['bin/mtgather'],
      install_requires = install_reqs,
      test_suite='nose.collector',
      include_package_data=True,
      tests_require=['nose'],
)
