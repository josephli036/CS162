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
            dns_run = subprocess.Popen(["dig", "+trace", "+tries=1", "+nofail", host], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, error = dns_run.communicate()

        if out:
            out = out.split('\n\n')
            out = out[0].split('\n')
            for o in out:
                print [o]


run_dig("sdfsdfsdf", "asdfsadf")