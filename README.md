# Mininet Network Experiments

Two network emulation experiments using Mininet — covering IP routing across multiple subnets and OpenFlow-based L2 flow control with OVS switches.

---

## Experiment 1 — IP Routing with Multiple Subnets (`exp1.py`)

Builds a custom topology with **3 hosts**, **2 Linux routers**, and **4 subnets**, then configures static routes and runs ping tests across subnets.

**Topology:**
```
h1 (10.0.0.1) ── r1 ── r2 ── h3 (10.0.2.2)
                  |
                 h2 (10.0.3.2)
```

**Subnets:**
- `10.0.0.0/24` — h1 ↔ r1
- `10.0.1.0/24` — r1 ↔ r2 (inter-router)
- `10.0.2.0/24` — r2 ↔ h3
- `10.0.3.0/24` — r1 ↔ h2

**Tests run:** h1→h3, h2→h3, h3→h1, h3→h2

Results saved to `result1.txt`

---

## Experiment 2 — OpenFlow L2 Flow Control with OVS (`exp2.py`)

Builds a topology with **2 OVS switches**, **3 hosts**, and installs custom OpenFlow rules to selectively allow or block traffic.

**Topology:**
```
h1 ── s1 ── s2 ── h3
h2 ──/
```

**Flow rules applied on s1:**
- `h2 → DROP` — all traffic from h2 blocked
- `h1 → forward to s2` — h1 traffic forwarded to h3

**Result:** h1 can ping h3, h2 cannot — demonstrating per-port flow control.

Results saved to `result2.txt`

---

## Setup

```bash
# Requires Mininet and Open vSwitch
sudo apt install mininet openvswitch-switch

# Run experiments
sudo python3 exp1.py
sudo python3 exp2.py
```

---
