from setuptools import setup

setup(
    name='trello-cms',
    author='Jaco du Plessis',
    author_email='jaco@jacoduplessis.co.za',
    description='Build websites with Trello data',
    url='https://github.com/jacoduplessis/trello_cms',
    keywords='trello cms ssg',
    version='0.0.10',
    packages=['trello_cms'],
    install_requires=[
        'jinja2',
        'markdown'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
)
