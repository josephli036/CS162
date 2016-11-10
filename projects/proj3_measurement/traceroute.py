import subprocess
import re
import json

def run_traceroute(hostnames, num_packets, output_filename):
    for host in hostnames:
        ping = subprocess.Popen(["traceroute", "-q", num_packets, host], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, error = ping.communicate()
        if out:
            file = open(output_filename)
            file.write(out)
        else:
            print 'No trace'

file = open('alexa_top_100')
websites = []
for website in file.readlines():
    websites.append(website.rstrip())
run_traceroute(websites, "1", 'traceoutput')

#["google.com", "facebook.com", "www.berkeley.edu", "allspice.lcs.mit.edu", "todayhumor.co.kr", "www.city.kobe.lg.jp", "www.vutbr.cz", "zanvarsity.ac.tz"]
