def run(os) {
  return {

    def start = "cd ${os}; . /root/.bashrc"

    docker.build("opsspace-${os}:${env.BUILD_ID}", "test/${os}").inside('-u root:root') {

      stage("${os}: Copy Source") {
        sh """
           test ! -d ${os} || rm -rf ${os}
           mkdir ${os}
           cp --parents `git ls-files` ${os}
           """
      }

      stage("${os}: Installation") {
        sh "${start}; python setup.py install"
      }

      stage("${os}: Unit Tests") {
        sh "${start}; opsspace-test"
      }
    }
  }
}

def osList = ['sl6', 'sl7', 'sl7py3']

node {
  checkout scm
  parallel osList.collectEntries{
    ["${it}": run(it)]
  }
}
