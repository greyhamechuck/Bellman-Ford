from socket import *
import json
import argparse
import time


N_node = 'next_hop'
Neighbour = 'neighbour'
Distance = 'distance'


def _argparse():
    parser = argparse.ArgumentParser(description="this is descrption")
    parser.add_argument('--node', action='store',required=True, dest = 'node',
                        help='node name')
    return parser.parse_args()

# How to read a json
def read_json(file_path):
    with open(file_path,'r',encoding='utf8')as fp:
        json_data = json.load(fp)
        # print('这是文件中的json数据：',json_data)
        # print('这是读取到文件数据的数据类型：', type(json_data))
    return json_data

def update_news(socket, address, node, dv):
    for ip in address:
        msg = {node: dv}
        datasent = json.dumps(msg)
        socket.sendto(datasent.encode(), (address[ip][0], address[ip][1]))

def main():
    arg = _argparse()
    node = arg.node

    this_distan = node +'_distance.json'
    this_address = node+'_ip.json'
    output_json = node + '_output.json'

    # read them
    distance_info = read_json(this_distan)
    # print(distance_info)
    data_sent = json.dumps(distance_info)
    ip_in = read_json(this_address)
    length_neighbour = len(ip_in)

    # Initialize the output json
    output = {}
    for i in distance_info:
        output[i] = {Distance: distance_info[i], N_node: i}
    print(output)
    with open(output_json, 'w+') as f:
        json.dump(output, f)

    #UDP Get other neighbours' information
    buf = 1024
    re = socket(AF_INET, SOCK_DGRAM)
    port = ip_in[node][1]
    re.bind(('', port))

    # split neighbour_ip
    # local_addr = (ip_list[0][0],ip_list[0][1])
    ip_list_send = {}
    for i in ip_in.keys():
        # print(ip_list[i])
        # ip = (ip_list[i][0])
        # port = (ip_list[i][1])
        ip_list_send[i] = ip_in[i]
        update_news(re, ip_list_send, node, distance_info)
    # Inform others that my dv

    while True:
        # Try to get news from neighbours
        try:
            load_message, addr = re.recvfrom(buf)
            data = json.loads(load_message.decode())

            for n in data.keys():
                new_node = n
                new_distance = data[new_node]
            #Next we will compare the new distance and node_name from other neighbours with our local distance and nodes
            for i in new_distance:
                if i != node:
                    if distance_info.__contains__(i):
                        local_distance = distance_info[i]
                        temp_distance = distance_info[new_node] + new_distance[i]
                        if temp_distance < local_distance:
                            distance_info[i] = temp_distance
                            output[i] = {Distance: temp_distance, N_node: new_node}
                            # After news, you need to inform others
                            update_news(re, ip_list_send, node, distance_info)
                            time.sleep(1)
                    else:
                        # It is new nodes
                        distance_info[i] = distance_info[new_node] + new_distance[i]
                        output[i] = {Distance: distance_info[i], N_node:new_node}
                        update_news(re, ip_list_send, node, distance_info)
                        time.sleep(1)

            # output the file
            with open(output_json, 'w+') as f:
                json.dump(output, f)
        except:
            pass
if __name__ == '__main__':
    main()