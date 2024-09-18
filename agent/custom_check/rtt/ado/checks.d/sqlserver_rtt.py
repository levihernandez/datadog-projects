import time
import importlib
from datadog_checks.base import AgentCheck

class SQLServerRTTCheck(AgentCheck):
    def check(self, instance):
        # Load configuration from YAML from Datadog conf.d/sqlserver_rtt.d/conf.yaml
        connector_type = instance.get('connector')
        if connector_type not in ['odbc', 'adodbapi']:
            self.log.error("Connector type not configured properly. Use 'odbc' or 'adodbapi'.")
            return

        # Dynamically import the necessary module based on the configuration
        if connector_type == 'odbc':
            try:
                global pyodbc
                pyodbc = importlib.import_module('pyodbc')
                connector = pyodbc
            except ImportError:
                self.log.error("pyodbc module not found. Please install pyodbc.")
                return
        elif connector_type == 'adodbapi':
            try:
                global adodbapi
                adodbapi = importlib.import_module('adodbapi')
                connector = adodbapi
            except ImportError:
                self.log.error("adodbapi module not found. Please install adodbapi.")
                return

        # Extract global custom metrics from the init_config
        metrics = self.get_global_config('global_custom_metrics')
        
        # Iterate over each global custom metric configuration
        for metric in metrics:
            query = metric['query']
            metric_name = metric['name']
            tags = metric.get('tags', [])

            # Build the connection string
            connection_str = self._build_connection_string(instance, connector_type)

            try:
                
                start_time = time.time()  # Record start time
                status="failure"
                resultset="0"

                # Use a context manager to ensure the connection is closed after use
                try:
                    # Use a context manager to ensure the connection is closed after use
                    with connector.connect(connection_str) as connection:
                        with connection.cursor() as cursor:
                            cursor.execute(query)
                            result = cursor.fetchone()
                            
                            if result is not None:
                                status="success"
                                resultset="1"
                                print(status,"successful connection")
                                
                            else:
                                status="failure"
                                resultset="0"
                                print(status,"no connection")

                except Exception as e:
                    self.log.error(f"Database connection error: {e}")
                finally:
                    self.log.warning(f"connection execution is {status}")

                rs=resultset
                st=status
                end_time = time.time()  # Record end time
                duration_ms = (end_time - start_time) * 1000  # Calculate duration in milliseconds

                # Send the duration of the query execution to Datadog
                self.gauge(f"{metric_name}.duration_ms", duration_ms, tags=tags + instance.get('tags', [])+ ['status:'+st,'resultset:'+rs,'connector:'+connector_type])
            except Exception as e:
                self.log.error(f"Error executing query '{query}': {e}")

    def _build_connection_string(self, instance, connector_type):
        """
        Build the connection string based on the connector type.
        
        Args:
            instance (dict): The instance configuration.
            connector_type (str): The type of connector ('odbc' or 'adodbapi').

        Returns:
            str: The connection string.
        """
        password = self._get_password(instance)
        
        if connector_type == 'odbc':
            return (f"DRIVER={instance.get('driver')};"
                    f"SERVER={instance.get('host')};"
                    f"PORT={instance.get('port')};"
                    f"DATABASE={instance.get('database')};"
                    f"UID={instance.get('username')};"
                    f"PWD={password};"
                    f"Connection Timeout={instance.get('connection_timeout')};")  # Set connection timeout to 30 seconds
        elif connector_type == 'adodbapi':
            datasource = instance.get('host')+","+str(instance.get('port'))
            return (f"Provider={instance.get('adoprovider')};"
                    f"Data Source={datasource};"
                    f"Initial Catalog={instance.get('database')};"
                    f"User ID={instance.get('username')};"
                    f"Password={password};"
                    f"Connection Timeout={instance.get('connection_timeout')};")  # Set connection timeout to 30 seconds

    def _get_password(self, instance):
        # Handle the password, decrypt if necessary
        password = instance.get('password', '')
        vault_url = instance.get('vault_url','') # 'https://vault.example.com'
        vault_token = instance.get('vault_token','') # 'your-vault-token'
        if password.startswith('ENC[') and password.endswith(']'):
            password = self._decrypt_vault_password(password, vault_url, vault_token)
        return password

    def _decrypt_vault_password(self, encrypted_password, vault_url, vault_token):
        """
        Decrypts a password stored in HashiCorp Vault or other secret management services.

        Args:
            encrypted_password (str): Encrypted password with an 'ENC[' prefix and ']' suffix.

        Returns:
            str: Decrypted plaintext password.
        """
        # Remove the 'ENC[' and ']' markers from the encrypted password string
        vault_secret_id = encrypted_password[4:-1]

        # Example: Implement the logic to fetch and decrypt the password from Vault
        # Initialize the Vault client and fetch the secret (example code, replace with actual implementation)
        import hvac
        client = hvac.Client(url=vault_url, token=vault_token)

        try:
            secret = client.secrets.kv.read_secret_version(path=vault_secret_id)
            password = secret['data']['data']['password']
        except hvac.exceptions.InvalidRequest as e:
            self.log.error(f"Invalid request when accessing Vault: {e}")
            password = ''
        except hvac.exceptions.InvalidRequest as e:
            self.log.error(f"Vault request error: {e}")
            password = ''
        except Exception as e:
            self.log.error(f"Unexpected error: {e}")
            password = ''

        return password

    def get_global_config(self, key):
        # Load global config from the init_config section
        config = self.init_config or {}
        return config.get(key, [])
