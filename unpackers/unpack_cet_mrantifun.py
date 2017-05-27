import zlib

keys = [
    b'\x2A\xAD\x2B\x41',      # Found in modified CE 6.4 32-bit.
    b'\x65\x42\x17\x43\x65',  # Found in modified CE 6.5 64-bit.
    b'\x65\x42\x17\x43',
]

def round_xor_const(data, ckey):
    for i in range(0, len(data)):
        data[i] = data[i] ^ ckey
        ckey = (ckey + 1) & 0xFF

def decrypt(data):
    """
    Decrypts the .CETRAINER from the CheatEngine modified by MrAntiFun.
    This corresponds to trainers published at: http://mrantifun.net/
    @param[in]  data  Original CETRAINER data as bytearray.
    """
    # Nothing to do for unprotected data
    if str(data[:5]) == "<?xml":
        print("    - Unprotected CETRAINER detected")
        return data

    result = None
    print("    - Protected CETRAINER detected. Decrypting...")
    # Apply first two waves as usual
    for i in range(2, len(data)):
        data[i] = data[i] ^ data[i-2]
    for i in range(len(data)-2, -1, -1):
        data[i] = data[i] ^ data[i+1]

    # Apply static-incrementing key relationship waves trying different keys
    for key in keys:
        try:
            print("    - Trying key: " + ":".join("{:02X}".format(c) for c in key))
            tempdata = data[:]
            for c in key:
                round_xor_const(tempdata, c)
            # Decompress if necessary and write data
            if tempdata[:5] == b'CHEAT':
                result = zlib.decompress(tempdata[5:], -15)
                result = result[4:]
                print("    - Decompressed CETRAINER using new method")
            else:
                result = zlib.decompress(tempdata, -15)
                print("    - Decompressed CETRAINER using old method")
            return result
        except Exception as e:
            pass
    raise Exception('No valid key found!')
