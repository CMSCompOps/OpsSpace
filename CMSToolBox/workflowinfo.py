# pylint: disable=protected-access, unexpected-keyword-arg

"""
Module containing and returning information about workflows.

:authors: Daniel Abercrombie <dabercro@mit.edu>
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
                       params={'status': status, 'detail': 'false'},
                       use_cert=True)

    return request['result']


def errors_for_workflow(workflow):
    """
    Get the useful status information from a workflow

    :param str workflow: the name of the workflow request
    :returns: a dictionary containing error codes in the following format::

              {step: {errorcode: {site: number_errors}}}

    :rtype: dict
    """

    result = get_json('cmsweb.cern.ch',
                      '/wmstatsserver/data/jobdetail/%s' % workflow,
                      use_cert=True)

    output = {}

    if len(result['result']) == 0:
        return output

    for step, stepdata in result['result'][0].get(workflow, {}).iteritems():
        errors = {}
        for code, codedata in stepdata.get('jobfailed', {}).iteritems():
            sites = {}
            for site, sitedata in codedata.iteritems():
                sites[site] = sitedata['errorCount']

            errors[code] = sites

        output[step] = errors

    return output


def explain_errors(workflow, errorcode):
    """
    Get example errors for a given workflow and errorcode

    :param str workflow: is the workflow name
    :param str errorcode: is the error code
    :returns: a dict of log snippets from different sites.
    :rtype: list
    """

    result = get_json('cmsweb.cern.ch',
                      '/wmstatsserver/data/jobdetail/%s' % workflow,
                      use_cert=True)

    output = []

    for stepdata in result['result'][0].get(workflow, {}).values():
        for sitedata in stepdata.get('jobfailed', {}).get(errorcode, {}).values():
            for samples in sitedata['samples'][0]['errors'].values():

                output.extend(samples)


    return output
