import subprocess
import re
import json
import utils.py

def run_dig(hostname_filename, output_filename, dns_query_server=None):
    websites = []
    result = []
    with open('alexa_top_100') as file:
        for website in file.readlines():
            websites.append(website.rstrip())

    websites = ["google.com"]

    for host in websites:
        host_dictionary = {NAME_KEY: host}
        if dns_query_server:
            dns_run = subprocess.Popen(["dig", host, "@"+str(dns_query_server)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        else:
            dns_run = subprocess.Popen(["dig", "+trace", "+tries=1", "+nofail", "+nodnssec", host], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, error = dns_run.communicate()
            if out:
                queries = parse_no_dns(out, host_dictionary)
                print queries

def parse_no_dns(out, host_dictionary):
    out = out.split('\n\n')
    out = out[:len(out)-1]

    success = False
    queries = []
    for query in out:
        awnsers = []
        lines = query.split('\n')
        if lines[1][0] == ';' and lines[0] == '':
            lines = lines[3:]
        print lines
        result = lines[len(lines)-1]
        time = int(re.findall(r" (\d+) ms$", result)[0])
        lines = lines[:len(lines)-1]
        for line in lines:
            temp = line.split()
            queried_name = temp[0]
            TTL = int(temp[1])
            d_type = temp[3]
            data = temp[4]
            print queried_name
            print TTL
            print d_type
            print data
            if d_type == "A" or d_type == "CNAME":
                success = True
            awnsers.append({QUERIED_NAME_KEY: queried_name, ANSWER_DATA_KEY: data, TYPE_KEY: d_type, TTL_KEY: TTL})
        queries.append({TIME_KEY: time, ANSWERS_KEY: awnsers})
    host_dictionary[SUCCESS_KEY] = success
    host_dictionary[QUERIES_KEY] = queries
    return host_dictionary



    return None




run_dig("sdfsdfsdf", "asdfsadf")