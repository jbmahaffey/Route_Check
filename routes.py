import sys
import os
import json
import jsonrpclib
import argparse
import ssl
import pprint
import argparse
import logging
ssl._create_default_https_context = ssl._create_unverified_context

def Main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--variables", default="variables.json", help="Location of necessary variables")
    parser.add_argument("--username", help="Switch username")
    parser.add_argument("--password", help="Switch password")
    parser.add_argument("--logging", default="", help="Logging levels info, error, or debug")
    args = parser.parse_args()

    #Only enable logging when necessary
    if args.logging != "":
        logginglevel = args.logging
        formattedlevel = logginglevel.upper()

        #Open logfile
        logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s',filename="routing_log.log", level=formattedlevel, datefmt='%Y-%m-%d %H:%M:%S')
    else:
        ()

    # Open JSON variable file
    with open(os.path.join(sys.path[0],args.variables), "r") as vars_:
        data = json.load(vars_)

    validity = Checknexthop(data["all"]["routers"], args.username, args.password)
    setint = Setinterface(data["all"]["routers"], args.username, args.password, validity)

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
                logging.debug(route["nextHop"])
                nexthops.append(route["nextHop"])
        except:
            logging.error("Error connecting to device " + str(switch) + " unable to read show ip bgp.")
 
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
    

if __name__ == "__main__":
   Main()