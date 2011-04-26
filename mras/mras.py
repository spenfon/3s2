#!/usr/bin/env python


# mras.py
# COP 4331 - Team 3S2
#
# Written by Spencer Fonte 
# with help form the rest of team 3S2
# 
# HISTORY
# Created on Feb. 27, 2011 
# Feb 27, 2011 -   Created framework and bank classes 
# March 8, 2011 -  Added user html form to upload an ad 
#                  and display images in the datastore.
#                  Images not being uploaded properly   
# March 11, 2011 - Fixed image upload problem, needed to 
#                  specify enctype in html forms for file upload.
# March 17, 2011 - Started experimenting with scoring ads on relevance 
# April 7, 2011 -  Finished back end functionality and just 
#                  outputting plain text on most the pages
# April 11, 2011 - Made a better looking GUI using basic HTML 
# April 16, 2011 - Improved GUI and appearance using CSS 
# April 20, 2011 - Fixed spelling errors in output and other minor display issues
# April 22, 2011 - Fixed a few more small things, added link to user manual


##Import Python Modules
import cgi
import random
import datetime
import time
import wsgiref.handlers

#Import App Engine Specific Modules
from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.api import images


#Create two classes for the database
#One for ads and one for accounts
class Advert(db.Model):
    text = db.StringProperty()
    url = db.StringProperty()
    age = db.IntegerProperty()
    age_importance = db.IntegerProperty()
    gender = db.StringProperty()
    gender_importance = db.IntegerProperty()
    user = db.UserProperty()
    image = db.BlobProperty(default=None)
    keywords = db.StringProperty()
    keywords_importance = db.IntegerProperty()
    times_displayed = db.IntegerProperty(default=0)
    clicks = db.IntegerProperty(default=0)
    
class Account(db.Model):
    user = db.UserProperty()
    account_type = db.IntegerProperty()  # -1 for advers 0 for CPs

    # These next two store the number of times an advirtiser's 
    # ads have been displayed and clicked, for CPs its the number
    # of times they have displayed ads and their users have clicked
    num_ads = db.IntegerProperty(default=0)     
    num_clicks = db.IntegerProperty(default=0)


#Main page class
class MainPage(webapp.RequestHandler):
    def get(self):

        #See if the user has an account with us
        accs = db.GqlQuery("SELECT * FROM Account WHERE user = :1", users.get_current_user())

        #If this is a new visitor then ask them what type of account they want
        if accs.count() < 1:
            user = users.get_current_user()
            greeting = ("""Welcome, %s! (<a style=\"color: #800000\" 
                            href=\"%s\">sign out</a>) <br>""" 
                            % (user.nickname(), users.create_logout_url("/")))

            self.response.out.write("""
                <html>
                    <link type="text/css" rel="stylesheet" href="/css/main.css"/>
                    <body>
                    <img src="/static_images/headerimg.jpg" width="1000" >
                    <br><br><br>
                    <div id="Content">
                        %s<br>
                        You do not have an account! Select the type of account 
                        you would like to create:<br><br>

                        <form action=/create_account/ method="post"> 
                        <input type="submit" name="CP" value="Content Provider">
                        <input type="submit" name="Adver" value="Advertiser">
                        </form>
                        </div><br><br>
                        <a style="font-size:12;" href="http://www.someurl.com" target="_blank"> Help </a>              
                    </body>
                <html>                    
                        """ % greeting)

        #If this user has an account direct them to the proper page
        else:
            for ac in accs: cur_account_type = ac.account_type #only one ac in accs

            if cur_account_type < 0:
                self.response.out.write('<meta http-equiv="Refresh" content="0; url=/Adver_Home/">')
            else:
                self.response.out.write('<meta http-equiv="Refresh" content="0; url=/CP_Home/">')


