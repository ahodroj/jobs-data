# -*- coding: utf-8 -*-
import click
import logging
import mailbox
from pathlib import Path
from dotenv import find_dotenv, load_dotenv
from datetime import datetime, timedelta
import duckdb
import polars as pl

from gmail_message import GmailMessage
from job_application import JobApplication    


@click.command()
@click.argument('input_filepath', type=click.Path(exists=True))
@click.argument('output_filepath', type=click.Path())
def main(input_filepath, output_filepath):
    """ Runs data processing scripts to turn raw data from (../raw) into
        cleaned data ready to be analyzed (saved in ../processed).
    """
    logger = logging.getLogger(__name__)
    logger.info('making processed data set from raw data')
    
    logger.info('making processed data set from' + input_filepath)
    
    logger.info('ingesting mailbox data')
    mb = mailbox.mbox(input_filepath + '/applications.mbox')
    reject_mb = mailbox.mbox(input_filepath + '/rejections.mbox')
    logger.info('ingested {0} applications and {1} rejections'.format(len(mb), len(reject_mb)))
    
    jobs = []
    # Look it up in duckdb 
    #con = duckdb.connect('data/raw/company.db', read_only=True)
    # Query a row from the table

    logger.info('creating job models')
    for idx, msg_payload in enumerate(mb):
        msg = GmailMessage(msg_payload)
        job = JobApplication(msg)
        
        a_date = datetime.strptime(job.apply_date, "%m/%d/%Y")
        start_date = datetime.strptime("9/1/2024", "%m/%d/%Y")
        if a_date >= start_date:
            jobs.append(job)

        #pdf = con.execute("SELECT * FROM company_us WHERE _name = $1", [job.company.lower().replace("'","")]).pl()        
        #if pdf.is_empty() == False:
        #    job.company_id, job.company_name_external, job.company_website = pdf['id'][0], pdf['_name'][0], pdf['website'][0]
       
    #con.close()

    logger.info('matching rejection dates')
    for idx, msg_payload in enumerate(reject_mb):
        msg = GmailMessage(msg_payload)
        
        subject = msg.email_subject
        sender = msg.email_from
        
        for j in jobs:
            if j.company in subject or j.company in sender:
                if j.reject_date == "":               
                    apply_date = datetime.strptime(j.apply_date, "%m/%d/%Y")
                    reject_date = datetime.strptime(msg.email_date, "%m/%d/%Y")
                    apply_time_frame = (reject_date - apply_date).days
                    if apply_time_frame <= 90 and apply_time_frame > -1:
                        j.reject_date = msg.email_date
    
    # sort jobs in descending order 
    jobs.sort(key=lambda x: datetime.strptime(x.apply_date, "%m/%d/%Y"), reverse=True)

    logger.info('write output csv file')
    with open(output_filepath + "/applications.csv", "w") as f:
        f.write('company\tapply_date\treject_date\n')
        for j in jobs:
            f.write('{1}\t{0}\t{2}\n'.format(j.apply_date, j.company, j.reject_date))
    


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    project_dir = Path(__file__).resolve().parents[2]

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    load_dotenv(find_dotenv())

    main()
