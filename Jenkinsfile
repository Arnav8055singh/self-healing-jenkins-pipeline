pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "self-healing-demo:${BUILD_NUMBER}"
        GEMINI_API_KEY = credentials('gemini-api-key')
        SLACK_WEBHOOK_URL = credentials('slack-webhook-url')
        JENKINS_USER = 'ARNROCK'
        JENKINS_API_TOKEN = credentials('jenkins-api-token')
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                sh 'pip3 install -r requirements.txt --break-system-packages'
            }
        }

        stage('Run Tests') {
            steps {
                sh 'python3 -m pytest test_app.py -v'
            }
        }

        stage('Build Docker Image') {
            steps {
                sh "docker build -t ${DOCKER_IMAGE} ."
            }
        }
    }

    post {
        failure {
            echo 'Build failed -- triggering AI diagnosis...'
            sh 'python3 diagnose_failure.py ${JOB_NAME} ${BUILD_NUMBER}'
        }
        success {
            echo 'Build succeeded!'
        }
    }
}