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


def send_log(subject, text, wfi=None, host=ELASTIC_SEARCH_HOST):
    """Tries :func:`try_send_log` and raises exception if fails

    :param str subject: The subject of the log to send
    :param str text: The text of the log to send
    :param wfi: Workflow info
    :type wfi: :class:WorkFlowInfo
    :param str host: The host url that the log is sent to
    """

    try:
        try_send_log(subject, text, wfi, host)
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


def try_send_log(subject, text, wfi=None, host=ELASTIC_SEARCH_HOST):
    """Tries to send a log to the elastic search host

    :param str subject: The subject of the log to send
    :param str text: The text of the log to send
    :param wfi: Workflow info
    :type wfi: :class:WorkFlowInfo
    :param str host: The host url that the log is sent to
    """

    # import pdb
    # pdb.set_trace()
    conn = httplib.HTTPConnection(host)

    meta_text = ""

    if wfi:
        # add a few markers automatically
        meta_text += '\n\n' + '\n'.join(['id: %s' % i for i in wfi.getPrepIDs()])
        _, prim, _, sec = wfi.getIO()

        if prim:
            meta_text += '\n\n' + '\n'.join(['in:%s' % i for i in prim])

        if sec:
            meta_text += '\n\n' + '\n'.join(['pu:%s' % i for i in sec])

        out = [i for i in wfi.request['OutputDatasets'] if i not in ['FAKE', 'None']]

        if out:
            meta_text += '\n\n' + '\n'.join(['out:%s' % i for i in out])

        meta_text += '\n\n' + wfi.request['RequestName']

    now_ = time.gmtime()

    conn.request("POST", '/logs/log/',
                 json.dumps({"author": os.getenv('USER'),
                             "subject": subject,
                             "text": text,
                             "meta": meta_text,
                             "timestamp": time.mktime(now_),
                             "date": time.asctime(now_)}
                           )
                )

    data = conn.getresponse().read()

    try:
        res = json.loads(data)
        print 'log:', res['_id'], "was created"
    except (AttributeError, NameError, KeyError)  as message:
        print "failed"
        print str(message)
