#!/bin/bash
echo "Getting credentials for staging cluster"
gcloud container clusters get-credentials staging-cluster
echo "Deploying the project to kubernetes cluster"
export DIR=${BASH_SOURCE%/*}
# Start KubeLego deployment
kubectl create -f ${DIR}/yamls/lego
# Start nginx deployment, ingress & service
kubectl create -f ${DIR}/yamls/nginx
# Start postgres persistent volume, deployment & service
kubectl create -f ${DIR}/yamls/postgres
# Start Elasticsearch deployment and service
kubectl create -f ${DIR}/yamls/elasticsearch
# Start the redirector deployment & service
kubectl create -f ${DIR}/yamls/redirector
# Start Redis deployment & service
kubectl create -f ${DIR}/yamls/redis
sleep 30
# Start celery deployment
kubectl create -f ${DIR}/yamls/celery
# Start web deployment & service
kubectl create -f ${DIR}/yamls/web
echo "Done. The project was deployed to kubernetes. :)"
