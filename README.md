# Route_Check

The setup.sh script will install the required python3 modules as defined in the requirements.txt document.  Please run this script first to ensure that all required modules are installed.

The first function in this script will trace the network path and compare against a manually defined valid path in the variables JSON file
***(Important note on the trace is that the traced path originates from the device running the script).***
 If the traced path has a valid IP in it then it will stop the script as the path is valid.  If there is no matching IP in the traced path then it will continue and login to the device and check show ip bgp for valid next hops by comparing those to the manually defined next hops in the variables file.  If no valid next hop exist or the prefix does not exist then script will enable an interface that should be connected to a tertiary ISP.  If a valid next hop does exist the script will ensure that the connection to the tertiary ISP is administratively down.  

Logging is disabled by default, if you would like to enable it for any purpose please use the switch --logging with the level set to info, error, or debug (ie. --logging info).

Variables should be updated in the variables JSON file.

Variables explained below:

        * "hostname": "spine1",               (This variable is the device name for easy identification)
        * "mgmt_ip": "172.16.2.3",            (This is the IP address that the script will connect to)
        * "route_1": "0.0.0.0",               (What route are we checking for in show ip bgp)
        * "validnexthop": ["10.13.56.2"],     (What is considered a valid next hop to keep from enabling the failover ISP interface)
        * "backupispint": "Ethernet4"         (What interface should we enable when no valid next hop exist)

List of available switches when running the script are below:

        * --variables variables.json           (This is the filename where you stored your variables, must be JSON. Default is variables.json)
        * --username username                  (Device Username)
        * --password password                  (Device Password)
        * --logging                            (Enable logging and set the leve to info, error, or debug)
        * --check                              (IP address to trace to for network path, default is 8.8.8.8)