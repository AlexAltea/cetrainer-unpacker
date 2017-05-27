import frida
import threading
import shlex
import sys

# Unpackers
from unpackers import unpack_cet
from unpackers import unpack_cet_barracuda
from unpackers import unpack_cet_mrantifun

code = """
'use strict';

// Static
var cet_handle = 0;
var cet_path = "";

// Exiting
var exit_addr = Module.findExportByName(null, "_exit");
var exit_func = new NativeFunction(exit_addr, 'void', ['int']);
var exit = function (code) {
    // Prevent frida-python from losing messages
    Thread.sleep(0.1);
    exit_func(code);
}

Interceptor.attach(Module.findExportByName(null, "CreateFileW"), {
    onEnter: function (args) {
        var path = Memory.readUtf16String(ptr(args[0]));
        this.targetFound = path.indexOf("CET_TRAINER.CETRAINER") !== -1;
        if (this.targetFound) {
            cet_path = path;
        }
    },
    onLeave: function (ret) {
        if (this.targetFound) {
            cet_handle = ret;
        }
    }
});
Interceptor.attach(Module.findExportByName(null, "CloseHandle"), {
    onEnter: function (args) {
        this.targetFound = cet_handle && args[0].equals(cet_handle);
    },
    onLeave: function (ret) {
        if (this.targetFound) {
            var message = {
                'type': 'cetrainer',
                'path': cet_path,
            };
            send(message);
            exit(0);
        }
    }
});
Interceptor.attach(Module.findExportByName(null, "CreateProcessA"), {
    onEnter: function (args) {
        var message = {
            'type': 'hook',
            'name': Memory.readUtf8String(ptr(args[0])),
            'args': Memory.readUtf8String(ptr(args[1])),
        };
        send(message);
        exit(0);
    }
});
"""

# Decrypts the .CETRAINER file
def decrypt(pathin, pathout):
    """
    Decrypts the .CETRAINER file
    @param[in]  pathin   Path to the input .CETRAINER file
    @param[in]  pathout  Path to the output .CETRAINER file
    """
    # Read data
    fin = open(pathin, "rb")
    data = bytearray(fin.read())
    fin.close()

    result = None
    handlers = [
        (unpack_cet.decrypt,            "CheatEngine (original)"),
        (unpack_cet_barracuda.decrypt,  "CheatEngine (mod-barracuda)"),
        (unpack_cet_mrantifun.decrypt,  "CheatEngine (mod-mrantifun)"),
    ]
    for handler, name in handlers:
        try:
            print("[*] Tring unpacker \'" + name + "\'.")
            result = handler(data[:])
            print("[*] Success!")
            break
        except Exception as e:
            print("[*] Failed!")

    # Write data
    if not result:
        print("[!] Could not decrypt the CETRAINER file")
    else:
        print("[*] Writing: " + pathout)
        fout = open(pathout, "wb")
        fout.write(result)
        fout.close()


# Extracts the .CETRAINER
class TrainerHook():
    def __init__(self, path, output=None):
        self._lock = threading.Lock()
        self._cond = threading.Condition(self._lock)
        self._procstack = [path]
        if not output:
            self._output = path + ".xml"
        else:
            self._output = output

    def run(self):
        while len(self._procstack) > 0:
            name = self._procstack.pop()
            print("[*] Attaching to: " + name)
            pid = frida.spawn([name])
            session = frida.attach(pid)
            session.on('detached', self.on_detached)
            script = session.create_script(code)
            script.on('message', lambda m, d: self.on_message(m, d))
            script.load()
            frida.resume(pid)
            with self._lock:
                self._cond.wait()
        frida.shutdown()

    def on_message(self, message, data=""):
        if 'payload' not in message:
            print(message)
        cmd = message['payload']
        # Handle new processes
        if cmd['type'] == 'hook':
            args = list(shlex.shlex(cmd['args']))
            for token in args:
                if 'CET_TRAINER.CETRAINER' in token:
                    cetpath = token.strip('"')
                    decrypt(cetpath, self._output)
                    return
            path = cmd['name']
            if path is None:
                path = args[0]
            self._procstack.append(path)
        # Handle trainer files
        if cmd['type'] == 'cetrainer':
            cetpath = cmd['path']
            print("[*] Found: " + cetpath)
            decrypt(cetpath, self._output)

    def on_detached(self):
        print("[*] Detaching...")
        with self._lock:
            self._cond.notify()


SCRIPT_USAGE = """CheatEngine Trainer Unpacker
About:    This program extracts and decrypts CheatEngine's .CETRAINER files
          packed inside arbitrary trainer executables
Version:  2017-03-12
Usage:    extract.py path/to/trainer.exe [path/to/trainer.xml]
          Second argument is optional and defaults to:
          path/to/trainer.exe.xml
"""

if __name__ == '__main__':
    if len(sys.argv) <= 1:
        print(SCRIPT_USAGE)
    else:
        path = sys.argv[1]
        th = TrainerHook(path)
        th.run()
