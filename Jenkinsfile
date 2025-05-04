pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE = 'pdf-extractor'
        DOCKER_TAG = "${env.BUILD_NUMBER}"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Build Docker Image') {
            steps {
                script {
                    // Ensure Docker is available
                    docker.withRegistry('') {
                        docker.build("${DOCKER_IMAGE}:${DOCKER_TAG}", ".")
                    }
                }
            }
        }
        
        stage('Push Docker Image') {
    steps {
        script {
            docker.withRegistry('https://index.docker.io/v1/', 'dockerhub-creds') {
                docker.image("${DOCKER_IMAGE}:${DOCKER_TAG}").push()
                // Also push as latest
                docker.image("${DOCKER_IMAGE}:${DOCKER_TAG}").push('latest')
            }
        }
    }
}
    }
    
    post {
        failure {
            echo 'Pipeline failed! Check logs.'
        }
        success {
            echo 'Pipeline succeeded!'
        }
    }
}
