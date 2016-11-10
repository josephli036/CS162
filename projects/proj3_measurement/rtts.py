import subprocess
import re
import json


def median(lst):
    lst = sorted(lst)
    if len(lst) < 1:
            return None
    if len(lst) %2 == 1:
            return lst[((len(lst)+1)/2)-1]
    else:
            return float(sum(lst[(len(lst)/2)-1:(len(lst)/2)+1]))/2.0

def run_ping(hostnames, num_packets, raw_ping_output_filename, aggregated_ping_output_filename):
    raw_output = {}
    agg_output = {}
    for host in hostnames:
        print host
        ping = subprocess.Popen(["ping", "-c", num_packets, host], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, error = ping.communicate()
        if out:
            lost = int(re.findall(r".*, (\d+)% packet loss.*", out)[0])
            print lost
            split = out.split('\n')
            rtts = []
            for i in split:
                print i
                if len(rtts) == int(num_packets):
                    continue
                rtt = re.findall(r".*time=(\d+)", i)
                seq = re.findall(r".*icmp_seq=(\d+)", i)
                if seq:
                    seq = int(seq[0])
                    while len(rtts) < seq:
                        rtts.append(-1.0)
                    if rtt:
                        rtts.append(float(rtt[0]))
                    else:
                        rtts.append(-1.0)
            raw_output[host] = rtts
            agg = {}
            if lost == 100:
                agg["drop_rate"] = 100.0
                agg["max_rtt"] = -1.0
                agg["median_rtt"] = -1.0
            else:
                agg["drop_rate"] = 100 * float(lost)/float(num_packets)
                agg["max_rtt"] = sorted(rtts)[len(rtts)-1]
                agg["median_rtt"] = median(rtts[lost:])
            agg_output[host] = agg
        else:
            print 'No ping'
    with open(raw_ping_output_filename, 'w') as raw_file:
        json.dump(raw_output, raw_file)
    with open(aggregated_ping_output_filename, 'w') as aggregated_file:
        json.dump(agg_output, aggregated_file)


file = open('alexa_top_100')
websites = []
for website in file.readlines():
    websites.append(website.rstrip())
run_ping(websites, '1', 'rtt_a_raw.json', 'rtt_a_agg.json')
