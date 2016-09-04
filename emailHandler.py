import webapp2


class EmailHandler(webapp2.RedirectHandler):
    def post(self):
        from utils import send_email

        subject = self.request.get("subject")
        to = self.request.get("email")
        body = self.request.get("body")
        attachments = self.request.POST.getall('attachments')
        attachments = [(f.filename, f.file.read()) for f in attachments]

        send_email(to=to, body=body, subject=subject, attachments=attachments)

        text = 'The email was sent'
        self.response.out.write(text)
        return


app = webapp2.WSGIApplication([('/emailHandler', EmailHandler)], debug=True)
