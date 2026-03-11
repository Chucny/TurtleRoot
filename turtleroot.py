import os
import gzip
import shutil
import tempfile
import struct
print("TurtleRoot - Made by Chucny")
def turtleRoot(input_img, su_src):
    output_img = input_img.replace(".img", "_su.img")
    input_img = os.path.abspath(input_img)
    su_src = os.path.abspath(su_src)
    orig_cwd = os.getcwd()

    if not os.path.exists(su_src):
        print(f"Error: {su_src} not found!")
        print(f"Make sure 'su_binary' is in the same folder as this script.")
        return

    with open(input_img, "rb") as f:
        data = f.read()

    if data[0:8] != b"ANDROID!":
        print("Error: Not a valid Android boot image.")
        return

    # Find Gzip Magic (1F 8B 08)
    r_off = data.find(b"\x1f\x8b\x08")
    if r_off == -1:
        print("Error: This script only supports Gzip-compressed ramdisks.")
        print(f"Found header bytes: {data[0x28:0x2A].hex()} - This might be LZ4 or uncompressed.")
        return

    with tempfile.TemporaryDirectory() as tmpdir:
        try:
            os.chdir(tmpdir)
            ramdisk_gz = data[r_off:]
            
            try:
                cpio_data = gzip.decompress(ramdisk_gz)
                print("Ramdisk successfully decompressed.")
            except Exception as e:
                print(f"Failed to decompress: {e}")
                return

            # Note: For a functional root, you need to actually unpack 
            # and repack the CPIO here. This script currently stops at decompression.
            print(f"Ready to inject {os.path.basename(su_src)}...")
            
        finally:
            os.chdir(orig_cwd)

if __name__ == "__main__":
    # Get the directory where THIS script (turtleroot.py) is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Automatically define the su_binary path in that same folder
    su_path = os.path.join(script_dir, "su_binary")
    
    print("--- TurtleRoot Patched ---")
    boot_path = input("Path to boot.img: ").strip().replace('"', '')
    
    if os.path.exists(boot_path):
        turtleRoot(boot_path, su_path)
    else:
        print("boot.img file not found.")
