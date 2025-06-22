from setuptools import setup, find_packages

setup(
    name='sqlmap_gui',
    version='1.1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'PyQt5',
    ],
    entry_points={
        'console_scripts': [
            'sqlmap-gui=sqlmap_gui.main:main',
        ],
    },
    package_data={
        'sqlmap_gui': ['resources/icon.png'],
    },
)
