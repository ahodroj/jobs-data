# -*- coding: utf-8 -*-
import click
import logging
import mailbox
from pathlib import Path
from dotenv import find_dotenv, load_dotenv

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
    
    logger.info('ingesting mailbox data')
    mb = mailbox.mbox('data/raw/jobs-tag.mbox')
    reject_mb = mailbox.mbox('data/raw/jobs-rejections-tag.mbox')
    logger.info('ingested {0} applications and {1} rejections'.format(len(mb), len(reject_mb)))
    
    jobs = []

    logger.info('creating job models')
    for idx, msg_payload in enumerate(mb):
        msg = GmailMessage(msg_payload)   
        job = JobApplication(msg)
        jobs.append(job)
        #print('Applied on {0} to {1}'.format(job.apply_date, job.company))

    logger.info('matching rejection dates')
    for idx, msg_payload in enumerate(reject_mb):
        msg = GmailMessage(msg_payload)
        
        subject = msg.email_subject
        sender = msg.email_from
        
        for j in jobs:
            if j.company in subject or j.company in sender:
                j.reject_date = msg.email_date
    
    
    logger.info('write output csv file')
    with open("data/processed/applications.csv", "w") as f:
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
