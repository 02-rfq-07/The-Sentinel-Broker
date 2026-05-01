import random

class DeviceSimulator:
    def __init__(self, device_id, device_type, base_criticality):
        self.device_id = device_id
        self.device_type = device_type
        self.base_criticality = base_criticality
        self.in_critical_event = False
        self.work_remaining = 0

    def generate_pulse(self, has_slice=False):
        # 1. Start new task if idle
        if not self.in_critical_event and not has_slice and random.random() < 0.15:
            self.in_critical_event = True
            self.work_remaining = random.randint(8, 15) # Longer tasks for better observation

        # 2. Progress work - STRICT logic
        if self.in_critical_event:
            # VIP Slice = 1.0 units, Standard = 0.2 units
            self.work_remaining -= (1.0 if has_slice else 0.2)
            
            if self.work_remaining <= 0:
                self.in_critical_event = False
                self.work_remaining = 0

        # 3. Define Intent
        if self.in_critical_event:
            intent = "VIP_SLICE_ACTIVE" if has_slice else "CRITICAL_TASK_ACTIVE"
            rsrq = -3.0 if has_slice else round(random.uniform(-18.0, -15.0), 2)
            jitter = 2.0 if has_slice else round(random.uniform(50.0, 70.0), 2)
        else:
            intent = "IDLE_OR_STANDARD"
            rsrq = round(random.uniform(-10.0, -5.0), 2)
            jitter = round(random.uniform(5.0, 10.0), 2)

        return {
            "device_id": self.device_id,
            "telemetry": {"rsrq_db": rsrq, "jitter_ms": jitter},
            "context": {
                "intent": intent, 
                "base_criticality": self.base_criticality,
                "progress": round(max(self.work_remaining, 0), 1)
            }
        }