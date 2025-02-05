# -*- coding: utf-8 -*-
import click
import logging
import duckdb
from pathlib import Path
from dotenv import find_dotenv, load_dotenv


@click.command()
@click.argument('input_filepath', type=click.Path(exists=True))
@click.argument('output_filepath', type=click.Path())
def main(input_filepath, output_filepath):
    """ Runs data processing scripts to turn processed data from (../processed) into
        a ready to use SQL database (saved in ../db).
    """
    logger = logging.getLogger(__name__)
    logger.info('making final database set from processed data')
    
    logger.info('creating duckdb in data/db/jobs.db')
    # Create a connection to the DuckDB database (in-memory by default)
    con = duckdb.connect(database = "data/db/jobs.db", read_only=False)

    logger.info('ingesting processed data')
    con.execute("""
        CREATE OR REPLACE TABLE job_applications AS 
        SELECT * 
            FROM read_csv_auto('data/processed/applications.csv', dateformat = '%m/%d/%Y', ignore_errors = true)
        """)
    
    logger.info('closing database connection. Database is persisted in data/db/jobs.db')
    con.close()


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    project_dir = Path(__file__).resolve().parents[2]

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    load_dotenv(find_dotenv())

    main()
