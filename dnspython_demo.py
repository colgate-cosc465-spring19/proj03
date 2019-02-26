#!/usr/bin/python3

import dns.resolver
import ipaddress

def print_record(record):
    # IPv4 address
    if (record.rdtype == dns.rdatatype.A):
        ipv4_address = record.address
        print('\t\tA %s' % (ipv4_address))
    # Name server domain name
    elif (record.rdtype == dns.rdatatype.NS):
        name_server_domain_name = record.target
        print('\t\tNS %s' % (name_server_domain_name))
    # Canonical name (i.e., alias)
    elif (record.rdtype == dns.rdatatype.CNAME):
        canonical_domain_name = record.target
        print('\t\tCNAME %s' % (canonical_domain_name))
    # Other type of record
    else:
        print('\t\t%s' % (record))

def print_record_set(record_set):
    domain_name = record_set.name
    print('\t%s' % (domain_name))
    for record in record_set:
        print_record(record)

def print_response(response):
    # Response code
    response_code = response.rcode()
    response_description = dns.rcode.to_text(response_code)
    print('Response code: %d %s' % (response_code, response_description))

    # Options
    print('Options:')
    for option in response.options:
        if (option.otype == dns.edns.ECS):
            print('\tECS %s/%d' % (option.address, option.scopelen))
        else:
            print(opt)

    # Answer
    print('Answers:')
    for record_set in response.answer:
        print_record_set(record_set)

    # Additional
    print('Additional:')
    for record_set in response.additional:
        print_record_set(record_set)

def construct_query(domain, record_type, client_network=None):
    if client_network is None:
        query = dns.message.make_query(domain, record_type)
    else:
        network_address = str(client_network.network_address)
        network_prefixlen = client_network.prefixlen
        ecs = dns.edns.ECSOption(network_address, network_prefixlen)
        query = dns.message.make_query(domain, record_type, use_edns=True, 
                options=[ecs])
    return query

def issue_query(domain, ns_ip, client_network=None):
    # Create query
    record_type = 'A' # Type of record to request
    print('Query name server %s for %s record for %s for client %s' % 
            (ns_ip, record_type, domain, client_network))
    query = construct_query(domain, record_type, client_network)

    # Issue query
    tout = 3 # Timeout in seconds
    try:
        response = dns.query.udp(query, ns_ip, timeout=tout)
    except dns.exception.Timeout:
        print('Query timed out')
        return

    # Print response
    print_response(response)
    
def main():
    # Query recursive resolver for www.colgate.edu
    RECURSIVE_RESOLVER = '149.43.80.9'
    issue_query('www.colgate.edu', RECURSIVE_RESOLVER)

    # Query Google name server for www.google.com
    GOOGLE_NAME_SERVER = '216.239.32.10'
    client_network = ipaddress.ip_network('149.43.80.0/22')
    issue_query('www.google.com', GOOGLE_NAME_SERVER, client_network)

if __name__ == '__main__':
    main()
