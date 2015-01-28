from setuptools import setup

setup(name='SLDB',
      version='4.0.0',
      author='Aaron M. Rosenfeld',
      author_email='ar374@drexel.edu',
      packages=[
          'sldb',
          'sldb.aggregation',
          'sldb.api',
          'sldb.common',
          'sldb.conversion',
          'sldb.identification',
          'sldb.trees',
          'sldb.util',
      ],
      scripts=[
          'bin/sldb_align',
          'bin/sldb_clones',
          'bin/sldb_clone_tree',
          'bin/sldb_conv_table',
          'bin/sldb_identify',
          'bin/sldb_mt2db',
          'bin/sldb_newick2json',
          'bin/sldb_rest',
          'bin/sldb_sample_stats',
          'bin/sldb_clone_stats',
      ],
      install_requires=[
          'gevent',
          'sqlalchemy>=0.9.8',
          'biopython',
          'bottle',
          'ete2>=2.2',
          'distance',
          'numpy',
          'scipy',
          'tabulate',
          'PyMySQL',
      ],
      package_data={'sldb': ['data/germlines/*']},
      license='LICENSE.txt',
      description='Various utilities for Drexel\'s Systems Immunology Lab.')
