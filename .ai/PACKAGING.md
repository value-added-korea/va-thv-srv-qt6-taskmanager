# Packaging Reference

> How the three packaging targets work, what tools are needed, and the
> conventions each system enforces. Read this before touching any packaging file.

---

## Debian / Ubuntu — `.deb` via debhelper

### Build pipeline

```
src/  +  debian/  →  dpkg-buildpackage  →  dist/*.deb
```

Two `.deb` files are produced from one source:

| Package | Contents | Deps |
|---|---|---|
| `la-toolhive-thv-ui` | GUI app, tray, desktop entries, icons, systemd unit, metainfo | python3, python3-pyqt6, python3-dbus |
| `la-toolhive-thv-ui-cli` | CLI only, man page | python3 |

A **third** `.deb` is built independently via `dpkg-deb --build build_cli_deb/`
for quick CLI-only distribution without the full debhelper build chain.

### Required tools

```bash
sudo apt install debhelper devscripts dpkg-dev
```

### Key files

| File | Role |
|---|---|
| `debian/control` | Package declarations, dependencies, descriptions |
| `debian/rules` | `make`-based build rules; overrides debhelper helpers |
| `debian/changelog` | Version history; the version in the first entry is the package version |
| `debian/copyright` | DEP-5 machine-readable copyright (required by policy) |
| `debian/la-toolhive-thv-ui.install` | Maps `src/` files to install destinations |
| `debian/la-toolhive-thv-ui.links` | Declares `/usr/bin/` symlinks |
| `debian/watch` | `uscan` upstream release tracking |
| `debian/source/format` | `3.0 (native)` — no upstream/Debian split |

### debhelper 13 conventions

- **Icons in `/etc/`** are automatically added to the conffile list by `dh_installdeb`.
  No manual `debian/conffiles` needed.
- `dh_installsystemduser` handles user service installation. We call it with
  `--no-enable --no-start` so the package never activates the service.
- `dh_install` reads the `.install` file to copy `src/` files into the staging tree.
- `dh_link` reads the `.links` file to create symlinks.

### debian/rules override pattern

The `override_dh_install` block in `debian/rules` handles things the `.install`
file cannot express as simple globs:

```makefile
override_dh_install:
    dh_install
    # Fan out icons into the hicolor tree
    find src/icons/ -name "*.svg" -exec install -Dm644 {} \
        debian/APP_PKG/usr/share/icons/hicolor/scalable/apps/ \;
    # Install user systemd service
    install -Dm644 src/systemd/*.service \
        debian/APP_PKG/usr/lib/systemd/user/
    # Install AppStream metainfo
    install -Dm644 src/metainfo/*.xml \
        debian/APP_PKG/usr/share/metainfo/
```

### Versioning

The package version is taken from the **first entry** in `debian/changelog`.
The `Makefile` also reads `VERSION` for naming output artefacts.
Keep both in sync. Use `dch -v 1.0.1` or edit manually.

### Build command

```bash
make deb
# Equivalent to:
dpkg-deb --build build_cli_deb dist/la-toolhive-thv-ui-cli_VERSION_all.deb
dpkg-buildpackage -us -uc
mv ../la-toolhive-thv-ui_VERSION_all.deb dist/
```

Output in `dist/`:
- `la-toolhive-thv-ui_VERSION_all.deb`
- `la-toolhive-thv-ui-cli_VERSION_all.deb`
- `la-toolhive-thv-ui_VERSION.dsc`
- `la-toolhive-thv-ui_VERSION_amd64.buildinfo`
- `la-toolhive-thv-ui_VERSION_amd64.changes`
- `la-toolhive-thv-ui_VERSION.tar.xz`

---

## Red Hat / Fedora / RHEL — `.rpm` via rpmbuild

### Build pipeline

```
src/  →  tar.gz  →  build_rpm/SOURCES/  →  rpmbuild  →  build_rpm/RPMS/  →  dist/
```

### Required tools

```bash
# Fedora / RHEL
sudo dnf install rpm-build
# Ubuntu (cross-build)
sudo apt install rpm
```

### Key file: `rpm/la-toolhive-thv-ui.spec`

Sections in order:

| Section | Purpose |
|---|---|
| Header | `Name`, `Version`, `Release`, `Summary`, `License`, `BuildArch` |
| `%package -n` | Define sub-packages (GUI, CLI) with their own `Requires:` |
| `%description -n` | Per-package descriptions |
| `%prep` | Extract source tarball (`%setup -q -c`) |
| `%install` | Copy files into `%{buildroot}` staging tree |
| `%post -n` / `%postun -n` | Post-install hooks (icon cache, desktop database) |
| `%files -n` | Declare which files belong to which package |

### `%install` conventions

```spec
# Python modules → app data directory
install -Dm755 src/app.py   %{buildroot}/usr/share/%{name}/app.py

# /usr/bin entry points via symlink
ln -sf ../share/%{name}/app.py  %{buildroot}/usr/bin/la-toolhive-thv-ui

# Icons → hicolor theme (both SVG and PNG must be handled)
find src/icons/ -name "*.svg" -exec install -Dm644 {} \
    %{buildroot}/usr/share/icons/hicolor/scalable/apps/ \;

# User systemd service (never auto-enabled)
install -Dm644 src/systemd/app.service \
    %{buildroot}/usr/lib/systemd/user/la-toolhive-thv-ui.service

# AppStream metainfo
install -Dm644 src/metainfo/app.metainfo.xml \
    %{buildroot}/usr/share/metainfo/com.vai-int.la-toolhive-thv-ui.metainfo.xml

# Static system config (if used)
install -Dm644 src/config/config.ini \
    %{buildroot}/etc/la-toolhive-thv-ui/config.ini
```

### `%config` directive

