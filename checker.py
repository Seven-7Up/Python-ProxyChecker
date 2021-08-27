#!/usr/bin/env python3

import pycurl
from io import BytesIO
import random
from sys import argv
from colorama import Fore
import json


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


    if proxy:
        session.setopt(session.PROXY, proxy)

    try:
        try:
            session.setopt(session.SSL_VERIFYHOST, 0)
            session.setopt(session.SSL_VERIFYPEER, 0)
            session.setopt(session.URL, url or proxy_judges["https"])
            session.perform()
            ssl_support = True
            debug(f"{ssl_support=}", verbose)
        except:
            session.setopt(session.URL, proxy_judges["http"])
            session.perform()
    except:
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


def check(proxy, in_check_protocols: list, verbose, force_ssl):
    protocols = {}
    timeout = 0

    for protocol in in_check_protocols:
        debug(f"Trying {protocol=}", verbose)
        res = send_requests(proxy=protocol + "://" + proxy, verbose=verbose)

        # Check if the request failed
        if not res:
            continue

        ssl_support = res["ssl_support"]
        if force_ssl and ssl_support:
            pass
        else:
            debug(f"Failed: cause {ssl_support=}", verbose=verbose)
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
        "country": country,
        "timeout": timeout
    }


def generate_proxychains(proxy=False, protocol=False):
    if proxy and protocol:
        ip_address = proxy.split(":")[0]
        port = proxy.split(":")[1]
        proxychains_file = open("proxychains.conf", "a")
        proxychains_file.write(
            "%s %s %s\n"
            % (protocol, ip_address, port)
        )
        proxychains_file.close()
    else:
        proxychains_file = open("proxychains.conf", "w")
        proxychains_file.write(
            "dynamic_chain\n"
            "proxy_dns\n"
            "remote_dns_subnet 224\n"
            "tcp_read_time_out 15000\n"
            "tcp_connect_time_out 8000\n"
            "localnet 127.0.0.0/255.0.0.0\n"
            "[ProxyList]\n"
        )
        proxychains_file.close()



def print_help():
    print(
        "%sUsage: %s [-h, --help] [-v, --verbose] [-p, --proxy proxy] [-f, --proxyfile filename] [-o, --outfile filename]\n\n"
        "  -h, --help                 : print help (current message)\n"
        "  -v, --verbose              : turn verbosity on\n"
        "  -p, --proxy       proxies  : check this proxies (separeted by comma ',')\n"
        "  -f, --proxyfile   filename : read this file and check her proxies (seperated by newline)\n"
        "  -o, --outfile     filename : write the good proxies and there info to the file (default: working_proxies.txt)\n"
        "  --protocols                : choose the right protocol for this proxies (default: http, socks4, socks5)\n"
        "  --force-ssl                : force ssl support as codition to accept any proxy\n"
        "  --gen-proxychains          : generate proxychains.conf for proxychains binary (see https://github.com/haad/proxychains)"
        % (blue, argv[0])
    )
    exit(0)


arguments = ["-h", "--help", "-v", "--verbose", "-o", "--output", "-p", "--proxy", "-f", "--proxyfile", "--protocols", "--force-ssl", "--gen-proxychains"]

verbose = False
check_proxies_line = False
check_proxies_file = False
force_ssl_suport = False
generate_proxychains_file = False
output_file = "working_proxies.txt"
in_check_protocols = ["http", "socks4", "socks5"]


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
            arg_index += 1
        elif argv[arg_index] in arguments[6: 8]:
            check_proxies_line = True
            proxies = argv[arg_index+1].split(",")
            arg_index += 1
        elif argv[arg_index] in arguments[8: 10]:
            check_proxies_file = True
            proxies_file = argv[arg_index+1]
            arg_index += 1
        elif argv[arg_index] == arguments[10]:
            in_check_protocols = argv[arg_index+1].split(",")
            for c in in_check_protocols:
                if c == "": continue
                if c not in ["http", "socks4", "socks5"]:
                    print("%sUnknow protocol: %s\n"
                          "list of proxies protocol: http, socks4, socks5"
                          % (red, c))
                    exit(1)
            arg_index += 1
        elif argv[arg_index] == arguments[11]:
            force_ssl_suport = True
            debug(f"{force_ssl_suport=}", verbose=verbose)
        elif argv[arg_index] == arguments[12]:
            generate_proxychains_file = True
            debug(f"{generate_proxychains_file=}", verbose=verbose)
        arg_index += 1
    else:
        print("%s%s %s is unknown!\n"
              "run %s --help to print infos"
              % (red, argv[0], argv[arg_index], argv[0]))
        exit(1)


if generate_proxychains_file:
    generate_proxychains()

if check_proxies_line:
    for current_proxy in proxies:
        if current_proxy == "": continue
        print("%sChecking %s proxy!" % (blue, current_proxy))
        infos = check(current_proxy, in_check_protocols, verbose=verbose, force_ssl=force_ssl_suport)
        if infos:
            print("%s%s : %s" % (green, current_proxy, infos))
            open(output_file, "a").write("%s : %s\n" % (current_proxy, infos))
            if generate_proxychains_file:
                generate_proxychains(current_proxy, random.choice(
                    ["socks5" if "socks5" in infos["protocols"] else "socks4" if "socks4" in infos["protocols"] else infos["protocols"]])[0])
        else:
            print("%sProxy %s is not working!" % (red, current_proxy))

if check_proxies_file:
    for current_proxy in [i.rstrip() for i in open(proxies_file, "r").readlines()]:
        print("%sChecking %s proxy!" % (blue, current_proxy))
        if current_proxy == "": continue
        infos = check(current_proxy, in_check_protocols, verbose=verbose, force_ssl=force_ssl_suport)
        if infos:
            print("%s%s : %s" % (green, current_proxy, infos))
            open(output_file, "a").write("%s : %s\n" % (current_proxy, infos))
            if generate_proxychains_file:
                generate_proxychains(current_proxy, random.choice(
                    ["socks5" if "socks5" in infos["protocols"] else "socks4" if "socks4" in infos["protocols"] else infos["protocols"]])[0])

        else:
            print("%sProxy %s is not working!" % (red, current_proxy))

