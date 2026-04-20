# Skills — Reusable Patterns and Codebase Knowledge

> Distilled know-how for working on projects built from this template.
> An AI reading this file can apply these patterns without re-deriving them
> from the packaging files.

---

## Adding a Python runtime dependency

All three packaging targets must be updated in sync.

### 1. Debian (`debian/control`)

```
Depends:
 ${misc:Depends},
 python3,
 python3-pyqt6,
 python3-dbus,
 python3-NEW-PACKAGE,       ← add here
```

### 2. RPM (`rpm/PKG.spec`)

In the `%package -n la-toolhive-thv-ui` header:
```spec
Requires: python3-pyqt6 python3-dbus python3-new-package
```

Package names on Fedora often differ from Debian. Look up with:
```bash
dnf search python3 | grep new-package
```

### 3. Arch (`arch/PKGBUILD`)

In `package_la-toolhive-thv-ui()`:
```bash
depends=('python' 'python-pyqt6' 'python-dbus' 'python-new-package')
```

Arch package names: usually `python-NAME` (lowercase, no version prefix).

### 4. Virtual environment (dev only)

```bash
.venv/bin/pip install new-package
```

---

## Adding a new installed file

### Step 1 — Add to `debian/PKG.install`

```
src/my-new-file.py     usr/share/la-toolhive-thv-ui/
```

Format: `<source>  <destination directory (relative to /)>`

### Step 2 — Add to `rpm/PKG.spec` in `%install`

```spec
install -Dm644 src/my-new-file.py \
    %{buildroot}/usr/share/%{name}/my-new-file.py
```

And in the relevant `%files -n` block:
```spec
/usr/share/%{name}/my-new-file.py
```

### Step 3 — Add to `arch/PKGBUILD`

In the relevant `package_*()` function:
```bash
install -Dm644 "${startdir}/../src/my-new-file.py" \
    "${pkgdir}/usr/share/${pkgbase}/my-new-file.py"
```

### Step 4 — Add a `/usr/bin/` entry point (if executable)

Add a symlink entry to `debian/PKG.links`:
```
usr/share/la-toolhive-thv-ui/my-new-file.py    usr/bin/my-new-command
```

Add to RPM `%install`:
```spec
ln -sf ../share/%{name}/my-new-file.py %{buildroot}/usr/bin/my-new-command
```

Add to Arch `package_*()`:
```bash
ln -s "../share/${pkgbase}/my-new-file.py" "${pkgdir}/usr/bin/my-new-command"
```

---

## Adding a new configuration option

### Dynamic user config (`src/config.py`)

Add the key to the `DEFAULTS` dict:
```python
DEFAULTS: dict[str, dict[str, str]] = {
    "general": {
        "autostart": "true",
        "theme":     "system",      # ← new key with default value
    },
    "network": {                    # ← new section
        "timeout": "30",
    },
}
```

Read in application code:
```python
import config
cfg = config.load()
theme   = cfg.get("general", "theme", fallback="system")
timeout = cfg.getint("network", "timeout", fallback=30)
```

Save after modification:
```python
cfg.set("general", "theme", "dark")
config.save(cfg)
```

### Static system config (`src/config/config.ini`)

Add section/key to the stub:
```ini
[general]
autostart = true
theme = system

[network]
timeout = 30
```

---

## Adding a new desktop environment action

Add a custom `Action` to `src/desktop/app.desktop`:

```ini
[Desktop Entry]
...
Actions=NewWindow;Preferences;

[Desktop Action NewWindow]
Name=New Window
Exec=/usr/bin/la-toolhive-thv-ui --new-window

[Desktop Action Preferences]
Name=Preferences
Exec=/usr/bin/la-toolhive-thv-ui --preferences
```

Actions appear in the right-click context menu in GNOME, KDE, and Xfce.

---

## Adding a new tray menu item

In `src/tray.py`, inside `_build_menu()`:

```python
action_prefs = QAction("Preferences", menu)
action_prefs.triggered.connect(self._on_preferences)
menu.addAction(action_prefs)   # Before the separator before Quit
```

Add the slot:
```python
def _on_preferences(self):
    # Import and show preferences dialog
    from preferences import PreferencesDialog
    dlg = PreferencesDialog()
    dlg.exec()
```

