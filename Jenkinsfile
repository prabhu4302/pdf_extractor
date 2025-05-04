pipeline {
    agent any

    environment {
        // Docker Hub credentials (configure in Jenkins)
        DOCKER_CREDS = credentials('docker-hub-creds')
        DOCKER_IMAGE = 'prabhudocker4302/nithya4525'
        DOCKER_TAG = 'latest'
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
        stage('Deploy to EC2') {
           steps {
               sshagent(['ec2-ssh-key']) {
            sh "ssh -o StrictHostKeyChecking=no ec2-user@3.110.107.194 'docker pull prabhudocker4302/nithya4525:latest && docker restart my-app'"
    }

    post {
        success {
            echo 'Docker image built and pushed successfully!'
        }
        failure {
            echo 'Pipeline failed! Check logs.'
        }
    }
}
