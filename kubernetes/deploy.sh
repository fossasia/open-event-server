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
# Starting nfs deployment for persistent storage. Tricky. So, we'll go file by file.
# create the persistent volume using a GCE persistent disk
kubectl create -f ${DIR}/yamls/persistent-store/nfs-server.yml
# Let us give the NFS server ample amount of time to start up
echo "Waiting for NFS server to start up"
sleep 60
# create the NFS deployment service to expose ports
kubectl create -f ${DIR}/yamls/persistent-store/nfs-server-service.yml
# create the persistent volume entry for the NFS Server with a ReadWriteMany access mode
kubectl create -f ${DIR}/yamls/persistent-store/nfs-pv.yml
# create the required claim for the NFS Server persistent volume
kubectl create -f ${DIR}/yamls/persistent-store/nfs-pv-claim.yml
echo "Waiting longer for NFS server to start up"
# I found the sometimes NFS required a little bit longer to start up after all this. So, let's just give it some more time.
sleep 30
# Start celery deployment
kubectl create -f ${DIR}/yamls/celery
# Start web deployment & service
kubectl create -f ${DIR}/yamls/web
echo "Done. The project was deployed to kubernetes. :)"
