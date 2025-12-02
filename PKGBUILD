# Maintainer: Rexilone <rexilone@example.com>
pkgname=ssh-backup
pkgver=1.0
pkgrel=1
pkgdesc="Modern SSH configuration backup tool"
arch=('any')
url="https://github.com/rexilone/ssh-backup"
license=('GPL3')
depends=('python' 'tk' 'python-paramiko' 'sshpass')
source=("$pkgname-$pkgver.tar.gz")
md5sums=('SKIP')

package() {
  cd "$srcdir/$pkgname-$pkgver"
  
  # Create directories
  install -d "$pkgdir/usr/bin"
  install -d "$pkgdir/opt/ssh-backup"
  install -d "$pkgdir/usr/share/applications"
  install -d "$pkgdir/usr/share/icons/hicolor/scalable/apps"
  
  # Install main script
  install -Dm755 ssh-backup.py "$pkgdir/opt/ssh-backup/ssh-backup.py"
  
  # Install launcher script
  cat > "$pkgdir/opt/ssh-backup/ssh-backup" << 'EOF'
#!/bin/bash
cd /opt/ssh-backup
python ssh-backup.py "$@"
EOF
  chmod +x "$pkgdir/opt/ssh-backup/ssh-backup"
  
  # Create symlink
  ln -sf /opt/ssh-backup/ssh-backup "$pkgdir/usr/bin/ssh-backup"
  
  # Install desktop file
  install -Dm644 ssh-backup.desktop "$pkgdir/usr/share/applications/ssh-backup.desktop"
  
  # Install icon
  install -Dm644 ssh-backup.svg "$pkgdir/usr/share/icons/hicolor/scalable/apps/ssh-backup.svg"
}
