pipeline {
    agent any

    environment {
        APP_DIR = '/opt/app/backend'
        DEPLOY_USER = 'saranobyl'          // your non-root VPS user
        VPS_HOST = '62.171.132.180'
        SSH_PORT = '2508'
    }

    stages {
        stage('Pull Latest Code') {
            steps {
                sshagent(['vps-deploy-key']) {
                    sh """
                        ssh -o StrictHostKeyChecking=no \
                            -p ${SSH_PORT} \
                            ${DEPLOY_USER}@${VPS_HOST} \
                            'cd ${APP_DIR} && git pull origin main'
                    """
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                sshagent(['vps-deploy-key']) {
                    sh """
                        ssh -p ${SSH_PORT} \
                            ${DEPLOY_USER}@${VPS_HOST} \
                            'cd ${APP_DIR} && docker compose build --no-cache'
                    """
                }
            }
        }

        stage('Deploy Containers') {
            steps {
                sshagent(['vps-deploy-key']) {
                    sh """
                        ssh -p ${SSH_PORT} \
                            ${DEPLOY_USER}@${VPS_HOST} \
                            'cd ${APP_DIR} && docker compose up -d'
                    """
                }
            }
        }
    }

    post {
        success {
            echo '✅ Deployment successful!'
        }
        failure {
            echo '❌ Deployment failed. Check console output above.'
        }
    }
}