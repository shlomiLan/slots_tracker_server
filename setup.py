from setuptools import setup

setup(
    name='slots_tracker',
    packages=['server'],
    include_package_data=True,
    install_requires=[
        'flask',
    ],
)
