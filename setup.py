from setuptools import setup

def parse_requirements(filename):
    """ load requirements from a pip requirements file """
    lineiter = (line.strip() for line in open(filename))
    return [line for line in lineiter if line and not line.startswith("#")]

# parse_requirements() returns generator of pip.req.InstallRequirement objects
install_reqs = parse_requirements("requirements.txt")

print(install_reqs)

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
      tests_require=['nose'],
)
