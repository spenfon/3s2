#!/usr/bin/env python


import cgi
import datetime
import wsgiref.handlers

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.api import urlfetch
from google.appengine.api import images


class Advert(db.Model):
    text = db.StringProperty()
    age = db.IntegerProperty()
    gender = db.BooleanProperty()
    useID = db.IntegerProperty()
    image = db.BlobProperty(default=None)

class MainPage(webapp.RequestHandler):
    def get(self):
        self.response.out.write('Log In page here!')
    

class AddAd(webapp.RequestHandler):
     def get(self):
        self.response.out.write("""
          <html>
            <body>

              <form action=/disp/ method="post">
                Adver ID: <input type="text" name="Adver ID" /><br />
                Text: <input type="text" name="Text" /><br />
                Age: <input type="text" name="Age" /><br />
                <input type="radio" name="sex" value="male" /> Male
                <input type="radio" name="sex" value="female" /> Female <br />
                Image File:<input type="file" name="if"/>

                    
                <div><input type="submit" value="Submit"></div>
              </form>

            </body>
          </html>""")


class Request(webapp.RequestHandler):
    def get(self, age, gender):
        self.response.out.write('age = ' + age + ', gender = ' + gender)
        


class Disp(webapp.RequestHandler):
    def post(self):
        self.response.out.write(cgi.escape(self.request.get('Adver ID'))+'<br />')
        self.response.out.write(cgi.escape(self.request.get('Text'))+'<br />')
        self.response.out.write(cgi.escape(self.request.get('Age'))+'<br />')
        self.response.out.write(cgi.escape(self.request.get('sex'))+'<br />')
        self.response.out.write(cgi.escape(self.request.get('if'))+'<br />')
        ad = Advert()
        ad.text = self.request.get('Text')
        ad.age = int(self.request.get('Age'))
        ad.useID = int(self.request.get('Adver ID'))

        if self.request.get('sex') == 'male':
            ad.gender=True
        else:
            ad.gender=False

        i = images.resize(self.request.get("if"), 60, 60)

        #ad.image=db.Blob(i)

        ad.put()
        
        

class Data(webapp.RequestHandler):
    def get(self):
        ads = db.GqlQuery("SELECT * FROM Advert")
        for ad in ads:
            self.response.out.write('ID=%s, age=%s, gender=%s, text = %s' %
                                   (str(ad.useID), str(ad.age), str(ad.gender), str(ad.text)))
            #self.response.out.write(str(ad.useID) + ',' + str(ad.age) + ',' + str(ad.gender) + ',' + ad.text) 
            self.response.out.write("<div><img src='img?img_id=%s'></img>" %
                                    ad.key())

            self.response.out.write('<br>')


class Image(webapp.RequestHandler):
    def get(self):
        ad = db.get(self.request.get("img_id"))
        if ad.image:
            self.response.headers['Content-Type'] = "image/png"
            self.response.out.write(ad.image)
        else:
            self.response.out.write("No image")
        
        


application = webapp.WSGIApplication([
    ('/', MainPage),
    (r'/request/(.*)/(.*)', Request),
    ('/disp/', Disp),
    ('/sub/', AddAd),
    ('/database/', Data),
    ('/img', Data),
], debug=True)


def main():
    wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
    main()
