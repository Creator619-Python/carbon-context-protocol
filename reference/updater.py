#!/usr/bin/env python3
"""
CCP Reference Implementation: Updater
Updates /run/carbon/* files every 30 minutes with carbon intensity data.
"""
import os
import time
import syslog
import shutil
from pathlib import Path

CARBON_DIR = Path("/run/carbon")

def log(message):
    """Log to syslog"""
    syslog.syslog(syslog.LOG_INFO, f"ccp-updater: {message}")

def get_carbon_intensity():
    """
    Get carbon intensity with graceful degradation.
    In a real implementation, this would fetch from electricityMap, CO2Signal, etc.
    """
    try:
        # Simulate fetching data
        hour = time.localtime().tm_hour
        
        # Simple time-based heuristic
        if 0 <= hour < 6:
            intensity = 180  # Night - cleaner
            period = "off-peak"
        elif 6 <= hour < 9:
            intensity = 320  # Morning shoulder
            period = "shoulder"
        elif 9 <= hour < 17:
            intensity = 450  # Day peak
            period = "peak"
        elif 17 <= hour < 21:
            intensity = 380  # Evening shoulder
            period = "shoulder"
        else:
            intensity = 220  # Late evening
            period = "off-peak"
        
        return {
            "intensity": intensity,
            "marginal": intensity + 30,
            "region": "US-CAISO",
            "confidence": "medium",
            "period": period,
            "source": "time-heuristic",
            "units": "gCO₂/kWh"
        }
    except Exception as e:
        log(f"Failed to fetch carbon data: {e}")
        # Fallback to unknown
        return {
            "intensity": -1,
            "marginal": -1,
            "region": "UNKNOWN",
            "confidence": "low",
            "period": "unknown",
            "source": "fallback",
            "units": "gCO₂/kWh"
        }

def update_context():
    """Atomic update of all carbon context files"""
    data = get_carbon_intensity()
    
    # Create temporary directory with .new suffix for atomic swap
    tmp_dir = Path("/run/carbon.new")
    
    # Clean up any previous failed update
    if tmp_dir.exists():
        shutil.rmtree(tmp_dir, ignore_errors=True)
    
    # Create new directory structure
    tmp_dir.mkdir(parents=True, exist_ok=True)
    
    # Write all files to temporary directory
    (tmp_dir / "intensity").write_text(str(data["intensity"]))
    (tmp_dir / "marginal").write_text(str(data["marginal"]))
    (tmp_dir / "region").write_text(data["region"])
    (tmp_dir / "confidence").write_text(data["confidence"])
    (tmp_dir / "period").write_text(data["period"])
    (tmp_dir / "source").write_text(data["source"])
    (tmp_dir / "units").write_text(data["units"])
    (tmp_dir / "updated_at").write_text(str(int(time.time())))
    (tmp_dir / "ttl").write_text("1800")  # 30 minutes
    
    # Create forecast directory
    forecast_dir = tmp_dir / "forecast"
    forecast_dir.mkdir()
    for offset in [15, 30, 60]:
        (forecast_dir / f"+{offset}").write_text(str(data["intensity"]))
    
    # Atomic directory swap
    try:
        # Create /run/carbon if it doesn't exist
        CARBON_DIR.mkdir(parents=True, exist_ok=True)
        
        # Atomic rename - POSIX guarantees this is atomic
        tmp_dir.rename(CARBON_DIR)
    except Exception as e:
        # Cleanup on failure
        shutil.rmtree(tmp_dir, ignore_errors=True)
        log(f"Atomic update failed: {e}")
        raise
    
    log(f"Updated carbon context: intensity={data['intensity']}, period={data['period']}")

if __name__ == "__main__":
    update_context()
