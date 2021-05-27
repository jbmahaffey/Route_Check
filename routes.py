import sys
import os
import json
import jsonrpclib
import argparse
import ssl
import pprint
import argparse
ssl._create_default_https_context = ssl._create_unverified_context

def Main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--variables", default="variables.json", help="Location of necessary variables")
    parser.add_argument("--username", help="Switch username")
    parser.add_argument("--password", default="M@h@ffey87", help="Switch password")
    args = parser.parse_args()

    # Open JSON variable file
    with open(os.path.join(sys.path[0],args.variables), "r") as vars_:
        data = json.load(vars_)

    nexthops = Checknexthop(data["all"]["routers"], args.username, args.password)

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
                #pprint.pprint(route["nextHop"])
                nexthops.append(route["nextHop"])
        except:
            pprint.pprint("Error connecting to host " + switch)
    
    # Determine if the nexthops returned are valid        
    for validhop in valid:
        if validhop in nexthops:
            print("Valid next hop route exist")
        else:
            print("No valid next hop exist")

    

if __name__ == "__main__":
   Main()