# Home page for content providers                        
class CPHome(webapp.RequestHandler):
    def get(self):

        # Get this users account enitity from the datastore
        accs = db.GqlQuery("SELECT * FROM Account WHERE user = :1", users.get_current_user())
        # There is only one ac in accs, get the needed values from it
        for ac in accs: 
            num_served = ac.num_ads
            num_clicked = ac.num_clicks

        # Make loggout link html
        user = users.get_current_user()
        logged = ("%s (<a href=\"%s\">sign out</a>)" %
                        (user.nickname(), users.create_logout_url("/")))

        self.response.out.write("""
                <html>
                    <link type="text/css" rel="stylesheet" href="/css/main.css" />
                    <body>
                    <img src="/static_images/headerimg.jpg" width="1000" ><br>
                    <div id="User"> %s</div><br>
                    <div id="Content">
                        You are a content provider<br><br>
                        You have displayed <b>%s</b> ads. <b>%s</b> have been clicked.<br><br>
                        Your user ID is <b>%s</b> <br><br>
                        You can request an ad from:<br><br>
                        http://cop4331-3s2.appspot.com/request -><br>
                        /'id'/'seed'/'element'/'age of user'/'gender of user'/'key words'<br><br>

                        id = %s <br>
                        seed = a random string or integer, it's suggested you use system time <br>
                        element = [img | link] (img for ad image, link for ad URL)<br>
                        age of user = integer <br>
                        gender of user = [male | female | unknown] <br>
                        keywords = seperate keywords by hyphens<br> <br>

                        Example: <br> 
                        http://cop4331-3s2.appspot.com<br>/request/%s/randomstuff/link/23/female/test-example-sample
                       
                        </form>
                    </div>
                    <br><br>
                    <a style="font-size:12;" href="http://www.someurl.com" target="_blank"> Help </a>              
                    </body>
                <html>                    
                        """ % (logged, num_served, num_clicked, users.get_current_user().user_id(),
                               users.get_current_user().user_id(), 
                               users.get_current_user().user_id()))

# This class takes in the type of account the user has chosen to create
# it then redirects the user to the homepage for that type of account
class Acc(webapp.RequestHandler):

    def post(self):
        ac = Account()
        ac.user = users.get_current_user()
    
        if (self.request.get('Adver')):
            ac.account_type = -1
            ac.put()
            self.response.out.write('<meta http-equiv="Refresh" content="0; url=/Adver_Home/">')
        elif(self.request.get('CP')):
            ac.account_type = 0
            ac.put()
            self.response.out.write('<meta http-equiv="Refresh" content="0; url=/CP_Home/">')
        else:
            print oops


        
        
class AddAd(webapp.RequestHandler):
     def get(self):

        #Create loggout link
        user = users.get_current_user()
        logged = ("%s (<a href=\"%s\">sign out</a>)" %
                        (user.nickname(), users.create_logout_url("/")))

        #Output html form for user to submit a new ad
        self.response.out.write("""
          <html>
            <link type="text/css" rel="stylesheet" href="/css/main.css" />

                <body>
                <img src="/static_images/headerimg.jpg" width="1000" ><br>
                <div id="User"> %s</div><br>
              <div id="Content">
              <h1>Please enter information about your new ad and select an image to upload:</h1> <br>
              <form action=/disp/ enctype="multipart/form-data" method="post">
                
                Name: <input type="text" name="Text" /><br><br>
                URL: <input type="text" name="URL" /><br><br>
                Age: <input type="text" name="Age" />

                &nbsp;Importance:
                <select name="age_pri">
                <option value="1">1</option>
                <option value="2">2</option>
                <option value="3">3</option>
                <option value="4">4</option>
                <option value="5">5</option>
                </select>

                <br><br>

                <input type="radio" name="sex" value="male" /> Male
                <input type="radio" name="sex" value="female" /> Female 

                &nbsp;Importance:
                <select name="sex_pri">
                <option value="1">1</option>
                <option value="2">2</option>
                <option value="3">3</option>
                <option value="4">4</option>
                <option value="5">5</option>
                </select>

                <br><br>

                Keywords, seperated by commas. <br>
                <TEXTAREA NAME="keywords" COLS=40 ROWS=6></TEXTAREA> <br>
                 Keyword Importance:
                <select name="key_pri">
                <option value="1">1</option>
                <option value="2">2</option>
                <option value="3">3</option>
                <option value="4">4</option>
                <option value="5">5</option>
                </select> <br><br>
                Image File:<input type="file" name="if"/><br><br>

                    
                <input type="submit" value="Submit"></form>
                <form action=/userads/ method="get">
                <input type="submit" value="Cancel">    
                </div><br><br>

                <a style="font-size:12;" href="http://www.someurl.com" target="_blank"> Help </a>              

            </body>
          </html>""" % logged)


