"""
Module containing and returning information about workflows.

:authors: Daniel Abercrombie <dabercro@mit.edu>
"""


import re

from .webtools import get_json
from .sitereadiness import site_list


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


def errors_for_workflow(workflow, url='cmsweb.cern.ch'):
    """
    Get the useful status information from a workflow

    :param str workflow: the name of the workflow request
    :param str url: the base url to find the information at
    :returns: a dictionary containing error codes in the following format::

              {step: {errorcode: {site: number_errors}}}

    :rtype: dict
    """

    result = get_json(url,
                      '/wmstatsserver/data/jobdetail/%s' % workflow,
                      use_cert=True)

    output = {}

    if not result['result']:
        return output

    for step, stepdata in result['result'][0].get(workflow, {}).iteritems():
        errors = {}
        for code, codedata in stepdata.get('jobfailed', {}).iteritems():
            sites = {}
            for site, sitedata in codedata.iteritems():
                if sitedata['errorCount']:
                    sites[site] = sitedata['errorCount']

            if sites:
                errors[code] = sites

        if errors:
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


class WorkflowInfo(object):
    """
    Class that holds methods for accessing various information about a workflow.
    """

    def __init__(self, workflow, url='cmsweb.cern.ch'):
        """
        Initialize the workflow info class

        :param str workflow: is the name of the workflow
        :param str url: is the url to fetch information from
        """

        self.workflow = workflow
        self.url = url
        # Is set the first time get_workflow_parameters() is called
        self.workflow_params = None
        # Is set the first time get_errors() is called
        self.errors = None
        # Is set the first time get_recovery_info() is called
        self.recovery_info = {}
        # Is set first time get_explanation() is called
        self.explanations = None

        # Is set first time _get_jobdetail() is called
        self.jobdetail = None

    def get_workflow_parameters(self):
        """
        Get the workflow parameters from ReqMgr2, or returns a cached value.
        See the `ReqMgr 2 wiki <https://github.com/dmwm/WMCore/wiki/reqmgr2-apis>`_
        for more details.

        :returns: Parameters for the workflow from ReqMgr2.
        :rtype: dict
        """

        if self.workflow_params:
            return self.workflow_params

        try:
            result = get_json(self.url,
                              '/reqmgr2/data/request',
                              params={'name': self.workflow},
                              use_https=True, use_cert=True)

            for params in result['result']:
                for key, item in params.iteritems():
                    if key == self.workflow:
                        self.workflow_params = item
                        return self.workflow_params

        except Exception as error:
            print 'Failed to get from reqmgr', self.workflow
            print str(error)

        return {}


    def get_errors(self):
        """
        A wrapper for :py:func:`errors_for_workflow` if you happen to have
        a :py:class:`WorkflowInfo` object already.

        :returns: a dictionary containing error codes in the following format::

                  {step: {errorcode: {site: number_errors}}}

        :rtype: dict
        """

        if not self.errors:
            self.errors = errors_for_workflow(self.workflow, self.url)

        return self.errors

    def get_recovery_info(self):
        """
        Get the recovery info for this workflow.

        :returns: a dictionary containing the information used in recovery.
                  The keys in this dictionary are arranged like the following::

                  { task: { 'sites_to_run': set(sites), 'missing_to_run': int() } }

        :rtype: dict
        """

        if self.recovery_info:
            return self.recovery_info

        docs = get_json(self.url,
                        '/couchdb/acdcserver/_design/ACDC/_view/byCollectionName',
                        params={'key': '"%s"' % self.workflow,
                                'include_docs': 'true',
                                'reduce': 'false'},
                        use_cert=True)

        recovery_docs = [row['doc'] for row in docs.get('rows', [])]

        for doc in recovery_docs:
            task = doc['fileset_name']
            # For each task, we have the following keys:
            # sites - a set of sites that the recovery docs say to run on.
            for replica, info in doc['files'].iteritems():
                # For fake files, just return the site whitelist
                if replica.startswith('MCFakeFile'):
                    locations = set(self.get_workflow_parameters()['SiteWhitelist'])
                else:
                    locations = set(info['locations'])

                vals = self.recovery_info.get(task, {})
                if not vals:
                    self.recovery_info[task] = {}

                self.recovery_info[task]['sites_to_run'] = \
                    (vals.get('sites_to_run', set()) | locations)
                self.recovery_info[task]['missing_to_run'] = \
                    (vals.get('missing_to_run', 0) + info['events'])

        return self.recovery_info


    def site_to_run(self, task):
        """
        Gets a list of sites that a task in the workflow can run at

        :param str task: The full name of the task to find sites for
        :returns: a list of site to run at
        :rtype: list
        """

        site_set = self.get_recovery_info().get(task, {}).get('sites_to_run', [])
        out_list = []
        all_site_list = site_list()

        for site in site_set:
            clean_site = re.sub(r'_(Disk|MSS)$', '', site)
            if clean_site not in out_list and clean_site and \
                    clean_site in all_site_list:
                out_list.append(clean_site)

        out_list.sort()
        return out_list

    def _get_jobdetail(self):
        """
        Get the jobdetail from the wmstatsserver

        :returns: The job detail json from the server or cache
        :rtype: dict
        """

        if self.jobdetail is None:
            self.jobdetail = get_json(self.url,
                                      '/wmstatsserver/data/jobdetail/%s' % self.workflow,
                                      use_cert=True)

        return self.jobdetail

    def get_explanation(self, errorcode, step=''):
        """
        Gets a list of error logs for a given error code.

        :param str errorcode: The error code to explain
        :param str step: The full name of the step to return explanations from
        :returns: list of error logs
        :rtype: list
        """

        if self.explanations is None:
            self.explanations = {}
            result = self._get_jobdetail()
            for stepname, stepdata in result['result'][0].get(self.workflow, {}).iteritems():
                for error, site in stepdata.get('jobfailed', {}).iteritems():
                    if error == '0':
                        continue

                    if self.explanations.get(error) is None:
                        self.explanations[error] = {}

                    if self.explanations[error].get(stepname) is None:
                        self.explanations[error][stepname] = []

                    for sitename, samples in site.iteritems():

                        #
                        # Flatten the following nested loops:
                        #
                        # for sample in samples['samples']:
                        #     for values in sample['errors'].values():
                        #         for detail in values:
                        #
                        # Both ways are equally unreadable, I think
                        #

                        for detail in sum(
                                [values for values in sum(
                                    [sample['errors'].values() for sample in samples['samples']],
                                    [])],
                                []):

                            self.explanations[error][stepname].append('\n\n'.join(
                                ['Site name: %s' % sitename,
                                 '%s (Exit code: %s)' % (detail['type'], detail['exitCode']),
                                 detail['details']]))

        explain = self.explanations.get(errorcode, {'': ['No info for this error code']})

        if step in explain.keys():
            return explain[step]

        return sum([val for val in explain.values()], [])

    def get_prep_id(self):
        """
        :returns: the PrepID for this workflow
        :rtype: str
        """

        return str(self.get_workflow_parameters()['PrepID'])
