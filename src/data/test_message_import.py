import mailbox 
from jobs_db.gmail_message import GmailMessage

def test():
    mb = mailbox.mbox('/Users/alihodroj/gdata/sources/gmail/jobs-tag.mbox')
    num_entries = len(mb)

    for idx, email_obj in enumerate(mb):
        email_data = GmailMessage(email_obj)
        print('"{0}","{1}","{2}"'.format(email_data.email_date, email_data.email_from, email_data.email_subject))