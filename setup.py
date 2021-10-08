import os
from setuptools import setup

ROOT = os.path.dirname(__file__)

def get_version():
    with open(os.path.join(ROOT, 'marathon_deploy', 'version.txt')) as version_file:
        return version_file.read().strip()

setup(
    name='marathon-deploy',
    version=get_version(),
    description='CLI tool to manage deployment of applications to Marathon from JSON files',
    author='Nicolas Villanueva',
    author_email='villanueva.arg@gmail.com',
    packages=['marathon_deploy', 'marathon_deploy.utils'],
    install_requires=['marathon>=0.9.3'],
    entry_points={
        'console_scripts': ['marathon-deploy = marathon_deploy.deploytool:main',
                            'marathon-check = marathon_deploy.checkappdeploy:main'],
    },
    include_package_data=True,
    zip_safe=False
)
