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
                sh "docker ps -aq --filter publish=5000 | xargs -r docker rm -f"
                sh "docker build -t ${DOCKERHUB_USER}/${APP_NAME}:unstable ."
                sh "docker run -d --name unstable-app -p 5000:5000 ${DOCKERHUB_USER}/${APP_NAME}:unstable"
                sh "sleep 50"
            }
        }
        stage('Unit Test') {
            steps {
                sh "docker exec unstable-app pip install pytest requests -q"
                sh "docker exec unstable-app pytest tests/test_api.py -v"
            }
        }
        stage('UI Test') {
            steps {
                sh "docker rm -f selenium-chrome || true"
                sh "docker run -d --name selenium-chrome --network host --shm-size=2g selenium/standalone-chrome:latest"
                sh "sleep 20"
                sh "docker exec unstable-app pip install pytest selenium requests -q"
                sh "docker exec -e BASE_URL=http://localhost:5000 -e SELENIUM_URL=http://localhost:4444/wd/hub unstable-app pytest tests/test_ui.py -v"
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
            sh "docker rm -f unstable-app || true"
            sh "docker rm -f selenium-chrome || true"
        }
    }
}
