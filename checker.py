#!/usr/bin/env python3

import pycurl
from io import BytesIO
import random
from sys import argv
from colorama import Fore
import json
import signal


proxy_judges = {
    "https": "https://httpbin.org/get",
    "http": "http://httpbin.org/get"
}

### Colors ########################################
red = Fore.RED
green = Fore.GREEN
blue = Fore.LIGHTBLUE_EX
magenta = Fore.MAGENTA
reset = Fore.RESET
###################################################


def debug(string: str, verbose):
    if verbose:
        print("%sDEBUG: %s%s" % (magenta, reset, string), flush=True)


def send_requests(proxy=None, url=None, verbose=False):
    session = pycurl.Curl()
    response = BytesIO()
    ssl_support = False

    session.setopt(session.WRITEDATA, response)
    session.setopt(session.TIMEOUT, 5)

    # session.setopt(session.SSL_VERIFYHOST, 0)
    # session.setopt(session.SSL_VERIFYPEER, 0)

    if proxy:
        session.setopt(session.PROXY, proxy)

    try:
        try:
            session.setopt(session.URL, url or proxy_judges["https"])
            session.perform()
            ssl_support = True
            debug(f"{ssl_support=}", verbose)
        except:
            session.setopt(session.URL, proxy_judges["http"])
            session.perform()
    except Exception as e:
        # print(e)
        return False

    # Return False if the status is not 200
    if session.getinfo(session.HTTP_CODE) != 200:
        debug(f"{session.HTTP_CODE=}", verbose)
        return False

    # Calculate the request timeout in milliseconds
    timeout = round(session.getinfo(session.CONNECT_TIME) * 1000)
    debug(f"{timeout=}", verbose)

    # Decode the response content
    response = response.getvalue().decode("iso-8859-1")

    return {"timeout": timeout, "ssl_support": ssl_support, "response": response}


def get_ip():
    response = send_requests(url="https://api.ipify.org/")
    if not response:
        return ""

    return response["response"]


self_ip = get_ip()


def check_anonymity(response):
    privacy_headers = [
        "VIA",
        "X-FORWARDED-FOR",
        "X-FORWARDED",
        "FORWARDED-FOR",
        "FORWARDED-FOR-IP",
        "FORWARDED",
        "CLIENT-IP",
        "PROXY-CONNECTION"
    ]

    if any([header in response for header in privacy_headers]):
        return "Anonymous"

    return "Elite"


def get_country(ip):
    res = send_requests(url="https://ip2c.org/" + ip)

    if res and res["response"][0] == "1":
        res = res["response"].split(";")
        return [res[3], res[1]]

    return ["-", "-"]


def check(proxy, verbose):
    protocols = {}
    timeout = 0

    for protocol in ["http", "https", "socks4", "socks5"]:
        debug(f"Trying {protocol=}", verbose)
        res = send_requests(proxy=protocol + "://" + proxy, verbose=verbose)

        # Check if the request failed
        if not res:
            continue

        protocols[protocol] = res
        timeout += res["timeout"]
        debug(f"{protocol} is working!", verbose)

    if (len(protocols) == 0):
        return False

    random_protocol = random.choice(list(protocols.keys()))
    r = protocols[random_protocol]["response"]
    ssl_support = protocols[random_protocol]["ssl_support"]

    country = get_country(proxy.split(":")[0])
    anonymity = check_anonymity(r)
    timeout = timeout // len(protocols)

    return {
        "proxy_address": json.loads(r)["origin"],
        "ssl_support": ssl_support,
        "protocols": list(protocols.keys()),
        "anonymity": anonymity,
        "timeout": timeout
    }


def print_help():
    print(
        "%sUsage: %s [-h, --help] [-v, --verbose] [-p, --proxy proxy] [-f, --proxyfile filename] [-o, --outfile filename]\n\n"
        "  -h, --help               : print help (current message)\n"
        "  -v, --verbose            : turn verbosity on\n"
        "  -p, --proxy     proxies  : check this proxies (separeted by comma ',')\n"
        "  -f, --proxyfile filename : read this file and check her proxies (seperated by newline)\n"
        "  -o, --outfile   filename : write the good proxies and there info to the file"
        % (blue, argv[0])
    )
    exit(0)


verbose = False
arguments = ["-h", "--help", "-v", "--verbose", "-o",
             "--output", "-p", "--proxy", "-f", "--proxyfile"]
output_file = "working_proxies.txt"


if len(argv) <= 1:
    print_help()

arg_index = 1
while arg_index < len(argv):
    if argv[arg_index] in arguments:
        if argv[arg_index] in arguments[0: 2]:
            print_help()
        elif argv[arg_index] in arguments[2: 4]:
            verbose = True
            debug(f"{verbose=}", verbose)
        elif argv[arg_index] in arguments[4: 6]:
            output_file = argv[arg_index+1]
        elif argv[arg_index] in arguments[6: 8]:
            for current_proxy in argv[arg_index+1].split(","):
                print("%sCheking %s proxy!" % (blue, current_proxy))
                if current_proxy == "":
                    break
                infos = check(current_proxy, verbose=verbose)
                if infos:
                    print("%s%s : %s" % (green, current_proxy, infos))
                    open(output_file, "a").write(
                        "%s : %s\n" % (current_proxy, infos))
                else:
                    print("%sProxy %s is not working!" % (red, current_proxy))
            arg_index += 2
        elif argv[arg_index] in arguments[8: 10]:
            for current_proxy in [i.rstrip() for i in open(argv[arg_index+1], "r").readlines()]:
                signal.signal(signal.SIGINT, lambda s, f: exit(0))
                print("%sCheking %s proxy!" % (blue, current_proxy))
                if current_proxy == "":
                    break
                infos = check(current_proxy, verbose=verbose)
                if infos:
                    print("%s%s : %s" % (green, current_proxy, infos))
                    open(output_file, "a").write(
                        "%s : %s\n" % (current_proxy, infos))
                else:
                    print("%sProxy %s is not working!" % (red, current_proxy))
            arg_index += 2
    else:
        print("%s%s %s is unknown!\n"
              "run %s --help to print infos"
              % (red, argv[0], argv[arg_index], argv[0])
              )
        exit(1)

    arg_index += 1
