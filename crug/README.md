# CockroachDB User Group (CRUG) & Datadog Monitoring

## Database Deployment: CockroachDB & Datadog with ArgoCD

* CRDB K8s cluster:
  * Create namespaces: cockroachdb, datadog, argocd
  ```bash
  kubectl apply -f https://raw.githubusercontent.com/levihernandez/datadog-projects/refs/heads/main/crug/create-db-namespaces.yaml
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
  kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d ; echo ""
  ```
  ### Install the Datadog Agent
  While we can directly install the Datadog Agent via `kubectl`, for the purpose of visualization, we will install it with ArgoCD.

  We will also enable the following tools within the Datadog Agent to gain insights into the CockroachDB cluster:
  * NPM - Network Performance Monitor, to understand the traffic between CRDB nodes & correlate to the application traces
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
  
  #### Deploy the Datadog Agent with ArgoCD

  * In ArgoCD UI go to: **Applications > New App** 
   * **Application Name:** `datadog-agent`
   * **Project Name:** `default`
   * **SYNC POLICY:** `Automatic`
   * **SOURCE > Repository URL:** `https://helm.datadoghq.com`
   * **Chart:** `datadog`
   * Choose the dropdown and set the version: **3.73.0**
   * **DESTINATION > Cluster URL:** `https://kubernetes.default.svc`
   * **Namespace:** `datadog`
   * **Helm > VALUE FILES:** `values.yaml`
   * copy the contents of this file
   ```bash
   https://raw.githubusercontent.com/levihernandez/datadog-projects/refs/heads/main/crug/datadog/k8s/crdb/helm/datadog-values.yaml
   ```
   * paste the contens in **VALUES**
   * Click **CREATE** button to deploy Datadog in your cluster


  ### Install CockroachDB

  #### Deploy CockroachDB with ArgoCD
  
  * Access the ArgoCD url `https://domain/` & use the password obtained from Kubernetes namespace `argocd`
  * In ArgoCD UI go to: **Applications > New App** 
   * **Application Name:** `cockroachdb-cluster`
   * **Project Name:** `default`
   * **SYNC POLICY:** `Automatic`
   * **SOURCE > Repository URL:** `https://github.com/levihernandez/datadog-projects.git`
   * **Revision:** `HEAD`
   * **Path:** `crug/cockroachdb/k8s`
   * **DESTINATION** > Cluster URL: `https://kubernetes.default.svc`
   * **Namespace:** `cockroachdb`
   * Click **CREATE** button to deploy CockroachDB in your cluster



## Application Deployment: MovR app & Datadog with ArgoCD

* MovR App K8s cluster:
  * Create namespaces:  datadog, argocd, movr, faztpay
  ```bash
  kubectl apply -f https://raw.githubusercontent.com/levihernandez/datadog-projects/refs/heads/main/crug/create-app-namespaces.yaml
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
  kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d; echo ""
  ```
  

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


  #### Deploy the Datadog Agent with ArgoCD
  
  We will also enable the following tools within the Datadog Agent to gain insights into the CockroachDB cluster:
    
  * NPM - Network Performance Monitor, to understand the traffic between CRDB nodes & correlate to the application traces
  * APM - Application Performance Monitor, to generate auto discovery of traces/spans with correlation to other tools
  * Metrics - Default collection of metrics from the host/cluster
  * Logs - To generate dashboards out of the SQL payload
  * Containers - Collect metrics from containers
  * Live Processes - Live preview of processes running inside the containers
  * USM - Universal Service Monitor, to preview the number of services (not traced) in the Kubernetes clusters (such as ArgoCD, Istio, etc)



  * In ArgoCD UI, create a Datadog application, go to: **Applications > New App** 
   * **Application Name:** `datadog-agent`
   * **Project Name:** `default`
   * **SYNC POLICY:** `Automatic`
   * **SOURCE > Repository URL:** `https://helm.datadoghq.com`
   * **Chart:** `datadog`
   * Choose the dropdown and set the version: **3.73.0**
   * **DESTINATION > Cluster URL:** `https://kubernetes.default.svc`
   * **Namespace:** `datadog`
   * **Helm > VALUE FILES:** `values.yaml`
   * copy the contents of this file 
   ```bash
   https://raw.githubusercontent.com/levihernandez/datadog-projects/refs/heads/main/crug/datadog/k8s/crdb/helm/datadog-values.yaml
   ```
   * paste the contens in **VALUES**
   * Click **CREATE** button to deploy Datadog in your cluster

  #### Deploy the MovR App with ArgoCD
  
  * Create secrets to connect to the database
  ```bash
  # Download MovR app secrets YAML and configure the DB connection
  curl -L -o movr-app-secret.yaml https://github.com/levihernandez/datadog-projects/raw/refs/heads/main/crug/applications/MovR/app-secret.yaml

  # Encode the API key
  echo -n "postgres://root:''@192.168.86.237:26257/movr?sslmode=disable" | base64

  # replace the   DB_URI: <db url base64 encoding> with the encoded key
  # apply the secret key for Datadog
  kubectl apply -f movr-app-secret.yaml -n movr
  ```
  * Update the secrets yaml to update the database credentials & url 
  * Access the ArgoCD url `https://domain/` & use the password obtained from Kubernetes namespace `argocd`
  * In ArgoCD UI go to: **Applications > New App**
   * **Application Name:** `movr-flask-app`
   * **Project Name:** `default`
   * **SYNC POLICY:** `Automatic`
   * **SOURCE > Repository URL:** `https://github.com/levihernandez/datadog-projects.git`
   * **Revision:** `HEAD`
   * **Path:** `crug/applications/MovR/k8s`
   * **DESTINATION** > Cluster URL: `https://kubernetes.default.svc`
   * **Namespace:** `movr`
   * Click **CREATE** button to deploy MovR Flask app in your cluster
   * 
  #### Deploy the FaztPay App with ArgoCD
  * Create secrets to connect to the database
  ```bash
  # Download FaztPay app secrets YAML and configure the DB connection
  curl -L -o faztpay-app-secret.yaml https://github.com/levihernandez/datadog-projects/raw/refs/heads/main/crug/applications/FaztPay/app-secret.yaml

  # Encode the SPRING_DATASOURCE_URL connection
  echo -n "jdbc:postgresql://root@192.168.86.237:26257/faztpay?application_name=payment-api&connect_timeout=15&sslmode=disable" | base64
  # Encode the SPRING_DATASOURCE_USERNAME
  echo "username" | base64
  # Encode the SPRING_DATASOURCE_PASSWORD
  echo "password" | base64

  # replace the   SPRING_DATASOURCE_URL: <db url base64 encoding>, SPRING_DATASOURCE_USERNAME: <base64 encoded db username>, SPRING_DATASOURCE_PASSWORD: <base64 encoded db password> with the encoded key
  # apply the secret key for Datadog
  kubectl apply -f faztpay-app-secret.yaml -n faztpay
  ```
  * Update the secrets yaml to update the database credentials & url 
  * Access the ArgoCD url `https://domain/` & use the password obtained from Kubernetes namespace `argocd`
  * In ArgoCD UI go to: **Applications > New App** 
   * **Application Name:** `faztpay-java-app`
   * **Project Name:** `default`
   * **SYNC POLICY:** `Automatic`
   * **SOURCE > Repository URL:** `https://github.com/levihernandez/datadog-projects.git`
   * **Revision:** `HEAD`
   * **Path:** `crug/applications/FaztPay/k8s`
   * **DESTINATION** > Cluster URL: `https://kubernetes.default.svc`
   * **Namespace:** `faztpay`
   * Click **CREATE** button to deploy Payments Java app in your cluster
