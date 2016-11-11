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
        if lines[1][0] == ';':
            lines = lines[3:]
        print lines
        result = lines[len(lines)-1]
        lines = lines[:len(lines)-1]
        for line in lines:
            queried_name = re.findall(r"^(\S+)\t\t\t", line)
            TTL = re.findall(r"^.*\.\t\t\t(\d+)\t", line)
            print line
            print queried_name
            print TTL


    return None




run_dig("sdfsdfsdf", "asdfsadf")