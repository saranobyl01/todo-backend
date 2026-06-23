pipeline {
    agent any

    environment {
        IMAGE_NAME   = 'todoapp-backend'
        COMPOSE_FILE = '/opt/myapp/backend/docker-compose.yml'
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
                echo "Building branch: ${env.BRANCH_NAME} | commit: ${env.GIT_COMMIT[0..6]}"
            }
        }

        stage('Build Image') {
            steps {
                sh """
                    docker build \
                        -t ${IMAGE_NAME}:latest \
                        -t ${IMAGE_NAME}:${env.GIT_COMMIT[0..6]} \
                        .
                """
            }
        }

        stage('Run Tests') {
            steps {
                sh '''
                    if [ -d tests ]; then
                        echo "Running tests inside built image..."
                        docker run --rm todoapp-backend:latest pytest tests/ -v
                    else
                        echo "No tests directory found — skipping tests"
                    fi
                '''
            }
        }

        stage('Deploy') {
            steps {
                withCredentials([
                    string(credentialsId: 'POSTGRES_PASSWORD', variable: 'POSTGRES_PASSWORD'),
                    string(credentialsId: 'SECRET_KEY',        variable: 'SECRET_KEY')
                ]) {
                    sh """
                        export POSTGRES_PASSWORD=\$POSTGRES_PASSWORD
                        export SECRET_KEY=\$SECRET_KEY
                        docker compose -f ${COMPOSE_FILE} up -d --remove-orphans
                    """
                }
            }
        }

        stage('Health Check') {
            steps {
                sh '''
                    echo "Waiting for backend to be ready..."
                    for i in $(seq 1 15); do
                        STATUS=$(docker inspect --format="{{.State.Status}}" todoapp-backend 2>/dev/null || echo "missing")
                        echo "Attempt $i: $STATUS"
                        if [ "$STATUS" = "running" ]; then
                            echo "Backend container is running!"
                            exit 0
                        fi
                        sleep 4
                    done
                    echo "Health check timed out — check container logs"
                    docker logs todoapp-backend --tail 30
                    exit 1
                '''
            }
        }
    }

    post {
        success {
            echo "✅ Backend pipeline succeeded — deployed commit ${env.GIT_COMMIT[0..6]}"
        }
        failure {
            echo "❌ Backend pipeline failed — check console output above"
            sh 'docker logs todoapp-backend --tail 50 || true'
        }
    }
}
