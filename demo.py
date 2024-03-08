import time
from time import sleep
from spicepy import Client
import threading

SPICEAI_API_KEY = '3232|2ea664a9be804002af9b212021749439'
LARGE_SQL_QUERY = 'SELECT * FROM eth.recent_traces trace JOIN eth.recent_transactions trans ON trace.transaction_hash = trans.hash ORDER BY trans.block_number DESC;'

###########################
#   Spice.ai Platform     #
###########################

# use API key from Spice.ai app to instantiate a client

# client = Client(SPICEAI_API_KEY)

# startTime = time.time()
# data = client.query(LARGE_SQL_QUERY)
# pd = data.read_chunk()
# endTime = time.time()

# print("Completed in {duration:.2f} seconds\n".format(duration = endTime - startTime))

# exit()

########################################
#   DO NOT COMMENT OUT THE LINE BELOW  #
########################################
client = Client(SPICEAI_API_KEY, 'grpc://127.0.0.1:50051')

###########################
#   Spice AI Datasource   #
###########################

while True:
    startTime = time.time()
    data = client.query(LARGE_SQL_QUERY)
    pd = data.r.read_chunk()
    endTime = time.time()

    print(pd.head(5))
 
    print("Completed in {duration:.2f} seconds\n".format(duration = endTime - startTime))

    sleep(1)

###########################
#    Dremio Datasource    #
###########################

while True:
    startTime = time.time()
    data = client.query('SELECT * FROM taxi_trips ORDER BY pickup_datetime DESC LIMIT 100')
    endTime = time.time()
    pd = data.read_pandas()

    print(pd.to_string() + "\n")
    print("Completed in {duration:.2f} seconds\n".format(duration = endTime - startTime))

    startTime = time.time()
    data = client.query('SELECT count(*) FROM taxi_trips')
    endTime = time.time()
    pd = data.read_pandas()

    print(pd.to_string() + "\n")
    print("Completed in {duration:.2f} seconds\n".format(duration = endTime - startTime))

###########################
# Spice/Dremio Datasource #
###########################

while True:
    startTime = time.time()
    data = client.query("""
        SELECT DISTINCT
            eth_recent_blocks.number as block_number, 
            taxi_trips.trip_distance_mi
        FROM eth_recent_blocks 
        LEFT JOIN taxi_trips 
        ON eth_recent_blocks.number%100 = taxi_trips.trip_distance_mi*10
        ORDER BY eth_recent_blocks.number DESC                
        LIMIT 10
        """)
    endTime = time.time()
    pd = data.read_pandas()

    print(pd.to_string() + "\n")
    print("Completed in {duration:.2f} seconds\n".format(duration = endTime - startTime))

    sleep(5)

#####################################
#    High-RPS Queries Simulation    # (OPTIONAL)
#####################################

# yaml file needs to be updated before running this code

def simulate_runtime_duckdb(user_id):
    #print("User " + str(user_id) + " started")
    # make a new client for each user
    client = Client(SPICEAI_API_KEY, 'grpc://127.0.0.1:50051')
    start = time.time()
    # make a query
    data = client.query('SELECT * FROM eth_recent_blocks_duckdb DESC;')
    pd = data.read_all()
    end = time.time()
    total = end - start
    
    print("User " + str(user_id) + ": " + str(total) + " seconds")

def simulate_runtime_arrow_mem(user_id):
    #print("User " + str(user_id) + " started")
    # make a new client for each user
    client = Client(SPICEAI_API_KEY, 'grpc://127.0.0.1:50051')
    start = time.time()
    # make a query
    data = client.query('SELECT * FROM eth_recent_blocks DESC;')
    pd = data.read_all()
    end = time.time()
    total = end - start
    
    print("User " + str(user_id) + ": " + str(total) + " seconds")

def simulate_sdk(user_id):
    #print("User " + str(user_id) + " started")
    # make a new client for each user
    client = Client(SPICEAI_API_KEY)
    start = time.time()
    # make a query
    data = client.query('SELECT * FROM eth.recent_blocks DESC;')
    pd = data.read_all()
    end = time.time()
    total = end - start
    
    print("User " + str(user_id) + ": " + str(total) + " seconds")
 
# simulate the number of users
def simulate_concurrent_queries(num_users, function_name):
    threads = []
 
    start_time = time.time()
 
    for user_id in range(num_users):
        t = threading.Thread(target=function_name, args=(user_id,))
        threads.append(t)
        t.start()
 
    for thread in threads:
        thread.join()
 
    end_time = time.time()
    total_time = end_time - start_time
 
    print("\n")

    return total_time

total_users = 20
time_sdk = simulate_concurrent_queries(total_users, simulate_sdk)
time_runtime_duckdb = simulate_concurrent_queries(total_users, simulate_runtime_duckdb)
time_runtime_arrow_mem = simulate_concurrent_queries(total_users, simulate_runtime_arrow_mem)

print("Simulating " + str(total_users) + " concurrent users making queries..")
print("Total Time for SDK: " + str(time_sdk) + " seconds")
print("Total Time for In Memory Runtime: " + str(time_runtime_arrow_mem) + " seconds")
print("Total Time for DuckDB Runtime: " + str(time_runtime_duckdb) + " seconds")

exit()