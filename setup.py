from setuptools import setup, find_packages

version = '0.1'


def description():
    try:
        return open('README.rst').read()
    except:
        return ''

setup(name='wsgithumb',
      version=version,
      description=("helpers to get a WebOb response to serve static files "
                   "and thumbnails in an efficient way"),
      long_description=description(),
      classifiers=[],
      keywords='pyramid wsgi thumbnail PIL X-Sendfile X-Accel-Redirect',
      author='Gael Pasgrimaud',
      author_email='gael@gawel.org',
      url='http://github.com/gawel/pyramid_thumbnail',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          'WebOb',
          'PIL',
      ],
      entry_points="""
      # -*- Entry points: -*-
      [paste.app_factory]
      main = wsgithumb:make_thumb_app
      file = wsgithumb:make_file_app
      """,
      )
