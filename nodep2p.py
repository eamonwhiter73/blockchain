from pyp2p.net import *
import time
import grequests
import requests
import pprint
import json

#Setup node's p2p node.
node = Net(passive_bind='192.168.1.131', passive_port=44445, node_type='passive', debug=1)
node.start()
node.bootstrap()
node.advertise()

port = "5000"
connections = []
first_time = True
#Event loop.
while 1:
    if not first_time or len(node.inbound) == 0:
        r = requests.get('http://0.0.0.0:5000/mine')
        print('\n //// last block mined\n')
        print(r.text)

    for con in node:
        con.send_line(port)
        for reply in con:
            print('\n //// GOT REPLY\n')
            print(reply)
            is_digit = False
            if reply.isdigit():
                found = False
                is_digit = True
                for index, item in enumerate(connections):
                    if item['ip'] == con.addr:
                        item['port'] = reply
                        found = True

                if not found:
                    print('\n //// Adding connection to connections\n')
                    connections.append({'ip': con.addr, 'port': reply})

            if is_digit and first_time:
                r = requests.get('http://' + con.addr + ':' + reply + '/chain_length')
                print('\n //// first time chain length from neighbor')
                print(r.text)
                
                first_time = False

    time.sleep(1)