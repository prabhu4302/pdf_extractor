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

        stage('Deploy to EC2') {
            steps {
                sshagent (credentials: ['ec2-ssh-key']) {
                    sh '''
                        ssh -o StrictHostKeyChecking=no ubuntu@13.233.33.93"
                            docker pull prabhudocker4302/pdf-extractor:${BUILD_NUMBER} &&
                            docker stop pdf-extractor || true &&
                            docker rm pdf-extractor || true &&
                            docker run -d --name pdf-extractor prabhudocker4302/pdf-extractor:${BUILD_NUMBER}
                        "
                    '''
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
