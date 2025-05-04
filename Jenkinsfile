pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE = 'prabhudocker4302/nithya4525'
        DOCKER_TAG = "${env.BUILD_NUMBER}"
    }
    
    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', 
                url: 'https://github.com/prabhu4302/pdf_extractor.git'
            }
        }
        
        stage('Build Docker Image') {
            steps {
                script {
                    docker.build("${DOCKER_IMAGE}:${DOCKER_TAG}")
                }
            }
        }
        
        stage('Push to Docker Hub') {
            steps {
                script {
                    docker.withRegistry('https://registry.hub.docker.com', 'docker-hub-creds') {
                        docker.image("${DOCKER_IMAGE}:${DOCKER_TAG}").push()
                    }
                }
            }
        }
    }
    
    post {
        success {
            echo 'Image successfully pushed to Docker Hub!'
        }
        failure {
            echo 'Pipeline failed!'
        }
    }
}
