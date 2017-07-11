#!/bin/bash
echo "Deploying the project to kubernetes cluster"
export DIR=${BASH_SOURCE%/*}
# Start KubeLego deployment
kubectl create -f ${DIR}/yamls/lego
# Start nginx deployment, ingress & service
kubectl create -f ${DIR}/yamls/nginx
# Start postgres persistent volume, deployment & service
kubectl create -f ${DIR}/yamls/postgres
# Start the redirector deployment & service
kubectl create -f ${DIR}/yamls/redirector
# Start Redis deployment & service
kubectl create -f ${DIR}/yamls/redis
# Let us give the NFS server ample amount of time to start up
echo "Waiting for Postgres server to start up"
sleep 60
# Start web deployment & service
kubectl create -f ${DIR}/yamls/web
echo "Done. The project was deployed to kubernetes. :)"
