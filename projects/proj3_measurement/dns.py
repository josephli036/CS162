import subprocess
import re
import json
import utils
import numpy as np
import matplotlib.pyplot as plt

def run_dig(hostname_filename, output_filename, dns_query_server=None):
    websites = []
    result = []
    with open(hostname_filename) as file:
        for website in file.readlines():
            websites.append(website.rstrip())

    for host in websites:
        for i in range(1):
            host_dictionary = {utils.NAME_KEY: host}
            if dns_query_server:
                dns_run = subprocess.Popen(["dig", host, "@"+str(dns_query_server)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                out, error = dns_run.communicate()
                if out:
                    queries = parse_dns(out, host_dictionary)
                    result.append(queries)
            else:
                dns_run = subprocess.Popen(["dig", "+trace", "+tries=1", "+nofail", "+nodnssec", host], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                out, error = dns_run.communicate()
                if out:
                    queries = parse_no_dns(out, host_dictionary)
                    result.append(queries)
    with open(output_filename, 'w') as output:
        json.dump(result, output)

def parse_dns(out, host_dictionary):
    out = out.split('\n')
    out = out[1:]

    check_success = out[3].split()[5]
    success = False

    if check_success == 'NOERROR,':
        host_dictionary[utils.SUCCESS_KEY] = True
    else:
        host_dictionary[utils.SUCCESS_KEY] = False

    time = None
    i = 0
    answers = []
    while i < len(out):
        line = out[i].split()
        if line:
            if line[1] == 'Query':
                time = line[3]
            if line[1] == 'ANSWER' or line[1] == 'ADDITIONAL':
                line = out[i+1].split()
                while line:
                    answers.append({utils.QUERIED_NAME_KEY: line[0], utils.ANSWER_DATA_KEY: line[4], utils.TYPE_KEY: line[3], utils.TTL_KEY: line[1]})
                    i+=1
                    line = out[i+1].split()
        i += 1
    queries = [{utils.TIME_KEY: time, utils.ANSWERS_KEY: answers}]
    host_dictionary[utils.QUERIES_KEY] = queries
    return host_dictionary


def parse_no_dns(out, host_dictionary):
    out = out.split('\n\n')
    out = out[:len(out)-1]

    success = False
    queries = []
    for query in out:
        answers = []
        lines = query.split('\n')
        if lines[1][0] == ';' and lines[0] == '':
            lines = lines[3:]
        result = lines[len(lines)-1]
        time = int(re.findall(r" (\d+) ms$", result)[0])
        lines = lines[:len(lines)-1]
        for line in lines:
            temp = line.split()
            queried_name = temp[0]
            TTL = int(temp[1])
            d_type = temp[3]
            data = temp[4]
            if d_type == "A" or d_type == "CNAME":
                success = True
            answers.append({utils.QUERIED_NAME_KEY: queried_name, utils.ANSWER_DATA_KEY: data, utils.TYPE_KEY: d_type, utils.TTL_KEY: TTL})
        queries.append({utils.TIME_KEY: time, utils.ANSWERS_KEY: answers})
    host_dictionary[utils.SUCCESS_KEY] = success
    host_dictionary[utils.QUERIES_KEY] = queries
    return host_dictionary

def get_average_ttls(filename):
    input_dicts = None
    with open(filename, 'r') as output:
        input_dicts = json.load(output)

    one_entries = 0
    one_total = 0.0
    two_entries = 0
    two_total = 0.0
    three_entries = 0
    three_total = 0.0
    four_entries = 0
    four_total = 0.0

    if input_dicts:
        for dictionary in input_dicts:
            if dictionary[utils.SUCCESS_KEY] == False:
                continue
            list_dict = dictionary[utils.QUERIES_KEY]
            root_answers = list_dict[0][utils.ANSWERS_KEY]
            tld_answers = list_dict[1][utils.ANSWERS_KEY]
            host_total = 0.0
            host_entries = 0
            temp_total = 0.0
            temp_entries = 0
            for answer in root_answers:
                temp_total += answer[utils.TTL_KEY]
                temp_entries += 1
            one_total += temp_total/temp_entries
            one_entries += 1
            temp_total = 0.0
            temp_entries = 0
            for answer in tld_answers:
                temp_total += answer[utils.TTL_KEY]
                temp_entries += 1
            two_total += temp_total/temp_entries
            two_entries += 1

            for i in range(2, len(list_dict)):
                query = list_dict[i]
                answers = query[utils.ANSWERS_KEY]
                temp_total = 0.0
                temp_entries = 0
                for answer in answers:
                    temp_total += answer[utils.TTL_KEY]
                    temp_entries += 1
                    if answer[utils.TYPE_KEY] == "A" or answer[utils.TYPE_KEY] == "CNAME":
                        host_total += answer[utils.TTL_KEY]
                        host_entries += 1
                three_total += temp_total/temp_entries
                three_entries += 1
            if host_entries > 0:
                four_entries += 1
                four_total += host_total/host_entries
        return [one_total/one_entries, two_total/two_entries, three_total/three_entries, four_total/four_entries]

def get_average_times(filename):
    input_dicts = None
    with open(filename, 'r') as output:
        input_dicts = json.load(output)

    entries = 0
    total = 0.0
    final_entries = 0
    final_total = 0.0
    if input_dicts:
        for dictionary in input_dicts:
            if dictionary[utils.SUCCESS_KEY] == False:
                continue
            entries += 1
            host_time = 0.0
            host_entries = 0
            list_dict = dictionary[utils.QUERIES_KEY]
            for query in list_dict:
                answers = query[utils.ANSWERS_KEY]
                total += query[utils.TIME_KEY]
                for answer in answers:
                    if answer[utils.TYPE_KEY] == "A" or answer[utils.TYPE_KEY] == "CNAME":
                        host_time += query[utils.TIME_KEY]
                        host_entries += 1
            if host_entries > 0:
                final_entries += 1
                final_total += host_time/host_entries
        return [total/entries, final_total/final_entries]

def generate_time_cdfs(json_filename, output_filename):
    input_dicts = None
    with open(json_filename, 'r') as output:
        input_dicts = json.load(output)

    total_time = []
    final_time = []
    if input_dicts:
        for dictionary in input_dicts:
            if dictionary[utils.SUCCESS_KEY] == False:
                continue
            total = 0.0
            list_dict = dictionary[utils.QUERIES_KEY]
            for query in list_dict:
                answers = query[utils.ANSWERS_KEY]
                final = False
                total += query[utils.TIME_KEY]
                for answer in answers:
                    if answer[utils.TYPE_KEY] == "A" or answer[utils.TYPE_KEY] == "CNAME":
                        final = True
                if final:
                    final_time.append(query[utils.TIME_KEY])
            total_time.append(total)

        total_time = np.sort(total_time)
        y = np.arange(len(total_time))/float(len(total_time)-1)
        plt.plot(total_time, y, 'r', label="total_time")

        final_time = np.sort(final_time)
        y = np.arange(len(final_time))/float(len(final_time)-1)
        plt.plot(final_time, y, 'b', label="final_time")
        plt.xscale('log')

        plt.legend()

        plt.savefig(output_filename, bbox_inches='tight')

def count_different_dns_responses(filename1, filename2):
    input_one = None
    input_two = None
    with open(filename1, 'r') as output1:
        input_one = json.load(output1)
    with open(filename2, 'r') as output2:
        input_two = json.load(output2)

    one = cddr_helper(input_one)
    for dictionary in input_two:
        input_one.append(dictionary)
    two = cddr_helper(input_one)
    return [one, two]


def cddr_helper(l):
    terminating = {}
    changed = 0
    already_changed = []

    for dictionary in l:
        host_name = dictionary[utils.NAME_KEY]
        if host_name in already_changed:
            continue
        term = []
        if dictionary[utils.SUCCESS_KEY] == False:
            continue
        list_dict = dictionary[utils.QUERIES_KEY]
        for query in list_dict:
            answers = query[utils.ANSWERS_KEY]
            for answer in answers:
                if answer[utils.TYPE_KEY] == "A" or answer[utils.TYPE_KEY] == "CNAME":
                    term.append(utils.ANSWER_DATA_KEY)
        if terminating.get(host_name) == None:
            terminating[host_name] = term
        else:
            if len(term) != len(terminating[host_name]):
                changed += 1
                already_changed.append(host_name)
                continue
            for item in term:
                if item not in terminating[host_name]:
                    changed += 1
                    already_changed.append(host_name)
                    continue
            for item in terminating[host_name]:
                if item not in term:
                    changed += 1
                    already_changed.append(host_name)
                    continue
    return changed




print get_average_times("dns_output_2.json")
print get_average_ttls("dns_output_2.json")
# generate_time_cdfs("dns_output_2.json", "dns_cdf.png")
# print count_different_dns_responses("dns_output_1.json", "dns_output_other_server.json")
# run_dig("alexa_top_100", "dns_output_1.json")
# run_dig("alexa_top_100", "dns_output_2.json")
# run_dig("alexa_top_100", "dns_output_other_server.json", '200.195.138.154')