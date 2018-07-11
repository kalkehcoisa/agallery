import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.txt')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.txt')) as f:
    CHANGES = f.read()

requires = [
    'boto3==1.7.54',
    'plaster_pastedeploy==0.5',
    'pyramid==1.9.2',
    'pyramid_debugtoolbar==4.4',
    'pyramid_jinja2==2.7',
    'pyramid_nacl_session==0.3',
    'pyramid_retry==0.5',
    'pyramid_tm==2.2',
    'SQLAlchemy==1.2.9',
    'transaction==2.2.1',
    'zope.sqlalchemy==1.0',
    'waitress==1.1.0',
    'WTForms-Alchemy==0.16.7'
]

tests_require = [
    'WebTest >= 1.3.1',  # py3 compat
    'pytest',
    'pytest-cov',
]

setup(
    name='agallery',
    version='0.0',
    description='Anchor Gallery',
    long_description=README + '\n\n' + CHANGES,
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Pyramid',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
    ],
    author='',
    author_email='',
    url='',
    keywords='web pyramid pylons',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    extras_require={
        'testing': tests_require,
    },
    install_requires=requires,
    entry_points={
        'paste.app_factory': [
            'main = agallery:main',
        ],
        'console_scripts': [
            'initialize_agallery_db = agallery.scripts.initializedb:main',
        ],
    },
)
