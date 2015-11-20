from setuptools import setup

VERSION = '0.2'

setup(
  name = 'django_macfly',
  packages = ['django_macfly',
              "django_macfly.management",
              "django_macfly.management.commands"],
  version = VERSION,
  description = 'Django helpers to run SQL schema migrations ahead of time.',
  author = 'Bruno Dupuis',
  author_email = 'bruno.dupuis@people-doc.com',
  url = 'https://github.com/novafloss/django-MacFly',
  download_url = 'https://github.com/novafloss/django-MacFly/tarball/%s' % VERSION,
  keywords = ['django', 'migrations', 'DBA'],
  classifiers = [],
)

