import zlib

keys = [
    0xCB,  # Found in modified CE ?.? ??-bit.
    0xCF,  # Found in modified CE 6.6 64-bit.
]

def decrypt(data):
    """
    Decrypts the .CETRAINER from the CheatEngine modified by Barracuda.
    @param[in]  data  Original CETRAINER data as bytearray.
    """
    # Decrypt data if necessary
    result = None
    if str(data[:5]) == "<?xml":
        print("    - Unprotected CETRAINER detected")
        result = data
    else:
        print("    - Protected CETRAINER detected. Decrypting...")
        # Apply first two waves as usual
        for i in range(2, len(data)):
            data[i] = data[i] ^ data[i-2]
        for i in range(len(data)-2, -1, -1):
            data[i] = data[i] ^ data[i+1]

        # Apply static-incrementing key relationship waves trying different keys
        for ckey in keys:
            try:
                print("    - Trying key: 0x%02X" % ckey)
                tempdata = data[:]
                for i in range(0, len(tempdata)):
                    tempdata[i] = tempdata[i] ^ ckey
                    ckey = (ckey + 1) & 0xFF
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
