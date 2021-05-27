# Route_Check

This script is intended to check BGP for a specific prefix and check that prefix against valid next hops.  If no valid next hop exist or the prefix does not exist then script will enable an interface that should be connected to a tertiary ISP.  If a valid next hop does exist the script will ensure that the connection to the tertiary ISP is administratively down.  

Variables should be updated in the variables JSON file.

Variables explained below:

        * "hostname": "spine1",               (This variable is the device name for easy identification)
        * "mgmt_ip": "172.16.2.3",            (This is the IP address that the script will connect to)
        * "route_1": "0.0.0.0",               (What route are we checking for in show ip bgp)
        * "validnexthop": ["10.13.56.2"],     (What is considered a valid next hop to keep from enabling the failover ISP interface)
        * "backupispint": "Ethernet4"         (What interface should we enable when no valid next hop exist)
