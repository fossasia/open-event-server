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

    def get(self, endpoint, headers=None, params=None, return_json=True):
        """
        Make a GET request
        :param return_json:
        :param params:
        :param headers:
        :param endpoint:
        :return:
        """
        if not headers:
            headers = self.headers
        response = requests.get(self.api_url + endpoint, headers=headers, params=params, verify=False)
        if return_json:
            return response.json()
        else:
            return response.text

    def get_pods(self, namespace=None):
        """
        Get all pods under a namespace
        :param namespace:
        :return:
        """
        if not namespace:
            namespace = self.namespace
        return self.get('namespaces/' + namespace + '/pods')

    def get_logs(self, pod, namespace=None):
        """
        :param namespace:
        :param pod:
        :return:
        """
        if not namespace:
            namespace = self.namespace
        params = {
            'pretty': 'true',
            'tailLines': 100
        }
        return self.get('namespaces/' + namespace + '/pods/' + pod + '/log', return_json=False, params=params)

    @staticmethod
    def is_on_kubernetes():
        return 'KUBERNETES_SERVICE_HOST' in os.environ
