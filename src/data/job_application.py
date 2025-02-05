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
        self.position = position
    
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
                      "greenhouse-mail.io": "greenhouse"
                      }
        for key in job_boards:
            if key in source:
                board = job_boards[key]
        
        return board

    def _get_company_name(self):
        subject = self.gmail_message.email_subject
        sender = self.gmail_message.email_from 
        
        if ("LinkedIn" in sender or "greenhouse" in sender):
            return self._get_company_from_subject()
            
        if "lever.co" in sender: 
            return sender.replace(" <no-reply@hire.lever.co>", "")
        
        if "@myworkday.com" in sender: 
            return sender.replace("@myworkday.com", "")
        
        if "ashbyhq.com" in sender:
            return sender.replace(" Hiring Team <no-reply@ashbyhq.com>", "")
        
        return subject

    def _get_company_from_subject(self):
        subject = self.gmail_message.email_subject
        patterns = {" at " : 1, " with ": 1, " to " : 1, " in " : 1, " Application Update " : 0}
        for p in patterns:
            chunks = subject.split(p)
            if len(chunks) > 1:
                index = patterns[p]
                return chunks[index]
        return subject 
 