import itertools
import subprocess
import sys
import threading
import time
from collections import defaultdict
from urllib.parse import unquote
import re

PCAP = ""
NOT_ORD_RE = re.compile(r"OR NOT ORD\(MID\((\(.+?\)),(\d+),1\)\)>(\d+)--", re.I)
ORD_RE = re.compile(r"OR ORD\(MID\((\(.+?\)),(\d+),1\)\)>(\d+)--", re.I)


def _spinner(stop_event, msg):
    chars = itertools.cycle(r"/-\|")
    while not stop_event.is_set():
        sys.stdout.write(f"\r  {msg} {next(chars)}   ")
        sys.stdout.flush()
        time.sleep(0.1)
    sys.stdout.write(f"\r  {msg} done.\n")
    sys.stdout.flush()


def run_tshark(*args, progress_msg=None):
    cmd = ["tshark", "-r", PCAP] + list(args)
    stop = threading.Event()
    if progress_msg:
        t = threading.Thread(target=_spinner, args=(stop, progress_msg), daemon=True)
        t.start()
    try:
        resp = subprocess.run(cmd, capture_output=True, text=True)
    finally:
        if progress_msg:
            stop.set()
            t.join()
    if resp.returncode != 0 and resp.stderr:
        print(resp.stderr, file=sys.stderr)
        sys.exit(1)
    return resp.stdout


def parse_requests():
    """Extract HTTP requests: stream -> [(frame, uri)]"""
    out = run_tshark(
        "-Y", "http.request.method==GET",
        "-T", "fields", "-E", "separator=\t",
        "-e", "frame.number", "-e", "tcp.stream", "-e", "http.request.uri",
        progress_msg="[1/3] Extracting HTTP requests"
    )
    stream_requests = defaultdict(list)
    for line in out.strip().split("\n"):
        if not line: continue
        
        parts = line.split("\t", 2)
        if len(parts) < 3: continue
        
        try:
            frame = int(parts[0])
            stream = int(parts[1])
            uri = unquote(parts[2].strip()) if parts[2].strip() else ""
        except (ValueError, IndexError):
            continue
        
        stream_requests[stream].append((frame, uri))

    return stream_requests


def extract_responses(stream_requests):
    """Run tshark for TRUE/FALSE packets, match to requests. Returns [(uri, result)]"""
    response_true = run_tshark(
        "-Y", 'frame contains "exists in the database"',
        "-T", "fields", "-E", "separator=\t",
        "-e", "frame.number", "-e", "tcp.stream",
        progress_msg="[2/3] Extracting TRUE responses"
    )
    response_false = run_tshark(
        "-Y", 'frame contains "MISSING from the database"',
        "-T", "fields", "-E", "separator=\t",
        "-e", "frame.number", "-e", "tcp.stream",
        progress_msg="[3/3] Extracting FALSE responses"
    )

    responses = {}
    for response, result in [(response_true, "TRUE"), (response_false, "FALSE")]:
        for line in response.strip().split("\n"):
            if not line: continue

            parts = line.split("\t")
            if len(parts) < 2: continue
            
            try:
                response_frame, stream = map(int, parts)
            except (ValueError, IndexError):
                continue

            requests = stream_requests.get(stream, [])
            best = None
            for request_frame, uri in requests:
                if request_frame < response_frame and (best is None or request_frame > best[0]):
                    best = (request_frame, uri)
            
            if best:
                request_frame, uri = best
                responses[(stream, request_frame)] = result

    requests_with_resp = []
    for stream, requests in stream_requests.items():
        for request_frame, uri in requests:
            response = responses.get((stream, request_frame))
            if response:
                requests_with_resp.append((uri, response))

    return requests_with_resp


def extract_searches(requests_with_resp):
    """Parse ORD(MID(...)) from URIs. Returns (query, pos) -> [(num, op)]"""
    searches = defaultdict(list)
    for uri, resp in requests_with_resp:
        m = NOT_ORD_RE.search(uri)
        if m:
            q, pos, num = m.group(1), int(m.group(2)), int(m.group(3))
            searches[(q, pos)].append((num, "<=" if resp == "TRUE" else ">"))
            continue
        m = ORD_RE.search(uri)
        if m:
            q, pos, num = m.group(1), int(m.group(2)), int(m.group(3))
            searches[(q, pos)].append((num, ">" if resp == "TRUE" else "<="))
    return searches


def resolve_chars(searches):
    """Convert binary search bounds to characters. Returns query -> {pos: char}"""
    queries = defaultdict(dict)
    for (query, pos), comparisons in searches.items():
        lower, upper = 0, 127
        for num, op in comparisons:
            if op == ">":
                lower = max(lower, num)
            else:
                upper = min(upper, num)
                
        val = upper if upper >= lower else lower
        if val == 0:
            continue
        if 32 <= val <= 126:
            queries[query][pos] = chr(val)
        else:
            queries[query][pos] = f"[{val}]"

    return queries


def main():
    stream_requests = parse_requests()
    requests_with_resp = extract_responses(stream_requests)

    total_reqs = sum(len(v) for v in stream_requests.values())
    print(f"Requests: {total_reqs}, Matched: {len(requests_with_resp)}")

    print("  Parsing injection payloads...", flush=True)
    searches = extract_searches(requests_with_resp)
    queries = resolve_chars(searches)

    print(f"\n=== LEAKED DATA ({len(queries)} queries) ===")
    for query in sorted(queries.keys(), key=lambda q: min(queries[q].keys())):
        positions = queries[query]
        result = "".join(positions[k] for k in sorted(positions))
        short = query[:80] + "..." if len(query) > 80 else query
        print(f"\nQuery: {short}")
        print(f"Data:  {result}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        PCAP = sys.argv[1]
    else:
        print(f"Usage: python {sys.argv[0]} <pcap file>")
        exit(1)
        
    main()
