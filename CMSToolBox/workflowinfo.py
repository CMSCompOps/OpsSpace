"""
Module containing and returning information about workflows.

:authors: Jean-Roch Vlimant <vlimant@cern.ch> \n
          Daniel Abercrombie <dabercro@mit.edu>
"""

import sys
import httplib
import os
import json
import copy
import pickle
import time
import math
import ssl
from collections import defaultdict

from .elasticsearch import send_log

BASE_DIR = os.getenv('UNIFIED_DIR', '/afs/cern.ch/user/c/cmst2/Unified/')


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


class WorkflowInfo(object):
    """
    A class that holds all of the useful information about a workflow
    """

    def __init__(self, workflow, url='cmsweb.cern.ch', spec=True, request=None,
                 stats=False, wq=False, errors=False):
        """
        :param str workflow: The name of the workflow to initialize with
        :param str url: The url to get the information from.
                        This can also be ``'cmsweb-testbed.cern.ch'``, for example
        :param bool spec:
        :param dict request:
        :param bool stats:
        :param bool wq:
        :param bool errors:
        """

        self.logs = defaultdict(str)
        self.url = url
        self.conn = httplib.HTTPSConnection(self.url, cert_file=os.getenv('X509_USER_PROXY'),
                                            key_file=os.getenv('X509_USER_PROXY'))
        if request is None:
            try:
                self.conn.request("GET", '/couchdb/reqmgr_workload_cache/' + workflow)
                self.request = json.loads(self.conn.getresponse().read())
            except Exception:
                try:
                    self.conn.request("GET", '/couchdb/reqmgr_workload_cache/' + workflow)
                    self.request = json.loads(self.conn.getresponse().read())
                except Exception as msg:
                    print "Failed to get workload cache for", workflow
                    print str(msg)
                    raise Exception("Failed to get workload cache for %s" % workflow)
        else:
            self.request = copy.deepcopy(request)

        self.full_spec = None
        if spec:
            self.get_spec()

        self.wmstats = None
        if stats:
            self.get_wm_stats()

        self.errors = None
        if errors:
            self.get_mw_errors()

        self.recovery_doc = None

        self.workqueue = None
        if wq:
            self.get_work_queue()

        self.summary = None

    def get_prep_ids(self):
        """
        :returns: Prep IDs for this workflow
        :rtype: list
        """

        pids = list()
        if 'Chain' in self.request['RequestType']:
            base = self.request['RequestType'].replace('Chain', '')
            itask = 1
            while True:
                t = '%s%d' % (base, itask)
                itask += 1
                if t in self.request:
                    if 'PrepID' in self.request[t]:
                        if not self.request[t]['PrepID'] in pids:
                            pids.append(self.request[t]['PrepID'])
                else:
                    break
            if pids:
                return pids
            else:
                return [self.request['PrepID']]

        elif 'PrepID' in self.request:
            return [self.request['PrepID']]
        else:
            return []

    def notify_requestor(self, message, mcm=None):
        """
        :param str message: Is a message to send to the workflow requester
        :param mcm:
        :type mcm: :py:class:`CMSToolBox.mcmclient.McMClient`
        """

        if not message:
            return

        try:

            if mcm is None:
                from .mcmclient import McMClient
                mcm = McMClient(dev=False)

            get_batches = lambda id: [batch for batch in \
                                      mcm.get2('batches', query='contains=%s' % id) \
                                      if batch['status'] in ['announced', 'done', 'reset']]

            wf_name = self.request['RequestName']
            items_notified = set()
            for pid in set(self.get_prep_ids()):
                replacements = {'PREPID': pid,
                                'WORKFLOW': self.request['RequestName']
                               }
                dedicated_message = message

                for src, dest in replacements.items():
                    dedicated_message = dedicated_message.replace(src, dest)

                batches = get_batches(wf_name) or get_batches(pid)

                if batches:
                    bid = batches[0]['prepid']
                    print "batch nofication to", bid
                    if bid not in items_notified:
                        mcm.put('/restapi/batches/notify',
                                {"notes": dedicated_message, "prepid": bid})
                        items_notified.add(bid)

                if pid not in items_notified:
                    print "request notification to", pid
                    mcm.put('/restapi/requests/notify',
                            {"message": dedicated_message, "prepids": [pid]})
                    items_notified.add(pid)

        except Exception as msg:
            print "could not notify back to requestor\n%s" % msg
            self.send_log('notify_requestor', 'could not notify back to requestor\n%s' % msg)

    def send_log(self, subject, text, show=True):
        if show:
            print text  ## to avoid having to duplicate it
        self.logs[subject] += '\n' + text

    def __del__(self):
        self.flush_log()

    def flush_log(self):
        ## flush the logs
        for sub, text in self.logs.items():
            send_log(sub, text, wfi=self, show=False, level='workflow')

    def get_spec(self):
        if not self.full_spec:
            self.conn.request("GET", '/couchdb/reqmgr_workload_cache/%s/spec' %
                              self.request['RequestName'])
            self.full_spec = pickle.loads(self.conn.getresponse().read())
        return self.full_spec

    def get_wm_errors(self, cache=0):
        try:
            f_cache = '/tmp/.%s.wmerror' % self.request['RequestName']
            if cache:
                if os.path.isfile(f_cache):
                    d_cache = json.loads(open(f_cache).read())
                    now = time.mktime(time.gmtime())
                    stamp = d_cache['timestamp']
                    if (now - stamp) < cache:
                        print "wmerrors taken from cache", f_cache
                        return d_cache['data']

            self.conn.request("GET", '/wmstatsserver/data/jobdetail/%s' %
                              self.request['RequestName'],
                              headers={"Accept": "*/*"})

            self.errors = json.loads(
                self.conn.getresponse().read()
            )['result'][0][self.request['RequestName']]

            open(f_cache, 'w').write(json.dumps({'timestamp': time.mktime(time.gmtime()),
                                                 'data': self.errors}))
            return self.errors
        except Exception:
            print "Could not get wmstats errors for", self.request['RequestName']
            return {}

    def get_dashboard(self, since=1, **args):
        dconn = httplib.HTTPConnection('dashb-cms-job.cern.ch')

        dargs = {
            'task': 'wmagent_%s' % self.request['RequestName'],
            'user': '',
            'site': '',
            'submissiontool': '',
            'application': '',
            'activity': '',
            'status': '',
            'check': 'submitted',
            'tier': '',
            'sortby': 'site',
            'ce': '',
            'rb': '',
            'grid': '',
            'jobtype': '',
            'submissionui': '',
            'dataset': '',
            'submissiontype': '',
            'subtoolver': '',
            'genactivity': '',
            'outputse': '',
            'appexitcode': '',
            'accesstype': '',
            'inputse': '',
            'cores': '',
            'date1': time.strftime(
                '%Y-%m-%d+%H:%M',
                time.gmtime(time.mktime(time.gmtime()) - (since * 24 * 60 * 60))
                ),
            'date2': time.strftime('%Y-%m-%d+%H:%M', time.gmtime())
        }

        for key in args:
            if key in dargs:
                dargs[key] = args[key]

        url = '/dashboard/request.py/jobsummary-plot-or-table2?' + '&'.join(
            ['%s=%s' % (k, v) for k, v in dargs.items()])
        dconn.request('GET', url)
        res = json.loads(dconn.getresponse().read())['summaries']
        ## transform into a dict
        return dict([(d['name'], d) for d in res])

    def get_wm_stats(self, cache=0):
        f_cache = '/tmp/.%s.wmstats' % self.request['RequestName']
        if cache:
            if os.path.isfile(f_cache):
                d_cache = json.loads(open(f_cache).read())
                now = time.mktime(time.gmtime())
                stamp = d_cache['timestamp']
                if (now - stamp) < cache:
                    print "wmstats taken from cache", f_cache
                    return d_cache['data']
        self.conn.request("GET",
                          '/wmstatsserver/data/request/%s' % self.request['RequestName'],
                          headers={"Accept": "application/json"})

        self.wmstats = json.loads(
            self.conn.getresponse().read()
        )['result'][0][self.request['RequestName']]

        open(f_cache, 'w').write(json.dumps({'timestamp': time.mktime(time.gmtime()),
                                             'data': self.wmstats}))
        return self.wmstats

    def get_recovery_doc(self):
        if self.recovery_doc != None:
            return self.recovery_doc
        try:
            self.conn.request("GET",
                              '/couchdb/acdcserver/_design/ACDC/_view/byCollectionName?'
                              'key="%s"&include_docs=true&reduce=false' %
                              self.request['RequestName'])

            rows = json.loads(self.conn.getresponse().read())['rows']
            self.recovery_doc = [r['doc'] for r in rows]
        except Exception:
            print "failed to get the acdc document for", self.request['RequestName']
            self.recovery_doc = None
        return self.recovery_doc

    def get_recovery_info(self):
        self.get_recovery_doc()

        where_to_run = defaultdict(list)
        missing_to_run = defaultdict(int)
        missing_to_run_at = defaultdict(lambda: defaultdict(int))
        for doc in self.recovery_doc:
            task = doc['fileset_name']
            for f, info in doc['files'].iteritems():
                where_to_run[task] = list(set(where_to_run[task] + info['locations']))
                missing_to_run[task] += info['events']
                for s in info['locations']:
                    missing_to_run_at[task][s] += info['events']

        return dict(where_to_run), dict(missing_to_run), missing_to_run_at

    def get_work_queueElements(self):
        wq = self.get_work_queue()
        wqes = [w[w['type']] for w in wq]
        return wqes

    def get_work_queue(self):
        if not self.workqueue:
            try:
                self.conn.request("GET",
                                  '/couchdb/workqueue/_design/WorkQueue/_view/'
                                  'elementsByParent?key="%s"&include_docs=true' %
                                  self.request['RequestName'])
                res = self.conn.getresponse()
            except Exception:
                try:
                    time.sleep(1)  ## time-out
                    self.conn.request("GET",
                                      '/couchdb/workqueue/_design/WorkQueue/_view/'
                                      'elementsByParent?key="%s"&include_docs=true' %
                                      self.request['RequestName'])

                    res = self.conn.getresponse()
                except Exception:
                    print "failed to get work queue for", self.request['RequestName']
                    self.workqueue = []
                    return self.workqueue
            self.workqueue = list([d['doc'] for d in json.loads(res.read())['rows']])
        return self.workqueue

    def get_agents(self):
        wq = self.get_work_queue()
        wqes = [w[w['type']] for w in wq]
        statuses = list(set([wqe['Status'] for wqe in wqes]))
        active_agents = defaultdict(lambda: defaultdict(int))
        for status in statuses:
            wq_s = [wqe for wqe in wqes if wqe['Status'] == status]
            for wqe in wq_s: active_agents[status][wqe['ChildQueueUrl']] += 1
        return active_agents

    def get_gq_locations(self):
        wq = self.get_work_queue()
        wqes = [w[w['type']] for w in wq]
        ins = defaultdict(list)
        for wqe in wqes:
            for i in wqe['Inputs']:
                ins[i] = list(set(ins[i] + wqe['Inputs'][i]))
        return ins

    def get_active_agents(self):
        wq = self.get_work_queue()
        wqes = [w[w['type']] for w in wq]
        active_agents = defaultdict(int)
        wq_running = [wqe for wqe in wqes if wqe['Status'] == 'Running']
        for wqe in wq_running: active_agents[wqe['ChildQueueUrl']] += 1
        return dict(active_agents)

    def get_summary(self):
        if self.summary:
            return self.summary

        self.conn = httplib.HTTPSConnection(self.url, cert_file=os.getenv('X509_USER_PROXY'),
                                            key_file=os.getenv('X509_USER_PROXY'))
        self.conn.request("GET", '/couchdb/workloadsummary/' + self.request['RequestName'],
                          headers={"Accept": "application/json"})

        self.summary = json.loads(self.conn.getresponse().read())
        return self.summary

    def get_glide_mon(self):
        try:
            gmon = json.loads(os.popen(
                'curl -s http://cms-gwmsmon.cern.ch/prodview/json/%s/summary' %
                self.request['RequestName']).read())
            return gmon
        except Exception:
            print "cannot get glidemon info", self.request['RequestName']
            return None

    def _tasks(self):
        return self.get_spec().tasks.tasklist

    def get_schema(self):
        # new_schema = copy.deepcopy( self.get_spec().request.schema.dictionary_())

        self.conn = httplib.HTTPSConnection(self.url, cert_file=os.getenv('X509_USER_PROXY'),
                                            key_file=os.getenv('X509_USER_PROXY'))
        self.conn.request("GET", '/reqmgr2/data/request?name=%s' % self.request['RequestName'],
                          headers={"Accept": "application/json"})

        new_schema = copy.deepcopy(
            json.loads(
                self.conn.getresponse().read()
            )['result'][0][self.request['RequestName']]
        )

        ## put in the era accordingly ## although this could be done in re-assignment
        ## take care of the splitting specifications ## although this could be done in re-assignment
        for (k, v) in new_schema.items():
            if v in [None, 'None']:
                new_schema.pop(k)
        return new_schema

    def _taskDescending(self, node, select=None):
        all_tasks = []
        if not select:  # or (select and node.taskType == select):
            all_tasks.append(node)
        else:
            for (key, value) in select.items():
                if (isinstance(value, list) and getattr(node, key) in value) or \
                        (not isinstance(value, list) and getattr(node, key) == value):
                    all_tasks.append(node)
                    break

        for child in node.tree.childNames:
            ch = getattr(node.tree.children, child)
            all_tasks.extend(self._taskDescending(ch, select))
        return all_tasks

    def get_work_tasks(self):
        return self.get_all_tasks(select={'taskType': ['Production', 'Processing', 'Skim']})

    def get_all_tasks(self, select=None):
        all_tasks = []
        for task in self._tasks():
            ts = getattr(self.get_spec().tasks, task)
            all_tasks.extend(self._taskDescending(ts, select))
        return all_tasks

    def get_splittings(self):

        spl = []
        for task in self.get_work_tasks():
            task_splitting = task.input.splitting
            spl.append({"splittingAlgo": task_splitting.algorithm,
                        "splittingTask": task.pathName,
                       })
            get_those = ['events_per_lumi', 'events_per_job', 'lumis_per_job',
                         'halt_job_on_file_boundaries', 'max_events_per_lumi',
                         'halt_job_on_file_boundaries_event_aware']
            translate = {
                'EventAwareLumiBased': [('events_per_job', 'avg_events_per_job')]
            }
            include = {
                'EventAwareLumiBased': {'halt_job_on_file_boundaries_event_aware': 'True'},
                'LumiBased': {'halt_job_on_file_boundaries': 'True'}
            }
            if task_splitting.algorithm in include:
                for key, value in include[task_splitting.algorithm].items():
                    spl[-1][key] = value

            for get in get_those:
                if hasattr(task_splitting, get):
                    set_to = get
                    if task_splitting.algorithm in translate:
                        for (src, des) in translate[task_splitting.algorithm]:
                            if src == get:
                                set_to = des
                                break
                    spl[-1][set_to] = getattr(task_splitting, get)

        return spl

    def get_current_status(self):
        return self.request['RequestStatus']

    def get_request_numevents(self):
        if 'RequestNumEvents' in self.request and int(self.request['RequestNumEvents']):
            return int(self.request['RequestNumEvents'])
        else:
            return int(self.request['Task1']['RequestNumEvents'])

    def get_priority(self):
        return self.request['RequestPriority']

    def get_multicore(self):
        mcores = [self.request.get('Multicore', 1)]
        if 'Chain' in self.request['RequestType']:
            mcores_d = self._collectinchain('Multicore', default=1)
            mcores.extend(mcores_d.values())
        return max(mcores)

    def get_block_whitelist(self):
        bwl = []
        if 'Chain' in self.request['RequestType']:
            bwl_t = self._collectinchain('BlockWhitelist')
            for task in bwl_t:
                bwl.extend(bwl_t[task])
        else:
            if 'BlockWhitelist' in self.request:
                bwl.extend(self.request['BlockWhitelist'])

        return bwl

    def get_lumi_whitelist(self):
        lwl = []
        if 'Chain' in self.request['RequestType']:
            lwl_t = self._collectinchain('LumiWhitelist')
            for task in lwl_t:
                lwl.extend(lwl_t[task])
        else:
            if 'LumiWhitelist' in self.request:
                lwl.extend(self.request['LumiWhitelist'])
        return lwl

    def get_run_whitelist(self):
        lwl = []
        if 'Chain' in self.request['RequestType']:
            lwl_t = self._collectinchain('RunWhitelist')
            for task in lwl_t:
                lwl.extend(lwl_t[task])
        else:
            if 'RunWhitelist' in self.request:
                lwl.extend(self.request['RunWhitelist'])
        return lwl

    def get_io(self):
        lhe = False
        primary = set()
        parent = set()
        secondary = set()

        def io_for_task(blob):
            lhe = False
            primary = set()
            parent = set()
            secondary = set()
            if 'InputDataset' in blob:
                primary = set(filter(None, [blob['InputDataset']]))
            # elif 'InputDatasets' in blob: primary = set(filter(None,blob['InputDatasets']))
            if primary and 'IncludeParent' in blob and blob['IncludeParent']:
                parent = findParent(primary)
            if 'MCPileup' in blob:
                secondary = set(filter(None, [blob['MCPileup']]))
            if 'LheInputFiles' in blob and blob['LheInputFiles'] in ['True', True]:
                lhe = True

            return (lhe, primary, parent, secondary)

        if 'Chain' in self.request['RequestType']:
            base = self.request['RequestType'].replace('Chain', '')
            t = 1
            while '%s%d' % (base, t) in self.request:
                (alhe, aprimary, aparent, asecondary) = IOforTask(self.request['%s%d' % (base, t)])
                if alhe: lhe = True
                primary.update(aprimary)
                parent.update(aparent)
                secondary.update(asecondary)
                t += 1
        else:
            (lhe, primary, parent, secondary) = IOforTask(self.request)

        return (lhe, primary, parent, secondary)

    def _collectinchain(self, member, func=None, default=None):
        if self.request['RequestType'] == 'StepChain':
            return self._collectin_uhm_chain(member, func, default, base='Step')
        elif self.request['RequestType'] == 'TaskChain':
            return self._collectin_uhm_chain(member, func, default, base='Task')
        else:
            raise Exception("should not call _collectinchain on non-chain request")

    def _collectin_uhm_chain(self, member, func=None, default=None, base=None):
        coll = {}
        t = 1
        while '%s%d' % (base, t) in self.request:
            if member in self.request['%s%d' % (base, t)]:
                if func:
                    coll[self.request['%s%d' % (base, t)]['%sName' % base]] = func(
                        self.request['%s%d' % (base, t)][member])
                else:
                    coll[self.request['%s%d' % (base, t)]['%sName' % base]] = \
                        self.request['%s%d' % (base, t)].get(member, default)
            t += 1
        return coll

    def get_primary_dsn(self):
        if 'Chain' in self.request['RequestType']:
            return self._collectinchain('PrimaryDataset').values()
        else:
            return [self.request['PrimaryDataset']]

    def get_campaigns(self):
        if 'Chain' in self.request['RequestType']:
            return self._collectinchain('AcquisitionEra').values()
        else:
            return [self.request['Campaign']]

    def acquisition_era(self):
        def invert_digits(st):
            if st[0].isdigit():
                number = ''
                while st[0].isdigit():
                    number += st[0]
                    st = st[1:]
                isolated = [
                    (st[i - 1].isupper() and st[i].isupper() and st[i + 1].islower())
                    for i in range(1, len(st) - 1)
                    ]
                if any(isolated):
                    insert_at = isolated.index(True) + 1
                    st = st[:insert_at] + number + st[insert_at:]
                    return st
                print "not yet implemented", st
                sys.exit(34)
            return st

        if 'Chain' in self.request['RequestType']:
            acqEra = self._collectinchain('AcquisitionEra', func=invert_digits)
        else:
            acqEra = invert_digits(self.request['Campaign'])
        return acqEra

    def processing_string(self):
        if 'Chain' in self.request['RequestType']:
            return self._collectinchain('ProcessingString')
        else:
            return self.request['ProcessingString']