# Class that handles incoming requests
class Request(webapp.RequestHandler):

    # Get these variables from URL
    def get(self, CP_ID, seed, element, age, gender, keywords):
        
        # Returns number of keywords that match using set intersection
        def keywords_matching(request_str, db_str):
            request_lst = request_str.split('-')
            db_lst = db_str.replace(' ', '').split(',')
            return len(set(request_lst) & set(db_lst))

        #Get all ads in the datastore
        ads = db.GqlQuery("SELECT * FROM Advert")

        scores = {} 
        text = False # debug code 

        #Loop through ads in the datastore
        for ad in ads:

            ####DELETE
            if (text):
                self.response.out.write(ad.text + "<br>")
                self.response.out.write("keywords matching = " +
                                    str(keywords_matching(keywords,ad.keywords))
                                        + "<br>")

                self.response.out.write("Age difference = " + str(abs(int(age) - 
                                        ad.age)) + "<br>")

                self.response.out.write("Gender  = " + str(gender == ad.gender)
                                        + "<br>")


            # Calculate the proportion of importance for each parameter 
            importance_total = float(ad.age_importance + ad.gender_importance +
                                ad.keywords_importance)
            age_frac = ad.age_importance / importance_total
            sex_frac = ad.gender_importance / importance_total
            key_frac = ad.keywords_importance/ importance_total

            # Calculate a score of relevance for each ad

            # Score from any matching keywords    
            if (keywords_matching(keywords,ad.keywords) > 3): 
                cur_score = (3*4) ** 1.5 * key_frac
            else: 
                cur_score = ((keywords_matching(keywords,ad.keywords)*4) ** 
                             1.5 * key_frac)

            # Add keyword score with the score for age difference and gender match
            cur_score += (15/(max(abs(int(age) - ad.age), 1) * age_frac) +
                          (gender == ad.gender) * 7 * sex_frac) + 1

            ###DELETE
            if (text):
                self.response.out.write("add key = " + str(ad.key()) + "<br>")
                self.response.out.write("cur_score = " + str(cur_score) + "<br>")

            scores[ad.key()] = int(cur_score**2)                                                       

       
        total = sum(scores.values())   

        # Create a random int using user's seed
        # this int lies between 1 and the sum of all ads scores
        random.seed(seed)
        r = random.randint(1, total)         

        ###DELETE
        if (text):
            self.response.out.write("%s, %s" % (total, r))


        # Select the ad coresponding with the random int
        score_sum = 0;
        for s in scores:
            score_sum += scores[s]
            if (r <= score_sum):
                chosen_ad = s
                break

        

        ###DELETE
        if (text):
            self.response.out.write("<br><br>The chosen add is %s, %s" % 
                                    (chosen_ad, dir(chosen_ad)))

        
        # Get the add itself from the datastore
        c_ad = db.get(chosen_ad)

        #Select the account of the uploader of the selected ad
        accs = db.GqlQuery("SELECT * FROM Account WHERE user = :1", c_ad.user)

        # Select all the acounts
        cps = db.GqlQuery("SELECT * FROM Account")
        

        # If the image is requested...
        if (not text and not element == "link"):

            c_ad.times_displayed = (ad.times_displayed + 1)
            c_ad.put()  #Updates the datastore entry

            # Increment and update adver's total of their ads displayed
            for ac in accs: 
                ac.num_ads = ac.num_ads + 1 
                ac.put()


            # Increment and update the requester's ads displayed total
            for cp in cps:
                if int(cp.user.user_id()) == int(CP_ID):
                    cp.num_ads = cp.num_ads + 1
                    cp.put()
        
            self.response.headers['Content-Type'] = "image/png"
            self.response.out.write(c_ad.image)
        # If the link is requested
        else:
            # Update the uploaders and requesters clicks totals
            for ac in accs: 
                ac.num_clicks = ac.num_clicks + 1 
                ac.put()
            for cp in cps:
                if int(cp.user.user_id()) == int(CP_ID):
                    cp.num_clicks = cp.num_clicks + 1
                    cp.put()

            # Increment the number of times this particular ad has been clicked
            c_ad.clicks = c_ad.clicks + 1;
            c_ad.put()

            # We need http:// or https:// to redirect of the page
            # if not already in the ad url append it
            if (c_ad.url[0:7] == "http://" or c_ad.url[0:8] == "https://"):
                redirect_url = c_ad.url
            else:
                redirect_url = "http://" + c_ad.url 

            #Output html to redirect user to the ad's site
            self.response.out.write("""<meta http-equiv="Refresh" 
                                    content="0; url=%s">""" % redirect_url)

