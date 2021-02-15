from setuptools import setup, find_packages

setup(
    name='zolocal',
    version='0.1.0',
    description='A Python tool kit for interacting with the locally hosted Zotero database.',
    url='https://github.com/sailist/pyzotero-local',
    author='Haozhe Yang',
    author_email='yyanghaozhe@outlook.com',
    license='GNU General Public License v3',
    include_package_data=True,
    install_requires=[],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3',
    ],
    keywords='zotero sqlite',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            # 'thexp = thexp.cli.cli:main'
        ]
    },
)
