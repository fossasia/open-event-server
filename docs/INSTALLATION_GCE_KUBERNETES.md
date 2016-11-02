# Installation of the Open Event Orga Server on the Google Container Engine with Kubernetes


## Setup and Requirements

If you don’t already have a Google Account (Gmail or Google Apps), you must []create one](https://accounts.google.com/SignUp). Then, sign-in to Google Cloud Platform console ([console.cloud.google.com](http://console.cloud.google.com/)) and create a new project:


Store your project ID into a variable as many commands below use it:

```
export PROJECT_ID="your-project-id"
```

Next, [enable billing](https://console.cloud.google.com/billing) in the Cloud Console in order to use Google Cloud resources and [enable the Container Engine API](https://console.cloud.google.com/project/_/kubernetes/list).

Install [Docker](https://docs.docker.com/engine/installation/), and [Google Cloud SDK](https://cloud.google.com/sdk/).

Finally, after Google Cloud SDK installs, run the following command to install `kubectl`:

```
gcloud components install kubectl
```

## Create your Kubernetes Cluster

First, choose a [Google Cloud Project zone](https://cloud.google.com/compute/docs/regions-zones/regions-zones) to run your service. We will be using us-central1-a. This is configured on the command line via:

```
gcloud config set compute/zone us-central1-a
```

Now, create a cluster via the `gcloud` command line tool:

```
gcloud container clusters create opev-cluster
```

Get the credentials for `kubectl` to use.

```
gcloud container clusters get-credentials opev-cluster
```

## Deploy our pods, services and deployments

From the project directory, use kubectl to deploy our application from the defined configuration files that are in the `kubernetes` directory.

```
kubectl create -f ./kubernetes
```

The Kubernetes master creates the load balancer and related Compute Engine forwarding rules, target pools, and firewall rules to make the service fully accessible from outside of Google Cloud Platform.

To find the ip addresses associated with the service run:

```
kubectl get services web
```

The `EXTERNAL_IP` may take several minutes to become available and visible. If the `EXTERNAL_IP` is missing, wait a few minutes and try again.

Note there are 2 IP addresses listed, both serving port 80. `CLUSTER_IP` is only visible inside your cloud virtual network. `EXTERNAL_IP` is externally accessible.

You should now be able to reach the web application by pointing your browser to this address: `http://EXTERNAL_IP`

## Other handy commands

- Delete all created pods, services and deployments

    ```
    kubectl delete -f kubernetes/
    ```
    
-  Access The Kubernetes dashboard Web GUI

    Run the following command to start a proxy.
    
    ```
    kubectl proxy
    ```
    
    and Goto [http://localhost:8001/ui](http://localhost:8001/ui)

- Deleting the cluster
    ```
    gcloud container clusters delete opev-cluster
    ```
