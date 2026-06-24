pipeline {
    agent any

    environment {
        APP_DIR = '/opt/app/backend'
    }

    stages {
        stage('Pull Latest Code') {
            steps {
                sh 'cd ${APP_DIR} && git pull origin main'
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'cd ${APP_DIR} && docker compose build --no-cache'
            }
        }

        stage('Deploy Containers') {
            steps {
                sh 'cd ${APP_DIR} && docker compose up -d'
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