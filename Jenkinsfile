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
        withCredentials([usernamePassword(
            credentialsId: 'dockerhub-creds',
            usernameVariable: 'DOCKER_USER',
            passwordVariable: 'DOCKER_PASS'
        )]) {
            sh """
                docker login -u $DOCKER_USER -p $DOCKER_PASS
                docker tag pdf-extractor:7 prabhudocker4302/pdf-extractor:7
                docker push prabhudocker4302/pdf-extractor:7
            """
        }
    }
}
}
