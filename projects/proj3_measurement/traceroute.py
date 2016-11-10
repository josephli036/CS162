import subprocess
import re
import json

def run_traceroute(hostnames, num_packets, output_filename):
    file = open(output_filename, 'w')
    for host in hostnames:
        ping = subprocess.Popen(["traceroute", "-A", "-q", num_packets, host], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, error = ping.communicate()
        if out:
            print out
            file.write(out)
        else:
            print 'No trace'

def parse_traceroute(raw_traceroute_filename, output_filename):
    file = open(raw_traceroute_filename)
    result = {}
    whole_output = file.read()
    whole_output = whole_output.split("traceroute")[1:]
    for trace in whole_output:
        trace = trace.split('\n')
        hostname = re.findall(r"(\S*) \(", trace)[0]
        result[hostname] = []
        for line in trace[1:len(trace)-1]:
            print line
            name = re.findall(r"\d  (\S*)", line)[0]
            if name == "*":
                result[hostname].append([{"name": "None", "ip": "None", "ASN": "None"}])
            else:
                name = re.findall(r"(\S*) \(", line)
                ip = re.findall(r"\((.*)\)", line)
                asn = re.findall(r"\[(.*)\]", line)
                total = []
                for i in range(0, len(name)-1):
                    temp = {"name": name[i], "ip": ip[i]}
                    if asn[i] == "*":
                        temp["ASN"] = "None"
                    else:
                        temp["ASN"] = asn[i]

                

file = open('alexa_top_100')
websites = []
trace_a_websites = ["google.com", "facebook.com", "www.berkeley.edu", "allspice.lcs.mit.edu", "todayhumor.co.kr", "www.city.kobe.lg.jp", "www.vutbr.cz", "zanvarsity.ac.tz"]
for website in file.readlines():
    websites.append(website.rstrip())
#run_traceroute(trace_a_websites, "5", 'traceoutput')
parse_traceroute("traceoutput", "tr_a.json")
