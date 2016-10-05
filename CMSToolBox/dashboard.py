"""
A module to gather and hold information from the dashboard.

:author: Jean-Roch Vlimant <jean-roch.vlimant@cern.ch>
"""

import os
import copy
import time
import json
import random
import httplib


def get_node_usage(url, node):
    """
    Get the disk function useage at a given site.

    :param str url: is the URL of the reporting service
    :param str node: is the site name to check
    :returns: The disk usage at the site in TB, or None if node info is not found
              as a function that takes no arguments
    :rtype: function
    """

    conn = httplib.HTTPSConnection(
        url,
        cert_file=os.getenv('X509_USER_PROXY'),
        key_file=os.getenv('X509_USER_PROXY')
        )
    conn.request(
        "GET", '/phedex/datasvc/json/prod/nodeusage?node=%s' % node
        )
    res = conn.getresponse()
    result = json.loads(res.read())

    conn.close()

    usage = 0

    for node in result['phedex']['node']:
        usage = max(
            sum([node[key] for key in node.keys() if key.endswith('_node_bytes')]),
            usage
            )

    # in TB
    return lambda: (int(usage / (1024. ** 4)) or None)


class DocCache(object):
    """
    This class gathers various information, mostly from the dashboard when it's requested.
    The information is cached with slightly random lifetimes to allow requests to be staggered.
    All of the information is obtained through system curl commands.
    """
    def __init__(self):
        """
        Initializes the DocCache without parameters.
        """

        def default_expiration():
            """
            :returns: A slightly varying time between 20-30 minutes for the cache duration
            :rtype: float
            """
            return 20 * 60 + random.random() * 10 * 60

        def load_json(url, key=''):
            """
            :param str url: is a URL that points to a JSON file containing useful information
            :param str key: is a key of the JSON file to return.
                            If left blank, the entire JSON file is returned
            :returns: a function that downloads a JSON file through curl from the URL.
                      This function has no parameters itself so that the
                      :py:func:`DocCache.get` function can figure things out on its own.
            :rtype: function
            """
            curl_call = 'curl -s --retry 5 "{0}"'.format(url)
            if key:
                return lambda: json.loads(os.popen(curl_call).read())[key]
            else:
                return lambda: json.loads(os.popen(curl_call).read())

        def make_cache_entry(getter, default):
            """
            :param function getter: is a function with no parameters that obtains the
                                    information to store in the cache.
            :param default: the default value to fill the cached data if the information
                            cannot be obtained.
            :type default: str, list, or dict
            :returns: a cache entry using the given getter function and default cache value
            :rtype: dict
            """
            return {
                'data': None,
                'timestamp': time.mktime(time.gmtime()),
                'expiration': default_expiration(),
                'getter': getter,
                'cachefile': None,
                'default': default
                }

        phedex_url = os.getenv('UNIFIED_PHEDEX', 'cmsweb.cern.ch')
        self.cache = {}

        # Get some columns from the dashboard
        columns = ['106', '107', '108', '109', '136', '158', '237', '159', '160']
        for col in columns:
            self.cache['ssb_{0}'.format(col)] = make_cache_entry(
                load_json('http://dashb-ssb.cern.ch'
                          '/dashboard/request.py/getplotdata'
                          '?columnid={0}&batch=1&lastdata=1'.format(col),
                          'csvdata'),
                []
                )

        self.cache['gwmsmon_totals'] = make_cache_entry(
            load_json('http://cms-gwmsmon.cern.ch/poolview/json/totals'), {}
            )

        self.cache['mcore_ready'] = make_cache_entry(
            load_json(
                'http://cmsgwms-frontend-global.cern.ch/vofrontend/stage/mcore_siteinfo.json'
                ),
            {}
            )

        self.cache['gwmsmon_prod_site_summary'] = make_cache_entry(
            load_json('http://cms-gwmsmon.cern.ch/prodview/json/site_summary'), {}
            )

        self.cache['gwmsmon_site_summary'] = make_cache_entry(
            load_json('http://cms-gwmsmon.cern.ch/totalview/json/site_summary'), {}
            )

        self.cache['detox_sites'] = make_cache_entry(
            lambda: os.popen(
                'curl --retry 5 -s '
                'http://t3serv001.mit.edu/~cmsprod/IntelROCCS/Detox/SitesInfo.txt'
                ).read().split('\n'),
            ""
            )

        sites = [
            'T1_DE_KIT_MSS', 'T1_US_FNAL_MSS', 'T1_ES_PIC_MSS', 'T1_UK_RAL_MSS',
            'T1_IT_CNAF_MSS', 'T1_FR_CCIN2P3_MSS', 'T1_RU_JINR_MSS', 'T0_CH_CERN_MSS'
            ]
        for site in sites:
            self.cache['{0}_usage'.format(site)] = make_cache_entry(
                get_node_usage(phedex_url, site), ""
                )

        self.cache['mss_usage'] = make_cache_entry(
            load_json('http://cmsmonitoring.web.cern.ch'
                      '/cmsmonitoring/StorageOverview/latest/StorageOverview.json'), {}
            )

        self.cache['hlt_cloud'] = make_cache_entry(
            load_json('http://137.138.184.204/cache-manager/images/cloudStatus.json'), {}
            )

        # create the cache files from the labels
        for src in self.cache:
            self.cache[src]['cachefile'] = '.' + src + '.cache.json'

    def get(self, label, fresh=False):
        """
        :param str label: dictionary key of self.cache for the information desired
        :param bool fresh: forces the cache to be refreshed if true.
                           Otherwise, the cache timestamp is checked.
        :returns: the values of the given cache if a correct label is given.
                  Otherwise returns None
        :rtype: dict or None
        """

        now = time.mktime(time.gmtime())

        if label in self.cache:
            try:
                cache = self.cache[label]

                def update_cache():
                    """perform update operations for the cache."""
                    cache['data'] = cache['getter']()
                    cache['timestamp'] = now
                    open(cache['cachefile'], 'w').write(
                        json.dumps(
                            {
                                'data': cache['data'],
                                'timestamp': cache['timestamp']
                            },
                            indent=2
                            )
                        )

                if not cache['data']:
                    # check the file version
                    if os.path.isfile(cache['cachefile']):
                        print "load", label, "from file", cache['cachefile']
                        f_cache = json.loads(open(cache['cachefile']).read())
                        cache['data'] = f_cache['data']
                        cache['timestamp'] = f_cache['timestamp']
                    else:
                        print "no file cache for", label, "getting fresh"
                        update_cache()

                ## check the time stamp
                if cache['expiration'] + cache['timestamp'] < now or fresh:
                    print "getting fresh", label
                    update_cache()

                return cache['data']

            except Exception as error:
                print "failed to get", label
                print str(error)
                return copy.deepcopy(cache['default'])
