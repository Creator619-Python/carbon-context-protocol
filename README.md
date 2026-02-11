# Carbon Context Protocol (CCP)

**A filesystem interface for grid-aware compute scheduling.**

CCP exposes real-time carbon intensity, grid period (peak/off-peak), and data confidence via `/run/carbon/*` — a zero-cost primitive any process can read.

---

## Who this is for

| Role | What CCP gives them |
|------|---------------------|
| **SRE / Platform Eng** | Shift batch jobs off-peak, reduce demand charges, improve grid resilience |
| **Sustainability Eng** | Trustworthy, auditable carbon signal for reporting and automation |
| **Cloud Ops** | Align spot instances with low-carbon periods, reduce cost and emissions |
| **Edge / Industrial IT** | Schedule non-urgent compute when grid stress is low — no cloud dependency |

---

## Why this exists

Grid-aware scheduling shouldn't require:

- ✅ A PhD in energy systems
- ✅ Per-application SDKs or API keys
- ✅ Vendor lock-in
- ✅ Permission from developers

It should be a **system property**, like load average or free memory.

CCP is that property.

---

## How it works

CCP is not a tool. It's a **location**:
