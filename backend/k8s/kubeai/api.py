import re
from typing import Any, Dict, List

from kubernetes import dynamic
from kubernetes.client import (
    CustomObjectsApi,
    V1Pod,
    V1PodList
)
from kubernetes.client.rest import ApiException

from k8s.api import corev1_api_list_namespaced_pod, corev1_api_read_namespaced_pod_log
from k8s.client import get_k8s_api_client, get_k8s_dynamic_client
from k8s.exception import KubernetesPodException
from k8s.kubeai.exception import KubeAIModelException


def create_kubeai_model_custom_resource(model_cr_yaml: Dict[str, Any]):
    """Create KubeAI Model Custom Resource to Kubernetes Cluster

    Args:
        model_cr_yaml (`Dict[str, Any]`): KubeAI Model Custom Resource YAML

    Raises:
        KubeAIModelException: If failed to create KubeAI Model Custom Resource
    """

    dynamic_client = get_k8s_dynamic_client()

    kubeai_models_client = dynamic_client.resources.get(
        api_version='kubeai.org/v1',
        kind='Model'
    )
    try:
        kubeai_models_client.create(body=model_cr_yaml)
    except ApiException as e:
        print(
            f"Failed to create KubeAI Model Custom Resource: {e}"
        )
        raise KubeAIModelException(e.reason, e.body)


def list_kubeai_model_custom_resource(namespace: str = "default") -> List[Dict[str, Any]]:
    """List all of KubeAI Model Custom Resources in Kubernetes Cluster

    Args:
        namespace (`str`, optional): Namespace. Defaults to 'default'.

    Returns:
        model_kind_items (`List[Dict[str, Any]]`): All of KubeAI Model Custom Resources in Kubernetes Cluster

    Raises:
        KubeAIModelException: If failed to list KubeAI Model Custom Resource
    """

    dynamic_client = get_k8s_dynamic_client()

    # Get model resource of KubeAI
    model_resource: dynamic.Resource = dynamic_client.resources.get(
        api_version='kubeai.org/v1',
        kind='Model'
    )

    # List model kind of KubeAI
    custom_obejct_api = CustomObjectsApi(api_client=dynamic_client.client)

    try:
        model_kind = custom_obejct_api.list_namespaced_custom_object(
            group=model_resource.group,
            version=model_resource.api_version,
            namespace=namespace,
            plural=model_resource.name
        )

        model_kind_items = model_kind["items"]

        return model_kind_items
    except ApiException as e:
        print(
            f"Failed to list KubeAI Model Custom Resource: {e}"
        )
        raise KubeAIModelException(e.reason, e.body)


def patch_kubeai_model_custom_resource(
    model_cr_yaml: Dict[str, Any],
    patch_body: Dict[str, Any] = {}
):
    """Patch KubeAI Model Custom Resource in Kubernetes Cluster

    Args:
        model_cr_yaml (`Dict[str, Any]`): KubeAI Model Custom Resource YAML
        patch_body (`Dict[str, Any]`, optional): Patch body. Defaults to {}.

    Returns:
        patched_model_kind: Patched KubeAI Model Custom Resource

    Raises:
        KubeAIModelException: If failed to patch KubeAI Model Custom Resource
    """

    api_client = get_k8s_api_client()
    custom_obejct_api = CustomObjectsApi(api_client=api_client)

    try:
        group = str(model_cr_yaml["apiVersion"]).split('/')[0]
        version = str(model_cr_yaml["apiVersion"]).split('/')[1]
        namespace = model_cr_yaml["metadata"]["namespace"]
        kind: str = model_cr_yaml["kind"]
        plural = f"{kind.lower()}s"

        patched_model_kind = custom_obejct_api.patch_namespaced_custom_object(
            group=group,
            version=version,
            namespace=namespace,
            plural=plural,
            name=model_cr_yaml["metadata"]["name"],
            body=patch_body
        )

        return patched_model_kind
    except ApiException as e:
        print(
            f"Failed to patch KubeAI Model Custom Resource: {e}"
        )
        raise KubeAIModelException(e.reason, e.body)


def apply_kubeai_model_custom_resource(model_cr_yaml: Dict[str, Any]):
    """Apply KubeAI Model Custom Resource to Kubernetes Cluster

    Args:
        model_cr_yaml (`Dict[str, Any]`): KubeAI Model Custom Resource YAML

    Raises:
        KubeAIModelException: If failed to apply KubeAI Model Custom Resource to Kubernetes Cluster
    """

    try:
        # Check if the model already exists
        kubeai_models = list_kubeai_model_custom_resource()

        # Apply the model to the Kubernetes cluster if it does not exist
        if len(kubeai_models) == 0:
            create_kubeai_model_custom_resource(model_cr_yaml)
        else:
            # Patch the model if it already exists in the Kubernetes cluster
            for kubeai_model in kubeai_models:
                if kubeai_model["metadata"]["name"] == model_cr_yaml["metadata"]["name"]:
                    patch_kubeai_model_custom_resource(
                        kubeai_model, model_cr_yaml
                    )
                    break
            else:
                # Create the model if it does not exist in the Kubernetes cluster
                create_kubeai_model_custom_resource(model_cr_yaml)
    except KubeAIModelException as e:
        print(
            f"Failed to apply KubeAI Model Custom Resource: {e.error}\nKubernetes REST ApiException:{e.kwargs}"
        )
        raise e


def list_kubeai_pod(namespace: str = "default") -> V1PodList:
    """List all of KubeAI Pods in Kubernetes Cluster

    Args:
        namespace (`str`, optional): Namespace. Defaults to 'default'.

    Returns:
        kubeai_pods (`V1PodList`): All of KubeAI Pods in Kubernetes Cluster

    Raises:
        KubernetesPodException: If failed to list all of KubeAI Pods in Kubernetes Cluster
    """

    try:
        pods = corev1_api_list_namespaced_pod(namespace=namespace)
        kubeai_pods: V1PodList = list(filter(
            lambda pod: pod.metadata.labels.get(
                "app.kubernetes.io/name"
            ) == "kubeai",
            pods.items
        ))

        return kubeai_pods
    except KubernetesPodException as e:
        print(
            f"Failed to list KubeAI Pods: {e.error}\nKubernetes REST ApiException:{e.kwargs}"
        )
        raise e


def log_kubeai_pod(namespace: str = "default"):
    """Log KubeAI Pod in Kubernetes Cluster

    Args:
        namespace (`str`, optional): Namespace. Defaults to 'default'.

    Raises:
        KubernetesPodException: If failed to output KubeAI Pod Log
    """

    try:
        kubeai_pod: V1Pod = list_kubeai_pod(namespace=namespace)[0]
        kubeai_pod_log = corev1_api_read_namespaced_pod_log(kubeai_pod)
        print(
            f"KubeAI Pod log:\n{kubeai_pod_log}"
        )
    except KubernetesPodException as e:
        print(
            f"Failed to output KubeAI Pod Log: {e.error}\nKubernetes REST ApiException:{e.kwargs}"
        )
        raise e


def parse_kubeai_pod_log(
    log_data: str,
    pattern: str | re.Pattern[str]
):
    """Parse logs of KubeAI Pod in Kubernetes Cluster using specified pattern

    Args:
        log_data (str): Logs of KubeAI Pod
        pattern (str | re.Pattern[str]): Pattern to parse logs

    Returns:
        results (`bool`): If the pattern is found in the logs
    """

    matches = re.finditer(pattern, log_data, re.MULTILINE)

    last_match = None
    for match in matches:
        last_match = match  # 每次迭代更新，確保抓到最後一次匹配的資料

    return True if last_match else False
