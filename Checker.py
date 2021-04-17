#!/usr/bin/env python3

import requests
from sys import argv
from colorama import Fore


def check(proxy):
    headersDic = {
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (X11; Win64 x64; rv:86.0) Gecko/20100101 Firefox/86.0",
        "Host": "httpbin.org"
    }
    proxyDic = {
        "http": "http://" + proxy,
        "https": "https://" + proxy,
    }
    r = requests.get("https://httpbin.org/ip",
                     headers=headersDic, proxies=proxyDic, timeout=10)
    print(Fore.LIGHTGREEN_EX, r.json(), ":", r.status_code)
    file_with_goods = open("good.txt", "a")
    file_with_goods.write(proxy + "\n")


def print_help():
    print(Fore.LIGHTRED_EX + "Note: The proxy should be <ip address>:<port>")
    print(Fore.LIGHTCYAN_EX + "Usage: -f <filename> - Check file with proxies")
    print(Fore.LIGHTCYAN_EX + "Usage: -p <proxy> - check only one proxy")
    print(Fore.LIGHTCYAN_EX + "Usage: --help - show this menu")


if len(argv) > 1:
    commands = ["--help", "-h", "-f", "--file", "-p", "--proxy"]
    if argv[1] in commands:
        if argv[1] in ("--help", "-h"):
            print_help()
        elif argv[1] in ("-f", "--file"):
            file = open(argv[2])
            list = file.readlines()
            print(Fore.LIGHTYELLOW_EX + "Checking " +
                  str(len(list)) + " proxies!")
            print("Please Wait :)")
            for index in range(len(list)):
                if index == "":
                    pass
                else:
                    line = list[index]
                    proxy = line.replace("\n", "")
                    try:
                        check(proxy)
                    except:
                        print(Fore.LIGHTRED_EX + proxy + " failed!")
                        pass
            file.close()
            print(Fore.LIGHTGREEN_EX + "GoodBye!")
        elif argv[1] in ("-p", "--proxy"):
            print(Fore.LIGHTYELLOW_EX + "Checking " + argv[2] + "!")
            try:
                check(argv[2])
            except:
                print(Fore.LIGHTRED_EX + "Failed!")
    else:
        print(Fore.LIGHTRED_EX + "Unknown option \"" + argv[1] + "\"")
else:
    print_help()
