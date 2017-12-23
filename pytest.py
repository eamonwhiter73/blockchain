import json

i = 1
f = open('blockchain.txt')
for line in f.readlines():
    print(line)
    if i != json.loads(line)['index']:
        print(f'\n //// something is wrong indexes dont match, index: {i}')
    i += 1