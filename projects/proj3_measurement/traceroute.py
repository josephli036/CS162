import subprocess
import re
import json
import time
import os

def run_traceroute(hostnames, num_packets, output_filename):
    file = open(output_filename, 'w')
    for host in hostnames:
        traceroute_run = subprocess.Popen(["traceroute", "-A", "-q", num_packets, host], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, error = traceroute_run.communicate()
        if out:
            # print out
            file.write(out)
        else:
            print 'No trace'

def parse_traceroute(raw_traceroute_filename, output_filename):
    file = open(raw_traceroute_filename)
    result = {}
    whole_output = file.read()
    whole_output = whole_output.split("route to")[1:]
    for trace in whole_output:
        hostname = re.findall(r".* (\S*) \(", trace)[0]
        trace = trace.split('\n')
        result[hostname] = []
        for line in trace[1:len(trace)-1]:
            print line
            name = re.findall(r"^\s*\d+\s*(\S*)", line)[0]
            if name == "*":
                result[hostname].append([{"name": "None", "ip": "None", "ASN": "None"}])
            else:
                name = re.findall(r" (\S*) \(", line)
                ip = re.findall(r" \((\S*)\) ", line)
                asn = re.findall(r" \[(.*)\] ", line)
                total = []
                # print name
                # print ip
                # print asn
                for i in range(0, len(name)):
                    temp = {"name": name[i]}
                    if ip and len(ip)>=i:
                        temp["ip"] = ip[i]
                    else:
                        temp["ip"] = name[i]
                    if not asn:
                        temp["ASN"] = "None"
                    elif asn[i] == "*" or asn[i] == 0:
                        temp["ASN"] = "None"
                    else:
                        temp["ASN"] = asn[i]
                    total.append(temp)
                result[hostname].append(total)
    with open(output_filename, "w") as output:
        json.dump(result, output)
# def part_one(filename):
#     with open(filename, 'r') as output:
#         input_one = output.readline()
#         input_two = output.readline()
#         input_three = output.readline()
#         input_four = output.readline()
#         input_five = output.readline()

#     l = [input_one, input_two, input_three, input_four, input_five]

#     for i in l:
#         i = i.split("\"")
#         o = ""
#         for items in i:
#             o += item
#         i = ""
#         for items in o:
#             items.split("/")
#             for item in items:
#                 i += " " + item
#         i = i.split()
#         for item in i:
#             if item == "ASN:":
#                 continue
#             elif item[0] == 'A' and item[1] == 'S':
#                 number = ""
#                 for i in range(2, len(item)):
#                     number += item[i]
#                 print number



p_servers = ["tpr-route-server.saix.net", "route-server.ip-plus.net", "route-views.oregon-ix.net", "route-views.on.bb.telus.com"]

# file = open('alexa_top_100')
run_output = "tr_a_trial.json"
# websites = []
# trace_a_websites = ["google.com", "facebook.com", "www.berkeley.edu", "allspice.lcs.mit.edu", "todayhumor.co.kr", "www.city.kobe.lg.jp", "www.vutbr.cz", "zanvarsity.ac.tz"]
# for website in file.readlines():
#     websites.append(website.rstrip())
timestamp = str(time.time())
run_traceroute(p_servers, "1", 'traceoutput')
parse_traceroute("traceoutput", run_output)
with open("tr_a.json", "a+") as output:
    single_output = open(run_output, "r")
    dictionary = json.load(single_output)
    dictionary["timestamp"] = timestamp
    single_output.close()
    single_output = open(run_output, "w")
    json.dump(dictionary, single_output)
    single_output.close()
    single_output = open(run_output, "r")
    json_output = single_output.read()
    if os.stat("tr_a.json").st_size != 0:
        output.write('\n' + json_output)
    else:
        output.write(json_output)

# 128.32.112.1
# 169.229.63.228

