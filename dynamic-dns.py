import urllib.request
import boto3
import socket

ZONE_ID = 'Z5I4NVRJK5HQ'
NAME = 'sub.mydomain.com'
TYPE = 'A'
TTL = 300

def is_valid_ipv4_address(address):
    try:
        socket.inet_pton(socket.AF_INET, address)
    except AttributeError:
        try:
            socket.inet_aton(address)
        except socket.error:
            return False
        return address.count('.') == 3
    except socket.error:
        return False
    return True


def upsert_route53_record(public_ip):
    client = boto3.client('route53')

    client.change_resource_record_sets(
        HostedZoneId= ZONE_ID,
        ChangeBatch={
            'Changes': [
                {
                    'Action': 'UPSERT',
                    'ResourceRecordSet': {
                        'Name': NAME,
                        'Type': TYPE,
                        'TTL': TTL,
                        'ResourceRecords': [
                                {
                                    'Value': public_ip
                                },
                        ]
                    }
                },
            ]
        }
    )


def read_saved_public_ip():
    if is_empty_saved_public_ip():
      return ''
    else:
      with open('last_public_ip', 'r') as f:
          content = f.read()
          return content


def write_public_ip(public_ip):
    with open('last_public_ip', 'w') as f:
        f.write(public_ip)


def is_empty_saved_public_ip():
    f = open('last_public_ip', 'w+')
    if not f.read(1):
      f.close()
      return True
    else:
      f.close()
      return False


public_ip = urllib.request.urlopen('http://api.ipify.org/').read().decode('utf8')

# validate ipify response
if is_valid_ipv4_address(public_ip):
    saved_public_ip = read_saved_public_ip()
    if saved_public_ip != public_ip:
      upsert_route53_record(public_ip)
      write_public_ip(public_ip)
else:
    # backup service
    public_ip = urllib.request.urlopen('http://ident.me').read().decode('utf8')
    if is_valid_ipv4_address(public_ip):
      saved_public_ip = read_saved_public_ip()
      if saved_public_ip != public_ip:
        upsert_route53_record(public_ip)
        write_public_ip(public_ip)
