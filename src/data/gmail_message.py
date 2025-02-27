import mailbox 
import bs4
from datetime import datetime
import email.header 


class GmailMessage():
    def __init__(self, email_data):
        if not isinstance(email_data, mailbox.mboxMessage):
            raise TypeError('Variable must be type mailbox.mboxMessage')
        self.email_data = email_data
        self.email_labels = self.email_data['X-Gmail-Labels']
        self.email_date = self._try_parsing_date()
        self.email_from = self.email_data['From']
        self.email_to = self.email_data['To']
        subj = self.email_data['Subject'].replace("\r\n", "")
        if "utf-" in subj.lower():
            subj = self._decode_mime_subject_string(subj)
        self.email_subject = subj
        self.email_text = self.read_email_payload() 

    def read_email_payload(self):
        email_payload = self.email_data.get_payload()
        if self.email_data.is_multipart():
            email_messages = list(self._get_email_messages(email_payload))
        else:
            email_messages = [email_payload]
        return [self._read_email_text(msg) for msg in email_messages]

    def _decode_mime_subject_string(self, s):
        decoded_parts = email.header.decode_header(s)
        final_string = ''
        for part, encoding in decoded_parts:
            if encoding:
                final_string += part.decode(encoding)
            else:
                final_string += part.decode('utf-8')
        return final_string


    def _get_email_messages(self, email_payload):
        for msg in email_payload:
            if isinstance(msg, (list,tuple)):
                for submsg in self._get_email_messages(msg):
                    yield submsg
            elif msg.is_multipart():
                for submsg in self._get_email_messages(msg.get_payload()):
                    yield submsg
            else:
                yield msg
                
    def _get_html_text(self,html):
        try:
            return bs4.BeautifulSoup(html, 'lxml').body.get_text(' ', strip=True)
        except AttributeError: # message contents empty
            return None
               
    def _try_parsing_date(self):
        date_str = self.email_data['Date']
        date_str =  " ".join(date_str.replace("  ", " ").split(" ")[0:4])
        
        #  Tue, 07 Jan 2025 -> '%a, %d %b %Y'
        # 15 Oct 2020 12:33:01 -> %d %b %Y %H:%M:%S
        for fmt in ('%a, %d %b %Y', '%d %b %Y %H:%M:%S'):
            try:
                return datetime.strptime(date_str, fmt).strftime("%m/%d/%Y")
            except ValueError:
                pass
        raise ValueError('no valid date format found')

   
    def _read_email_text(self, msg):
        content_type = 'NA' if isinstance(msg, str) else msg.get_content_type()
        encoding = 'NA' if isinstance(msg, str) else msg.get('Content-Transfer-Encoding', 'NA')
        if 'text/plain' in content_type and 'base64' not in encoding:
            msg_text = msg.get_payload()
        elif 'text/html' in content_type and 'base64' not in encoding:
            msg_text = self._get_html_text(msg.get_payload())
        elif content_type == 'NA':
            msg_text = self._get_html_text(msg)
        else:
            msg_text = None
        return (content_type, encoding, msg_text)