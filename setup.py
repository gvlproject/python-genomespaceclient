from setuptools import setup, find_packages

setup(name='python-genomespaceclient',
      version="0.1.1",
      description='Python bindings and commandline client to the GenomeSpace'
      ' API',
      author='GVL Project',
      author_email='help@genome.edu.au',
      url='http://python-genomespaceclient.readthedocs.org/',
      install_requires=['boto3', 'python-swiftclient'],
      packages=find_packages(),
      license='MIT',
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: MIT License',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: Implementation :: CPython',
          'Programming Language :: Python :: Implementation :: PyPy'],
      entry_points={
          'console_scripts': [
              'genomespace = genomespaceclient:main'
          ]
      }
      )
