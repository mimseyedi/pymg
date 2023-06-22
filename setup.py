from setuptools import setup, find_packages
from pathlib import Path


HERE = Path(__file__).parent
README = (HERE / "README.md").read_text()
install_requires = ['rich', 'click', 'requests']
dependency_links = ['rich', 'click', 'requests']


setup (
 name = 'pymg',
 description = 'pymg is a CLI tool that can interpret Python files by the Python interpreter and display the error message in a more readable way if an exception occurs.',
 version = '1.1.1',
 packages = find_packages(),
 install_requires = install_requires,
 python_requires='>=3.11',
 entry_points='''
        [console_scripts]
        pymg=pymg.pymg:main
    ''',
 author="mimseyedi",
 keyword=["pymg", "debugger", "CLI", "Python", "bug", "debugger-tool"],
 long_description=README,
 long_description_content_type="text/markdown",
 license='GNU General Public License v3 (GPLv3)',
 url='https://github.com/mimseyedi/pymg',
 dependency_links=dependency_links,
 author_email='mim.seyedi@gmail.com',
 classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
    ]
)