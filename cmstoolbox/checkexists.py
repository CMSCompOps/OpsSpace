#pylint: disable=bad-format-character

"""
This module checks if a file exists using xrdfs on the system
"""

import re
import sys
import subprocess

def exists(path):
    """
    Determines if a ROOT file exists somewhere using `xrdfs`
    :param str path: The full path of the file, including the redirector
    :returns: If the file exists under the given path
    :rtype: bool
    """

    match = re.match(r'(root://[\w\.\-]+(:\d+)?/)(/[/\w\-]+\.root)', path)

    if not match:
        return False

    door = match.group(1)
    filename = match.group(3)

    if not door or not filename:
        return False

    encoded_string = b'xrdfs %s locate %s &\nsleep 15\nkill %s\nsleep 1' \
        % (door, filename, '%1') if sys.version_info.major == 2 else \
        b'xrdfs %b locate %b &\nsleep 15\nkill %b\nsleep 1' \
        % (bytes(door, 'utf8'), bytes(filename, 'utf8'), b'%1')

    out, _ = subprocess.Popen(
        ['bash'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE).\
        communicate(encoded_string)

    return b'ReadWrite' in out
