from setuptools import setup, find_packages
from pip.req import parse_requirements
import uuid

# parse_requirements() returns generator of pip.req.InstallRequirement objects
install_reqs = parse_requirements('requirements.txt', session=uuid.uuid1())

# reqs is a list of requirement
# e.g. ['django==1.5.1', 'mezzanine==1.4.6']
reqs = [str(ir.req) for ir in install_reqs]

version = '0.7'

setup(
    name='tshoot',
    version=version,
    py_modules=[''],
    packages=find_packages(),
    install_requires=reqs,
    include_package_data=True,
    description = 'Python script that inject multiple faults into a scenario / lab for training purpose use.',
    author = 'Francesco Marangione',
    author_email = 'mft@mftnet.com',
    url = 'https://github.com/mft3000/tshoot', # use the URL to the github repo
    download_url = 'https://github.com/tshoot/tarball/%s' % version,
    keywords = ['cisco', 'networking', 'training', 'ccie', 'troubleshooting'],
    classifiers = [],
)