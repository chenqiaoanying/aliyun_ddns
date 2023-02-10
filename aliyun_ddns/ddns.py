import click
import json
import re
import subprocess
import os

from aliyunsdkcore.client import AcsClient
from .logger import logger


def get(aliyun_client: AcsClient, domain_name, resolve_record, record_type):
    from aliyunsdkalidns.request.v20150109.DescribeSubDomainRecordsRequest import DescribeSubDomainRecordsRequest
    request = DescribeSubDomainRecordsRequest()
    request.set_accept_format('json')
    request.set_DomainName(domain_name)
    request.set_SubDomain(resolve_record + '.' + domain_name)
    request.set_Type(record_type)
    return json.loads(aliyun_client.do_action_with_exception(request))


def update(aliyun_client: AcsClient, record_id, resolve_record, record_type, value):
    from aliyunsdkalidns.request.v20150109.UpdateDomainRecordRequest import UpdateDomainRecordRequest
    request = UpdateDomainRecordRequest()
    request.set_accept_format('json')
    request.set_RecordId(record_id)
    request.set_RR(resolve_record)
    request.set_Type(record_type)
    request.set_Value(value)
    return aliyun_client.do_action_with_exception(request)


def add(aliyun_client: AcsClient, domain_name, resolve_record, record_type, value):
    from aliyunsdkalidns.request.v20150109.AddDomainRecordRequest import AddDomainRecordRequest
    request = AddDomainRecordRequest()
    request.set_accept_format('json')
    request.set_DomainName(domain_name)
    request.set_RR(resolve_record)
    request.set_Type(record_type)
    request.set_Value(value)
    return aliyun_client.do_action_with_exception(request)


def delete(aliyun_client: AcsClient, domain_name, resolve_record, record_type):
    from aliyunsdkalidns.request.v20150109.DeleteSubDomainRecordsRequest import DeleteSubDomainRecordsRequest
    request = DeleteSubDomainRecordsRequest()
    request.set_accept_format('json')
    request.set_DomainName(domain_name)
    request.set_RR(resolve_record)
    request.set_Type(record_type)
    return aliyun_client.do_action_with_exception(request)


def is_public_ipv6(address: str):
    prefix = address.partition(":")[0]
    return prefix != "" and int(prefix, 16) & int("E000", 16) == int("2000", 16)


def retrieve_public_ipv6():
    ip_result = subprocess.check_output(["ip", "-6", "a"]).decode("UTF-8")
    ipv6_addresses = re.findall(r'(?<=inet6\s)[0-9a-fA-F:]*(?=/?)', ip_result, re.U)
    public_ipv6_address = []
    for ipv6_address in ipv6_addresses:
        if is_public_ipv6(ipv6_address):
            public_ipv6_address.append(ipv6_address)
    if not public_ipv6_address:
        return
    public_ipv6_address.sort()
    return public_ipv6_address[0]


def update_dns_mapping(aliyun_client: AcsClient, subdomain: str, ipv6_address: str):
    if subdomain.count(".") == 1:
        resolve_record = "@"
        domain = subdomain
    else:
        partition_index = subdomain.rindex(".", 0, subdomain.rindex("."))
        resolve_record = subdomain[:partition_index]
        domain = subdomain[partition_index + 1:]

    try:
        domain_list = get(aliyun_client, domain, resolve_record, "AAAA")
    except:
        logger.exception("fail to get record from aliyun")
        domain_list = {'TotalCount': 0, 'DomainRecords': {}}

    if domain_list['TotalCount'] == 0:
        logger.info("域名%s的解析信息不存在。", subdomain)
    else:
        logger.info("域名%s的解析信息:%s", subdomain, domain_list['DomainRecords']['Record'])

    if domain_list['TotalCount'] == 0:
        add(aliyun_client, domain, resolve_record, "AAAA", ipv6_address)
        logger.info("新建域名%s的解析信息为%s。", subdomain, ipv6_address)
    elif domain_list['TotalCount'] == 1:
        current_record = domain_list['DomainRecords']['Record'][0]
        if current_record['Value'].strip() != ipv6_address.strip():
            update(aliyun_client, current_record['RecordId'], resolve_record, "AAAA", ipv6_address)
            logger.info("修改域名%s的解析信息为%s。", subdomain, ipv6_address)
        else:
            logger.info("IPv6地址没变，无需更新DNS.")
    elif domain_list['TotalCount'] > 1:
        delete(aliyun_client, domain, subdomain, "AAAA")
        add(aliyun_client, domain, subdomain, "AAAA", ipv6_address)
        logger.info("修改域名%s的解析信息为%s。", subdomain, ipv6_address)


def check_ipv6_address(on_ip_change):
    filename = "/var/run/ddns_ipv6_address"
    current_ipv6_address = retrieve_public_ipv6()
    if not current_ipv6_address:
        logger.info("无公网IPv6地址")
        return

    if os.path.exists(filename):
        with open(filename, 'r') as file:
            previous_ipv6_address = file.readline()
            ip_change = not current_ipv6_address == previous_ipv6_address
    else:
        ip_change = True

    if ip_change:
        logger.info("IPv6地址已改变: %s", current_ipv6_address)
        on_ip_change(current_ipv6_address)
        with open(filename, 'w') as file:
            file.write(current_ipv6_address)


def ddns(key, secret, domains):
    aliyun_client = AcsClient(key, secret)

    def update_dns(ipv6_address: str):
        for domain in domains:
            update_dns_mapping(aliyun_client, domain, ipv6_address)

    check_ipv6_address(update_dns)


@click.command()
@click.option("--key", required=True, help="aliyun access key id")
@click.option("--secret", required=True, help="aliyun secret key id")
@click.argument("domains", required=True, nargs=-1)
def cli(key, secret, domains):
    ddns(key, secret, domains)
