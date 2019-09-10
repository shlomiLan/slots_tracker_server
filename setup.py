from setuptools import setup

setup(
    version='3.2.0',
    name='slots_tracker',
    packages=['server'],
    include_package_data=True,
    install_requires=[
        'flask',
    ],
)
