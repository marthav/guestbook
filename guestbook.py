import os
import urllib
import logging

from google.appengine.api import users
# [START import_ndb]
from google.appengine.ext import ndb
# [END import_ndb]

import jinja2
import webapp2

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'])

good_deal = "good deal the data is going in!"
no_blanks = "we can't add blanks to the database!"


DEFAULT_GUESTBOOK_NAME = 'default_guestbook'

# We set a parent key on the 'Greetings' to ensure that they are all
# in the same entity group. Queries across the single entity group
# will be consistent.  However, the write rate should be limited to
# ~1/second.

def guestbook_key(guestbook_name=DEFAULT_GUESTBOOK_NAME):
    """Constructs a Datastore key for a Guestbook entity.
    We use guestbook_name as the key.
    """
    return ndb.Key('Guestbook', guestbook_name)


# [START greeting]
class Author(ndb.Model):
    """Sub model for representing an author."""
    identity = ndb.StringProperty(indexed=False)
    email = ndb.StringProperty(indexed=False)


class Greeting(ndb.Model):
    """A main model for representing an individual Guestbook entry."""
    author = ndb.StructuredProperty(Author)
    content = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)
# [END greeting]


# [START main_page]
class MainPage(webapp2.RequestHandler):
#Well, I hope I understand this correctly.  The class detail below addresses 
#the behavior of the get post and validate functions in the guestbook form.
#the method or class here of get is going to retrieve data from the server.  Data 
#that has been previously posted.

    def get(self):
        guestbook_name = self.request.get('guestbook_name',
                                          DEFAULT_GUESTBOOK_NAME)
        greetings_query = Greeting.query(
            ancestor=guestbook_key(guestbook_name)).order(-Greeting.date)
        num_greetings = 10
        greetings = greetings_query.fetch(num_greetings)

        user = users.get_current_user()
        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        template_values = {
            'user': user,
            'greetings': greetings,
            'guestbook_name': urllib.quote_plus(guestbook_name),
            'url': url,
            'url_linktext': url_linktext,
        }

        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))
        #The GET method that is passing data retrieved from database
        #(line 59) to the template (line78).  The template fills in 
        #the variables with data retrived from the database and the
        #result is rendered to the user. (this was taken almost verbatim
        #from the reviewer's notes)
        

# [START guestbook]
class Guestbook(webapp2.RequestHandler):
    def post(self):
        # We set the same parent key on the 'Greeting' to ensure each
        # Greeting is in the same entity group. Queries across the
        # single entity group will be consistent. However, the write
        # rate to a single entity group should be limited to
        # ~1/second.
        # in this method, under the Guestbook class we are posting data
        # to the server by way of the guestbook form.
        # we are also validating/retrieving data from the database
        

        guestbook_name = self.request.get('guestbook_name',
                                          DEFAULT_GUESTBOOK_NAME)
        greeting = Greeting(parent=guestbook_key(guestbook_name))

        if users.get_current_user():
            greeting.author = Author(
                    identity=users.get_current_user().user_id(),
                    email=users.get_current_user().email())

        #greeting.content = self.request.get('content')
        #str = 'greeting.content'
        #if str.isspace() == True :
        #    print "we can't add blanks to the database!"
        #else:
        #    print "good deal it's going in now"
        #    greeting.put()

    
        greeting.content = self.request.get('content')
        #if (greeting.content == '' or greeting.content.isspace()):
         #  print'no_blanks'
        #else:
        #   print'good_deal'
        #    greeting.put()
        
        if (greeting.content == '' or greeting.content.isspace()): 
            alert = no_blanks 
        else: alert = good_deal greeting.put()


        query_params = {'guestbook_name': guestbook_name, 'alert': alert}
        self.redirect('/?' + urllib.urlencode(query_params))
# [END guestbook]

application = webapp2.WSGIApplication([
    ('/', MainPage), # this calls the MainPage class
    ('/sign?guestbook_name', Guestbook), #this calls the Guestbook class
], debug=True)




