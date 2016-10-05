"""
Module the caches and holds the Site Readiness status

:author: Daniel Abercrombie <dabercro@mit.edu>
"""


import time


class SiteInfo():

    def __init__(self):
        """Initialization does not need any parameters"""
        self.get_info()

    def get_info(self):
        """Fills members of the SiteInfo class"""
        self.info = expensive http call
        self.timestamp = time.time()


SITE_INFO = SiteInfo()
"""Cache of SiteInfo for each instance"""

CACHE_TIMEOUT = 60 * 60
"""Time between cache refreshing in seconds"""


def get_info():
    """
    Maybe add a parameter to specify what info you'd like
    :returns: info of sites after checking cache.
    :rtype: dict?, tuple? 
    """

    if site_info.timestamp is old:
        site_info.get_info()

    return site_info.info


def site_readiness(site_name):
    """Returns the readiness status for a given site
    :param str site_name: Name of the site
    :returns: Readiness status. Possibilities are:
              - 'Ready'
              - 'Waiting Room'
              - 'Morgue'
    :rtype: str
    """

    info = get_info()
    return filtered info


def site_average_uptime(site_name, duration):
    """Returns the average site readiness over the past duration (up to some value)
    :param str site_name: Name of the site
    :param float/int? duration: Amount of time to average over in day/weeks/months...
    :returns: Average uptime in hours/days
    :rtype: float
    """
    info = get_info()
    return more complicated filter of info


def iterator_site_readiness():
    """Iterates over site readiness for the user
    :returns: iterator tuple with site, readiness status
    :rtype: iterator
    """
    info = get_info()

    for thing in info:
        # Get site and readiness
        yield site, readiness
