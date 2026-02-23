import argparse
import binascii
import re
import struct
from dataclasses import dataclass


def ve(v):
    """Encode integer as RAR5 variable-length integer."""
    r = bytearray()
    while True:
        b = v & 0x7F
        v >>= 7
        if v:
            b |= 0x80
        r.append(b)
        if not v:
            break
    return bytes(r)


def vd(data, offset):
    """Decode RAR5 vint at offset, return (value, new_offset)."""
    val = 0
    shift = 0
    while True:
        b = data[offset]
        val |= (b & 0x7F) << shift
        shift += 7
        offset += 1
        if not (b & 0x80):
            break
    return val, offset


def hdr(payload):
    """Build RAR5 header: CRC32 + payload."""
    crc = binascii.crc32(payload) & 0xFFFFFFFF
    return struct.pack('<I', crc) + payload


def parse_extra_area(raw, offset, size):
    """Parse extra area records, return dict of {type: data}."""
    records = {}
    end = offset + size
    while offset < end:
        rec_size, offset = vd(raw, offset)
        rec_start = offset
        rec_type, offset = vd(raw, offset)
        rec_data = raw[offset:rec_start + rec_size]
        records[rec_type] = rec_data
        offset = rec_start + rec_size
    return records


@dataclass
class Entry:
    type: int
    name: str
    data_offset: int
    data_size: int
    unpack_size: int
    data_crc: int
    comp_info: int
    stream_name: str


def parse_rar5(raw):
    """Parse all RAR5 headers and yield Entry objects."""
    assert raw[:8] == b'Rar!\x1a\x07\x01\x00', "Not a RAR5 archive"
    pos = 8

    while pos < len(raw):
        if pos + 7 > len(raw):
            break
        pos += 4
        hdr_size, pos = vd(raw, pos)
        body_end = pos + hdr_size

        hdr_type, p = vd(raw, pos)
        hdr_flags, p = vd(raw, p)

        extra_size = 0
        data_size = 0
        if hdr_flags & 0x01:
            extra_size, p = vd(raw, p)
        if hdr_flags & 0x02:
            data_size, p = vd(raw, p)

        if hdr_type == 5:
            break

        name = ""
        unpack_size = 0
        data_crc = 0
        comp_info = 0
        stream_name = ""

        if hdr_type in (2, 3):
            file_flags, p = vd(raw, p)
            unpack_size, p = vd(raw, p)
            _attrib, p = vd(raw, p)
            if file_flags & 0x02:
                p += 4
            if file_flags & 0x04:
                data_crc = struct.unpack_from('<I', raw, p)[0]
                p += 4
            comp_info, p = vd(raw, p)
            _host_os, p = vd(raw, p)
            name_len, p = vd(raw, p)
            name = raw[p:p + name_len].decode('utf-8', errors='replace')
            p += name_len

            if extra_size > 0:
                extra_records = parse_extra_area(raw, body_end - extra_size, extra_size)
                if 7 in extra_records:
                    sn = extra_records[7].rstrip(b'\x00').decode('utf-8', errors='replace')
                    stream_name = sn

        data_offset = body_end
        yield Entry(
            type=hdr_type,
            name=name,
            data_offset=data_offset,
            data_size=data_size,
            unpack_size=unpack_size,
            data_crc=data_crc,
            comp_info=comp_info,
            stream_name=stream_name,
        )
        pos = body_end + data_size


def filename_from_stream(stream_name):
    r"""Extract a safe filename from an ADS stream path like ':..\..\..\path\to\file.bat'."""
    cleaned = stream_name.lstrip(':')
    basename = cleaned.replace('\\', '/').rsplit('/', 1)[-1]
    basename = re.sub(r'[<>:"/\\|?*]', '_', basename)
    return basename or 'extracted'


def default_filename(entry):
    if entry.stream_name:
        return filename_from_stream(entry.stream_name)
    if entry.name and entry.type == 2:
        return entry.name
    return "extracted.bin"


def build_single_file_rar(raw, entry, filename):
    cd = raw[entry.data_offset:entry.data_offset + entry.data_size]
    fname = filename.encode("utf-8")
    body = (
        ve(2)                               +  # type: file header
        ve(0x02)                            +  # flags: data area present
        ve(len(cd))                         +  # data size
        ve(0x04)                            +  # file flags: CRC32 present
        ve(entry.unpack_size)               +  # unpacked size
        ve(0x20)                            +  # attributes
        struct.pack("<I", entry.data_crc)   +  # data CRC32
        ve(entry.comp_info)                 +  # compression info
        ve(0)                               +  # host OS
        ve(len(fname))                      +  # name length
        fname                                  # file name
    )
    fhdr = hdr(ve(len(body)) + body)
    eoa = hdr(ve(2) + ve(5) + ve(0))
    return raw[:24] + fhdr + cd + eoa


def select_target(parser, entries, index):
    if index is not None:
        if index < 0 or index >= len(entries):
            parser.error(f"Index {index} out of range (0-{len(entries)-1})")
        target = entries[index]
        if target.data_size == 0:
            parser.error(f"Entry [{index}] has no data area")
        return target

    stm = [entry for entry in entries if entry.type == 3 and entry.data_size > 0]
    if not stm:
        parser.error("No STM service headers with data found. Use -l to inspect.")
    return stm[0]


def print_entries(path, raw, entries):
    type_names = {1: 'MAIN', 2: 'FILE', 3: 'SERVICE', 4: 'CRYPT', 5: 'END'}
    print(f"[+] {path} ({len(raw)} bytes) — {len(entries)} entries\n")
    for index, entry in enumerate(entries):
        tn = type_names.get(entry.type, f"UNK({entry.type})")
        line = ( # Pwetty format
            f"[{index:2d}] {tn:8s} name={entry.name!r} "
            f"data={entry.data_size}B unpack={entry.unpack_size}B "
            f"crc=0x{entry.data_crc:08x} comp=0x{entry.comp_info:x}"
        )
        if entry.stream_name:
            line += f" stream={entry.stream_name!r}"
        print(line)


def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('input', help="Path to the RAR5 archive containing ADS entries")
    parser.add_argument('-l', '--list', action='store_true', help="List all headers and exit")
    parser.add_argument('-e', '--entry', type=int, default=None, help="Entry index to extract (default: first STM)")
    parser.add_argument('-o', '--output', default=None, help="Output RAR5 path (default: <filename>.rar)")
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    with open(args.input, 'rb') as f:
        raw = f.read()

    entries = list(parse_rar5(raw))

    if args.list:
        print_entries(args.input, raw, entries)
        return

    target = select_target(parser, entries, args.entry)
    filename = default_filename(target)
    out_rar = args.output or f"{filename}.rar"
    out = build_single_file_rar(raw, target, filename)

    with open(out_rar, 'wb') as f:
        f.write(out)

    print(f"[+] Extracted entry: {target.name!r} "
          f"({target.data_size}B -> {target.unpack_size}B)")
    if target.stream_name:
        print(f"    Stream: {target.stream_name}")
    print(f"[+] Created {out_rar} ({len(out)} bytes)")
    print(f"    Extract with: unrar x {out_rar}")


if __name__ == '__main__':
    main()
