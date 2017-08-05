#!/usr/bin/python
__author__ = 'ender_al'
from tornado import httpclient
from tornado import ioloop
from tornado import escape
import sys
import urllib

#------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------


class AsynchronousClient():
    def __init__(self):
        #self.url = "http://10.10.0.16:8184/pm"
        self.url = "http://PsecNIP:8184/pm"
        self.response = None
        self.post_data = None

    def async_call(self, response):
        if response.error:
            print 'Error retrieving server response:', response.error
            sys.exit(1)
        ioloop.IOLoop.instance().stop()
        self.response = response
        return True

    def get_request(self):
        try:
            http_client = httpclient.AsyncHTTPClient()
            http_client.fetch(self.url, self.async_call)
            ioloop.IOLoop.instance().start()
        except:
            print("Error in asynchronous client request")
            sys.exit(1)
        return True

    def post_request(self):
        if type(self.post_data) == dict:
            body = escape.json_encode(self.post_data)
            headers = {"Content-Type":"application/json"}
        else:
            body = urllib.urlencode(self.post_data) #Transform data into a post request
            headers = None
        try:
            http_client = httpclient.AsyncHTTPClient()
            http_client.fetch(self.url, self.async_call, method='POST', headers=headers, body=body)
            ioloop.IOLoop.instance().start()
        except:
            print("Error in asynchronous client request")
            sys.exit(1)
        return True

#------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------


class SynchronousClient():
    def __init__(self):
        #self.url = "http://10.10.0.16:8184/pm"
        self.url = "http://PsecNIP:8191/pm"
        self.response = None
        self.post_data = None

    def get_request(self):
        http_client = httpclient.HTTPClient()
        try:
            self.response = http_client.fetch(self.url)
        except httpclient.HTTPError as e:
            # HTTPError is raised for non-200 responses; the response
            # can be found in e.response.
            print("Error retrieving server response: " + str(e))
            sys.exit(1)
        except Exception as e:
            # Other errors are possible, such as IOError.
            print("Error: " + str(e))
            sys.exit(1)
        http_client.close()
        return True

    def post_request(self):
        if type(self.post_data) == dict:
            body = escape.json_encode(self.post_data)
            headers = {"Content-Type":"application/json"}
        else:
            body = urllib.urlencode(self.post_data) #Transform data into a post request
            headers = None

        http_client = httpclient.HTTPClient()
        try:
            request = httpclient.HTTPRequest(self.url, method='POST', headers=headers, body=body)
            self.response = http_client.fetch(request)
        except httpclient.HTTPError as e:
            # HTTPError is raised for non-200 responses; the response
            # can be found in e.response.
            print("Error retrieving server response: " + str(e))
            print e.response
            sys.exit(1)
        except Exception as e:
            # Other errors are possible, such as IOError.
            print("Error: " + str(e))
            sys.exit(1)
        return True

if __name__ == "__main__":
    print 'Client'
    client = AsynchronousClient()
    client.url = "http://localhost:8888/getAuthorizedMitigationActionList"
    client.get_request()
    print client.response.body
