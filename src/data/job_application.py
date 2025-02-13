import re
from src.data.gmail_message import GmailMessage


class JobApplication():
    def __init__(self, gmail_message):
        #if not isinstance(gmail_message, GmailMessage):
        #    raise TypeError('Variable must be type GmailMessage')
        self.gmail_message = gmail_message
        self.job_board = self._get_job_board()
        self.apply_date = gmail_message.email_date
        self.reject_date = ""
        self.accept_date = ""
        company, position = self._get_company_and_position()
        self.company = company
        self.company_id = ""
        self.company_website = ""
        self.company_name_external = ""
        self.position = position
        self.original_sender = self.gmail_message.email_from
    
    def _get_company_and_position(self):
        position = "()"
        company = self._get_company_name()
        
        return company, position
    
    def _get_job_board(self):
        board = "unknown"
        source = self.gmail_message.email_from 
        
        job_boards = {"linkedin.com": "linkedin", 
                      "lever.co": "lever", 
                      "ashbyhq.com" : "ashby", 
                      "myworkday.com" : "workday", 
                      "greenhouse-mail.io": "greenhouse",
                      "@ icims" : "icims",
                      "rippling.com" : "rippling"
                      }
        for key in job_boards:
            if key in source:
                board = job_boards[key]
        
        return board

    def _get_company_name(self):
        subject = self.gmail_message.email_subject
        sender = self.gmail_message.email_from
        company_name = ""
        
        if ("LinkedIn" in sender or "greenhouse" in sender):
            company_name = subject   
        elif "lever.co" in sender: 
            company_name = sender.replace(" <no-reply@hire.lever.co>", "")
        elif "@myworkday.com" in sender: 
            company_name = sender.replace("@myworkday.com", "")
        elif "ashbyhq.com" in sender:
            company_name = sender.replace(" Hiring Team <no-reply@ashbyhq.com>", "")
        elif "ats.rippling.com" in sender:
            company_name = sender.split(" <no-reply@ats.rippling.com>")[0]
        elif "talent.icims.com" in sender:
            company_name = sender.split(" @ icims")[0].replace('"', '')
        else:
            company_name = subject 
        
        # clean up subject from common strings 
        string_list = [
            "Thank you for applying to ",
            "Thank you for your application at ",
            "Ali, your application was sent to ",
            "Thanks for your application to ",
            "Thanks for applying to ",
            "Ali, thank you for your application to ",
            "Thank you for your application to ",
            "Thank you for considering ",
            ", Ali",
            " // Thank you for applying!"
            " - Thank you for your application Ali!",
            " Thank you for your application!",
            "Thank You for Your Interest in ",
            "Additional Information Request for "
            "!"
        ]
        pattern = '|'.join(map(re.escape, string_list))
        company_name = re.sub(pattern, '', company_name)
        
        patterns = {" at " : 1, " with ": 1, " to " : 1, " in " : 1, " Application Update " : 0, " - " : 0}
        for p in patterns:
            chunks = company_name.split(p)
            if len(chunks) > 1:
                index = patterns[p]
                return chunks[index]
        return company_name
