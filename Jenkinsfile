environment {
    DOCKER_IMAGE = 'prabhudocker4302/pdf-extractor'  // Must include your username
    DOCKER_TAG = "${env.BUILD_NUMBER}"
}

stages {
    stage('Build Docker Image') {
        steps {
            script {
                docker.build("${DOCKER_IMAGE}:${DOCKER_TAG}")
            }
        }
    }
    
    stage('Push Docker Image') {
        steps {
            script {
                docker.withRegistry('https://index.docker.io/v1/', 'dockerhub-creds') {
                    docker.image("${DOCKER_IMAGE}:${DOCKER_TAG}").push()
                }
            }
        }
    }
}
