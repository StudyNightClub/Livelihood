# livelihood-database v3.0.0

Create and populate livelihood DB (psycopg).

## Installation

    $ pip3 install git+https://github.com/StudyNightClub/livelihood-database.git

## Run

For development, you can create the database and populate all data to the livelihood DB server based on setting of the environment variables.

    $ export LDB_DATABASE=<server_administrator>
    $ export LDB_USER=<server_administrator>
    $ export ULDB_PASS=<server_administrator>
    $ export LDB_HOST=<server_administrator>
    $ export LDB_PORT=<server_administrator>
    
If any of the environment variable isn't set, runtime error will happen.
    
## Usage

    # Create DB
    livelihood.create_database()

    # Populate data
    livelihood.import_all()

If the provided `<filename_set>` already contains target tables, `create_database()` will fail. Please contact the server administrator.
