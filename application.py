import os.path
import tornado.ioloop
import tornado.web

import re, praw, requests, os, glob, sys
from bs4 import BeautifulSoup

def addimagetolist(submissions, image_list):
  # Process all the submissions from the front page
    for submission in submissions:

        # Check for all the cases where we will skip a submission:
        if "imgur.com/" not in submission.url:
            continue # skip non-imgur submissions

        if 'http://imgur.com/a/' in submission.url:
            # This is an album submission.
            albumId = submission.url[len('http://imgur.com/a/'):]
            htmlSource = requests.get(submission.url).text
            soup = BeautifulSoup(htmlSource)
            matches = soup.select('.album-view-image-link a')
            for match in matches:
                imageUrl = match['href']
                if imageUrl.endswith('gifv'):
                    imageUrl=imageUrl[:-4]
                    imageUrl=imageUrl+'webm'
                    image_list.append(['http:' + imageUrl, submission.title, submission])

        elif 'http://i.imgur.com/' in submission.url:
            if submission.url.endswith('gifv'):
                submission.url=submission.url[:-4]
                submission.url=submission.url+'webm'
                image_list.append([submission.url, submission.title, submission])
            elif submission.url.endswith(tuple(['gif','png','jpg','jpeg'])):
                image_list.append([submission.url, submission.title, submission])
            else:
                submission.url=submission.url+'jpg'
                image_list.append([submission.url, submission.title, submission])

        elif 'http://imgur.com/' in submission.url:
            # This is an Imgur page with a single image.
            htmlSource = requests.get(submission.url).text # download the image's page
            soup = BeautifulSoup(htmlSource)
            imageUrl =''
            for a in soup.select('.image a'):
                imageUrl = a['href']
                if imageUrl.startswith('//'):
                    # if no schema is supplied in the url, prepend 'http:' to it
                    imageUrl = 'http:' + imageUrl
                    if imageUrl.endswith('gifv'):
                        imageUrl=imageUrl[:-4]
                        imageUrl=imageUrl+'webm'
                        image_list.append([imageUrl, submission.title, submission])
                    if imageUrl.endswith(tuple(['gif','png','jpg','jpeg'])):
                        image_list.append([imageUrl, submission.title, submission])
                    else:
                        imageUrl=imageUrl+'jpg'
                        image_list.append([imageUrl, submission.title, submission])
                else:
                    print submission.url
class MainHandler(tornado.web.RequestHandler):
    def get(self):
        image_list = []
        imgurUrlPattern = re.compile(r'(http://i.imgur.com/(.*))(\?.*)?')
        r = praw.Reddit(user_agent='test') # Note: Be sure to change the user-agent to something unique.
        submissions = r.get_subreddit('funny').get_hot(limit=50)
        # Or use one of these functions:
        #                                       .get_top_from_year(limit=25)
        #                                       .get_top_from_month(limit=25)
        #                                       .get_top_from_week(limit=25)
        #                                       .get_top_from_day(limit=25)
        #                                       .get_top_from_hour(limit=25)
        #                                       .get_top_from_all(limit=25)
        addimagetolist(submissions, image_list)
        self.render("index.html", 
                    image_list=image_list)                   


class TopHandler(tornado.web.RequestHandler):
    def get(self, param1):
        image_list = []
        imgurUrlPattern = re.compile(r'(http://i.imgur.com/(.*))(\?.*)?')
        r = praw.Reddit(user_agent='test') # Note: Be sure to change the user-agent to something unique.
        if param1 >= '1' and param1 <= '500':
            number = int(param1)
            submissions = r.get_subreddit('funny').get_top_from_day(limit=number)
            addimagetolist(submissions, image_list)
            self.render("index.html", 
                        image_list=image_list)    
        else:
            submissions = r.get_subreddit('funny').get_top_from_day(limit=50)
            addimagetolist(submissions, image_list)
            self.render("index.html", 
                        image_list=image_list) 


class NewHandler(tornado.web.RequestHandler):
    def get(self, param1):
        image_list = []
        imgurUrlPattern = re.compile(r'(http://i.imgur.com/(.*))(\?.*)?')
        r = praw.Reddit(user_agent='test') # Note: Be sure to change the user-agent to something unique.
        if param1 >= '1' and param1 <= '500':
            number = int(param1)
            submissions = r.get_subreddit('funny').get_new(limit=number)
            addimagetolist(submissions, image_list)
            self.render("index.html", 
                        image_list=image_list)    
        else:
            submissions = r.get_subreddit('funny').get_new(limit=50)
            addimagetolist(submissions, image_list)
            self.render("index.html", 
                        image_list=image_list) 

handlers = [
    (r"/", MainHandler),
    (r"/top/(?P<param1>[^\/]+)", TopHandler),
    (r"/new/(?P<param1>[^\/]+)", NewHandler)
]

settings = dict(
        template_path=os.path.join(os.path.dirname(__file__), "templates"),
        static_path=os.path.join(os.path.dirname(__file__), "static"),
)               

application = tornado.web.Application(handlers, **settings)

if __name__ == "__main__":
    port = os.environ['PORT'] if os.environ['PORT'] else 8888
    application.listen(port)
    tornado.ioloop.IOLoop.instance().start()
