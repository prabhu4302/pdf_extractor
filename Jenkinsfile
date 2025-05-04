pipeline {
    agent any
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Build Docker Image') {
            steps {
                script {
                    docker.build("prabhudocker4302/pdf-extractor:${env.BUILD_NUMBER}")
                }
            }
        }
        
        stage('Push Docker Image') {
            steps {
                script {
                    docker.withRegistry('https://index.docker.io/v1/', 'dockerhub-creds') {
                        docker.image("prabhudocker4302/pdf-extractor:${env.BUILD_NUMBER}").push()
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
