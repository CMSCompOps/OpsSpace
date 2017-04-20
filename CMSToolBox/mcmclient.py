# pylint: disable=bad-option-value, redefined-variable-type

"""
Defines the McMClient object.
I (Dan) do not know what it does at the moment.
Someone else should update the documentation.

:author: Jean-Roch Vlimant <vlimant@cern.ch>
"""

import sys
import os
import json
import httplib
import cStringIO
import traceback

import pycurl


class McMClient(object):
    """
    Object for interacting with McM.
    """

    def __init__(self, identity='sso', debug=False, cookie=None, dev=True, is_int=False):
        """
        :param str identity: Specify the way to identify the user.
                             Can either be ``'sso'`` or ``'cert'``.
        :param bool debug: Sets the verbosity level of the class.
        :param str cookie: Name of file with cookie to eat.
        :param bool dev: Determines which server to use, takes precedence.
        :param bool is_int: Other bool to determine which server to use
        """

        if os.getenv('UNIFIED_MCM') == 'dev':
            dev = True

        if dev:
            self.server = 'cms-pdmv-dev.cern.ch/mcm/'
        elif is_int:
            self.server = 'cms-pdmv-int.cern.ch/mcm/'
        else:
            self.server = 'cms-pdmv.cern.ch/mcm/'

        ## once secured
        self._response = ''
        self.headers = {}
        self.identity = identity
        self.debug = debug
        self.cookie_filename = cookie
        self.curl = None
        self.output = None
        self.__http = None
        self.connect()

    def connect(self, cookie=None):
        """
        :param str cookie: File name of the cookie to consume for ``'sso'`` identity
        """
        if self.identity == 'cert':
            self.__http = httplib.HTTPSConnection(
                self.server, cert_file=os.getenv('X509_USER_PROXY'),
                key_file=os.getenv('X509_USER_PROXY'))
        elif self.identity == 'sso':
            if cookie:
                self.cookie_filename = cookie
            else:
                if '-dev' in self.server:
                    self.cookie_filename = '%s/private/dev-cookie.txt' % (os.getenv('HOME'))
                elif '-int' in self.server:
                    self.cookie_filename = '%s/private/int-cookie.txt' % (os.getenv('HOME'))
                else:
                    self.cookie_filename = '%s/private/prod-cookie.txt' % (os.getenv('HOME'))

            if not os.path.isfile(self.cookie_filename):
                print "The required sso cookie file is absent. Trying to make one for you"
                os.system('cern-get-sso-cookie -u https://%s -o %s --krb' %
                          (self.server, self.cookie_filename))
                if not os.path.isfile(self.cookie_filename):
                    print "The required sso cookie file cannot be made."
                    sys.exit(1)

            self.curl = pycurl.Curl()
            print "Using sso-cookie file", self.cookie_filename
            self.curl.setopt(pycurl.COOKIEFILE, self.cookie_filename)
            self.output = cStringIO.StringIO()
            self.curl.setopt(pycurl.SSL_VERIFYPEER, 1)
            self.curl.setopt(pycurl.SSL_VERIFYHOST, 2)
            self.curl.setopt(pycurl.CAPATH, '/etc/pki/tls/certs')
            self.curl.setopt(pycurl.WRITEFUNCTION, self.output.write)
        else:
            self.__http = httplib.HTTPConnection(self.server)

    #################
    ### generic methods for GET, PUT, DELETE
    def get(self, url):
        """
        :param str url: The part of the request that comes after ``'/mcm/'``
        :returns: A JSON in dictionary form.
                  I don't know what's supposed to be in it.
        :rtype: dict
        """

        fullurl = 'https://' + self.server + url
        if self.debug:
            print 'url=|' + fullurl + '|'
        if self.identity == 'sso':
            self.curl.setopt(pycurl.HTTPGET, 1)
            self.curl.setopt(pycurl.URL, str(fullurl))
            self.curl.perform()
        else:
            self.__http.request("GET", url, headers=self.headers)

        try:
            output = json.loads(self.response())
            return output
        except Exception:
            print "ERROR"
            print traceback.format_exc()
            print self._response
            return None

    def put(self, url, data):
        """
        :param str url: The part of the request that comes after ``'/mcm/'``
        :param str data: Probably the data for the PUT request
        :returns: A JSON in dictionary form.
                  I don't know what's supposed to be in it.
        :rtype: dict
        """

        fullurl = 'https://' + self.server + url
        if self.debug:
            print 'url=|' + fullurl + '|'
        if self.identity == 'sso':
            self.curl.setopt(pycurl.URL, str(fullurl))
            p_data = cStringIO.StringIO(json.dumps(data))
            self.curl.setopt(pycurl.UPLOAD, 1)
            self.curl.setopt(pycurl.READFUNCTION, cStringIO.StringIO(json.dumps(data)).read)
            if self.debug:
                print 'message=|' + p_data.read() + '|'
            self.curl.perform()
        else:
            self.__http.request("PUT", url, json.dumps(data), headers=self.headers)

        try:
            output = json.loads(self.response())
            return output
        except Exception:
            # print "ERROR", self._response
            print "ERROR"
            return None

    def delete(self, url):
        """
        :param str url: The part of the request that comes after ``'/mcm/'``
        :returns: A JSON in dictionary form.
                  I don't know what's supposed to be in it.
        :rtype: dict
        """

        fullurl = 'https://' + self.server + url
        if self.debug:
            print 'url=|' + fullurl + '|'
        if self.identity == 'sso':
            self.curl.setopt(pycurl.CUSTOMREQUEST, 'DELETE')
            self.curl.setopt(pycurl.URL, str(fullurl))
            self.curl.perform()
        else:
            print "Not implemented Yet ?"
            self.__http.request("DELETE", url, headers=self.headers)

        try:
            output = json.loads(self.response())
            return output
        except Exception:
            print "ERROR"
            return None
            #####################

    #### generic methods for i/o
    def clear(self):
        """
        I have no idea what this might be used for.
        """
        if self.identity == 'sso':
            self.output = cStringIO.StringIO()
            self.curl.setopt(pycurl.WRITEFUNCTION, self.output.write)

    def response(self):
        """
        I have no idea what this might be used for.

        :returns: A response
        :rtype: str
        """
        if self.identity == 'sso':
            self._response = self.output.getvalue()
            self.clear()
            return self._response

        return self.__http.getresponse().read()

    #####################
    def get2(self, something, someone=None, query='', method='get', page=-1):
        """
        :param str something: I think variable names tend to explain themselves
        :param str someone: Not actually a person
        :param str query: Like in a DB
        :param str method: ???
        :param int page: For you heavy readers
        :returns: part of the JSON from :py:func:`get`
        :rtype: dict?
        """
        if someone:
            url = 'restapi/%s/%s/%s' % (something, method, someone.strip())
        else:
            url = 'search/?db_name=%s&page=%d&%s' % (something, page, query)

        output = self.get(url)
        if output:
            return output['results']

        return None

    def put2(self, something, what, update='save'):
        """
        :param str something:
        :param str what:
        :param str update: Can be ``'save'``, ``'update'``, or ``'manage'``
        :returns: something from :py:func:`put`
        :rtype: dict
        """
        url = 'restapi/%s/%s' % (something, update)

        output = self.put(url, what)

        return output
