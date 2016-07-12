"""
Contains tools for interacting with elastic search

:author: Jean-Roch Vlimant <jean-roch.vlimant@cern.ch>
"""


import httplib
import os
import time
import json


elastic_search_host = 'cms-elastic-fe.cern.ch:9200'
"""The default location to send and search for logs"""


def send_log(subject, text, wfi=None, host=elastic_search_host):
    """Tries :py:func:try_send_log and outputs exception if fails

    :param subject: The subject of the log to send
    :param text: The text of the log to send
    :param wfi: Don't actually know. Learn this
    :param host: The host that the log is sent to
    """

    try:
        try_send_log(subject, text, wfi, host)
    except Exception as e:
        print "failed to send log to elastic search"
        print str(e)


def search_logs(q, host=elastic_search_host):
    """Use the elastic search at CERN to look through production logs

    :param q: The query string to pass to elastic search
    :param host: The name of the host to query for logs
    :returns: A list of logs where each log is a dictionary with ['_source']['text'] and ['_source']['meta']
    """

    conn = httplib.HTTPConnection(host)
    goodquery = {
        "query": {
            "bool": {
                "must": [
                    {
                        "wildcard": {
                            "meta": "*%s*" % q
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
    o = json.loads(data)
    return o['hits']['hits']


def try_send_log(subject, text, wfi=None, host=elastic_search_host):
    """Tries to send a log to the elastic search host"""

    # import pdb
    # pdb.set_trace()
    conn = httplib.HTTPConnection(host)

    meta_text = ""
    if wfi:
        # add a few markers automatically
        meta_text += '\n\n' + '\n'.join(map(lambda i: 'id: %s' % i, wfi.getPrepIDs()))
        _, prim, _, sec = wfi.getIO()
        if prim:
            meta_text += '\n\n' + '\n'.join(map(lambda i: 'in:%s' % i, prim))
        if sec:
            meta_text += '\n\n' + '\n'.join(map(lambda i: 'pu:%s' % i, sec))
        out = filter(lambda d: not any([c in d for c in ['FAKE', 'None']]), wfi.request['OutputDatasets'])
        if out:
            meta_text += '\n\n' + '\n'.join(map(lambda i: 'out:%s' % i, out))
        meta_text += '\n\n' + wfi.request['RequestName']

    now_ = time.gmtime()
    now = time.mktime(now_)
    now_d = time.asctime(now_)
    doc = {"author": os.getenv('USER'),
           "subject": subject,
           "text": text,
           "meta": meta_text,
           "timestamp": now,
           "date": now_d}

    conn.request("POST", '/logs/log/', json.dumps(doc))
    response = conn.getresponse()
    data = response.read()
    try:
        res = json.loads(data)
        print 'log:', res['_id'], "was created"
    except Exception as e:
        print "failed"
        print str(e)
        pass
