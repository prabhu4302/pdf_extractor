pipeline {
    agent any

    environment {
        IMAGE_NAME = 'prabhudocker4302/nithya4525'
    }

    stages {
        stage('Checkout') {
            steps {
                git 'https://github.com/prabhu4302/pdf_extractor.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    docker.build("${IMAGE_NAME}:latest")
                }
            }
        }

        stage('Push Docker Image') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub-creds', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    sh '''
                      echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
                      docker push ${IMAGE_NAME}:latest
                    '''
                }
            }
        }
    }
}
