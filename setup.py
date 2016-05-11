import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='wagtailvisualdiff',
    version='0.2',
    packages=find_packages(),
    include_package_data=True,
    license='MIT License',
    description='A wagtail addon to screenshot whenever changes to a page are published and deliver a Diff to Slack.',
    long_description=README,
    url='https://www.github.com/adriangoe/wagtailvisualdiff',
    author='Adrian Goedeckemeyer',
    author_email='adrian@minerva.kgi.edu',
    keywords="wagtail cms diff visual screenshot",
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    install_requires=[
        "wagtail>=1.4",
        "jsondiff",
    ],
)
