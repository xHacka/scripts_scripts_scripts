import asyncio
import aiohttp
from argparse import ArgumentParser

URL = 'https://api.first.org/data/v1/epss'

async def check_single_cve(session, cve):
    async with session.get(URL, params={'cve': cve}) as response:
        data = await response.json()
        if len(data['data']) == 0:
            return f'{cve}: No data'
        epss = float(data['data'][0]['epss']) * 100
        return f'{cve}: {epss:.2f}%'

async def epss_check(cves):
    async with aiohttp.ClientSession() as session:
        tasks = [check_single_cve(session, cve.strip()) for cve in cves]
        results = await asyncio.gather(*tasks)
        return results

async def main():
    parser = ArgumentParser()
    parser.add_argument('-f', '--file', help='File to read CVEs from', required=False)
    parser.add_argument('-c', '--cve', help='CVE to check', required=False)

    args = parser.parse_args()
    if args.file:
        with open(args.file, 'r', encoding='utf-8') as f:
            cves = [line.strip() for line in f if line.strip()]
    elif args.cve:
        cves = [args.cve]
    else:
        parser.print_help()
        exit(1)

    results = await epss_check(cves)
    for result in results:
        print(result)

if __name__ == '__main__':
    asyncio.run(main())
