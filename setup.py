#! /usr/bin/env python

"""
File mostly intended to set up working environment for operator as a script.

:author: Daniel Abercrombie <dabercro@mit.edu>
"""

import os
import sys
import urllib
import glob
from distutils.core import setup

try:
    import pip
except ImportError:
    print '\nIt does not look like you have pip installed.'
    print 'That is the one dependency I need to install other dependencies.'
    print 'Try running the following script:\n'
    print 'https://bootstrap.pypa.io/get-pip.py\n'
    exit()

from CMSToolBox.simplefiletools import load_env, append_to_file


VERSION='0.4'


class Installer(object):
    """Class the holds the information for installing workspace"""

    possibleProfiles = [
        '.bashrc',
        '.bash_profile'
    ]
    """List of profiles searched for in user's home to append to PYTHONPATH"""

    CentralGitHub = 'CMSCompOps'
    """Default GitHub account containing packages that can be installed"""

    InstallDirectory = os.path.dirname(os.path.realpath(__file__))
    """Location of the OpsSpace"""

    gitHubUrl = 'https://github.com/'
    """Remote repository location"""

    ValidPackages = []
    """List of valid packages that can be installed with this script.
    Set in :py:func:`set_packages`.
    """

    def set_packages(self):
        """Read from list of valid package and append to valid list."""
        if len(self.ValidPackages) == 0:
            with open(os.path.join(self.InstallDirectory, 'PackageList.txt'), 'r') as list_file:
                for package in list_file.readlines():
                    self.ValidPackages.append(package.strip('\n'))

    def __init__(self, github_user=None):
        """Initialize with the GitHub username of the operator."""
        self.user_name = github_user or self.CentralGitHub

        self.set_packages()

    def print_valid_packages(self):
        """Displays valid packages for the user"""

        print '\nValid package names:\n'
        for package in self.ValidPackages:
            print '  ' + package
        print ''

    def install_requirements(self, package_name):
        """Look for requirements.txt and install requirements, if needed.
        Also runs any install.?? script in the package

        :param str package_name: is the directory that will be searched
                                 for the requirements.txt and install.?? file
        """
        requirements_location = os.path.join(self.InstallDirectory, package_name,
                                             'requirements.txt')
        if os.path.exists(requirements_location):
            pip.main(['install', '-r', requirements_location])

        # Next, search for an additional installation script
        install_script_location = glob.glob(
            os.path.join(self.InstallDirectory, package_name, 'install.??'))
        # Make sure there's only one script to match to
        if len(install_script_location) == 1:
            os.system(install_script_location[0])


    def install_package(self, package_name):
        """Install a given package into the operator workspace.

        If the file requirements.txt exists inside of the package,
        the requirements are installed through pip.

        :param str package_name: must match the repository name in
                                 the valid packages list and GitHub
        """
        user = self.user_name
        installed = False

        # Location to install the package
        target_install = self.InstallDirectory + '/' + package_name

        if not os.path.exists(target_install):
            while not installed:
                # First pass will look at operator username, then the central repository
                check = urllib.urlopen(self.gitHubUrl + user + '/' + package_name)

                if check.getcode() == 404:

                    # If checking central repository and getting 404, something is wrong
                    if user == self.CentralGitHub:
                        error_string = 'Cannot find package ' + package_name
                        if user != self.user_name:
                            error_string += ' in ' + self.user_name + ' or'
                        error_string += (' in ' + user +
                                         ' repository! Check again for package location.')
                        print error_string

                        # I probably have it in my own GitHub
                        user = 'dabercro'

                    # If not checking central repository, check that next
                    else:
                        user = self.CentralGitHub

                # If repository exists, clone it
                else:

                    # Clone the repository inside the OpsSpace package
                    command = ('git clone ' + self.gitHubUrl + user + '/' +
                               package_name + '.git ' + target_install)
                    print command
                    os.system(command)

                    # If operator username, add the central location to remotes
                    if user != self.CentralGitHub:
                        # Lines to write to config
                        to_write = [
                            '[remote "' + self.CentralGitHub + '"]',
                            ('\turl = ' + self.gitHubUrl + self.CentralGitHub + '/' +
                             package_name + '.git'),
                            '\tfetch = +refs/heads/*:refs/remotes/' + self.CentralGitHub + '/*'
                        ]

                        # Append to the config file
                        append_to_file(os.path.join(self.InstallDirectory,
                                                    package_name, '.git/config'),
                                       to_write)

                    installed = True
        else:
            print package_name + ' already installed at ' + target_install + '!'

        # Check the .gitignore for the package name and add it, if needed
        # .gitignore location
        git_ignore = os.path.join(self.InstallDirectory, '.gitignore')
        # Line to write to .gitignore
        git_ignore_line = package_name + '/*'

        # Get contents
        with open(git_ignore, 'r') as git_ignore_file:
            git_ignore_list = git_ignore_file.readlines()

        # Check for line
        if git_ignore_line + '\n' not in git_ignore_list:
            append_to_file(git_ignore, git_ignore_line)

        self.install_requirements(package_name)

    def install_packages(self, package_list):
        """Calls install_package for a list of packages"""

        has_invalid_package = False
        for package in package_list:
            if package in self.ValidPackages:
                self.install_package(package)
            else:
                print package + ' is an invalid package!!!'
                has_invalid_package = True

        # If user tried to install any invalid package, give list of valid packages
        if has_invalid_package:
            self.print_valid_packages()

    def add_pythonpath(self):
        """Appends modified $PYTHONPATH variable to bash profile"""

        # Location to add to PYTHONPATH
        target_dir = self.InstallDirectory

        for profile_name in self.possibleProfiles:
            profile_path = os.environ.get('HOME') + '/' + profile_name

            # Search for profile files
            if os.path.exists(profile_path):

                # If there, source the profile file to get most updated variables
                load_env(profile_path)

                # If this directory is not in PYTHON path, append to profile
                if target_dir not in os.environ.get('PYTHONPATH', '').split(':'):
                    append_to_file(profile_path, ['', '# Python objects in OpsSpace',
                                                  'export PYTHONPATH=$PYTHONPATH:' + target_dir])


