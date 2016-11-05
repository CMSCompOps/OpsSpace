# pylint: disable=protected-access, unexpected-keyword-arg

"""
Module containing and returning information about workflows.

:authors: Jean-Roch Vlimant <vlimant@cern.ch> \n
          Daniel Abercrombie <dabercro@mit.edu>
"""


from ._webtools import get_json


def list_workflows(status):
    """
    Get the list of workflows currently in a given status.
    For a list of valid requests, visit the
    `Request Manager Interface <https://cmsweb.cern.ch/reqmgr2/>`_.

    :param str status: The status of the workflow lists being looked for
    :returns: A list of workflows matching the status
    :rtype: list
    """

    request = get_json('cmsweb.cern.ch', '/reqmgr2/data/request',
                       params={'status': status}, use_cert=True,
                       headers={'accept': 'application/json'})

    return [wf for wf in request['result'][0].keys()]
