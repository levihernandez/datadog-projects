import pyodbc
import time
from datadog_checks.base import AgentCheck


class SQLServerRTTCheck(AgentCheck):
    def check(self, instance):
        # Extract the global custom metrics from the init_config
        metrics = self.get_global_config('global_custom_metrics')
        
        # Iterate over each global custom metric configuration
        for metric in metrics:
            query = metric['query']
            metric_name = metric['name']
            tags = metric.get('tags', [])

            connection_str = (f"DRIVER={instance.get('driver')};"
                              f"SERVER={instance.get('host')};"
                              f"PORT={instance.get('port')};"
                              f"DATABASE={instance.get('database')};"
                              f"UID={instance.get('username')};"
                              f"PWD={instance.get('password')}")
            
            try:
                start_time = time.time()  # Record start time

                # Use a context manager to ensure the connection is closed after use
                with pyodbc.connect(connection_str) as connection:
                    with connection.cursor() as cursor:
                        cursor.execute(query)
                        result = cursor.fetchone()

                end_time = time.time()  # Record end time

                duration_ms = (end_time - start_time) * 1000  # Calculate duration in milliseconds

                if result:
                    # Assuming result is a single value; adjust as needed for different result formats
                    value = result[0]
                    self.gauge(metric_name, value, tags=tags + instance.get('tags', []))
                else:
                    self.warning(f"No result from query: {query}")

                # Send the duration of the query execution to Datadog
                self.gauge(f"{metric_name}.duration_ms", duration_ms, tags=tags + instance.get('tags', []))
            except Exception as e:
                self.error(f"Error executing query '{query}': {e}")

    def get_global_config(self, key):
        # Load global config from the init_config section
        config = self.init_config or {}
        return config.get(key, [])
