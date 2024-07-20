import sys
import zlib

def parse_end(bs):
    return None, 0

def parse_byte(bs):
    return int.from_bytes(bs[0:1], byteorder='big', signed=True), 1

def parse_short(bs):
    return int.from_bytes(bs[0:2], byteorder='big', signed=True), 2

def parse_int(bs):
    return int.from_bytes(bs[0:4], byteorder='big', signed=True), 4
    
def parse_long(bs):
    return int.from_bytes(bs[0:8], byteorder='big', signed=True), 8

def parse_float(bs):
    return float.from_bytes(bs[0:4]), 4

def parse_double(bs):
    return float.from_bytes(bs[0:8]), 8

def parse_byte_array(bs):
    size = int.from_bytes(bs[0:4], byteorder='big', signed=True)
    return bs[4:4+size], 4+size

def parse_string(bs):
    length = int.from_bytes(bs[0:2], byteorder='big', signed=True)
    return bs[2:2+length].decode('utf-8'), 2+length

def parse_list(bs):
    type = bs[0]
    func = parse_funcs[type]
    size = int.from_bytes(bs[1:5], byteorder='big', signed=True)
    items = []

    len = 5

    for i in range(size):
        res, nlen = func(bs[len:])
        items.append(res)
        len += nlen

    return items, len

def parse_compound(bs):
    res = {}
    len = 0

    while True:
        (nxt, nlen) = parse_nbt(bs[len:])
        len += nlen

        if nxt == None:
            break

        res = res | nxt

    return res, len

def parse_int_array(bs):
    size = int.from_bytes(bs[0:4], byteorder='big', signed=True)
    items = []

    len = 4

    for i in range(size):
        nxt, _ = parse_int(bs[len:])
        items.append(nxt)
        len += 4

    return items, len

def parse_long_array(bs):
    size = int.from_bytes(bs[0:4], byteorder='big', signed=True)
    items = []

    len = 4

    for i in range(size):
        nxt, _ = parse_long(bs[len:])
        items.append(nxt)
        len += 8

    return items, len


parse_funcs = [
    parse_end,
    parse_byte,
    parse_short,
    parse_int,
    parse_long,
    parse_float,
    parse_double,
    parse_byte_array,
    parse_string,
    parse_list,
    parse_compound,
    parse_int_array,
    parse_long_array
]

def parse_nbt(bs):
    ty = bs[0]

    # TAG_End
    if ty == 0:
        return None, 1
    
    name_len = int.from_bytes(bs[1:3], byteorder='big', signed=False)
    name = bs[3:3+name_len].decode('utf-8')

    bs = bs[3+name_len:]
    res, len = parse_funcs[ty](bs)
    return { name : res }, len+3+name_len


if __name__ == "__main__":
    # open and read the file
    f = open(".minecraft/saves/superflat/region/r.0.0.mca", "rb")
    data = f.read()

    # skip to the chunks section and parse the length of the first chunk
    payload = data[0x2000:]
    length = int.from_bytes(payload[:4], byteorder='big', signed=False)

    # compression type *must* be zlib
    assert payload[4] == 2

    # decompress the chunk data
    chunk_comp = payload[5:length-1+5]
    assert len(chunk_comp) == length-1
    
    chunk = zlib.decompress(chunk_comp)
    nbt, _ = parse_nbt(chunk)
    print(nbt)
    breakpoint()
