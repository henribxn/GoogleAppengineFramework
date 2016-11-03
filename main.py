import webapp2


class MainHandler(webapp2.RequestHandler):

    def get(self):
        with open("html/input_form.html") as f:
            html = f.read()
        self.response.write(html)



app = webapp2.WSGIApplication([('/', MainHandler)], debug=True)
