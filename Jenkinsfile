pipeline {
    agent any

    environment {
        IMAGE_NAME    = 'myapp-backend'
        COMPOSE_FILE  = '/opt/myapp/backend/docker-compose.yml'
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
                echo "Building branch: ${env.BRANCH_NAME} | commit: ${env.GIT_COMMIT[0..6]}"
            }
        }

        stage('Test') {
            steps {
                sh '''
                    python3 -m venv .venv
                    . .venv/bin/activate
                    pip install -r requirements.txt --quiet
                    # Run tests if tests/ directory exists
                    if [ -d "tests" ]; then
                        pytest tests/ -v
                    else
                        echo "No tests directory found — skipping tests"
                    fi
                '''
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
                // Wait for container to be healthy before declaring success
                sh '''
                    echo "Waiting for backend to be ready..."
                    for i in $(seq 1 15); do
                        STATUS=$(docker inspect --format="{{.State.Health.Status}}" myapp-backend 2>/dev/null || echo "starting")
                        echo "Attempt $i: $STATUS"
                        if [ "$STATUS" = "healthy" ]; then
                            echo "Backend is healthy!"
                            exit 0
                        fi
                        sleep 4
                    done
                    echo "Health check timed out — check container logs"
                    docker logs myapp-backend --tail 30
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
            sh 'docker logs myapp-backend --tail 50 || true'
        }
        always {
            // Clean up the virtual env created during test stage
            sh 'rm -rf .venv || true'
        }
    }
}
