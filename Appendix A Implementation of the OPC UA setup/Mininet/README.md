# Mininet

This part uses Mininet in Python script to emulate networks to test the NRM server simulation.

## Characteristics


## Tests in the tests folder

* NRM_sim_server_short_test_no_vlan
* NRM_sim_server_short_test_with_vlan

The "NRM_sim_server_short_test_no_vlan" sets bandwidth based on 5-tuple information. Without 5-tuple it sets the entire link's bandwidth.
A tc-flow filter is used to limit the specific communications bandwidth, which can be updated.
It sets delay based the link specified by the NRM server. The Vlan ID is accepted, but not set in this example.
Success and failure to set values is sent back.

The "NRM_sim_server_short_test_with_vlan" sets bandwidth and delay similarly to the "NRM_sim_server_short_test_no_vlan".
The difference is, that the hosts are replaced with VLANHOSTs, which use VLAN tags. The VLAN IDs are configured at start and NRM server can change them, when receiving Group Management requests (POST, PATCH, PUT).

## How to run 

NRM_sim_server_short_test_no_vlan

```
python3 NRM_sim_server_short_test_no_vlan.py
```

NRM_sim_server_short_test_with_vlan

```
python3 NRM_sim_server_short_test_with_vlan.py
```

Commands were run from the tests folder.
