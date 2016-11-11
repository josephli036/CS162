import subprocess
import re
import json
import time

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
    whole_output = whole_output.split("traceroute")[1:]
    for trace in whole_output:
        hostname = re.findall(r".* (\S*) \(", trace)[0]
        trace = trace.split('\n')
        result[hostname] = []
        for line in trace[1:len(trace)-1]:
            # print line
            name = re.findall(r"\d  (\S*)", line)[0]
            if name == "*":
                result[hostname].append([{"name": "None", "ip": "None", "ASN": "None"}])
            else:
                name = re.findall(r" (\S*) \(", line)
                ip = re.findall(r" \((\S*)\) ", line)
                asn = re.findall(r" \[(\S*)\] ", line)
                total = []
                # print name
                # print ip
                # print asn
                for i in range(0, len(name)):
                    temp = {"name": name[i], "ip": ip[i]}
                    if asn[i] == "*":
                        temp["ASN"] = "None"
                    else:
                        temp["ASN"] = asn[i]
                    total.append(temp)
                result[hostname].append(total)
    with open(output_filename, "w") as output:
        json.dump(result, output)
                

file = open('alexa_top_100')
run_output = "tr_a_trial.json"
websites = []
trace_a_websites = ["google.com", "facebook.com", "www.berkeley.edu", "allspice.lcs.mit.edu", "todayhumor.co.kr", "www.city.kobe.lg.jp", "www.vutbr.cz", "zanvarsity.ac.tz"]
for website in file.readlines():
    websites.append(website.rstrip())
timestamp = str(time.time())
run_traceroute(trace_a_websites, "5", 'traceoutput')
parse_traceroute("traceoutput", run_output)
with open("tr_a.json", "w") as output:
    single_output = open(run_output, "r")
    dictionary = json.load(single_output)
    dictionary["timestamp"] = timestamp
    single_output.close()
    single_output = open(run_output, "w")
    json.dump(dictionary, single_output)
    single_output.close()
    single_output = open(run_output, "e")
    json_output = single_output.read()
    output.append(json_output)

