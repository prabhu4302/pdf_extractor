pipeline {
    agent any

    environment {
        DOCKER_CREDS = credentials('docker-hub-creds')  // Jenkins credentials ID
        DOCKER_IMAGE = 'prabhudocker4302/nithya4525'
        DOCKER_TAG = "${env.BUILD_NUMBER}"  // Using build number instead of 'latest'
        EC2_IP = '3.110.107.194'             // Consider moving to Jenkins credentials
        APP_CONTAINER_NAME = 'pdf-extractor'  // More specific than 'my-app'
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
                    // Build with no-cache for production
                    docker.build("${DOCKER_IMAGE}:${DOCKER_TAG}", "--no-cache .")
                    
                    // Optionally scan for vulnerabilities
                    // sh "docker scan ${DOCKER_IMAGE}:${DOCKER_TAG}"
                }
            }
        }

        stage('Push to Docker Hub') {
            steps {
                script {
                    docker.withRegistry('https://registry.hub.docker.com', 'docker-hub-creds') {
                        docker.image("${DOCKER_IMAGE}:${DOCKER_TAG}").push()
                        // Optionally push as latest
                        // docker.image("${DOCKER_IMAGE}:${DOCKER_TAG}").push('latest')
                    }
                }
            }
        }

        stage('Deploy to EC2') {
            steps {
                script {
                    sshagent(['ec2-ssh-key']) {
                        sh """
                        ssh -o StrictHostKeyChecking=no ec2-user@${EC2_IP} '
                            # Stop and remove existing container
                            docker stop ${APP_CONTAINER_NAME} || true &&
                            docker rm ${APP_CONTAINER_NAME} || true &&
                            
                            # Pull new image
                            docker pull ${DOCKER_IMAGE}:${DOCKER_TAG} &&
                            
                            # Run new container with proper resource limits
                            docker run -d \
                                --name ${APP_CONTAINER_NAME} \
                                --restart unless-stopped \
                                --memory 512m \
                                --cpus 1 \
                                -p 80:3000 \
                                -v /home/ec2-user/pdf-data:/app/data \
                                ${DOCKER_IMAGE}:${DOCKER_TAG}'
                        """
                    }
                    
                    // Verify deployment
                    sh """
                        ssh -o StrictHostKeyChecking=no ec2-user@${EC2_IP} \
                        'docker inspect --format=\"{{.State.Status}}\" ${APP_CONTAINER_NAME}' | grep running
                    """
                }
            }
        }
    }

    post {
        always {
            // Clean up workspace
            cleanWs()
        }
        success {
            slackSend(color: 'good', message: "SUCCESS: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]'")
        }
        failure {
            slackSend(color: 'danger', message: "FAILED: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]'")
            // Automatic rollback could be implemented here
        }
    }
}     
