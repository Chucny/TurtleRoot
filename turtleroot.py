import os
import subprocess
import shutil
import tempfile
import struct

def turtleRoot(input_img, su_src, output_img=None):
    if output_img is None:
        output_img = input_img.replace(".img", "_su.img")

    def run(cmd, shell=False):
        print("Running:", " ".join(cmd) if not shell else cmd)
        subprocess.check_call(cmd, shell=shell)

    # Store absolute paths because we change directories
    input_img = os.path.abspath(input_img)
    su_src = os.path.abspath(su_src)
    output_img = os.path.abspath(output_img)

    with tempfile.TemporaryDirectory() as tmpdir:
        orig_cwd = os.getcwd()
        os.chdir(tmpdir)
        print(f"Working in: {tmpdir}")

        # 1. Read boot header
        with open(input_img, "rb") as f:
            header = f.read(4096)

        if header[0:8] != b"ANDROID!":
            raise ValueError("Not a valid Android boot image")

        kernel_size = struct.unpack("<I", header[0x10:0x14])[0]
        ramdisk_size = struct.unpack("<I", header[0x28:0x2C])[0]
        ramdisk_offset = 4096 + ((kernel_size + 4095) // 4096) * 4096

        # 2. Extract original ramdisk
        with open(input_img, "rb") as f_in:
            f_in.seek(ramdisk_offset)
            with open("ramdisk_original.img", "wb") as f_out:
                f_out.write(f_in.read(ramdisk_size))

        # 3. Decompress
        run(["gzip", "-dc", "ramdisk_original.img", ">", "ramdisk.cpio"], shell=True)

        # 4. Unpack cpio
        os.makedirs("ramdisk", exist_ok=True)
        os.chdir("ramdisk")
        run(["cpio", "-i", "--no-absolute-filenames", "-F", "../ramdisk.cpio"])
        os.chdir("..")

        # 5. Inject su binary
        sbin_dir = os.path.join("ramdisk", "sbin")
        os.makedirs(sbin_dir, exist_ok=True)
        su_dest = os.path.join(sbin_dir, "su")
        shutil.copy(su_src, su_dest)
        os.chmod(su_dest, 0o755)

        try:
            os.symlink("/sbin/su", os.path.join("ramdisk", "su"))
        except:
            pass

        # 6. Repack cpio
        os.chdir("ramdisk")
        run(r'find . ! -name . | sort | cpio -o -H newc -R root:root -F ../ramdisk_new.cpio', shell=True)
        os.chdir("..")

        # 7. Re-compress
        # Using a redirection-friendly approach for the function version
        with open("ramdisk_new.img", "wb") as f_out:
            subprocess.check_call(["gzip", "-9", "-c", "ramdisk_new.cpio"], stdout=f_out)

        # 8. Build final image
        shutil.copy(input_img, output_img)
        with open("ramdisk_new.img", "rb") as f_new:
            new_data = f_new.read()

        with open(output_img, "r+b") as f:
            f.seek(ramdisk_offset)
            f.write(new_data)
            f.seek(0x28)
            f.write(struct.pack("<I", len(new_data)))

        os.chdir(orig_cwd)
        print(f"Patched image → {output_img}")
        return output_img
