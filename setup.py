#! /usr/bin/env python

"""
File mostly intended to set up working environment for operator as a script.

:author: Daniel Abercrombie <dabercro@mit.edu>
"""

import os
import urllib

from ToolBox.simplefiletools import load_env, append_to_file


class Installer:
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
    """List of valid packages that can be installed with this script"""

    def set_packages(self):
        """Read from list of valid package and append to valid list."""
        list_file = open(self.InstallDirectory + '/config/packagesList.txt', 'r')
        for package in list_file.readlines():
            self.ValidPackages.append(package.strip('\n'))

        list_file.close()

    def __init__(self, github_user):
        """Initialize with the GitHub username of the operator."""
        self.UserName = github_user or self.CentralGitHub

        self.set_packages()

    def print_valid_packages(self):
        """Displays valid packages for the user"""

        print('\nValid package names:\n')
        for package in self.ValidPackages:
            print('  ' + package)
        print('')

    def install_package(self, package_name):
        """Install a given package into the operator workspace"""

        user = self.UserName
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
                        if user != self.UserName:
                            error_string += ' in ' + self.UserName + ' or'
                        error_string += ' in ' + user + ' repository! Check again for package location.'
                        print(error_string)
                        exit(1)

                    # If not checking central repository, check that next
                    else:
                        user = self.CentralGitHub

                # If repository exists, clone it
                else:

                    # Clone the repository inside the OpsSpace package
                    command = 'git clone ' + self.gitHubUrl + user + '/' + package_name + '.git ' + target_install
                    print(command)
                    os.system(command)

                    # If operator username, add the central location to remotes
                    if user != self.CentralGitHub:
                        # Lines to write to config
                        to_write = [
                            '[remote "' + self.CentralGitHub + '"]',
                            '\turl = ' + self.gitHubUrl + self.CentralGitHub + '/' + package_name + '.git',
                            '\tfetch = +refs/heads/*:refs/remotes/' + self.CentralGitHub + '/*'
                        ]

                        # Append to the config file
                        append_to_file(self.InstallDirectory + '/' + package_name + '/.git/config', to_write)

                    installed = True
        else:
            print(package_name + ' already installed at ' + target_install + '!')

        # Check the .gitignore for the package name and add it, if needed
        # .gitignore location
        git_ignore = self.InstallDirectory + '/.gitignore'
        # Line to write to .gitignore
        git_ignore_line = package_name + '/*'

        # Get contents
        git_ignore_file = open(git_ignore, 'r')
        git_ignore_list = git_ignore_file.readlines()
        git_ignore_file.close()

        # Check for line
        if git_ignore_line + '\n' not in git_ignore_list:
            append_to_file(git_ignore, git_ignore_line)

    def install_packages(self, package_list):
        """Calls install_package for a list of packages"""

        has_invalid_package = False
        for package in package_list:
            if package in self.ValidPackages:
                self.install_package(package)
            else:
                print(package + ' is an invalid package!!!')
                has_invalid_package = True

        # If user tried to install any invalid package, give list of valid packages
        if has_invalid_package:
            self.print_valid_packages()

    def add_pythonpath(self):
        """Appends modified $PYTHONPATH variable to bash profile"""

        # Location to add to PYTHONPATH
        target_dir = '/'.join(self.InstallDirectory.split('/')[:-1])

        for profile_name in self.possibleProfiles:
            profile_path = os.environ.get('HOME') + '/' + profile_name
            # Search for profile files
            if os.path.exists(profile_path):
                # If there, source the profile file to get most updated variables
                load_env(profile_path)
                # If this directory is not in PYTHON path, append to profile
                if target_dir not in os.environ.get('PYTHONPATH').split(':'):
                    append_to_file(profile_path, ['', '# Python objects in CMSCompOps workspace',
                                                  'export PYTHONPATH=$PYTHONPATH:' + target_dir])


def main():
    """Main functionality of the install script"""

    # Using optparse for backwards compatibility with Python 2.6
    from optparse import OptionParser

    usage = 'Usage: %prog [options] package1 package2 ...'

    parser = OptionParser(usage)
    parser.add_option('--UserName', '-u', metavar='UserName', dest='gitUser', default=os.environ.get('USER'),
                      help='GitHub user name, where the packages will be searched for first (default $USER)')
    parser.add_option('--AddPath', action='store_true', dest='addPath',
                      help='Add the location of this package to the user\'s PYTHONPATH.')

    (options, args) = parser.parse_args()
    packages = args

    installer = Installer(options.gitUser)

    if len(packages) == 0 or packages[0] == '':
        parser.print_help()
        installer.print_valid_packages()
    else:
        print(
            '\n' +
            'I will now search for packages in ' + installer.UserName + '\'s repositories. ' +
            'If not found, will fall back on ' + installer.CentralGitHub + '.\n'
        )
        installer.install_packages(packages)

    if options.addPath:
        installer.add_pythonpath()


if __name__ == '__main__':
    main()
