import os

import requests


class KubernetesApi:
    service_host = os.getenv('KUBERNETES_SERVICE_HOST', '')
    api_url = 'https://' + service_host + '/api/v1/'
    token = ''
    namespace = 'default'
    headers = {}

    def __init__(self):
        self.token = open('/var/run/secrets/kubernetes.io/serviceaccount/token', 'r').read().replace('\n', '')
        self.namespace = open('/var/run/secrets/kubernetes.io/serviceaccount/namespace', 'r').read().replace('\n', '')
        self.headers = {'Authorization': 'Bearer ' + self.token}
        pass

    def get(self, endpoint):
        return requests.get(self.api_url + endpoint, headers=self.headers, verify=False).json()

    def get_pods(self):
        return self.get('namespaces/' + self.namespace + '/pods')

    @staticmethod
    def is_on_kubernetes():
        return 'KUBERNETES_SERVICE_HOST' in os.environ
