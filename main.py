import webapp2


class MainHandler(webapp2.RequestHandler):

    def get(self):
        with open("html/input_form.html") as f:
            html = f.read()
        self.response.write(html)

    def post(self):
        from utils import save_file_to_bucket, add_msg_to_queue, start_compute_engine
        from re import match
        from datetime import datetime
        from secret import BUCKET_FOLDER_NAME, INSTANCE_NAME

        text = ''
        # Save file to bucket
        file_content = self.request.POST.multi['img_input'].file.read()
        basename = self.request.POST.multi['img_input'].filename
        basename = basename + "__" + datetime.now().isoformat()
        full_name = save_file_to_bucket(basename, file_content, BUCKET_FOLDER_NAME)
        if full_name:
            text += "Your file has been saved<br>"
        else:
            self.response.out.write("There was an error in saving your file, please try again later")
            return

        # Check if email is valid
        email = self.request.get("email_input")
        email.replace(" ", "")
        if not match(r'[^@]+@[^@]+\.[^@]+', email):
            self.response.out.write("Your email is invalid:<br>{0}<br><br>Please try with a correct email".format(email))
            return

        # Save the job to the queue
        json = {"email": email, "basename": basename}
        if add_msg_to_queue(json):
            text += "Your request was received<br>"
        else:
            self.response.out.write("There was an error in saving your request, please try again later")
            return
        text += "<br>You will shortly receive the picture processed to this email: " + email

        start_compute_engine(INSTANCE_NAME)

        self.response.out.write(text)
        return


app = webapp2.WSGIApplication([('/', MainHandler)], debug=True)
