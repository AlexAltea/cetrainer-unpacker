import zlib

def decrypt(data):
    """
    Decrypts the .CETRAINER from the original CheatEngine.
    @param[in]  data  Original CETRAINER data as bytearray.
    """
    # Decrypt data if necessary
    result = None
    if str(data[:5]) == "<?xml":
        print("    - Unprotected CETRAINER detected")
        result = data
    else:
        print("    - Protected CETRAINER detected. Decrypting...")
        ckey = 0xCE
        for i in range(2, len(data)):
            data[i] = data[i] ^ data[i-2]
        for i in range(len(data)-2, -1, -1):
            data[i] = data[i] ^ data[i+1]
        for i in range(0, len(data)):
            data[i] = data[i] ^ ckey
            ckey = (ckey + 1) & 0xFF

        # Decompress if necessary and write data
        if data[:5] == b'CHEAT':
            result = zlib.decompress(data[5:], -15)
            result = result[4:]
            print("    - Decompressed CETRAINER using new method")
        else:
            result = zlib.decompress(data, -15)
            print("    - Decompressed CETRAINER using old method")
    return result
