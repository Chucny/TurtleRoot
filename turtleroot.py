#!/usr/bin/env python3
import os
import subprocess
import shutil
import tempfile
import struct
import sys
import gzip
import platform

print("TurtleRoot - Made by Chucny v1.2")

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

            # ===== Unpack CPIO =====

            cpio = get_tool_path("cpio")
            if cpio is None:
                prRed("cpio command not found!")
                return

            os.makedirs("ramdisk", exist_ok=True)

            with open("ramdisk.cpio", "rb") as cpio_file:
                subprocess.check_call(
                    [cpio, "-idmv", "--no-absolute-filenames"],
                    cwd="ramdisk",
                    stdin=cpio_file
                )

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

            # ===== Repack CPIO =====

            file_list = []

            for root, dirs, files in os.walk("ramdisk", topdown=False):
                for name in files + dirs:
                    path = os.path.join(root, name)
                    rel = os.path.relpath(path, "ramdisk").replace(os.sep, "/")
                    file_list.append(rel)

            file_list.append(".")

            with open("ramdisk_new.cpio", "wb") as out_cpio:

                p = subprocess.Popen(
                    [cpio, "-0", "-o", "-H", "newc"],
                    cwd="ramdisk",
                    stdin=subprocess.PIPE,
                    stdout=out_cpio
                )

                p.stdin.write(b'\0'.join(x.encode() for x in file_list) + b'\0')
                p.stdin.close()

                if p.wait() != 0:
                    raise RuntimeError("cpio repack failed")

            # ===== Recompress ramdisk =====

            if raw_ramdisk.startswith(b'\x1f\x8b'):

                with open("ramdisk_new.cpio", "rb") as f:
                    cpio_data = f.read()

                with open("ramdisk_new.img", "wb") as f:
                    f.write(gzip.compress(cpio_data, 9))

            else:

                lz4 = get_tool_path("lz4")

                compressed = subprocess.check_output(
                    [lz4, "-9", "-c", "ramdisk_new.cpio"]
                )

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

    prYellow("TurtleRoot 1.2\n")

    script_dir = os.path.dirname(os.path.abspath(__file__))
    su_path = os.path.join(script_dir, "su_binary")

    boot_path = input("Path to init_boot.img or boot.img: ").strip().replace('"', '')

    if os.path.exists(boot_path):
        turtleRoot(boot_path, su_path)
    else:
        prRed("File not found!")

    input("\nPress Enter to exit...")
