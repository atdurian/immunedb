ImmuneDB |travisci| |codecov| |pypi| |docker|
========
.. |travisci| image:: https://img.shields.io/travis/arosenfeld/immunedb/master.svg
  :target: https://travis-ci.org/arosenfeld/immunedb
.. |codecov| image:: https://img.shields.io/codecov/c/github/arosenfeld/immunedb.svg
  :target: https://codecov.io/gh/arosenfeld/immunedb
.. |docker| image:: https://img.shields.io/docker/pulls/arosenfeld/immunedb.svg
  :target: https://hub.docker.com/r/arosenfeld/immunedb
.. |pypi| image:: https://img.shields.io/pypi/v/immunedb.svg
  :target: https://pypi.python.org/pypi/ImmuneDB

**ImmuneDB** is a system that facilitate efficient storage and analysis
of high-throughput B- and T-cell sequence data.  It provides V- and J-gene
identification, clonal assignment, lineage construction, selection pressure
calculation, and thorough exporting functionality.

ImmuneDB is comprised of two code bases: Python analysis tools
(`GitHub <https://github.com/arosenfeld/immunedb>`_) and a web interface
(`GitHub <https://github.com/arosenfeld/immunedb-frontend>`_).  You can see a
demo of the interface `here <http://immunedb.com/demo>`_.

The system aims to:

- **Reduce ad-hoc scripting:** Data analysis performed on an ad-hoc basis with
  custom scripts and data formats is error-prone and leads to inconsistencies.
  ImmuneDB provides a standardized analysis platform, performing many common tasks
  automatically.

- **Minimize flat-files:** Flat files are currently the standard method of
  data exchange in the biological sciences.  There are a myriad of drawbacks
  when using these including a lack of `referential integrity
  <http://en.wikipedia.org/wiki/Referential_integrity>`_, unclear `provenance
  <http://en.wikipedia.org/wiki/Provenance#Data_provenance>`_, and
  non-standardized formats.

  ImmuneDB attempts to reduce the need for flat files, through the use of an
  industry-leading database, MySQL.  When data must be exchanged as a flat-file,
  many export options, including FASTA and tab-delineation, are available.

- **Provide a generic API:** ImmuneDB provides both a REST API for language-agnostic
  database querying as well as a suite of Python classes for interacting directly
  with the database for customized querying.

ImmuneDB has four primary components:

- **Clonal identification pipeline:** A series of steps which identify probable
  V- and J-genes from raw FASTA files and subsequently groups sequences from the
  same subject into clones.  At each step, statistics and metadata are stored in
  the underlying database for later analysis.

- **Analysis framework:** A module that provide detailed analysis of sequences.
  This includes mutation analysis, gene utilization breakdowns, and feature
  distributions  (e.g. CDR3 length, V-gene utilization).

- **API:**  ImmuneDB includes two APIs.  First, the REST API allows native and web
  applications (via AJAX) to interact with the underlying database without writing
  any database specific code.  Further, the REST API is language agnostic, using
  HTTP to exchange data.

  Second, the Python API which implements the data models and querying
  functionality.  This allows developers to write customized queries directly
  interacting with the database.

- **Web interface:** Distributed separately of ImmuneDB is a web interface which
  utilizes the REST API to allow for easy browsing of analysis results.


Each of the components can be used independently so long as the underlying
database is properly populated.

Table of Contents
---------------
.. toctree::
    :maxdepth: 2

    getting_started_docker
    getting_started_local
    pipeline
    database

Underlying Technologies
-----------------------

- `MySQL <http://www.mysql.com>`_: The database (agnostic
  of implementation like `MariaDB <https://mariadb.org>`_) which enforces rigorous
  data guarantees, indexes the data for fast retrieval, and enforces atomicity
  of operations

- `SQLAlchemy <http://www.sqlalchemy.org>`_: The interface between Python and
  the database which abstracts SQL queries from the implementation and enforces
  the data model within Python.

- `Bottle <http://bottlepy.org>`_: A lightweight web-framework for Python which
  serves content via the REST API allowing web-applications to issue AJAX requests
  to the ImmuneDB framework.


Modules
====================
.. toctree::
    :maxdepth: 2

    common
    models
    api
    referencing

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
