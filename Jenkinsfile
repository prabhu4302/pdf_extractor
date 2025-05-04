pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE = 'your-username/pdf-extractor'
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
                    // Only needed if pushing to a registry
                    docker.withRegistry('https://registry.hub.docker.com', 'docker-hub-credentials') {
                        docker.image("${DOCKER_IMAGE}:${DOCKER_TAG}").push()
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
