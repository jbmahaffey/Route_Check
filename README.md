# Route_Check

Variables should be updated in the variables JSON file.

Variables explained below:

        * "hostname": "spine1",               (This variable is the device name for easy identification)
        * "mgmt_ip": "172.16.2.3",            (This is the IP address that the script will connect to)
        * "route_1": "0.0.0.0",               (What route are we checking for in show ip bgp)
        * "validnexthop": ["10.13.56.2"],     (What is considered a valid next hop to keep from enabling the failover ISP interface)
        * "backupispint": "Ethernet4"              (What interface should we enable when no valid next hop exist)
