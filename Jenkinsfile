pipeline {
    agent { label 'agent1' }
    environment {
        DOCKERHUB_USER = 'pakarmy786'
        APP_NAME = 'sentiment-api'
    }
    stages {
        stage('Fetch') {
            steps { checkout scm }
        }
        stage('Build and Run') {
            steps {
                sh "docker stop unstable-app || true"
                sh "docker rm unstable-app || true"
                sh "docker build -t ${DOCKERHUB_USER}/${APP_NAME}:unstable ."
                sh "docker run -d --name unstable-app -p 5000:5000 ${DOCKERHUB_USER}/${APP_NAME}:unstable"
                sh "sleep 50"
            }
        }
        stage('Unit Test') {
            steps {
                sh "docker run --rm --network host -e BASE_URL=http://localhost:5000 -v \$(pwd)/tests:/tests python:3.10-slim bash -c 'pip install pytest requests -q && cd /tests && pytest test_api.py -v'"
            }
        }
        stage('UI Test') {
            steps {
                sh "docker run --rm --network host -e BASE_URL=http://localhost:5000 -v \$(pwd)/tests:/tests python:3.10-slim bash -c 'pip install pytest selenium -q && cd /tests && pytest test_ui.py -v' || true"
            }
        }
        stage('Build and Push') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub-credentials', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    sh "echo \$DOCKER_PASS | docker login -u \$DOCKER_USER --password-stdin"
                    sh "docker push ${DOCKERHUB_USER}/${APP_NAME}:unstable"
                    sh "git checkout stable-fallback"
                    sh "docker build -t ${DOCKERHUB_USER}/${APP_NAME}:stable ."
                    sh "docker push ${DOCKERHUB_USER}/${APP_NAME}:stable"
                    sh "git checkout main"
                }
            }
        }
        stage('Deploy to Minikube') {
            steps {
                sh "eval \$(minikube docker-env)"
                sh "kubectl apply -f k8s/pvc.yaml"
                sh "kubectl apply -f k8s/blue-deployment.yaml"
                sh "kubectl apply -f k8s/green-deployment.yaml"
                sh "kubectl apply -f k8s/service.yaml"
                sh "kubectl patch svc sentiment-api-service --type=merge -p '{\"spec\":{\"selector\":{\"slot\":\"blue\"}}}'"
            }
        }
    }
    post {
        always {
            sh "docker stop unstable-app || true"
            sh "docker rm unstable-app || true"
        }
    }
}
