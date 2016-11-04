# pylint: disable=protected-access, unexpected-keyword-arg

"""
A high-level module for getting JSON information from web services.
The HTTP vs HTTPS and certificate handling is done here.

:author: Daniel Abercrombie <dabercro@mit.edu>
"""


import os
import json
import httplib
import ssl
import urllib


def get_json(host, request, params='', body='', headers={},
             port='', use_https=False, use_cert=False,
             cert_file=os.getenv('X509_USER_PROXY'), use_post=False):
    """
    Function for getting JSON from a URL that handles the connection
    and certificates with just a couple of bools.

    :param str host: The name of the host to connect to
    :param str request: The request to make to the host
    :param dict params: The parameters to pass to the request
    :param dict headers: Headers to pass to request
    :param str port: The port to access, if a not default value
    :param bool use_https: Uses HTTP connection by default
    :param bool use_cert: Does not pass a certificate by default
    :param str cert_file: The location of the certificate file.
                          Default is ``$X509_USER_PROXY``.
    :param bool use_post: Determines whether to use POST or GET.
    :returns: The JSON from the query
    :rtype: dict
    """

    check_for_port = host.split(':')
    if len(check_for_port) == 2:
        host = check_for_port[0]
        port = check_for_port[1]

    if port:
        use_port = port
    else:
        use_port = 443

    if use_cert:

        try:
            conn = httplib.HTTPSConnection(
                host, use_port, cert_file=cert_file, key_file=cert_file,
                context = ssl._create_unverified_context())

        except AttributeError:
            conn = httplib.HTTPSConnection(
                host, use_port, cert_file=cert_file, key_file=cert_file)

    elif use_https:

        try:
            conn = httplib.HTTPSConnection(
                host, use_port, context = ssl._create_unverified_context())

        except AttributeError:
            conn = httplib.HTTPSConnection(host, use_port)

    else:
        if not port:
            use_port = 80
        conn = httplib.HTTPConnection(host, use_port)

    if body:
        use_post = True

    method = "POST" if use_post else "GET"

    full_request = '%s?%s' % (request, urllib.urlencode(params)) if params else request

    conn.request(
        method, full_request, json.dumps(body), headers)

    res = conn.getresponse()

    print("STATUS", res.status, "REASON", res.reason)

    result = json.loads(res.read())

    conn.close()

    return result