def main():
    """Main functionality of the install script.

    Uses system arguments to determine which packages to install.
    """

    # Using optparse for compatibility with Python 2.6
    from optparse import OptionParser

    usage = ('Usage: ./%prog [options] package1 package2 ... \n'
             '         --or-- \n'
             '       ./%prog install [--force]')

    parser = OptionParser(usage)

    parser.add_option('--user-name', '-u', metavar='UserName', dest='gitUser',
                      default='CMSCompOps',
                      help='GitHub user name, where the packages will be '
                           'searched for first (default CMSCompOps)')

    parser.add_option('--add-path', '-p', action='store_true', dest='addPath',
                      help='Add the location of this package to the user\'s PYTHONPATH '
                           'in their .bashrc or .bash_profile. The default '
                           'behavior is to let the user adjust PYTHONPATH on their own. '
                           'This option can be run without selecting any packages.')

    parser.add_option('--force', action='store_true', dest='installAll',
                      help='Install all possible packages when running ./setup.py install. '
                           '--force used since readthedocs tries it.')

    (options, args) = parser.parse_args()
    packages = args

    installer = Installer(options.gitUser)

    if len(sys.argv) != 1:
        installer.install_requirements('.')

    if options.installAll:
        installer.install_packages(installer.ValidPackages)

    if len(packages) == 1 and packages[0] in ['install', 'sdist']:

        def full_dirs(packages):
            """
            Get the full list of packages from the base packages list.

            :param list packages: The list of base packages to install
            :returns: The list of packages and sub-packages that are valid python modules
            :rtype: list
            """
            output = []
            for package in packages:
                output.extend([direct for direct, _, files in \
                                   os.walk(package) if '__init__.py' in files])

            return output

        packages = ['CMSToolBox', 'dbs', 'RestClient'] + \
            [cpack for cpack in ['cjson', 'pycurl'] if os.path.exists(cpack)] + \
            [pack for pack in installer.ValidPackages if os.path.exists(pack)]

        setup(name='OpsSpace',
              version=VERSION,
              packages=full_dirs(packages))

    else:
        if options.addPath:
            installer.add_pythonpath()

        if len(packages) == 0 or packages[0] == '':
            if not options.addPath:
                parser.print_help()
                installer.print_valid_packages()
                exit()
        else:
            print(
                '\n' +
                'I will now search for packages in ' + installer.user_name + '\'s repositories. ' +
                'If not found, will fall back on ' + installer.CentralGitHub + '.\n'
            )
            installer.install_packages(packages)


if __name__ == '__main__':
    main()
