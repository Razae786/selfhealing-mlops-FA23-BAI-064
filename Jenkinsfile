pipeline {
    agent { label 'agent1' }
    environment {
        DOCKERHUB_USER = 'pakarmy786'
        APP_NAME = 'sentiment-api'
    }
    stages {
        stage('Fetch') { steps { checkout scm } }
        stage('Build and Run') {
            steps {
                sh "docker rm -f unstable-app || true"
                sh "docker build -t ${DOCKERHUB_USER}/${APP_NAME}:unstable ."
                sh "docker run -d --name unstable-app --network host ${DOCKERHUB_USER}/${APP_NAME}:unstable"
                sh """
                    echo 'Waiting for Flask app to be ready...'
                    for i in \$(seq 1 60); do
                        if curl -s http://localhost:5000/health | grep -q 'healthy'; then
                            echo 'App is ready!'
                            break
                        fi
                        sleep 2
                    done
                """
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
                sh "sleep 15"
                sh "docker run --rm --network host -e BASE_URL=http://localhost:5000 -e SELENIUM_URL=http://localhost:4444/wd/hub -v \$(pwd)/tests:/tests python:3.10-slim bash -c 'pip install pytest selenium requests -q && cd /tests && pytest test_ui.py -v'"
            }
        }
        stage('Build and Push') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub-credentials', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    sh "echo \$DOCKER_PASS | docker login -u \$DOCKER_USER --password-stdin"
                    sh "docker push ${DOCKERHUB_USER}/${APP_NAME}:unstable"
                    sh "git fetch origin"
                    sh "git checkout stable-fallback"
                    sh "git reset --hard origin/stable-fallback"
                    sh "docker build -t ${DOCKERHUB_USER}/${APP_NAME}:stable ."
                    sh "docker push ${DOCKERHUB_USER}/${APP_NAME}:stable"
                    sh "git checkout main"
                    sh "git reset --hard origin/main"
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
            script {
                def committer = sh(script: "git log -1 --pretty=format:'%an <%ae>'", returnStdout: true).trim()
                def statusEmoji = currentBuild.currentResult == 'SUCCESS' ? '✅' : '❌'
                def emailBody = """
${statusEmoji} CI/CD Pipeline Status: ${currentBuild.currentResult}
Committer: ${committer}
Duration: ${currentBuild.durationString}
Build URL: ${env.BUILD_URL}

Pipeline Stages Executed:
1. Fetch (Checkout SCM)
2. Build and Run (Docker build & run unstable)
3. Unit Test (PyTest API tests)
4. UI Test (Selenium headless Chrome)
5. Build and Push (DockerHub push stable & unstable)
6. Deploy to Minikube (K8s manifests applied)

View full console output here: ${env.BUILD_URL}console
"""
                mail to: 'razaeilyas123@gmail.com',
                     subject: "${statusEmoji} CI/CD Pipeline ${currentBuild.currentResult} - Build #${env.BUILD_NUMBER}",
                     body: emailBody
            }
            sh "docker rm -f unstable-app || true"
            sh "docker rm -f selenium-chrome || true"
        }
    }
}
