import uuid
import random

# Define the number of records to generate
num_records = 500

# Function to generate a random username
def generate_username(index):
    return f"user_{index}"

# Function to generate a random balance greater than 0
def generate_balance():
    return round(random.uniform(1, 10000), 2)

# Open a file to write the SQL insert statements
with open("insert_records.sql", "w") as f:
    f.write("BEGIN;\n")  # Start a transaction

    # Generate records
    for i in range(num_records):
        record_id = str(uuid.uuid4())
        username = generate_username(i)
        balance = generate_balance()
        f.write(f"INSERT INTO accounts (id, username, balance) VALUES ('{record_id}', '{username}', {balance});\n")

    f.write("COMMIT;\n")  # Commit the transaction

print(f"{num_records} records have been generated and saved to insert_records.sql")