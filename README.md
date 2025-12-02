SSH Config Backup Tool ⚡
<div align="center">

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Platform](https://img.shields.io/badge/platform-Linux-orange)
![Arch Linux](https://img.shields.io/badge/Arch%20Linux-Supported-blueviolet)
![Status](https://img.shields.io/badge/status-active-brightgreen)

</div>
✨ Features

+ 🔒 Secure SSH connections with password support
+ 📁 Multi-protocol copying (SCP, SFTP, recursive)
+ ⏰ Automatic scheduling via crontab
+ 🔍 Remote file verification and accessibility checks
+ 📊 Detailed logging of all operations
+ 🚀 Easy configuration management
+ 🎯 Smart file type detection (files/directories)

## 📸 Screenshots

<div align="center">

<table width="100%">
<tr>
<td width="33%" align="center"><strong>📁 Config Management</strong></td>
<td width="33%" align="center"><strong>🔧 SSH Settings</strong></td>
<td width="33%" align="center"><strong>⏰ Auto Backup</strong></td>
</tr>
<tr>
<td><img src="screenshots/1.png" width="100%"></td>
<td><img src="screenshots/2.png" width="100%"></td>
<td><img src="screenshots/3.png" width="100%"></td>
</tr>
</table>

</div>

📦 Installation

Arch Linux (AUR/makepkg)

```bash
# Clone the repository
git clone https://github.com/Rexilone/ssh-config-backup.git
cd ssh-config-backup

# Build and install the package
makepkg -si
```

Install dependencies

```bash
sudo pacman -S python python-tk python-paramiko openssh sshpass
```
