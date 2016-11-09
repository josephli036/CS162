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
        ping = subprocess.Popen(["ping", "-n", num_packets, host], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, error = ping.communicate()
        if out:
            maximum = float(re.findall(r"Maximum = (\d+)", out)[0])
            lost = int(re.findall(r"Lost = (\d+)", out)[0])
            split = out.split('\n')
            rtts = []
            for i in split:
                # print i
                rtt = re.findall(r".*time=(\d+)", i)
                if rtt:
                    # print float(rtt[0])
                    rtts.append(float(rtt[0]))
                elif i == "Request timed out.\r":
                    # print -1.0
                    rtts.append(-1.0)
            raw_output[host] = rtts
            agg = {}
            agg["drop_rate"] = 100 * float(lost)/float(num_packets)
            if lost == int(num_packets):
                agg["drop_rate"] = 100.0
                agg["max_rtt"] = -1.0
                agg["median_rtt"] = -1.0
            else:
                agg["drop_rate"] = 100 * float(lost)/float(num_packets)
                agg["max_rtt"] = maximum
                agg["median_rtt"] = median(rtts[lost:])
            agg_output[host] = agg
        else:
            print 'No ping'
    with open(raw_ping_output_filename, 'w') as raw_file:
        json.dump(raw_output, raw_file)
    with open(aggregated_ping_output_filename, 'w') as aggregated_file:
        json.dump(agg_output, aggregated_file)

run_ping(['google.com'], '10', 'rtt_a_raw.json', 'rtt_a_agg.json')
