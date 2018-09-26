pipeline {
  agent {
    docker {
      image 'python:2.7-slim'
      args '-u root:root'
    }
  }

  stages {
    stage ('Installation') {
      steps {
        sh 'python setup.py install'
      }
    }

    stage ('Unit Tests') {
      steps {
        sh 'opsspace-test'
      }
    }
  }
}
