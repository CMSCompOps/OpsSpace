#! /usr/bin/python

""" @file install.py

File mostly intended to set up working environment for operator as a script.
@author Daniel Abercrombie <dabercro@mit.edu>
"""

import json
import os
import sys
import urllib

class CompOpsWorkspaceInstaller:
    """Class the holds the information for installing workspace"""

    ValidPackages = ['SiteReadiness', 'TransferTeam', 'WmAgentScripts']
    CentralGitHub = 'CMSCompOps'
    InstallDirectory = os.path.dirname(os.path.realpath(__file__))
    apiBaseUrl = 'https://api.github.com/repos/'
    gitHubUrl  = 'https://github.com/'

    def __init__(self, githubUser):
        self.userName = githubUser or self.CentralGitHub

    def PrintValidPackages(self):
        """Displays valid packages for the user"""

        print('\nValid package names:\n')
        for package in self.ValidPackages:
            print('  ' + package)
        print('')
        

    def InstallPackage(self, packageName):
        """Install a given package into the operator workspace"""

        # First check if the repository exists

        user = self.userName
        installed = False
        
        while not installed:
            check = urllib.urlopen(self.apiBaseUrl + user + '/' + packageName)
            if check.getcode() == 404:

                if user == self.CentralGitHub:
                    errorString = 'Cannot find package ' + packageName
                    if user != self.userName:
                        errorString += ' in ' + self.userName + ' or'
                    errorString += ' in ' + user + ' repository! Check again for package location.'
                    print(errorString)
                    exit(1)

                else:
                    user = self.CentralGitHub

            else:
                command = 'git clone ' + self.gitHubUrl + user + '/' + packageName + '.git ' + self.InstallDirectory + '/' + packageName
                print(command)
                os.system(command)
                if user != self.CentralGitHub:
                    toWrite = [
                        '[remote "' + self.CentralGitHub + '"]',
                        '\turl = ' + self.gitHubUrl + self.CentralGitHub + '/' + packageName + '.git',
                        '\tfetch = +refs/heads/*:refs/remotes/' + self.CentralGitHub + '/*'
                        ]
                    gitConfig = open(self.InstallDirectory + '/' + packageName + '/.git/config','a')
                    for line in toWrite:
                        gitConfig.write(line+'\n')

                    gitConfig.close()

                installed = True

    def InstallPackages(self, packageList):
        """Calls InstallPackage for a list of packages"""

        invalidPackage = False
        for package in packageList:
            if package in self.ValidPackages:
                self.InstallPackage(package)
            else:
                print(package + ' is an invalid package!!!')
                invalidPackage = True

        if invalidPackage:
            self.PrintValidPackages()

def main():
    """Main functionality of the install script"""

    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('--username', '-u', metavar = 'USERNAME', dest = 'gitUser', default = os.environ.get('USER'),
                        help = 'GitHub user name, where the packages will be searched for first (default ' + os.environ.get('USER') + ')')
    parser.add_argument('packages', metavar = 'PACKAGES', nargs = '*',
                        help = 'List of valid packages to be installed. Giving no package will show list of possible packages to install')

    args = parser.parse_args()

    installer = CompOpsWorkspaceInstaller(args.gitUser)

    if len(args.packages) == 0:
        parser.print_help()
        installer.PrintValidPackages()
    else:
        print(
            '\n' +
            'I will now search for packages in ' + installer.userName + '\'s repositories. ' +
            'If not found, will fall back on ' + installer.CentralGitHub + '.\n'
            )
        installer.InstallPackages(args.packages)

if __name__ == '__main__':
    main()
