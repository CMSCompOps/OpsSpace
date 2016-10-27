"""
Module containing and returning information about workflows.

:authors: Jean-Roch Vlimant <vlimant@cern.ch> \n
          Daniel Abercrombie <dabercro@mit.edu>
"""

import httplib
import os
import json
import ssl


def list_workflows(status):
    """
    Get the list of workflows currently in a given status.
    For a list of valid requests, visit the
    `Request Manager Interface <https://cmsweb.cern.ch/reqmgr2/>`_.

    :param str status: The status of the workflow lists being looked for
    :returns: A list of workflows matching the status
    :rtype: list
    """

    conn = httplib.HTTPSConnection('cmsweb.cern.ch',
                                   cert_file=os.getenv('X509_USER_PROXY'),
                                   key_file=os.getenv('X509_USER_PROXY'),
                                   context=ssl._create_unverified_context()
                                  )
    conn.request("GET", '/reqmgr2/data/request?status=' + status,
                 headers={'accept': 'application/json'})

    request = json.loads(conn.getresponse().read())
    conn.close()

    return [wf for wf in request['result'][0].keys()]
