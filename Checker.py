#!/usr/share/python3

import requests
from sys import argv

def check(proxy):
    headers = {
        'Accept':'application/json',
        'User-Agent':'Mozilla/5.0 (X11; Win64 x64; rv:86.0) Gecko/20100101 Firefox/86.0',
        }
    r = requests.get('https://httpbin.org/ip', headers=headers, proxies={'http': 'http://' + proxy, 'https': 'https://' + proxy}, timeout=7)
    print(r.status_code)
    file_with_goods = open('good.txt','a')
    file_with_goods.write(proxy)

def print_help():
    print('Usage: -f <filename> - Check file with proxies')
    print('Usage: -p <proxy> - check only one proxy')
    print('Usage: --help - show this menu')

if len(argv) > 1:
    commands = ['--help','-h','-f','-p','--file','--proxy']
    if argv[1] in commands:
        if argv[1] in ('--help','-h'):
            print_help()
        elif argv[1] in ('-f','--file'):
            file = open(argv[2])
            list = file.readlines()
            print('Checking ' + str(len(list)) + ' proxies!')
            print('Please Wait :)')
            for line in range(len(list)):
                proxy = list[line]
                try:
                    check(proxy)
                except:
                    pass
            file.close()
            print('GoodBye!')
            exit()
        elif argv[1] in ('-p','--proxy'):
            argv[2] = argv[2].split(' ')[0]
            try:
                check(argv[2])
            except:
                print('Failed!')
    else:
        print('Unknown option \"' + argv[1] + '\"')
else:
    print_help()