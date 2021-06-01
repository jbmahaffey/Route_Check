import sys
import os
import json
import jsonrpclib
import argparse
import ssl
import argparse
import logging
from scapy.all import *
ssl._create_default_https_context = ssl._create_unverified_context

def Main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--variables", default="variables.json", help="Location of necessary variables")
    parser.add_argument("--username", help="Switch username")
    parser.add_argument("--password", help="Switch password")
    parser.add_argument("--logging", default="", help="Logging levels info, error, or debug")
    parser.add_argument("--check", default="8.8.8.8", help="IP address you want to trace path to")
    args = parser.parse_args()

    # Only enable logging when necessary
    if args.logging != "":
        logginglevel = args.logging
        formattedlevel = logginglevel.upper()

        # Open logfile
        logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s',filename="routing_log.log", level=formattedlevel, datefmt='%Y-%m-%d %H:%M:%S')
    else:
        ()

    # Open JSON variable file
    with open(os.path.join(sys.path[0],args.variables), "r") as vars_:
        data = json.load(vars_)

    # Check network path using ping and if next hops are not valid then execute check BGP 
    validhops = []
    devices = data["all"]["routers"]
    for device in devices:
        validhops.extend(device["validnexthop"])

    hostname = args.check
    currenthops = []
    for i in range(1, 8):
        pkt = IP(dst=hostname, ttl=i) / UDP(dport=33434)
        # Send the packet and get a reply
        reply = sr1(pkt, timeout=3, verbose=0)
        if reply is None:
            currenthops.append("None")
        else:
            currenthops.append(reply.src)
    
    for hops in validhops:
        if hops in currenthops:
            badhops = False
            break
        else:
            badhops = True
    
    if badhops == True:
        validity = Checknexthop(data["all"]["routers"], args.username, args.password)
        logging.debug("%s next hops", validity)
        setint = Setinterface(data["all"]["routers"], args.username, args.password, validity)
    else:
        sys.exit()
        
def Checknexthop(devices, username, password):
    nexthops = []
    valid = []

    # Create a list of current nexthops based on show ip bgp {route}
    for device in devices:
        switch = device["mgmt_ip"]
        route = device["route_1"]
        valid.extend(device["validnexthop"])
        url = "{proto}://{user}:{passwd}@{switch}/command-api".format(proto="https", user=username, passwd=password, switch=switch)
        try: 
            connect = jsonrpclib.Server(url)
            response = connect.runCmds( 1, ["show ip bgp " + str(route)])
            for route in response[0]["vrfs"]["default"]["bgpRouteEntries"]["0.0.0.0/0"]["bgpRoutePaths"]:
                nexthops.append(route["nextHop"])
        except:
            logging.error("Error connecting to device " + str(switch) + " unable to read show ip bgp.")
    logging.debug("Current next hops are %s", nexthops)
    logging.debug("Valid next hops are %s", valid)
    # Determine if the nexthops returned are valid  
    l1 = []      
    for validhop in valid:
        if validhop in nexthops:
            l1.append("valid")
        else:
            l1.append("invalid")
    if "valid" in l1:
        return "valid"
    else:
        return "invalid"
            
            
def Setinterface(devices, username, password, valid):
    if valid == "invalid":
        for device in devices:
            switch = device["mgmt_ip"]
            interface = device["backupispint"]
            if interface != "":
                url = "{proto}://{user}:{passwd}@{switch}/command-api".format(proto="https", user=username, passwd=password, switch=switch)
                try:
                    connect = jsonrpclib.Server(url)
                    response = connect.runCmds( 1, ["enable",
                                                        "configure terminal",
                                                        "interface " + str(interface),
                                                        "no shutdown"])
                except:
                    logging.error("Error connecting to device " + str(switch) + " to enable interface " + str(interface))
            else:
                logging.info("No backup ISP interface on " + str(switch) + " to enable.")
    else:
        for device in devices:
            switch = device["mgmt_ip"]
            interface = device["backupispint"]
            if interface != "":
                url = "{proto}://{user}:{passwd}@{switch}/command-api".format(proto="https", user=username, passwd=password, switch=switch)
                try:
                    connect = jsonrpclib.Server(url)
                    response = connect.runCmds( 1, ["show interfaces " + str(interface)])
                    for iface in response:
                        if iface["interfaces"][interface]["lineProtocolStatus"] == "up":
                            shutdown = connect.runCmds(1, ["enable",
                                                                "configure",
                                                                "interface " + str(interface),
                                                                "shutdown"])
                            logging.info("Interface shutdown on device " + str(switch))
                        else:
                            logging.info("Interfaces Already down on device " + str(switch) + ", no action required.")
                except:
                    logging.error("Error connecting to device " + str(switch) + " to shutdown interface.")
            else:
                logging.debug("No backup ISP interface on " + str(switch) + " no action required.")
    
#Run the main function
if __name__ == "__main__":
   Main()