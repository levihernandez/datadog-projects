# Auto Instrumentation in Datadog

The following example enables several tools at the Datadog Agent YAML values via the Operator (recommended deployment).
There are commented areas if not using the (as of September 2024) Beta APM Automatic Instrumentation, see the scenarios below: 

* Current method: Autodiscovery is performed through labels, annotations. Files to modify are Helm/Operator YAML, Application Deployment YAML, and Dockerfile.
   * Agent: install the datadog agent and enable APM, and other tools (NPM, Processes, Security, etc)
      * see `datadog/kubernetes/datadog-values-operator.yaml`
   * App: configure labels in the application Deployment YAML to categorize your services by env, service, version
      * see `java/kubernetes/app-manifest.yaml` labels, annotations, & env
   * App: configure your Dockerfile to include the libraries (Java, .NET) and enable tracing of your applications. See example in Maven and .NET 
      * see `java/Dockerfile` for Datadog java library requirements

* Beta method: APM Instrumentation (Agent) OR Single Step Instrumentation (App Deployment config)
   * Agent: enable APM Instrumentation. This performs autodiscovery across all apps running in your cluster. No additional configuration is required for Dockerfile
   * App: if the Datadog agent is already running (no APM Beta Instrumentation was set) you can opt to configure your K8s Deployments by the app service you deploy and enabling "Single Step Instrumentation". No additional configurations are required for Dockerfile
   * This is the approach I have taken for the current approach


With APM Instrumentation, I activated it at the Datadog agent to trace all apps:

![](apm-auto-instrumentation.png)


