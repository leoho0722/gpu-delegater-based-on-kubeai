from kubernetes import watch
from kubernetes.client import (
    V1Pod,
    V1PodList,
    V1PodStatus,
    V1ObjectMeta
)

from backend.k8s.api import corev1_api_list_namespaced_pod, get_pod_ip, watch_corev1_api_namespaced_pod
from backend.k8s.exception import KubernetesPodException
from backend.k8s.kubeai.exception import KubeAIOllamaModelPodException


def list_kubeai_ollama_model_pod(namespace: str = "default") -> V1PodList:
    """List all of KubeAI Ollama Model Pods in Kubernetes Cluster

    Args:
        namespace (`str`, optional): Kubernetes Namespace. Defaults to 'default'.

    Returns:
        kubeai_ollama_model_pods (`V1PodList`): All of KubeAI Ollama Model Pods in Kubernetes Cluster

    Raises:
        KubeAIOllamaModelPodException: If failed to list all of KubeAI Ollama Model Pods in Kubernetes Cluster
    """

    try:
        pods = corev1_api_list_namespaced_pod(namespace=namespace)
        kubeai_ollama_model_pods: V1PodList = list(filter(
            lambda pod: pod.metadata.labels.get(
                "app.kubernetes.io/managed-by"
            ) == "kubeai",
            filter(
                lambda pod: pod.metadata.labels.get(
                    "app.kubernetes.io/name"
                ) == "ollama",
                pods.items
            )
        ))

        return kubeai_ollama_model_pods
    except KubernetesPodException as e:
        print(
            f"Failed to list all of KubeAI Ollama Model Pods: {e.error}\nKubernetes REST ApiException:{e.kwargs}"
        )
        raise KubeAIOllamaModelPodException(e.error, e.kwargs)


def watch_kubeai_ollama_model_pod(model_name: str, namespace: str = "default") -> V1Pod:
    """Watch KubeAI Ollama Model Pod in Kubernetes Cluster

    Args:
        model_name (`str`): The name of the model to watch
        namespace (`str`, optional): Kubernetes Namespace. Defaults to 'default'.

    Returns:
        kubeai_ollama_model_pod (`V1Pod`): KubeAI Ollama Model Pod in Kubernetes Cluster
    """

    def _filter_conditions(pod: V1Pod) -> bool:
        """Filter KubeAI Ollama Model Pod using conditions

        Args:
            pod (`V1Pod`): Pod

        Returns:
            bool: True if the Pod is KubeAI Ollama Model Pod, False otherwise
        """

        pod_metadata: V1ObjectMeta = pod.metadata
        pod_metadata_labels: dict[str, str] = pod_metadata.labels
        pod_status: V1PodStatus = pod.status

        managed_by = pod_metadata_labels.get("app.kubernetes.io/managed-by")
        name = pod_metadata_labels.get("app.kubernetes.io/name")
        model = pod_metadata_labels.get("model")

        print(
            f"Managed By: {managed_by}, Name: {name}, Model: {model}, Pod Status: {pod_status.phase}"
        )

        managed_by_condition = (managed_by == "kubeai")
        name_condition = (name == "ollama")
        model_condition = (model == model_name)
        pod_status_condition = (pod_status.phase == "Running")

        return managed_by_condition and name_condition and model_condition and pod_status_condition

    try:
        watch_result = watch_corev1_api_namespaced_pod(namespace=namespace)
        w: watch.Watch = watch_result[0]
        stream = watch_result[1]
        for event in stream:
            pod: V1Pod = event["object"]
            if _filter_conditions(pod):
                w.stop()

                return pod
    except KubernetesPodException as e:
        print(
            f"Failed to watch KubeAI Ollama Model Pod: {e.error}\nKubernetes REST ApiException:{e.kwargs}"
        )
        raise KubeAIOllamaModelPodException(e.error, e.kwargs)


def list_kubeai_ollama_model_filtered_pod(model: str, namespace: str = "default"):
    """List filtered KubeAI Ollama Model Pod in Kubernetes Cluster

    Args:
        model (`str`): The name of the model to filter by
        namespace (`str`, optional): Kubernetes Namespace. Defaults to 'default'.

    Returns:
        kubeai_ollama_model_filtered_pod (`V1Pod`): Filtered KubeAI Ollama Model Pod in Kubernetes Cluster
    """

    try:
        kubeai_ollama_model_pods = list_kubeai_ollama_model_pod(namespace)
        kubeai_ollama_model_filtered_pod: V1Pod = list(filter(
            lambda pod: pod.metadata.labels.get("model") == model,
            kubeai_ollama_model_pods
        ))[0]

        return kubeai_ollama_model_filtered_pod
    except KubeAIOllamaModelPodException as e:
        print(
            f"Failed to list filtered KubeAI Ollama Model Pod: {e.error}\nKubernetes REST ApiException:{e.kwargs}"
        )
