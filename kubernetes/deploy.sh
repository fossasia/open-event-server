#!/bin/bash
echo "Getting credentials for staging cluster"
gcloud container clusters get-credentials staging-cluster
export DIR=${BASH_SOURCE%/*}

if [ "$1" = "delete" ]; then
    echo "Clearing the cluster."
    kubectl delete -f ${DIR}/yamls/lego/00-namespace.yml
    kubectl delete -f ${DIR}/yamls/postgres/00-namespace.yml
    kubectl delete -f ${DIR}/yamls/redis/00-namespace.yml
    kubectl delete -f ${DIR}/yamls/nginx/00-namespace.yml
    kubectl delete -f ${DIR}/yamls/web/00-namespace.yml
    echo "Done. The project was removed from the cluster."
elif [ "$1" = "create" ]; then
    echo "Deploying the project to kubernetes cluster"
    # Start KubeLego deployment
    kubectl create -R -f ${DIR}/yamls/lego
    # Start nginx deployment, ingress & service
    kubectl create -R -f ${DIR}/yamls/nginx
    # Start Redis deployment & service
    kubectl create -R -f ${DIR}/yamls/redis
    # Start postgres persistent volume, deployment & service
    kubectl create -R -f ${DIR}/yamls/postgres
    echo "Waiting for postgres to startup. Will start in ~30s."
    sleep 30
    # Create web namespace
    kubectl create -R -f ${DIR}/yamls/web
    # Start the redirector deployment & service
    kubectl create -R -f ${DIR}/yamls/redirector
    # Create API server deployment and service
    kubectl create -R -f ${DIR}/yamls/api
    echo "Done. The project was deployed to kubernetes. :)"
fi
