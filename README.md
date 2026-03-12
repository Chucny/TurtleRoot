<h1>🐢 TurtleRoot  </h1>
<strong><p>v1.3</p></strong>
<p><strong>TurtleRoot</strong> is a lightweight Python tool for patching Android boot images
(<code>boot.img</code> or <code>init_boot.img</code>) and injecting a <code>su</code> binary to enable root access.</p>

<p>This project is intended for rooting android devices</p><br>
<strong>IMPORTANT: ONLY GIVES ROOT, EXPECTS A MANAGER APP, FOR EXAMPLE MAGISK TO WORK</strong><br><strong>The application also supports a custom <code>su</code>
 binary in the same folder as your TurtleRoot.py! If you want a custom binary, enter the filename. Otherwise, just press enter.</strong>
<hr>





<hr>

<h2>⚠️ Warning</h2>

<p>Flashing modified boot images can <strong>brick your device</strong> if done incorrectly.</p>

<p>Always:</p>

<ul>

<li>Backup your original <code>boot.img</code></li>
<li>Verify firmware compatibility</li>
<li>Understand the risks</li>
</ul>

<p>You are responsible for your device.</p>

<hr>
<h2>⚙️ Installing Required Tools</h2>

<p>
TurtleRoot requires a few command line utilities to unpack Android ramdisks:
</p>

<ul>
<li><b>cpio</b> – used to extract and rebuild the ramdisk</li>
<li><b>lz4</b> – used for some compressed ramdisks</li>
</ul>

<p>
These tools are automatically available on Linux, but Windows users must install them manually.
</p>

<hr>

<h2>🪟 Windows Installation</h2>

<p>The easiest method is installing <b>Git for Windows</b>, which includes all required Unix tools.</p>

<h3>Step 1 – Download Git for Windows</h3>

<p>
Download from the official website:
</p>

<pre><code>https://git-scm.com/download/win</code></pre>

<h3>Step 2 – Install</h3>

<ol>
<li>Run the installer</li>
<li>Use default settings</li>
<li>Finish installation</li>
</ol>

<p>
Git installs useful tools including:
</p>

<pre><code>
cpio
gzip
lz4
tar
find
</code></pre>

<h3>Step 3 – Verify Installation</h3>

Open <b>Command Prompt</b> or <b>PowerShell</b> and run:
</p>

<pre><code>cpio --version</code></pre>

<p>If installed correctly, you should see something like:</p>

<pre><code>cpio (GNU cpio) 2.13</code></pre>

<hr>

<h3>Alternative (Portable)</h3>

You can also place the tools directly in the TurtleRoot folder:

<pre><code>
TurtleRoot/
 ├── turtleroot.py
 ├── su_binary
 ├── cpio.exe
 ├── lz4.exe
</code></pre>

This makes TurtleRoot portable and avoids installing system packages.

<hr>

<h2>🐧 Linux Installation</h2>

Most Linux distributions include these tools in their package manager.

<h3>Debian / Ubuntu / Kali</h3>

<pre><code>sudo apt update
sudo apt install cpio lz4 -y</code></pre>

<h3>Arch Linux</h3>

<pre><code>sudo pacman -S cpio lz4</code></pre>

<h3>Fedora</h3>

<pre><code>sudo dnf install cpio lz4</code></pre>

<h3>Verify Installation</h3>

Run:

<pre><code>cpio --version
lz4 --version</code></pre>

<hr>

<h2>🚀 After Installing</h2>

Once the tools are installed, run TurtleRoot:

<pre><code>python turtleroot.py</code></pre>

Example:

<pre><code>
Path to init_boot.img or boot.img: boot.img
Detected ramdisk...
Injected su...
SUCCESS!
</code></pre>

<hr>



<h2>🧰 Requirements</h2>

<ul>
<li>Python 3.8+</li>
<li>Unlocked Android bootloader</li>
<li>ADB / Fastboot installed</li>
<li>Extracted firmware containing <code>boot.img</code> or <code>init_boot.img</code></li>
</ul>

<hr>

<h2>📥 Installation</h2>

<p>Clone the repository:</p>

<pre><code>git clone https://github.com/chucny/turtleroot.git
</code></pre>

<p>Enter the folder:</p>

<pre><code>cd turtleroot
</code></pre>

<p>Run the tool:</p>

<pre><code>python turtleroot.py
</code></pre>

<hr>

<h2>🛠 Usage</h2>

<p>Run TurtleRoot with a boot image:</p>

<pre><code>python turtleroot.py
</code></pre>

<p>Example:</p>

<pre><code>python turtleroot.py
Enter file path for your boot.img/init_boot.img: 
</code></pre>

<p>The tool will:</p>

<ol>
<li>Extract the boot image</li>
<li>Inject the <code>su</code> binary</li>
<li>Repack the boot image</li>
<li>Create a patched image</li>
</ol>

<p>Output example:</p>

<pre><code>patched_boot.img
</code></pre>

<hr>

<h2>📱 Flashing the Patched Image</h2>

<h3>1. Boot into fastboot</h3>

<pre><code>adb reboot bootloader
</code></pre>

<p>or manually with hardware keys.</p>

<h3>2. Flash patched boot image</h3>

<p>For most devices:</p>

<pre><code>fastboot flash boot patched_boot.img
</code></pre>

<p>For newer devices using init_boot:</p>

<pre><code>fastboot flash init_boot patched_boot.img
</code></pre>

<h3>3. Reboot device</h3>

<pre><code>fastboot reboot
</code></pre>

<hr>

<h2>🔎 Checking Root</h2>
Install any root manager app, reboot and:<br>
<pre><code>adb shell
su
</code></pre>

<p>If successful, the shell should switch to root.</p>

<hr>

<h2>📊 Compatibility</h2>

<table>
<tr>
<th>Android Version</th>
<th>Status</th>
</tr>
<tr>
<td>Android 7</td>
<td>Supported</td>
</tr>
<tr>
<td>Android 8</td>
<td>Supported</td>
</tr>
<tr>
<td>Android 9</td>
<td>Supported</td>
</tr>
<tr>
<td>Android 10</td>
<td>Supported</td>
</tr>
<tr>
<td>Android 11+</td>
<td>Supported, uses WandersonKalil su 30.5 (should work with most modern android devices)</td>
</tr>
 <tr>
<td>Android 13+</td><br>
<td>Supports A13+, init_boot supported, since the ramdisk is only the thing needed for writing the su binaries.</td>
</tr>
</table>

<p>Modern Android versions include security protections like:</p>

<ul>
<li>Android Verified Boot (AVB)</li>
<li>dm-verity</li>
<li>boot image signature verification</li>
</ul>

<p>These protections may prevent TurtleRoot from working.</p>

<hr>

<h2>📚 Educational Purpose</h2>

<p>TurtleRoot is useful for:</p>

<ul>
<li>Android security research</li>
<li>Learning about boot images</li>
<li>Rooting experiments</li>

</ul>

<hr>

<h2>🐢 Why TurtleRoot?</h2>

<p><strong>RurtleRoot - The magic turtle behind android</strong></p>



<hr>

<h2>📜 License</h2>

<p>Copyright (C) 2026 <strong>Chucny</strong></p>

<hr>

<h2>⭐ Credits</h2>

<p>Major credit goes to:</p>

<p><strong>Chucny</strong><br>
Creator of TurtleRoot<br>
Lead developer and maintainer</p><br><p><strong>WandersonKalil</strong> - Creator of the su binary</p>

