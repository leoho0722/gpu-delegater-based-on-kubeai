from typing import Any, Generator, Tuple

from kubernetes import watch
from kubernetes.client import (
    CoreV1Api,
    V1Pod,
    V1PodList,
    V1PodStatus
)
from kubernetes.client.rest import ApiException

from k8s.client import get_k8s_api_client
from k8s.exception import KubernetesPodError


def corev1_api_list_namespaced_pod(namespace: str = 'default') -> V1PodList:
    """List all of Pods in Kubernetes Cluster

    Args:
        namespace (str, optional): Namespace. Defaults to 'default'.

    Returns:
        pods (`V1PodList`): All of Pods in Kubernetes Cluster

    Raises:
        KubernetesPodException: If failed to list all of Pods in the namespace
    """

    try:
        api_client = get_k8s_api_client()

        corev1_api = CoreV1Api(api_client=api_client)
        pods: V1PodList = corev1_api.list_namespaced_pod(
            namespace=namespace,
            async_req=True,
            pretty="true"
        ).get()

        return pods
    except ApiException as e:
        print(
            f"Failed to list all of Pods in the {namespace} namespace: {e}"
        )
        raise KubernetesPodError(e.reason, e.body)


def corev1_api_read_namespaced_pod_log(pod: V1Pod):
    """Read logs of Pod in Kubernetes Cluster

    Args:
        pod (`V1Pod`): Pod

    Returns:
        pod_log (`str`): Logs of Pod

    Raises:
        KubernetesPodException: If failed to read logs of Pod in the namespace
    """

    try:
        api_client = get_k8s_api_client()

        corev1_api = CoreV1Api(api_client=api_client)
        pod_log = corev1_api.read_namespaced_pod_log(
            name=pod.metadata.name,
            namespace=pod.metadata.namespace,
            pretty="true",
            async_req=True
        ).get()

        return pod_log
    except ApiException as e:
        print(
            f"Failed to read logs of Pod {pod.metadata.name} in {pod.metadata.namespace}: {e}"
        )
        raise KubernetesPodError(e.reason, e.body)


def watch_corev1_api_namespaced_pod(namespace: str = 'default') -> Tuple[watch.Watch, Generator[Any | dict | str, Any, None]]:
    """Watch Pod in Kubernetes Cluster

    Args:
        namespace (`str`, optional): Namespace. Defaults to 'default'.

    Returns:
        w (`watch.Watch`): Watch
        w.stream (`Generator[Any | dict | str, Any, None]`): Watch stream of Pod in the namespace

    Raises:
        KubernetesPodException: If failed to watch Pod in the namespace
    """

    try:
        api_client = get_k8s_api_client()
        corev1_api = CoreV1Api(api_client=api_client)

        w = watch.Watch()

        return w, w.stream(
            func=corev1_api.list_namespaced_pod,
            namespace=namespace,
            timeout_seconds=600
        )
    except ApiException as e:
        print(
            f"Failed to watch Pod in the {namespace} namespace: {e}"
        )
        raise KubernetesPodError(e.reason, e.body)


def get_pod_ip(pod: V1Pod) -> str:
    """Get Pod allocated IP in Kubernetes Cluster

    Args:
        pod (`V1Pod`): Kubernetes Pod

    Returns:
        pod_allocated_ip (`str`): Pod allocated IP
    """

    pod_status: V1PodStatus = pod.status
    pod_allocated_ip = pod_status.pod_ip

    return pod_allocated_ip
