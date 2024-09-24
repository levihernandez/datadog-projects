# Deploy Datadog

```bash
# Install the datadog operator
helm repo add datadog https://helm.datadoghq.com
helm install datadog-operator datadog/datadog-operator

# Apply configs for the Datadog agent
kubectl apply -f datadog-secrets.yaml
kubectl apply -f datadog-values-operator.yaml
```

