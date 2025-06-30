from kubernetes import client, config

def scale_k8s_deployment(namespace, deployment, replicas):
    """Scale a Kubernetes deployment."""
    config.load_kube_config()
    api = client.AppsV1Api()
    body = {"spec": {"replicas": replicas}}
    api.patch_namespaced_deployment_scale(
        name=deployment,
        namespace=namespace,
        body=body
    )
    return f"Scaled {deployment} in {namespace} to {replicas} replicas."