import time
import requests
from telemetry import DeviceSimulator

CORE_API_URL = "http://127.0.0.1:8000"

class SentinelAgent:
    def __init__(self):
        self.active_slices = {} # {device_id: {"slice_id": x, "score": y}}

    def calculate_priority_score(self, criticality, jitter):
        urgency = min(jitter / 100.0, 1.0)
        return round((0.6 * criticality) + (0.4 * urgency), 3)

    def evaluate_and_act(self, pulse):
        device_id = pulse["device_id"]
        intent = pulse["context"]["intent"]
        score = self.calculate_priority_score(pulse["context"]["base_criticality"], pulse["telemetry"]["jitter_ms"])
        
        # --- ACTION: RELEASE ---
        if intent == "IDLE_OR_STANDARD" and device_id in self.active_slices:
            slice_id = self.active_slices[device_id]["slice_id"]
            requests.post(f"{CORE_API_URL}/release_slice/{slice_id}")
            del self.active_slices[device_id]
            return "♻️ RELEASED (Done)"

        # --- ACTION: REQUEST / PRE-EMPT ---
        if intent == "CRITICAL_TASK_ACTIVE" and device_id not in self.active_slices:
            payload = {"device_id": device_id, "requested_bandwidth_mbps": 500, "priority_score": score}
            response = requests.post(f"{CORE_API_URL}/provision_slice", json=payload)
            
            if response.status_code == 200:
                self.active_slices[device_id] = {"slice_id": response.json()["slice_id"], "score": score}
                return f"✅ BOUGHT | Score: {score}"
            
            elif response.status_code == 503: # Network Full
                # Find weakest score currently in the network
                weakest_id = min(self.active_slices, key=lambda k: self.active_slices[k]["score"])
                weakest_score = self.active_slices[weakest_id]["score"]
                
                if score > weakest_score:
                    # ATOMIC HANDOFF: Revoke Weakest -> Take their spot
                    requests.post(f"{CORE_API_URL}/release_slice/{self.active_slices[weakest_id]['slice_id']}")
                    del self.active_slices[weakest_id]
                    
                    # Immediately re-try for current device
                    retry = requests.post(f"{CORE_API_URL}/provision_slice", json=payload)
                    if retry.status_code == 200:
                        self.active_slices[device_id] = {"slice_id": retry.json()["slice_id"], "score": score}
                        return f"⚡ PRE-EMPTED {weakest_id} (Score: {score})"
                
                return f"⏳ QUEUED (Wait for capacity)"

        return None

def run_agent():
    print("Sentinel Broker v2.1 | Atomic Pre-emption")
    agent = SentinelAgent()
    devices = [
        DeviceSimulator("med-drone-alpha", "Healthcare_UAV", 0.95),
        DeviceSimulator("factory-robot-B", "Industrial_IoT", 0.80),
        DeviceSimulator("exec-laptop-99",  "Enterprise_Media", 0.50)
    ]

    try:
        while True:
            # Print Tower Status at the start of every tick
            status = requests.get(f"{CORE_API_URL}/network_status").json()
            avail = status["available_bandwidth_mbps"]
            print(f"\n[TOWER STATUS] Available: {avail} Mbps | Active: {status['active_slices_count']}")
            print("-" * 115)
            
            for device in devices:
                has_slice = device.device_id in agent.active_slices
                pulse = device.generate_pulse(has_slice=has_slice)
                action = agent.evaluate_and_act(pulse)
                
                intent = pulse["context"]["intent"]
                prog = pulse["context"]["progress"]
                action_display = action if action else ("(Holding VIP)" if has_slice else "(Monitoring)")
                
                print(f"{device.device_id:<18} | {intent:<22} | Progress: {prog:<4} | {action_display}")
            
            time.sleep(2.5)
    except KeyboardInterrupt: pass

if __name__ == "__main__": run_agent()