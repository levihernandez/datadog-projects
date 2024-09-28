# CockroachDB User Group (CRUG) & Datadog Monitoring

## CockroachDB & Datadog with ArgoCD Deployment
For the current example, there are two separate K8s clusters.

* CRDB K8s cluster:
  * Create namespaces: cockroachdb, datadog, argocd
  ```bash
  kubectl apply -f https://raw.githubusercontent.com/levihernandez/datadog-projects/refs/heads/main/crug/create-namespaces.yaml
  ```
  ### Install ArgoCD
  ```bash
  # Install ArgoCD via Manifest
  kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

  # Change the ClusterIP to a LoadBalancer type so ArgoCD can be available on port 443
  kubectl patch svc argocd-server -n argocd -p '{"spec": {"type": "LoadBalancer"}}'

  # IP info for the public port can be obtain with: 
  kubectl get svc -n argocd
  
  # Once installed, get the ArgoCD password with:
  kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
  ```
  ### Install the Datadog Agent

  ### Install CockroachDB
  * Access the ArgoCD url `https://domain/` & use the password obtained from Kubernetes namespace `argocd`
  * In ArgoCD UI go to: Applications > New App 
   * Application Name: `cockroachdb-cluster`
   * Project Name: `default`
   * SYNC POLICY: `Automatic`
   * SOURCE > Repository URL: `https://github.com/levihernandez/datadog-projects.git`
   * Revision: `HEAD`
   * Path: `crug/cockroachdb/k8s`
   * DESTINATION > Cluster URL: `https://kubernetes.default.svc`
   * Namespace: `cockroachdb`
   * Click CREATE button to deploy CockroachDB in your cluster






