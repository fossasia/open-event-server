#!/bin/bash
export DIR=${BASH_SOURCE%/*}

if [ "$1" = "delete" ]; then
    echo "Clearing the cluster."
    if [ "$2" = "all" ]; then
        kubectl delete -f ${DIR}/yamls/lego/00-namespace.yml
        kubectl delete -f ${DIR}/yamls/nginx/00-namespace.yml
    fi
    kubectl delete -f ${DIR}/yamls/postgres/00-namespace.yml
    kubectl delete -f ${DIR}/yamls/redis/00-namespace.yml
    kubectl delete -f ${DIR}/yamls/elasticsearch/00-namespace.yml
    kubectl delete -f ${DIR}/yamls/web/00-namespace.yml
    echo "Done. The project was removed from the cluster."
elif [ "$1" = "create" ]; then
    echo "Deploying the project to kubernetes cluster"
    if [ "$2" = "all" ]; then
        # Start KubeLego deployment
        kubectl create -R -f ${DIR}/yamls/lego
        # Start nginx deployment, ingress & service
        kubectl create -R -f ${DIR}/yamls/nginx
    fi
    # Start Redis deployment & service
    kubectl create -R -f ${DIR}/yamls/redis
    # Start Elasticsearch deployment & service
    # kubectl create -R -f ${DIR}/yamls/elasticsearch
    # Start postgres deployment & service
    kubectl create -R -f ${DIR}/yamls/postgres
    echo "Waiting for postgres to startup. Will start in ~30s."
    sleep 30
    # Create web namespace
    kubectl create -R -f ${DIR}/yamls/web
    # Create API server deployment and service
    kubectl create -R -f ${DIR}/yamls/api-server
    echo "Waiting for server to start up. ~30s."
    sleep 30
    echo "Done. The project was deployed to kubernetes. :)"
fi
