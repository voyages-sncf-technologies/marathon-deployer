from setuptools import setup

setup(
    name='MarathonDeployTool',
    version='2.0',
    url="nourlforthis.com",
    description='CLI tool to manage deployment of applications to Marathon',
    author='Nicolas Villanueva',
    author_email='villanueva.arg@gmail.com',
    py_modules=['deploytool'],
    install_requires=[
        'marathon>=0.9.3'
    ],
    entry_points={
        'console_scripts': [
            'deploy=deploytool:main'
        ]
    },
    include_package_data=True,
    zip_safe=False
)