# Class to store form data from new ad entry
class Disp(webapp.RequestHandler):
    def post(self):        
        
        # Create a new ad in the datastore and put the apropiate info
        # recieved from the get method into them
        ad = Advert()
        ad.text = self.request.get('Text')
        ad.age = int(self.request.get('Age'))
        ad.keywords = self.request.get('keywords')
        ad.url = cgi.escape(self.request.get('URL'))
        ad.age_importance = int(cgi.escape(self.request.get('age_pri')))
        ad.gender_importance = int(cgi.escape(self.request.get('sex_pri')))
        ad.keywords_importance = int(cgi.escape(self.request.get('key_pri')))
        ad.gender = self.request.get('sex')
        ad.user = users.get_current_user()


        # Store image
        #Not resizing when running on my machine do to some jpeg lib missing
        #i = images.resize(self.request.get('if'), 60, 60)
        i = self.request.get('if')
        ad.image=db.Blob(i)        

        # Update in the datastore    
        ad.put()

        # Refresh back to the main advertiser page
        self.response.out.write("""<meta http-equiv="Refresh" 
                                content="0; url=/Adver_Home/">""")

        
class Data(webapp.RequestHandler):
    def get(self):
        ads = db.GqlQuery("SELECT * FROM Advert")

        self.response.out.write('<html> <body> <a href="/sub/">Click Here to add an ad</a> <form  action="/del/" method="POST">')
        self.response.out.write(' <input type="hidden" name="%s" value="%s">'% ("reurl", "/database/"))
        for ad in ads:

            self.response.out.write(' <input type="checkbox" name="%s"value="%s">'% (ad.key(), "pointless"))
            

            self.response.out.write('Upload User=%s, age=%s, gender=%s, text = %s, times disp = %s'  %
                                   (str(ad.user), str(ad.age), str(ad.gender), str(ad.text), str(ad.times_displayed)))
            for i in ad.keywords.replace(' ', '').split(','):
                self.response.out.write("<br>" + str(i) + "<br>")

            # IMAGE
            self.response.out.write("<div><img src='/img?img_id=%s'></img><br>" %
                                   ad.key())


        self.response.out.write('<div><input type="submit" value="Delete"></div><br></form></body></html>')


# Class to delete selected ads
class Delete(webapp.RequestHandler):
    def post(self):
        # Get all the passed in arguments from the GET method
        keys_to_del = self.request.arguments()

        # Loop through the keys of ads and delete them
        for key in keys_to_del:
            if key != u'reurl':
                db.get(key).delete()

        # Redirect the user back to where they came from
        self.response.out.write("""<meta http-equiv="Refresh" 
                                  content="0; url=%s">""" 
                                  % self.request.get('reurl'))

        
        
