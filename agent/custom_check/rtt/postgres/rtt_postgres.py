import time
import psycopg2
from checks import AgentCheck

class MeasureRTT(AgentCheck):
    def check(self, instance):
        try:

            # Connect to your PostgreSQL database
            conn = psycopg2.connect(
                dbname= instance['database'],
                host = instance['host'],
                port = instance['port'],  # Default PostgreSQL port
                user = instance['username'],
                password = instance['password']
            )
        
        
            query = instance['query']

            metric = "postgres.rtt.query"
            
            # Start timer
            start_time = time.time()

            # Create a cursor object using the connection
            cursor = conn.cursor()
            
            # Execute the test query
            cursor.execute(query)
            cursor.fetchone()  # Fetch result
            
            # End timer
            end_time = time.time()
            
            # Calculate round-trip time (RTT)
            rtt_seconds = end_time - start_time

            # Convert RTT to milliseconds
            rtt_milliseconds = rtt_seconds * 1000
            
            # Report the RTT as a custom metric to Datadog
            self.gauge(metric, rtt_milliseconds,tags=['unit:milliseconds'],)
        
        except Exception as e:
            self.log.error(f"Error executing query or connecting to PostgreSQL: {e}")
            # Optionally, report a failed metric or a default value if desired
            self.gauge(metric, -1)  # -1 can signify an error in your metrics
    
        finally:
            # Ensure cursor and connection are closed
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()
