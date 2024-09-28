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
  While we can directly install the Datadog Agent via `kubectl`, for the purpose of visualization, we will install it with ArgoCD.

  We will also enable the following tools within the Datadog Agent to gain insights into the CockroachDB cluster:
  * NPM - Network Performance Monitor, to understand the traffic between CRDB nodes & correlate to the application traces
  * APM - Application Performance Monitor, to generate traces/spans with correlation to other tools
  * Metrics - Default collection of metrics from the host/cluster
  * Logs - To generate dashboards out of the SQL payload
  * Containers - Collect metrics from containers
  * Live Processes - Live preview of processes running inside the containers
  * USM - Universal Service Monitor, to preview the number of services (not traced) in the Kubernetes clusters (such as ArgoCD, Istio, etc)

  #### Setup Datadog in K8s & ArgoCD
  * Download the `datadog-secret.yaml` and add the `base64` API key in the Kubernetes cluster
  ```bash
  # Get the Datadog Helm repo
  helm repo add datadog https://helm.datadoghq.com
  
  # Install the Datadog Operator
  helm install datadog-operator datadog/datadog-operator
  
  # Download Datadog Secrets
  curl -L -o datadog-secret.yaml https://raw.githubusercontent.com/levihernandez/datadog-projects/refs/heads/main/crug/datadog/k8s/datadog-secret.yaml

  # Encode the API key
  echo "apikey" | base64

  # replace the   api-key: <base 64 encoded api key> with the encoded key
  # apply the secret key for Datadog
  kubectl apply -f datadog-secret.yaml -n datadog
  ```
  
  #### Setup in ArgoCD

  * Create Datadog application in the ArgoCD UI
   * Application Name: `datadog-agent`
   * Project Name: `default`
   * SYNC POLICY: `Automatic`
   * SOURCE > Repository URL: `https://github.com/levihernandez/datadog-projects.git`
   * Revision: `HEAD`
   * Path: `crug/datadog/k8s/crdb/operator/`
   * DESTINATION > Cluster URL: `https://kubernetes.default.svc`
   * Namespace: `datadog`
   * Click CREATE button to deploy Datadog in your cluster


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






