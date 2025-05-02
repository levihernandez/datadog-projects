#!/usr/bin/env python3

from typing import Any, Dict, List, Optional
from datadog_checks.base import AgentCheck, ConfigurationError
from datadog_checks.base.utils.db import QueryManager
import psycopg2
from contextlib import contextmanager

class PostgresQueryCheck(AgentCheck):
    __NAMESPACE__ = 'custom.postgres.query'

    def __init__(self, name, init_config, instances):
        super().__init__(name, init_config, instances)
        self.query_manager = QueryManager(self, self.execute_query_raw, queries=[], tags=[])

    def check(self, instance):
        # Extract configuration
        host = instance.get('host', 'localhost')
        port = instance.get('port', 5432)
        user = instance.get('username')
        password = instance.get('password')
        dbname = instance.get('dbname')
        tags = instance.get('tags', [])
        queries = instance.get('queries', [])
        min_collection_interval = instance.get('min_collection_interval', 60)  # Default to 60 seconds

        # Set the check interval
        self.instance_check_interval = min_collection_interval

        if not all([user, password, dbname]):
            raise ConfigurationError('Missing required PostgreSQL connection details')

        # Process each query
        for query in queries:
            query_tags = tags + [
                f'db:{dbname}',
                f'host:{host}',
                f'port:{port}'
            ]
            
            # Add custom tags from query config if present
            if 'tags' in query:
                query_tags.extend(query['tags'])

            try:
                self.log.debug(f"Connection details - Host: {host}, Port: {port}, Database: {dbname}, User: {user}")
                self.log.debug(f"Attempting to connect to database {dbname} for query: {query.get('metric_name')}")
                with self.get_connection(host, port, user, password, dbname) as conn:
                    self.log.debug(f"Successfully connected to database {dbname}")
                    cursor = conn.cursor()
                    cursor.execute('SELECT version()')
                    version = cursor.fetchone()[0]
                    self.log.debug(f"Connected to PostgreSQL version: {version}")
                    cursor.execute('SELECT current_database(), current_user, current_timestamp, current_setting(\'timezone\')')
                    db_info = cursor.fetchone()
                    self.log.debug(f"Current database: {db_info[0]}, Current user: {db_info[1]}")
                    self.log.debug(f"Database timestamp: {db_info[2]}, Timezone: {db_info[3]}")
                    cursor = conn.cursor()
                    # Clean and prepare the multiline query
                    sql_query = query['query'].strip()
                    self.log.debug(f"Executing query for metric {query.get('metric_name')}: {sql_query}")
                    if 'interval' in sql_query.lower() or 'timestamp' in sql_query.lower() or 'now()' in sql_query.lower():
                        self.log.debug(f"Time-based query detected. Current server time: {db_info[2]}")
                    cursor.execute(sql_query)
                    try:
                        rows = cursor.fetchone()
                        self.log.debug(f"Query execution completed. Row count: {cursor.rowcount}")
                        self.log.debug(f"Column names: {[desc[0] for desc in cursor.description]}")
                        
                        if rows is None:
                            self.log.warning(f"Query execution returned None: {query['query']}")
                            continue
                            
                        self.log.debug(f"Query result: {rows}")
                        
                        if len(rows) == 0:
                            self.log.warning(f"Query returned empty result set: {query['query']}")
                            self.log.debug(f"SQL Query that returned no results: {sql_query}")
                            continue
                        
                        # Process query results based on the specified type
                        for row in rows:
                            try:
                                # Ensure we have a valid numeric value
                                value = row if row is not None else 0
                                self.log.debug(f"Processing value: {value} for metric: {query['metric_name']}")
                                
                                if not isinstance(value, (int, float)):
                                    self.log.warning(f"Unexpected value type: {type(value)} for metric: {query['metric_name']}")
                                    continue
                                    
                                if query.get('type') == 'gauge':
                                    self.gauge(
                                        query['metric_name'],
                                        value,
                                        tags=query_tags
                                    )
                                elif query.get('type') == 'count':
                                    self.count(
                                        query['metric_name'],
                                        value,
                                        tags=query_tags
                                    )
                            except (IndexError, TypeError) as e:
                                self.log.error(f"Error processing row {row}: {str(e)}")
                                continue
                    except Exception as e:
                        self.log.error(f"Error fetching results: {str(e)}")
                        raise
                    finally:
                        cursor.close()
            except Exception as e:
                self.log.error(f'Error executing query: {str(e)}')
                self.service_check(
                    'success',
                    AgentCheck.CRITICAL,
                    tags=query_tags,
                    message=str(e)
                )
            else:
                self.service_check(
                    'success',
                    AgentCheck.OK,
                    tags=query_tags
                )

    @contextmanager
    def get_connection(self, host: str, port: int, user: str, password: str, dbname: str):
        """Create a new database connection with proper error handling."""
        conn = None
        try:
            conn = psycopg2.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                dbname=dbname
            )
            yield conn
        except Exception as e:
            if conn:
                conn.close()
            raise e
        else:
            if conn:
                conn.close()

    def execute_query_raw(self, query: str, tags: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Execute a raw query and return the results."""
        # This method is required by QueryManager but we're not using it in this implementation
        pass