* Create the database in Postgres or CockroachDB (must have the local [cockroach binary](https://www.cockroachlabs.com/docs/releases/#production-releases))

```bash
cockroach sql --insecure --host=192.168.86.235
```

```sql
-- Create the database
CREATE DATABASE faztpay;

-- Switch to the new database (PostgreSQL)
\c faztpay;

-- Create the accounts table
CREATE TABLE accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(255) NOT NULL UNIQUE,
    balance DECIMAL(10, 2) NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);
```

## Insert Sample Data to DB
To generate the SQL insert statements and save them to a file for loading into CockroachDB, you can modify the Python script as follows:

### Python Script to Generate SQL Inserts


Script is in the seed directory. All is needed is to execute as `python generate_data.py`


### Explanation:

1. **File Handling**: The script opens a file called `insert_records.sql` in write mode.
2. **Transaction Control**: It starts with a `BEGIN;` statement and ends with a `COMMIT;` statement for better performance.
3. **Insert Statements**: Each generated record is formatted as an SQL insert statement and written to the file.
4. **Completion Message**: The script informs you when the file has been created.

### Load SQL File into CockroachDB

Once you have your `insert_records.sql` file, you can load it into CockroachDB using the `cockroach sql` command-line tool. Here’s how to do that:

1. **Start CockroachDB** (if it’s not already running):
   ```bash
   cockroach start --insecure --host=192.168.86.235
   ```

2. **Open a SQL shell**:
   ```bash
   cockroach sql --insecure --host=192.168.86.235 --database=faztpay
   ```

3. **Run the SQL file**:
   Inside the SQL shell, you can execute the SQL file using:
   ```sql
   \i 'insert_records.sql';
   ```



## Build/Execute the application


* Run the application locally

```bash
# Skip tests
mvn clean package -DskipTests

# Or run a clean install
mvn clean install

# Test the app before running it
mvn test

# Run app
mvn spring-boot:run
```

Here are the `curl` commands you can use to submit payments and withdraw money using your updated API endpoints.

## Test the application (regardless of deployment method: local, docker, or kubernetes)

### Pull data from CockroachDB or Postgres to test values in the following cURL calls:

```bash
cockroach sql --insecure --host=192.168.86.235 --database=faztpay -e "SELECT id, username FROM accounts LIMIT 10;"
```

Use the returned values to test the APIs below:

### 1. Submit a Payment

To submit a payment, use the following `curl` command. Replace `<accountId>`, `<userId>`, and `<amount>` with the appropriate values.

```bash
curl -X POST "http://<your-server>/api/payments/submit" \
     -d "accountId=<accountId>" \
     -d "userId=<userId>" \
     -d "amount=<amount>" \
     -H "Content-Type: application/x-www-form-urlencoded"
```

### Example:

```bash
curl -X POST "http://localhost:8080/api/payments/submit" \
     -d "accountId=0589054f-c917-467e-a0cb-58b041f5d98a" \
     -d "username=user_1727134887603" \
     -d "amount=150.0" \
     -H "Content-Type: application/x-www-form-urlencoded"

     
curl -X POST "http://192.168.86.234/api/payments/submit" \
     -d "accountId=0589054f-c917-467e-a0cb-58b041f5d98a" \
     -d "username=user_1727134887603" \
     -d "amount=150.0" \
     -H "Content-Type: application/x-www-form-urlencoded"

```

### 2. Withdraw Money

To withdraw money, use the following `curl` command. Again, replace `<accountId>`, `<userId>`, and `<amount>` with the appropriate values.

```bash
curl -X POST "http://<your-server>/api/payments/withdraw" \
     -d "accountId=<accountId>" \
     -d "username=<userId>" \
     -d "amount=<amount>" \
     -H "Content-Type: application/x-www-form-urlencoded"
```

### Example:

```bash
curl -X POST "http://localhost:8080/api/payments/withdraw" \
     -d "accountId=0589054f-c917-467e-a0cb-58b041f5d98a" \
     -d "username=user_1727134887603" \
     -d "amount=30.0" \
     -H "Content-Type: application/x-www-form-urlencoded"
```

### Notes

- Replace `http://localhost:8080` with your server's address and port if it is different.
- Make sure the `accountId` you are using is valid and exists in the database, and that the `userId` corresponds to that account.




* Run the app with Docker/Docker Compose

```bash
# Build the docker image
docker build -t <your-dockerhub-username>/payment-api:latest .

# Push the image to docker hub registry
docker login
docker push <your-dockerhub-username>/payment-api:latest

# Docker Compose
# Start app
docker compose up --build

# Stop app
docker-compose down
```


## Git

To create a new Git remote repository via the command line, you typically need to follow these steps. I'll cover the common platforms like GitHub and GitLab, but the steps are quite similar across various services.

### For GitHub

1. **Log into GitHub**: Use your web browser to log into your GitHub account.

2. **Create a new repository on GitHub**:
   - Navigate to your GitHub homepage.
   - Click on the "+" icon in the top-right corner and select "New repository."
   - Fill in the repository details (name, description, visibility, etc.) and click "Create repository."

3. **Initialize a local repository (if you haven't already)**:
   ```bash
   mkdir my-project
   cd my-project
   git init
   ```

4. **Add a remote to your local repository**:
   ```bash
   git remote add origin https://github.com/username/my-project.git
   ```
   Replace `username` with your GitHub username and `my-project` with your repository name.

5. **Push your local changes**:
   ```bash
   git add .
   git commit -m "Initial commit"
   git push -u origin main
   ```

### For GitLab

1. **Log into GitLab**: Use your web browser to log into your GitLab account.

2. **Create a new project**:
   - Click on "New Project."
   - Fill in the project details and click "Create project."

3. **Initialize a local repository (if you haven't already)**:
   ```bash
   mkdir my-project
   cd my-project
   git init
   ```

4. **Add a remote to your local repository**:
   ```bash
   git remote add origin https://gitlab.com/username/my-project.git
   ```

5. **Push your local changes**:
   ```bash
   git add .
   git commit -m "Initial commit"
   git push -u origin master
   ```

### Additional Notes

- Make sure to replace URLs and placeholders with your actual username and repository name.
- If you are using SSH, the remote URL would look like `git@github.com:username/my-project.git` for GitHub, or `git@gitlab.com:username/my-project.git` for GitLab. In this case, ensure you have your SSH keys set up correctly.

* Kubernetes: set secrets yaml to handle encoding of DB url, passwords

```bash
  # Connection to CockroachDB via JDBC
  echo -n 'jdbc:postgresql://192.168.86.235:26257/faztpay?application_name=app-accounts-java&connect_timeout=15&sslmode=disable' | base64
  # Connection fo Postgres
  echo -n 'jdbc:postgresql://192.168.86.235:26257/faztpay'| base64
  # Encode username
  echo -n 'root' | base64
  # Encode password
  echo -n 'MySecretPass' | base64
```

Deployment can be handled by ArgoCD, see argo Manifest to deploy the app

```yaml
project: default
source:
  repoURL: 'http://192.168.86.53:3000/jpnoles/dd-apm-examples.git'
  path: java/kubernetes
  targetRevision: HEAD
destination:
  server: 'https://kubernetes.default.svc'
  namespace: accounts-app
syncPolicy:
  automated: {}
```

