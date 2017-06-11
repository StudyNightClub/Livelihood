# livelihood-database v3.0.0

Create and populate livelihood DB (sqlite).

## Installation

    $ pip3 install git+https://github.com/StudyNightClub/livelihood-database.git

## Usage

    from livelihood_database import livelihood

    # Create DB
    livelihood.create_database(database=<filename>)

    # Populate data
    livelihood.import_all(database=<filename>)

If the provided `<filename>` already contains target tables, `create_database()`
will fail. The default database file name is `livelihood.db`.
