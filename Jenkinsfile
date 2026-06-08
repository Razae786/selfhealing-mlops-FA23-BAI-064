pipeline {
    agent { label 'agent1' }

    environment {
        DOCKERHUB_CREDS = credentials('dockerhub-credentials')
        IMAGE_UNSTABLE  = "pakarmy786/sentiment-api:unstable"
        IMAGE_STABLE    = "pakarmy786/sentiment-api:stable"
        CONTAINER_NAME  = "sentiment-app-test"
    }

    stages {

        stage('Fetch') {
            steps {
                checkout scm
            }
        }

        stage('Build and Run') {
            steps {
                sh '''
                    docker build -t ${IMAGE_UNSTABLE} .
                    docker rm -f ${CONTAINER_NAME} || true
                    docker run -d --name ${CONTAINER_NAME} \
                        -p 5000:5000 \
                        ${IMAGE_UNSTABLE}
                    sleep 20
                    curl -f http://localhost:5000/health || exit 1
                '''
            }
        }

        stage('Unit Test') {
            steps {
                sh '''
                    docker run --rm \
                        --network host \
                        -e BASE_URL=http://localhost:5000 \
                        -v ${WORKSPACE}/tests:/tests \
                        python:3.10-slim bash -c "
                            pip install pytest requests &&
                            cd /tests &&
                            pytest test_api.py -v
                        "
                '''
            }
        }

        stage('UI Test') {
            steps {
                sh '''
                    docker run --rm \
                        --network host \
                        -e BASE_URL=http://localhost:5000 \
                        -e DISPLAY=:99 \
                        -v ${WORKSPACE}/tests:/tests \
                        selenium/standalone-chrome:latest bash -c "
                            pip install pytest selenium requests &&
                            cd /tests &&
                            pytest test_ui.py -v
                        " || true
                '''
            }
        }

        stage('Build and Push') {
            steps {
                sh '''
                    echo ${DOCKERHUB_CREDS_PSW} | docker login -u ${DOCKERHUB_CREDS_USR} --password-stdin

                    docker build -t ${IMAGE_UNSTABLE} .
                    docker push ${IMAGE_UNSTABLE}

                    git fetch origin stable-fallback
                    git checkout stable-fallback -- app.py
                    docker build -t ${IMAGE_STABLE} .
                    docker push ${IMAGE_STABLE}

                    git checkout HEAD -- app.py
                '''
            }
        }

        stage('Deploy to Minikube') {
            steps {
                sh '''
                    export KUBECONFIG=/var/lib/jenkins/.kube/config
                    kubectl apply -f k8s/pvc.yaml
                    kubectl apply -f k8s/blue-deployment.yaml
                    kubectl apply -f k8s/green-deployment.yaml
                    kubectl apply -f k8s/service.yaml
                    kubectl rollout status deployment/sentiment-blue-deployment --timeout=180s
                '''
            }
        }
    }

    post {
        always {
            sh 'docker rm -f ${CONTAINER_NAME} || true'
        }
    }
}
