CETRAINER files
===============

This documents covers *CETRAINER* files in the original Cheat Engine software, and lists the documentation of all modifications of Cheat Engine found in trainers.

---

## Original CE

There are two major ways the files are saved based on the version of Cheat Engine being used to create them. There is also two ways a trainer can be saved and protected:

* As a stand-alone *.EXE* file.
* As a compiled/protected *.CETRAINER* file that Cheat Engine understands how to read.

### Stand-Alone Executable File (*.EXE*)

Using this approach, trainer makers can create a stand-alone solution within Cheat Engine that actually does a few things pretty interesting for the user and makes their trainer able to make use of Cheat Engine fully. When Cheat Engine generates a stand-alone executable it does the following steps:

1. The users cheat table is compressed with zlib.
2. The users cheat table is then XOR-encrypted multiple times.
3. Cheat Engine creates a new SFX file for the trainer using a base exectuable.
4. Cheat Engine builds an archive file that contains the various files that this trainer will need to run.
5. Cheat Engine injects this new archive into the SFX file's resources and names it `ARCHIVE`.
6. Cheat Engine injects another resource named `DECOMPRESSOR`, used to extract the `ARCHIVE` resource.
7. Cheat Engine finalizes the image and renames it to the trainer creators desired name.

When this file is executed, it will startup and look for the `DECOMPRESSOR` and `ARCHIVE` resources and extract them. The decompressor will then run and extract the contents of archive. This archive contains a number of files based on what the trainer requires to run. By default this will at least include:

* `cheatengine-i386.exe` or `cheatengine-x86_64.exe`
* `lua.dll`
* `dbghelp.dll`

Outside of that it can also include various files based on the trainers needs such as the `dbk32/64.sys` driver, `speedhack.dll`, etc. 

Once the files are extracted, if a `.CETRAINER` file is found in the archive, the decompressor will launch the Cheat Engine executable with the trainer file as the second argument. Then the following information for loading a `.CETRAINER` file comes into play.

### CETRAINER File (*.CETRAINER*)

`CETRAINER` files can come in two manners, protected and unprotected. These files are simple XML files that hold the Cheat Table information. If protected, the files are compressed and encrypted via a simple XOR encryption. These files are loaded follows:

* Cheat Engine loads the file.
* Checks if the file is already XML by seeing if `<?xml` exists as the first 5 characters.
* If `<?xml` exists, just load the table as normal.
* If not, then the file is considered protected and must be decoded.
* The first layer of protection is a 3-way XOR encryption. 
    * The first wave is a before-key relationship where the the first byte (*x*) starts at 2 and the first XOR key starts at *x-2*.
    * The second wave is an after-key relationship where the first byte (*x*) starts at length-2 and the first XOR key starts at *x+1*.
    * The last wave is a static-incrementing key relationship where the key starts at 0xCE and increments each XOR.
* Next the newly XOR'd data is then decompressed using zlib.
    * __Old Decompress Method__: Older trainer files have no special compression or buffer, the entire buffer is assumed to be compressed and can be processed.
    * __New Decompress Method__: Newer trainer files will show a 5-byte header saying `CHEAT`. This should be skipped before attempting to decompress the buffer. Next the newer files also have the compressed data size after the 'CHEAT' header which should be read and used to know how much data to read and inflate from the compressed data stream.
* At this point the `.CETRAINER` file should be clean .XML text and can be reused/edited/etc. again.


## Modified CE

Some trainer developers have done minor modifications to the CETRAINER decryption algorithm described above, or packaging method as a stand-alone executable. Below is the list of all known modifications used by trainer developers:

| Trainers  | Documentation                                                |
|-----------|--------------------------------------------------------------|
| Barracuda | [/docs/cetrainer-barracuda.md](/docs/cetrainer-barracuda.md) |
| MrAntiFun | [/docs/cetrainer-mrantifun.md](/docs/cetrainer-mrantifun.md) |


## Sources

[1] http://atom0s.com/forums/viewtopic.php?t=83