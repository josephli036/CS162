import subprocess
import re
import json

def run_traceroute(hostnames, num_packets, output_filename):
    file = open(output_filename, 'w')
    for host in hostnames:
        ping = subprocess.Popen(["traceroute", "-q", num_packets, host], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, error = ping.communicate()
        if out:
            print out
            file.write(out)
        else:
            print 'No trace'

def parse_traceroute(raw_traceroute_filename, output_filename):
    file = open(raw_traceroute_filename)
    whole_output = file.read()
    whole_output = whole_output.split("traceroute")[1:]
    for trace in whole_output:
        print [trace]



file = open('alexa_top_100')
websites = []
trace_a_websites = ["google.com", "facebook.com", "www.berkeley.edu", "allspice.lcs.mit.edu", "todayhumor.co.kr", "www.city.kobe.lg.jp", "www.vutbr.cz", "zanvarsity.ac.tz"]
for website in file.readlines():
    websites.append(website.rstrip())
run_traceroute(trace_a_websites, "5", 'traceoutput')
parse_traceroute("traceoutput", "tr_a.json")