# Page that displays the user's current ads
class DataForUser(webapp.RequestHandler):
    def get(self):
        # Query all of this user's ads
        ads = db.GqlQuery("SELECT * FROM Advert WHERE user = :1", 
                            users.get_current_user())
        # Query this user's account
        accs = db.GqlQuery("SELECT * FROM Account WHERE user = :1", 
                            users.get_current_user())
        # Get the total number of clicks and displays from the users account entity
        for ac in accs: 
            num_ads = ac.num_ads
            num_clicks = ac.num_clicks

        # Make loggout URL
        user = users.get_current_user()
        logged = ("%s (<a href=\"%s\">sign out</a>)" %
                        (user.nickname(), users.create_logout_url("/")))

        # Output adver info and table header with all the user's ads and info
        self.response.out.write("""
            <html>     
                <link type="text/css" rel="stylesheet" href="/css/main.css" />
                <body>
                <img src="/static_images/headerimg.jpg" width="1000" ><br>
                    <div id="User">%s</div><br>
                <div id="Content"> 
                Your ads have been displayed a total of %s times and clicked %s times.<br><br>
                <form  action="/sub/" method="GET">
                <input type="submit" value="Add a new ad"><br><br>
                </form>
                <Content>
                <table border="1" bordercolor="#c86260" bgcolor="#ffffcc" >   
                    <tr><th>Select</th>
                    <th>Displayed<br>(Clicked)</th>
                    <th>Name</th><th>URL</th> 
                    <th>Target Age</th> 
                    <th>Target Gender</th> 
                    <th>Keywords</th>
                    </tr>  
                <form  action="/del/" method="POST">
                """ % (logged, num_ads, num_clicks))

        # Add a hidden type to tell the delete to redirect back here
        self.response.out.write(' <input type="hidden" name="reurl" value="/userads/">')

        # For each add make a row in the table with info and image
        for ad in ads:
            # Ouput checkbox
            self.response.out.write("""<tr> 
                                        <td> 
                                            <input type="checkbox" 
                                            name="%s"value="%s"
                                        </td>"""
                                    % (ad.key(), "pointless"))

            #Output the ad info 
            self.response.out.write("""<td>%s(%s)</td> <td>%s</td> 
                                       <td style="max-width:300px; 
                                                    word-wrap: break-word;">
                                        %s </td> 
                                      <td>%s</td> <td>%s</td> <td>%s</td><tr>""" 
                                     % (ad.times_displayed, ad.clicks, ad.text, 
                                     ad.url, ad.age, ad.gender, ad.keywords))

            # Ouput image
            self.response.out.write("""<tr><td colspan="9">
                                    <div><img src='/img?img_id=%s'></img>
                                    </td></tr>""" % ad.key())
                                  

        self.response.out.write("""</table><br><input type="submit" 
                                value="Delete selected"><br></form></div>
                                <br><br>
                                <a style="font-size:12;" 
                                href="http://www.someurl.com" 
                                target="_blank"> Help </a>              
                                </body></html>""")  


# Class to dynamicly serve a image based on ad's key
class Image(webapp.RequestHandler):
    def get(self):
        # Get the ad's image from the datastore
        ad = db.get(self.request.get("img_id"))
        # If there an image display it else error
        if ad.image:
            self.response.headers['Content-Type'] = "image/png"
            self.response.out.write(ad.image)
        else:
            self.response.out.write("No image")

# Used for some testing
class Test(webapp.RequestHandler):
    def get(self):

        userID = 123
        seed = time.time()
        age = 24
        gender = "male"
        keywords = "technology-computer-internet"

        self.response.out.write("""
        <html>
            <link type="text/css" rel="stylesheet" href="/css/main.css" />
                <body>
                <h2> This is a test. An ad should be displayed below:</h2><br><br>
                <a href="http://cop4331-3s2.appspot.com/request/%s/%s/%s/%s/%s/%s">
                <img src="http://cop4331-3s2.appspot.com/request/%s/%s/%s/%s/%s/%s">
                <alt="Ads privded by Mobile Advertisement Network"/>
                </a>
                </body>
        </html>
        """ % (userID, seed, "link", age, gender, keywords,
              userID, seed, "img", age, gender, keywords))
        
        

# Which class to call for each URL
application = webapp.WSGIApplication([
    ('/', MainPage),
    (r'/request/(.*)/(.*)/(.*)/(.*)/(.*)/(.*)', Request),
    ('/disp/', Disp),
    ('/create_account/', Acc),
    ('/sub/', AddAd),
    ('/database/', Data),
    ('/userads/', DataForUser),
    ('/img', Image),
    ('/del/', Delete),
    ('/Adver_Home/', DataForUser),
    ('/CP_Home/', CPHome),
    ('/test/', Test),
], debug=True)


def main():
    wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
    main()
