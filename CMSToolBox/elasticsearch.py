"""
Contains tools for interacting with elastic search

.. todo::

  Add workflowinfo class in ToolBox somewhere, since it's used here

:author: Jean-Roch Vlimant <jean-roch.vlimant@cern.ch>
"""


import httplib
import os
import time
import json


ELASTIC_SEARCH_HOST = 'cms-elastic-fe.cern.ch:9200'
"""The default location to send and search for logs"""


def send_log(subject, text, host=ELASTIC_SEARCH_HOST,
             show=False, level='info'):
    """Tries :func:`try_send_log` and raises exception if fails

    :param str subject: The subject of the log to send
    :param str text: The text of the log to send
    :param str host: The host url that the log is sent to
    :param bool show: Determines if the log should be printed or not
    :param str level: Level displayed in Meta information
    """

    try:
        try_send_log(subject, text, host, show, level)
    except (AttributeError, NameError, KeyError)  as message:
        print "failed to send log to elastic search"
        print str(message)


def search_logs(query, host=ELASTIC_SEARCH_HOST):
    """Use the elastic search at CERN to look through production logs

    :param str query: The query string to pass to elastic search
    :param str host: The host url to query for logs
    :returns: A list of logs where each log is a dictionary with
              ['_source']['text'] and ['_source']['meta']
    :rtype: list of dicts
    """

    conn = httplib.HTTPConnection(host)
    goodquery = {
        "query": {
            "bool": {
                "must": [
                    {
                        "wildcard": {
                            "meta": "*%s*" % query
                            }
                        },
                    ]
                }
            },
        "sort": [
            {
                "timestamp": "desc"
                }
            ],
        "_source": [
            "text",
            "subject",
            "date",
            "meta"
            ]
        }
    conn.request("POST", '/logs/_search?size=1000', json.dumps(goodquery))
    response = conn.getresponse()
    data = response.read()
    out = json.loads(data)
    return out['hits']['hits']


def try_send_log(subject, text, host=ELASTIC_SEARCH_HOST,
                 show=False, level='info'):
    """Tries to send a log to the elastic search host

    :param str subject: The subject of the log to send
    :param str text: The text of the log to send
    :param str host: The host url that the log is sent to
    :param bool show: Determines if the log should be printed or not
    :param str level: Level displayed in Meta information
    """

    if show:
        print text

    # import pdb
    # pdb.set_trace()
    conn = httplib.HTTPConnection(host)

    meta_text = 'level:%s\n' % level

    now_ = time.gmtime()

    conn.request('POST', '/logs/log/',
                 json.dumps({'author': os.getenv('USER'),
                             'subject': subject,
                             'text': text,
                             'meta': meta_text,
                             'timestamp': time.mktime(now_),
                             'date': time.asctime(now_)}
                           )
                )

    data = conn.getresponse().read()

    try:
        res = json.loads(data)
        print 'log:', res['_id'], 'was created'
    except (AttributeError, NameError, KeyError)  as message:
        print 'failed'
        print str(message)
