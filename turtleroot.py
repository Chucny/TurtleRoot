#!/usr/bin/env python3
import os
import shutil
import tempfile
import struct
import sys
import gzip
import platform
import subprocess

print("TurtleRoot - Made by Chucny v1.4")

def prRed(s): print("\033[91m{}\033[00m".format(s))
def prGreen(s): print("\033[92m{}\033[00m".format(s))
def prYellow(s): print("\033[93m{}\033[00m".format(s))
def prCyan(s): print("\033[96m{}\033[00m".format(s))

# === Turtle ASCII ===
prGreen("""
                         ========
                       ==+**++**+==
                       ==+**++**+==
                       ============
                       ============
                        ==========
                       ============
             ================================
           ============+#%%#+==+##++%%+========
            =========+##*+++===+%%++%%+=======
              ========+*#%%#+==+%@%%@@#=====
             ==========++***#*+++*****+======
           ============+*###**+================
           ============+*##*+==================
             ================================
                       ============
                         ========
                           ====
                           ====
""")

is_windows = platform.system() == "Windows"

def get_tool_path(tool):
    """Find an external tool like lz4 if needed"""
    if not is_windows:
        return tool

    git_path = rf"C:\Program Files\Git\usr\bin\{tool}.exe"
    if os.path.exists(git_path):
        return git_path

    try:
        subprocess.check_call([tool, "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return tool
    except:
        pass

    return None

def run(cmd):
    print("→", " ".join(cmd) if isinstance(cmd, list) else cmd)
    subprocess.check_call(cmd)

def suinput():
    u = input("Press enter to continue, or enter filename for a custom su binary in the same folder as TurtleRoot.py ")
    return "su_binary" if u == "" else u

# ===== Pure Python CPIO extractor =====
def extract_cpio_newc(data, out_dir):
    pos = 0
    while pos < len(data):
        header = data[pos:pos+110]
        pos += 110

        # Parse header fields in hex
        namesize = int(header[94:102].decode(), 16)
        filesize = int(header[54:62].decode(), 16)

        name = data[pos:pos+namesize-1].decode()
        pos += namesize
        if (110 + namesize) % 4 != 0:
            pos += 4 - ((110 + namesize) % 4)  # padding

        if name == "TRAILER!!!":
            break

        file_data = data[pos:pos+filesize]
        pos += filesize
        if filesize % 4 != 0:
            pos += 4 - (filesize % 4)  # padding

        path = os.path.join(out_dir, name)

        # ---- FIX FOR WINDOWS FILE/DIR CONFLICT ----
        dir_name = os.path.dirname(path)
        if dir_name:
            if os.path.exists(dir_name) and os.path.isfile(dir_name):
                os.remove(dir_name)  # remove file blocking directory
            if not os.path.exists(dir_name):
                os.makedirs(dir_name)

        # Write file
        if not name.endswith("/"):  # skip directory entries
            with open(path, "wb") as f:
                f.write(file_data)
def repack_cpio_newc(src_dir, output_file):
    """Minimal repacker for newc format"""
    entries = []

    for root, dirs, files in os.walk(src_dir, topdown=True):
        for name in files + dirs:
            path = os.path.join(root, name)
            rel = os.path.relpath(path, src_dir).replace(os.sep, "/")
            entries.append((path, rel))

    with open(output_file, "wb") as out:
        for path, rel in entries:
            st_size = os.path.getsize(path) if os.path.isfile(path) else 0
            header = (
                b"070701" +                  # c_magic
                b"00000000"*6 +               # inode, mode, uid, gid, nlink, mtime
                f"{st_size:08x}".encode() +  # filesize
                b"00000000"*3 +               # devmajor, devminor, rdevmajor, rdevminor
                f"{len(rel)+1:08x}".encode() + # namesize
                b"00000000"                    # check
            )
            header = header.ljust(110, b'0')
            out.write(header)
            out.write(rel.encode() + b'\0')
            if (110 + len(rel)+1) % 4 != 0:
                out.write(b'\0' * (4 - ((110 + len(rel)+1) % 4)))

            if os.path.isfile(path):
                with open(path, "rb") as f:
                    out.write(f.read())
                if st_size % 4 != 0:
                    out.write(b'\0' * (4 - (st_size % 4)))

        # write trailer
        trailer = b"070701" + b"0"*102 + b'\0'*4
        trailer_name = b"TRAILER!!!\0"
        trailer += trailer_name
        if (110 + len(trailer_name)) % 4 != 0:
            trailer += b'\0' * (4 - ((110 + len(trailer_name)) % 4))
        out.write(trailer)

# ================= MAIN =================

def turtleRoot(input_img, su_src):

    input_img = os.path.abspath(input_img)
    su_src = os.path.abspath(su_src)
    output_img = input_img.replace(".img", "_su.img")

    if not os.path.exists(su_src):
        prRed("Error: su_binary not found!")
        return

    with open(input_img, "rb") as f:
        header = f.read(4096)

    if header[0:8] != b"ANDROID!":
        prRed("Error: Not a valid Android boot image.")
        return

    kernel_size = struct.unpack("<I", header[8:12])[0]
    ramdisk_size = struct.unpack("<I", header[16:20])[0]
    page_size = struct.unpack("<I", header[36:40])[0]

    kernel_padded = ((kernel_size + page_size - 1) // page_size) * page_size
    ramdisk_offset = page_size + kernel_padded

    prCyan(f"Detected ramdisk at offset {ramdisk_offset} (size {ramdisk_size} bytes)")

    original_cwd = os.getcwd()

    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        try:
            # ===== Extract ramdisk =====
            with open(input_img, "rb") as f:
                f.seek(ramdisk_offset)
                raw_ramdisk = f.read(ramdisk_size)

            with open("ramdisk_raw.img", "wb") as f:
                f.write(raw_ramdisk)

            # ===== Detect compression =====
            if raw_ramdisk.startswith(b'\x1f\x8b'):
                prGreen("Gzip ramdisk detected")
                with gzip.open("ramdisk_raw.img", "rb") as f:
                    ramdisk_cpio = f.read()
                with open("ramdisk.cpio", "wb") as f:
                    f.write(ramdisk_cpio)

            elif raw_ramdisk.startswith(b'\x04\x22\x4d\x18'):
                prGreen("LZ4 ramdisk detected")
                lz4 = get_tool_path("lz4")
                if lz4 is None:
                    prRed("lz4 command not found!")
                    return
                run([lz4, "-d", "ramdisk_raw.img", "ramdisk.cpio"])

            else:
                prRed("Unsupported ramdisk compression")
                return

            # ===== Extract CPIO using Python =====
            os.makedirs("ramdisk", exist_ok=True)
            with open("ramdisk.cpio", "rb") as f:
                data = f.read()
            extract_cpio_newc(data, "ramdisk")

            # ===== Inject SU =====
            sbin = os.path.join("ramdisk", "sbin")
            os.makedirs(sbin, exist_ok=True)
            su_dest = os.path.join(sbin, "su")
            shutil.copy(su_src, su_dest)
            os.chmod(su_dest, 0o755)
            prGreen("Injected su → /sbin/su")
            try:
                os.symlink("/sbin/su", os.path.join("ramdisk", "su"))
            except:
                pass

            # ===== Repack CPIO using Python =====
            repack_cpio_newc("ramdisk", "ramdisk_new.cpio")

            # ===== Recompress ramdisk =====
            if raw_ramdisk.startswith(b'\x1f\x8b'):
                with open("ramdisk_new.cpio", "rb") as f:
                    cpio_data = f.read()
                with open("ramdisk_new.img", "wb") as f:
                    f.write(gzip.compress(cpio_data, 9))
            else:
                lz4 = get_tool_path("lz4")
                compressed = subprocess.check_output([lz4, "-9", "-c", "ramdisk_new.cpio"])
                with open("ramdisk_new.img", "wb") as f:
                    f.write(compressed)

            # ===== Build final image =====
            shutil.copy(input_img, output_img)
            with open("ramdisk_new.img", "rb") as f:
                new_ramdisk = f.read()
            with open(output_img, "r+b") as f:
                f.seek(ramdisk_offset)
                f.write(new_ramdisk)
                f.seek(16)
                f.write(struct.pack("<I", len(new_ramdisk)))

            prGreen(f"""
🚀 SUCCESS!
Patched image created:
{output_img}
""")

        finally:
            os.chdir(original_cwd)

# ================= CLI =================

if __name__ == "__main__":

    prYellow("TurtleRoot 1.4\n")

    boot_path = input("Path to init_boot.img or boot.img: ").replace('"','').strip()
    if not os.path.exists(boot_path):
        prRed(f"File not found: {boot_path}")
        input("\nPress Enter to exit...")
        sys.exit(1)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    su_path = os.path.join(script_dir, suinput())

    turtleRoot(boot_path, su_path)
    input("\nPress Enter to exit...")
