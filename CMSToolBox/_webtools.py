# pylint: disable=protected-access, unexpected-keyword-arg, redefined-variable-type

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


def get_json(host, request, params='', body='',
             headers={'Accept': 'application/json'},
             port='', **kwargs):
    """
    Function for getting JSON from a URL that handles the connection
    and certificates with just a couple of bools.

    :param str host: The name of the host to connect to
    :param str request: The request to make to the host
    :param dict params: The parameters to pass to the request
    :param str body: The body to send in a POST request
    :param dict headers: Headers to pass to request
    :param str port: The port to access, if a not default value
    :param kwargs: Additional aruments that can be used to change
                   the connection behavior.
                   These are listed below:

                   - use_https (bool) - Uses HTTP connection by default
                   - use_cert (bool) - Does not pass a certificate by default
                   - cert_file (str) - Default is ``$X509_USER_PROXY``.
                   - use_post (bool) - Determines whether to use POST or GET.

    :returns: The JSON from the query
    :rtype: dict
    """

    check_for_port = host.split(':')
    if len(check_for_port) == 2:
        host = check_for_port[0]
        port = check_for_port[1]

    use_cert = kwargs.get('use_cert', False)
    use_https = kwargs.get('use_https', use_cert)

    if use_https:
        use_port = port or 443
        cert_file = kwargs.get('cert_file', os.getenv('X509_USER_PROXY')) \
            if use_cert else None

        try:
            conn = httplib.HTTPSConnection(
                host, use_port, cert_file=cert_file, key_file=cert_file,
                context=ssl._create_unverified_context())

        except AttributeError:
            conn = httplib.HTTPSConnection(
                host, use_port, cert_file=cert_file, key_file=cert_file)

    else:
        use_port = port or 80
        conn = httplib.HTTPConnection(host, use_port)

    method = "POST" if kwargs.get('use_post', bool(body)) else "GET"
    full_request = '%s?%s' % (request, urllib.urlencode(params)) if params else request

    conn.request(
        method, full_request, json.dumps(body), headers)

    res = conn.getresponse()

    print("STATUS", res.status, "REASON", res.reason)

    result = json.loads(res.read())

    conn.close()

    return result
