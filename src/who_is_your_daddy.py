from tabulate import tabulate
from whois import whois
from argparse import ArgumentParser

def get_whois_data(domain):
    whois_data = whois(domain)
    result = []
    for key, value in whois_data.items():
        if 'Prohibited' in str(value):
            continue
        if isinstance(value, list):
            value = ", ".join(map(str, value))
        elif value is None:
            continue
        else:
            value = str(value)
        
        result.append([key, value])

    return result

parser = ArgumentParser()
parser.add_argument('domain', help='Domain to get whois records for')
parser.add_argument('-f', '--format', help='Output table format', default='github')
parser.add_argument('-r', '--raw', help='Output as plain text', action='store_true')

args = parser.parse_args()
data = get_whois_data(args.domain)
if args.raw:
    for field, value in data:
        print(f'{field}: {value}')
else:
    table = tabulate(data, headers=["Field", "Value"], tablefmt=args.format)
    print(table)
