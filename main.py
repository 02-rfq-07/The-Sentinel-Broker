from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uuid

app = FastAPI(title="Sentinel 5G Core Simulator (NEF API)")

NETWORK_STATE = {
    "total_bandwidth_mbps": 1200, # Resource scarcity forced
    "used_bandwidth_mbps": 0,
    "active_slices": {}
}

class SliceRequest(BaseModel):
    device_id: str
    requested_bandwidth_mbps: int
    priority_score: float

@app.get("/network_status")
async def get_network_status():
    available = NETWORK_STATE["total_bandwidth_mbps"] - NETWORK_STATE["used_bandwidth_mbps"]
    return {
        "available_bandwidth_mbps": available,
        "active_slices_count": len(NETWORK_STATE["active_slices"])
    }

@app.post("/provision_slice")
async def provision_slice(req: SliceRequest):
    available = NETWORK_STATE["total_bandwidth_mbps"] - NETWORK_STATE["used_bandwidth_mbps"]
    
    if req.requested_bandwidth_mbps > available:
        raise HTTPException(status_code=503, detail="Network Full")
    
    slice_id = str(uuid.uuid4())
    NETWORK_STATE["used_bandwidth_mbps"] += req.requested_bandwidth_mbps
    NETWORK_STATE["active_slices"][slice_id] = {"device_id": req.device_id, "bandwidth": req.requested_bandwidth_mbps}
    
    return {"status": "success", "slice_id": slice_id}

@app.post("/release_slice/{slice_id}")
async def release_slice(slice_id: str):
    if slice_id not in NETWORK_STATE["active_slices"]:
        raise HTTPException(status_code=404, detail="Not found")
        
    freed_bandwidth = NETWORK_STATE["active_slices"][slice_id]["bandwidth"]
    NETWORK_STATE["used_bandwidth_mbps"] -= freed_bandwidth
    del NETWORK_STATE["active_slices"][slice_id]
    return {"status": "success"}