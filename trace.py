import sys
import os
import json
import argparse
from scapy.all import *
from routes import Mainroute

def Main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--variables", default="variables.json", help="Location of necessary variables")
    args = parser.parse_args()

    # Open JSON variable file
    with open(os.path.join(sys.path[0],args.variables), "r") as vars_:
        data = json.load(vars_)
    
    validhops = []
    devices = data["all"]["routers"]
    for device in devices:
        validhops.extend(device["validnexthop"])

    hostname = "8.8.8.8"
    currenthops = []
    for i in range(1, 8):
        pkt = IP(dst=hostname, ttl=i) / UDP(dport=33434)
        # Send the packet and get a reply
        reply = sr1(pkt, timeout= 5, verbose=0)
        if reply is None:
            currenthops.append("None")
        else:
            currenthops.append(reply.src)
    
    for hops in validhops:
        if hops in currenthops:
            badhops = False
        else:
            badhops = True
    
    if badhops == True:
        Mainroute()
    else:
        ()

#Run the main function
if __name__ == "__main__":
   Main()