"""
Uses the `reqmgr2 APIs <https://github.com/dmwm/WMCore/wiki/reqmgr2-apis>`_
to get information about workflows.

.. Warning::

   Depreciated. Delete this once everything is done using it.

:author: Daniel Abercrombie <dabercro@mit.edu>
"""

from .webtools import get_json

def get_workflow_parameters(workflow):
    """
    Get the workflow parameters from ReqMgr2

    :param str workflow: The name of the workflow
    :returns: Parameters for the workflow
    :rtype: dict
    """

    try:
        result = get_json('cmsweb.cern.ch',
                          '/reqmgr2/data/request',
                          params={'name': workflow},
                          use_https=True, use_cert=True)

        for params in result['result']:
            for key, item in params.iteritems():
                if key == workflow:
                    return item
    except Exception as error:
        print 'Failed to get from reqmgr', workflow
        print str(error)

    return {}
