def run(os) {
  return {

    docker.build("opsspace-${os}:${env.BUILD_ID}", "test/${os}").inside('-u root:root') {

      stage("${os}: Copy Source") {
        sh """
           test ! -d ${os} || rm -rf ${os}
           mkdir ${os}
           cp --parents `git ls-files` ${os}
           """
      }

      stage("${os}: Installation") {
        sh "cd ${os}; python setup.py install"
      }

      stage("${os}: Unit Tests") {
        sh "cd ${os}; opsspace-test"
      }
    }
  }
}

def osList = ['sl6', 'sl7']

node {
  checkout scm
  parallel osList.collectEntries{
    ["${it}": run(it)]
  }
}
