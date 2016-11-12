import subprocess
import re
import json
import time
import os

def run_traceroute(hostnames, num_packets, output_filename):
    timestamp = str(time.time())
    file = open(output_filename, 'w')
    file.write(timestamp + '\n')
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
    timestamp = whole_output.split('\n')[0]
    result["timestamp"] = timestamp

    whole_output = whole_output.split("route to")[1:]
    for trace in whole_output:
        hostname = re.findall(r".* (\S*) \(", trace)[0]
        trace = trace.split('\n')
        result[hostname] = []
        for line in trace[1:len(trace)-1]:
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
                    elif asn[i] == "*" or asn[i] == '0' or asn[i] == 'AS0':
                        temp["ASN"] = "None"
                    else:
                        temp["ASN"] = asn[i][2:]
                    total.append(temp)
                result[hostname].append(total)
    with open(output_filename, "w") as output:
        json.dump(result, output)


def part_one(filename):
    with open(filename, 'r') as output:
        input_one = json.load(output)

    best_key = None
    best_count = None

    for key in input_one:
        if key == "timestamp":
            continue
        else:
            seen = []
            count = 0
            l = input_one[key]
            for li in l:
                for dictionary in li:
                    if dictionary["ASN"] not in seen:
                        seen.append(dictionary["ASN"])
                        count += 1
            if best_count == None or count < best_count:
                best_key = key
                best_count = count

    return [best_key, best_count]




p_servers = ["tpr-route-server.saix.net", "route-server.ip-plus.net", "route-views.oregon-ix.net", "route-views.on.bb.telus.com"]

# file = open('alexa_top_100')
run_output = "tr_a_trial.json"
# websites = []
# trace_a_websites = ["google.com", "facebook.com", "www.berkeley.edu", "allspice.lcs.mit.edu", "todayhumor.co.kr", "www.city.kobe.lg.jp", "www.vutbr.cz", "zanvarsity.ac.tz"]
# for website in file.readlines():
#     websites.append(website.rstrip())
# timestamp = str(time.time())
run_traceroute(p_servers, "1", 'traceoutput')
parse_traceroute("traceoutput", run_output)
# with open("tr_b.json", "a+") as output:
#     single_output = open(run_output, "r")
#     dictionary = json.load(single_output)
#     dictionary["timestamp"] = timestamp
#     single_output.close()
#     single_output = open(run_output, "w")
#     json.dump(dictionary, single_output)
#     single_output.close()
#     single_output = open(run_output, "r")
#     json_output = single_output.read()
#     if os.stat("tr_b.json").st_size != 0:
#         output.write('\n' + json_output)
#     else:
#         output.write(json_output)

# print part_one("blah.json")

# 128.32.112.1
# 169.229.63.228

