#! /usr/bin/python

""" @file install.py

File mostly intended to set up working environment for operator as a script.
@author Daniel Abercrombie <dabercro@mit.edu>
"""

import os
import urllib


class CompOpsWorkspaceInstaller:
    """Class the holds the information for installing workspace"""

    ValidPackages = ['SiteReadiness', 'TransferTeam', 'WmAgentScripts']
    CentralGitHub = 'CMSCompOps'
    InstallDirectory = os.path.dirname(os.path.realpath(__file__))
    apiBaseUrl = 'https://api.github.com/repos/'
    gitHubUrl = 'https://github.com/'

    def __init__(self, github_user):
        self.UserName = github_user or self.CentralGitHub

    def print_valid_packages(self):
        """Displays valid packages for the user"""

        print('\nValid package names:\n')
        for package in self.ValidPackages:
            print('  ' + package)
        print('')

    def install_package(self, package_name):
        """Install a given package into the operator workspace"""

        # First check if the repository exists

        user = self.UserName
        installed = False

        while not installed:
            check = urllib.urlopen(self.apiBaseUrl + user + '/' + package_name)
            if check.getcode() == 404:

                if user == self.CentralGitHub:
                    error_string = 'Cannot find package ' + package_name
                    if user != self.UserName:
                        error_string += ' in ' + self.UserName + ' or'
                    error_string += ' in ' + user + ' repository! Check again for package location.'
                    print(error_string)
                    exit(1)

                else:
                    user = self.CentralGitHub

            else:
                command = 'git clone ' + self.gitHubUrl + user + '/' + package_name + '.git ' + \
                          self.InstallDirectory + '/' + package_name
                print(command)
                os.system(command)
                if user != self.CentralGitHub:
                    to_write = [
                        '[remote "' + self.CentralGitHub + '"]',
                        '\turl = ' + self.gitHubUrl + self.CentralGitHub + '/' + package_name + '.git',
                        '\tfetch = +refs/heads/*:refs/remotes/' + self.CentralGitHub + '/*'
                    ]
                    git_config = open(self.InstallDirectory + '/' + package_name + '/.git/config', 'a')
                    for line in to_write:
                        git_config.write(line + '\n')

                    git_config.close()

                installed = True

    def install_packages(self, package_list):
        """Calls install_package for a list of packages"""

        has_invalid_package = False
        for package in package_list:
            if package in self.ValidPackages:
                self.install_package(package)
            else:
                print(package + ' is an invalid package!!!')
                has_invalid_package = True

        if has_invalid_package:
            self.print_valid_packages()


def main():
    """Main functionality of the install script"""

    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('--UserName', '-u', metavar='UserName', dest='gitUser', default=os.environ.get('USER'),
                        help='GitHub user name, where the packages will be searched for first (default ' +
                             os.environ.get('USER') + ')')
    parser.add_argument('packages', metavar='PACKAGES', nargs='*',
                        help='List of valid packages to be installed. Giving no package will show list of possible ' +
                             'packages to install')

    args = parser.parse_args()

    installer = CompOpsWorkspaceInstaller(args.gitUser)

    if len(args.packages) == 0:
        parser.print_help()
        installer.print_valid_packages()
    else:
        print(
            '\n' +
            'I will now search for packages in ' + installer.UserName + '\'s repositories. ' +
            'If not found, will fall back on ' + installer.CentralGitHub + '.\n'
        )
        installer.install_packages(args.packages)


if __name__ == '__main__':
    main()
