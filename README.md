# livelihood-database v6.0.0

Create and populate livelihood DB.

## Installation

    $ pip install git+https://github.com/StudyNightClub/livelihood-database.git

## Usage

In shell:

    # Setup DB URL (e.g., mysql://localhost:3306/db)
    $ export LDB_URL=<database_url>
    $ export GOOGLE_GEO_KEY=<google_geocode_api_key>

Since 4.0, livelihood_database uses sqlalchemy to handle database actions, so
multiple DB types are supported. Specify your DB type in the URL schema.
For detailed documentation, check
[here](http://docs.sqlalchemy.org/en/latest/index.html).

In python:

    from livelihood_database import livelihood

    # Create DB tables (or do nothing if the tables already exist.)
    livelihood.create_tables()

    # Populate data
    livelihood.import_all()
