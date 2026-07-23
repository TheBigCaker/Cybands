# Copyright (c) 2026 David Baker (Delta Vector) and the Sol Mech R&D team.
# Licensed under the Business Source License 1.1 (BSL 1.1). See LICENSE.md in the project root for license information.

import time
import threading
import statistics
from src.comms import ZMQBridge, CommsMode

def server_thread():
    server = ZMQBridge(mode=CommsMode.SERVER, req_port=5557, pub_port=5558)
    
    def handle_ping(msg):
        # Echo back
        return {"pong": msg["ts"]}
        
    server.command_handler = handle_ping
    server.start()
    time.sleep(10)
    server.stop()

def client_thread():
    client = ZMQBridge(mode=CommsMode.CLIENT, req_port=5557, pub_port=5558)
    client.start()
    
    time.sleep(1) # Wait for connection
    
    latencies = []
    print("Starting Latency Test (100 pings)...")
    
    for _ in range(100):
        start = time.time()
        resp = client.send_command("PING", {})
        end = time.time()
        latencies.append((end - start) * 1000) # ms
        time.sleep(0.01)
        
    avg = statistics.mean(latencies)
    p99 = statistics.quantiles(latencies, n=100)[98]
    
    print(f"Latency Results:")
    print(f"  Avg: {avg:.3f} ms")
    print(f"  P99: {p99:.3f} ms")
    print(f"  Min: {min(latencies):.3f} ms")
    print(f"  Max: {max(latencies):.3f} ms")
    
    client.stop()

if __name__ == "__main__":
    t_server = threading.Thread(target=server_thread)
    t_server.start()
    
    time.sleep(0.5)
    
    client_thread()
    t_server.join()