---

## Adding a post-install script (Debian)

Create `debian/PKG_NAME.postinst`:

```bash
#!/bin/sh
set -e
case "$1" in
    configure)
        # Create a system user if needed
        # adduser --system --no-create-home la-toolhive-thv-ui || true
        # Update caches
        update-desktop-database /usr/share/applications || true
        ;;
esac
#DEBHELPER#
exit 0
```

debhelper will call this at the right time. The `#DEBHELPER#` token is
replaced by debhelper with any auto-generated postinst fragments.

---

## Adding a new sub-package

### Debian: add a new `Package:` stanza to `debian/control`

```
Package: la-toolhive-thv-ui-extra
Architecture: all
Depends: ${misc:Depends}, la-toolhive-thv-ui
Description: Extra component for la-toolhive-thv-ui
 Description here.
```

Then create `debian/la-toolhive-thv-ui-extra.install`.

### RPM: add a `%package` block to the spec

```spec
%package -n la-toolhive-thv-ui-extra
Summary: Extra component
Requires: la-toolhive-thv-ui = %{version}-%{release}

%description -n la-toolhive-thv-ui-extra
Description here.

%files -n la-toolhive-thv-ui-extra
/usr/share/%{name}/extra/
```

### Arch: add to `pkgname` array and add a `package_*()` function

```bash
pkgname=('la-toolhive-thv-ui' 'la-toolhive-thv-ui-cli' 'la-toolhive-thv-ui-extra')

package_la-toolhive-thv-ui-extra() {
    depends=("la-toolhive-thv-ui=${pkgver}")
    install -d "${pkgdir}/usr/share/${pkgbase}/extra"
    # ...
}
```

---

## Changing the version

1. Update `VERSION`:
   ```
   1.0.1
   ```

2. Update `debian/changelog` (add a new entry at the top):
   ```bash
   dch -v 1.0.1 "Description of changes."
   # or manually prepend a stanza
   ```

3. Update `CHANGELOG.md` with a new dated `## [1.0.1]` section.

4. Tag and push:
   ```bash
   git tag v1.0.1
   git push origin v1.0.1
   ```

---

## Running / testing without installing

```bash
# Activate venv (if used)
source .venv/bin/activate

# Run the main GUI directly
python3 src/app.py

# Run the tray directly
python3 src/tray.py

# Run tests
python3 -m pytest tests/
```

---

## Packaging gotchas

| Situation | Rule |
|---|---|
| File in `.install` not found at build time | Path is relative to project root, not `src/`. Check carefully. |
| `dpkg-buildpackage` says "version mismatch" | `VERSION` and `debian/changelog` are out of sync. |
| `appstreamcli validate` fails on `<id>` | The `<id>` value must match the `.desktop` file basename exactly. |
| Tray icon not shown on GNOME | `QSystemTrayIcon.isSystemTrayAvailable()` returns `False`. User needs AppIndicator extension. |
| `/etc/` file overwritten on `apt upgrade` | Missing `conffiles` registration. With debhelper 13 this is automatic for files installed to `/etc/`. |
| RPM upgrade overwrites `/etc/` edits | Missing `%config(noreplace)` in `%files`. |
| Arch upgrade overwrites `/etc/` edits | Missing entry in `backup=()` array in PKGBUILD. |
| `make rpm` fails: "Source not found" | Source tarball in `build_rpm/SOURCES/` not created. Check the `tar czf` command in `Makefile`. |
| `makepkg` can't find `src/` files | PKGBUILD uses `${startdir}/../src/`. Run `make arch` from the project root, not from `arch/`. |

---

## DE-specific behaviour summary

| Behaviour | GNOME | Xfce | KDE Plasma |
|---|---|---|---|
| System tray | Needs AppIndicator extension | Native | Native |
| `.desktop` launcher | ✓ | ✓ | ✓ |
| XDG autostart | ✓ | ✓ | ✓ |
| systemd user service | ✓ | ✓ | ✓ |
| AppStream in software centre | GNOME Software | — | KDE Discover |
| `setDesktopFileName()` effect | Taskbar grouping, no duplicate icon | Taskbar grouping | Taskbar grouping |
| Notification bubbles | ✓ (libnotify) | ✓ | ✓ |
