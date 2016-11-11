import subprocess
import re
import json

def run_dig(hostname_filename, output_filename, dns_query_server=None):
    websites = []
    result = []
    with open('alexa_top_100') as file:
        for website in file.readlines():
            websites.append(website.rstrip())

    websites = ["google.com"]

    for host in websites:
        host_dictionary = {"Name": host}
        if dns_query_server:
            dns_run = subprocess.Popen(["dig", host, "@"+str(dns_query_server)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        else:
            dns_run = subprocess.Popen(["dig", "+trace", "+tries=1", "+nofail", "+nodnssec", host], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, error = dns_run.communicate()
            if out:
                queries = parse_no_dns(out, host_dictionary)

def parse_no_dns(out, host_dictionary):
    out = out.split('\n\n')
    out = out[:len(out)-1]

    for query in out:
        success = False
        lines = query.split('\n')
        if lines[1][0] == ';' and lines[0] == '':
            lines = lines[3:]
        print lines
        result = lines[len(lines)-1]
        lines = lines[:len(lines)-1]
        for line in lines:
            temp = line.split()
            queried_name = temp[0]
            TTL = temp[1]
            print queried_name
            print TTL



    return None




run_dig("sdfsdfsdf", "asdfsadf")