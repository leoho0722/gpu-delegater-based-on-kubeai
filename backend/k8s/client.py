from kubernetes import config, dynamic
from kubernetes.client import api_client


def get_k8s_api_client():
    """Get Kubernetes API client

    Returns:
        k8s_api_client (`api_client.ApiClient`): Kubernetes API client
    """

    k8s_api_client = api_client.ApiClient(config.load_kube_config())

    return k8s_api_client


def get_k8s_dynamic_client():
    """Get Kubernetes Dynamic client

    Returns:
        k8s_dynamic_client (`dynamic.DynamicClient`): Kubernetes Dynamic client
    """

    k8s_api_client = get_k8s_api_client()

    k8s_dynamic_client = dynamic.DynamicClient(k8s_api_client)

    return k8s_dynamic_client