Config files installed to `/etc/` must be marked so RPM does not overwrite
user edits on upgrade:

```spec
%files -n la-toolhive-thv-ui
%config(noreplace) /etc/la-toolhive-thv-ui/config.ini
```

### Post-install hooks

These update the desktop file index and icon theme cache after install/removal:

```spec
%post -n la-toolhive-thv-ui
/usr/bin/update-desktop-database &>/dev/null || true
/usr/bin/gtk-update-icon-cache /usr/share/icons/hicolor &>/dev/null || true

%postun -n la-toolhive-thv-ui
/usr/bin/update-desktop-database &>/dev/null || true
/usr/bin/gtk-update-icon-cache /usr/share/icons/hicolor &>/dev/null || true
```

### Build command

```bash
make rpm
# Equivalent to:
mkdir -p build_rpm/{SPECS,SOURCES,BUILD,RPMS,SRPMS}
cp rpm/la-toolhive-thv-ui.spec build_rpm/SPECS/
tar czf build_rpm/SOURCES/la-toolhive-thv-ui-VERSION.tar.gz \
    --transform 's|^\./|la-toolhive-thv-ui-VERSION/|' ./src
rpmbuild --define "_topdir $(PWD)/build_rpm" \
    -ba build_rpm/SPECS/la-toolhive-thv-ui.spec
```

---

## Arch Linux — `.pkg.tar.zst` via makepkg

### Build pipeline

```
src/  (local)  →  makepkg  →  arch/*.pkg.tar.zst  →  dist/
```

There is no upstream source tarball; `source=()` is empty and files are
referenced from the parent directory via `${startdir}/../src/`.

### Required tools

```bash
sudo pacman -S base-devel
```

### Key file: `arch/PKGBUILD`

Uses the **split package** pattern — one PKGBUILD produces multiple packages:

```bash
pkgbase=la-toolhive-thv-ui
pkgname=('la-toolhive-thv-ui' 'la-toolhive-thv-ui-cli')
pkgver=1.0.0
pkgrel=1
```

Two functions install the GUI and CLI subsets:

```bash
package_la-toolhive-thv-ui() {
    depends=('python' 'python-pyqt6' 'python-dbus')
    install -Dm755 "${startdir}/../src/app.py" \
        "${pkgdir}/usr/share/${pkgbase}/app.py"
    # icons, desktop entry, autostart, systemd, metainfo ...
}

package_la-toolhive-thv-ui-cli() {
    depends=('python')
    install -Dm755 "${startdir}/../src/app.py" \
        "${pkgdir}/usr/share/${pkgbase}/app.py"
    # man page only
}
```

### `backup=()` array

Protects config files from being overwritten on package upgrade
(pacman prompts the user):

```bash
backup=('etc/la-toolhive-thv-ui/config.ini')
```

Note: no leading `/` in backup paths.

### User systemd service

```bash
install -Dm644 "${startdir}/../src/systemd/app.service" \
    "${pkgdir}/usr/lib/systemd/user/la-toolhive-thv-ui.service"
```

Arch packages do not call `systemctl --user enable` — the user does this manually.

### Build command

```bash
make arch
# Equivalent to:
cd arch && makepkg --nodeps -f
mv arch/*.pkg.tar.zst dist/
```

`--nodeps` skips dependency resolution during build (dependencies are
installed when the user installs the package).

---

## Cross-distribution conventions

### Icon installation (all three)

```
/usr/share/icons/hicolor/scalable/apps/la-toolhive-thv-ui.svg    ← SVG (preferred)
/usr/share/icons/hicolor/256x256/apps/la-toolhive-thv-ui.png     ← PNG fallback
/usr/share/la-toolhive-thv-ui/icons/tray-active.svg      ← Tray icons (private)
/usr/share/la-toolhive-thv-ui/icons/tray-inactive.svg
```

After installation, the icon cache must be refreshed:
- Debian: handled automatically by `dh_icons`
- RPM: `%post` calls `gtk-update-icon-cache`
- Arch: no explicit refresh; pacman triggers it via hooks

### AppStream metainfo (all three)

File: `/usr/share/metainfo/com.vai-int.la-toolhive-thv-ui.metainfo.xml`

Required by GNOME Software, KDE Discover, and Flathub. Key validation:
```bash
appstreamcli validate /usr/share/metainfo/com.vai-int.la-toolhive-thv-ui.metainfo.xml
```

### User systemd services (all three)

Install to `/usr/lib/systemd/user/la-toolhive-thv-ui.service`.
**Never** auto-enable in packaging scripts. User enables with:
```bash
systemctl --user enable --now la-toolhive-thv-ui.service
```

### System tmpfiles (all three)

If a `/var/` directory is needed, create
`/usr/lib/tmpfiles.d/la-toolhive-thv-ui.conf` with:
```
d  /var/lib/la-toolhive-thv-ui  0755  root  root  -
```
systemd processes this on boot via `systemd-tmpfiles --create`.

### Desktop database (all three)

After installing `.desktop` files, refresh the index:
```bash
update-desktop-database /usr/share/applications
```
Debian: `dh_desktop` handles this. RPM: `%post`. Arch: pacman hooks.

---

## CI matrix (``.github/workflows/build.yml``)

| Job | Runner | Container | Output |
|---|---|---|---|
| `build-deb` | `ubuntu-latest` | native | `dist/*.deb` → artifact |
| `build-rpm` | `ubuntu-latest` | `fedora:latest` | `dist/*.rpm` → artifact |
| `build-arch` | `ubuntu-latest` | `archlinux:latest` | `dist/*.pkg.tar.zst` → artifact |
| `release` | `ubuntu-latest` | native | GitHub Release with all artifacts |

The `release` job runs only on `refs/tags/v*` pushes and requires all
three build jobs to succeed first.
