from setuptools import setup

setup(name='jockbot_nhl',
      version='0.0.7',
      description='Retrieve info from NHL API',
      url='http://github.com/jalgraves/jockbot_nhl',
      author='Jonny Graves',
      author_email='jalgraves@yahoo.com',
      license='MIT',
      packages=['jockbot_nhl'],
      zip_safe=False,
      install_requires=['pytz', 'requests'],
      include_package_data=True
      )
