#! /usr/bin/python2.7

""" @file install.py

File mostly intended to set up working environment for operator as a script.
@author Daniel Abercrombie <dabercro@mit.edu>
"""

import os
import urllib

from ToolBox.utils import load_env, append_to_file


class Installer:
    """Class the holds the information for installing workspace"""

    # List of valid packages that can be installed with this script
    ValidPackages = [
        'SiteReadiness',
        'TransferTeam',
        'WmAgentScripts'
    ]

    # List of profiles searched for in user's home to append to PYTHONPATH
    possibleProfiles = [
        '.bashrc',
        '.bash_profile'
    ]

    # Default GitHub account containing packages that can be installed
    CentralGitHub = 'CMSCompOps'

    # Location of the OpsSpace
    InstallDirectory = os.path.dirname(os.path.realpath(__file__))

    # Remote repository location
    gitHubUrl = 'https://github.com/'

    def __init__(self, github_user):
        """Initialize with the GitHub username of the operator."""
        self.UserName = github_user or self.CentralGitHub

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

    packages = []
    git_user = ''

    # If argparse available, use it
    try:
        from argparse import ArgumentParser
        parser = ArgumentParser()
        parser.add_argument('--UserName', '-u', metavar='UserName', dest='gitUser', default=os.environ.get('USER'),
                            help='GitHub user name, where the packages will be searched for first (default ' +
                            os.environ.get('USER') + ')')
        parser.add_argument('packages', metavar='PACKAGES', nargs='*',
                            help='List of valid packages to be installed. ' +
                                 'Giving no package will show list of possible ' +
                                 'packages to install')

        args = parser.parse_args()
        packages = args.packages
        git_user = args.gitUser

    # Otherwise, use optparser
    except ImportError:
        from optparse import OptionParser
        parser = OptionParser()
        parser.add_option('--UserName', '-u', metavar='UserName', dest='gitUser', default=os.environ.get('USER'),
                          help='GitHub user name, where the packages will be searched for first (default ' +
                          os.environ.get('USER') + ')')
        parser.add_option('-p', '--Packages', metavar = 'PackageNames', dest = 'packages', default = '',
                          help = 'List of packages to install. Separated by commas, no spaces. ' +
                                 'Examples:  -p package1,package2 or --Packages=package1,package2')

        (options, args) = parser.parse_args()
        packages = options.packages.split(',')
        git_user = options.gitUser


    installer = Installer(git_user)

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

    installer.add_pythonpath()


if __name__ == '__main__':
    main()
