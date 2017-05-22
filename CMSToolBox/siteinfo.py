"""
A module that returns various information about sites

:author: Daniel Abercrombie <dabercro@mit.edu>
"""


from .webtools import get_json


def pfn_from_phedex(site_name, lfn):
    """
    Get the PFN of a directory from phedex for a given LFN.

    :param str site_name: is the name of the site to check
    :param str lfn: is the LFN to find
    :returns: PFN of the folder
    :rtype: str
    """

    result = get_json(host='cmsweb.cern.ch',
                      request='/phedex/datasvc/json/prod/lfn2pfn',
                      params={'node': site_name,
                              'protocol': 'direct',
                              'lfn': lfn
                             },
                      use_https=True
                     )

    location = result['phedex']['mapping'][0]['pfn']
    return location

def get_domain(site):
    """ Get the domain name of a given site for use in hostname matching.

    .. Note::

       Is currently a simple map, and we'd love for someone to come along
       and improve it.

    """

    host_map = {
        'T1_ES_PIC':        'pic.es',
        'T1_US_FNAL':       'fnal.gov',
        'T2_AT_Vienna':     'oeaw.ac.at',
        'T2_BE_IIHE':       'iihe.ac.be',
        'T2_BE_UCL':        'ucl.ac.be',
        'T2_BR_SPRACE':     'sprace.org.br',
        'T2_CH_CERN':       'eoscms-srv-b2.cern.ch',
        'T2_CH_CSCS':       'cscs.ch',
        'T2_DE_DESY':       'desy.de',
        'T2_ES_CIEMAT':     'ciemat.es',
        'T2_ES_IFCA':       'ifca.es',
        'T2_FR_CCIN2P3':    'in2p3.fr',
        'T2_UK_London_IC':  'ic.ac.uk',
        'T2_US_Caltech':    'ultralight.org',
        'T2_US_Florida':    'ufl.edu',
        'T2_US_MIT':        'mit.edu',
        'T2_US_Nebraska':   'unl.edu',
        'T2_US_Purdue':     'purdue.edu',
        'T2_US_Wisconsin':  'wisc.edu',
        'T2_US_UCSD':       'ucsd.edu',
        'T2_US_Vanderbilt': 'vanderbilt.edu',
        }

    domain = host_map.get('site')

    if domain:
        return domain

    # If the key includes the site name, return the domain.
    # This is for things like T1_US_FNAL_Disk, etc.
    for key, domain in host_map.iteritems():
        if key in site:
            return domain

    return ''
