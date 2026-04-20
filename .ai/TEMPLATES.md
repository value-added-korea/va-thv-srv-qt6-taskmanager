# Template System Reference

> How placeholder tokens work, what `scaffold.py` does to each file,
> and how feature flags map to file changes. An AI can use this to
> understand the pre-scaffold state of any file or to predict what a
> scaffolded project will look like.

---

## Placeholder token reference

All template files use these tokens. `scaffold.py` replaces them in every
tracked text file in the repository tree.

| Token | Example value | Source |
|---|---|---|
| `la-toolhive-thv-ui` | `la-toolhive-thv-ui` | Package name (kebab-case) |
| `la-toolhive-thv-ui` | `la-toolhive-thv-ui` | Same as source name (binary package) |
| `la-toolhive-thv-ui-cli` | `la-toolhive-thv-ui-cli` | Binary package name + `-cli` suffix |
| `la-toolhive-thv-ui` | `la-toolhive-thv-ui` | Same as package name (used in paths) |
| `com.vai-int.la-toolhive-thv-ui` | `com.vai-int.la-toolhive-thv-ui` | Reverse-domain ID |
| `A user UI to start, stop toolhive mcp-optimizer using thv command line` | `ToolHive management UI` | One-line description, no trailing period |
| `thv command line has more features and options than Toolhive UI, additionally it is more stable.  The package is to give simular administrative functions to the user for thv but using the users UI (KDE, Gnome, XFCE) and has a system tray notification to indicate the state of the users thv service and the running mcp servers.  The package is adress short comings with Linux and Podman Rootless use cases.` | `Manages the ToolHive…` | Two-sentence description |
| `Utility` | `System Monitor` | XDG generic category label |
| `Gerald Staruiala` | `Jane Doe` | Full name |
| `value.added.kr@gmail.com` | `jane@example.com` | Email address |
| `OWNER/la-toolhive-thv-ui` | `myorg/la-toolhive-thv-ui` | GitHub owner/repo slug |
| `OWNER` | `myorg` | GitHub owner (derived from `OWNER/la-toolhive-thv-ui`) |
| `la-toolhive-thv-ui` | `la-toolhive-thv-ui` | GitHub repo (derived from `OWNER/la-toolhive-thv-ui`) |
| `la-toolhive-thv-ui` | `la-toolhive-thv-ui` | Alias for `la-toolhive-thv-ui` (copyright/watch) |
| `2026-04-13` | `2026-04-13` | Release date |
| `2026` | `2026` | Copyright year |

---

## Legacy string replacements

In addition to `APP_*` tokens, `scaffold.py` replaces legacy project-specific
strings left over from the original project this template was derived from:

| Legacy string | Replaced with |
|---|---|
| `la-toolhive-thv-ui` | `la-toolhive-thv-ui` |
| `la-toolhive-thv-ui-cli` | `la-toolhive-thv-ui-cli` |
| `la-toolhive-thv-ui` | `la-toolhive-thv-ui` |
| `la-toolhive-thv-ui` | `la-toolhive-thv-ui` |
| `la_toolhive_thv_ui_tray` | `MODULE_NAME_tray` |
| `la_toolhive_thv_ui` | `MODULE_NAME` |

---

## Name derivation rules

Given a kebab-case package name, scaffold.py derives:

| Derived value | Rule | Example (`la-toolhive-thv-ui`) |
|---|---|---|
| Display name | Title-case each word | `La Toolhive Thv Ui` (overridable) |
| Module name (Python) | Replace `-` with `_` | `la_toolhive_thv_ui` |
| Class name (PascalCase) | Capitalise each word, join | `LaToolhiveTHVUI` |
| Executable name | Same as package name | `la-toolhive-thv-ui` |
| CLI package name | Append `-cli` | `la-toolhive-thv-ui-cli` |
| App ID default | Prepend `com.example.` | `com.vai-int.la-toolhive-thv-ui` |

---

## Files modified by scaffold.py (full list)

### Always modified (every run)

| File | What changes |
|---|---|
| `src/app.py` | All `APP_*` tokens → real values |
| `src/tray.py` | All `APP_*` tokens → real values |
| `src/app.1` | All `APP_*` tokens → real values |
| `src/desktop/app.desktop` | All `APP_*` tokens → real values |
| `src/metainfo/app.metainfo.xml` | All `APP_*` tokens → real values |
| `debian/control` | All `APP_*` tokens → real values |
| `debian/copyright` | Tokens → real values |
| `debian/watch` | Tokens → real values |
| `debian/rules` | `APP_PKG` variable → real package name |
| `debian/la-toolhive-thv-ui.install` | Tokens → real values; **renamed** to `PKG.install` |
| `debian/la-toolhive-thv-ui.links` | Tokens → real values; **renamed** to `PKG.links` |
| `debian/changelog` | **Completely rewritten** with new package name, maintainer, RFC 2822 date |
| `rpm/la-toolhive-thv-ui.spec` | All `APP_*` tokens → real values; **renamed** to `PKG.spec` |
| `arch/PKGBUILD` | All `APP_*` tokens → real values |
| `build_cli_deb/DEBIAN/control` | All `APP_*` tokens → real values |
| `Makefile` | No tokens (reads `VERSION` and `debian/control` at runtime) |
| `CHANGELOG.md` | `OWNER/la-toolhive-thv-ui` → real slug |
| `README.md` | `OWNER/la-toolhive-thv-ui` → real slug (if present) |

---

## Feature flags → file changes

### No system tray (`has_tray = no`)

Files **removed**:
- `src/tray.py`
- `src/desktop/app-autostart.desktop`
- `src/systemd/app.service`
- `src/systemd/` (if empty after removal)

Packaging files **patched** (lines containing these strings removed):
- `tray.py` lines removed from `debian/PKG.install`
- `autostart` lines removed from `debian/PKG.install`
- `systemd` lines removed from `debian/PKG.install`
- Same removals applied to `rpm/PKG.spec` and `arch/PKGBUILD`

### Tray yes, XDG autostart = no

File **removed**: `src/desktop/app-autostart.desktop`
Lines containing `autostart` removed from packaging files.

### Tray yes, systemd service = no

File **removed**: `src/systemd/app.service`
Lines containing `systemd` removed from packaging files.

### User config = dynamic (creates `src/config.py`)

```python
# src/config.py — generated
CONFIG_DIR  = Path(XDG_CONFIG_HOME or ~/.config) / la-toolhive-thv-ui
CONFIG_FILE = CONFIG_DIR / "config.ini"
DEFAULTS    = { "general": { "autostart": "true" } }

def load() -> configparser.ConfigParser: ...
def save(parser) -> None: ...
```

### User config = static (creates `src/config/config.ini`)

- Stub INI file created at `src/config/config.ini`
- `debian/PKG.install` gets: `src/config/config.ini  etc/la-toolhive-thv-ui/`
- `arch/PKGBUILD` gets: `backup=('etc/la-toolhive-thv-ui/config.ini')`
- debhelper auto-marks `/etc/` files as conffiles

### User data dir = yes (creates `src/data.py`)

```python
# src/data.py — generated
DATA_DIR  = Path(XDG_DATA_HOME or ~/.local/share) / la-toolhive-thv-ui
CACHE_DIR = Path(XDG_CACHE_HOME or ~/.cache) / la-toolhive-thv-ui

def ensure_dirs() -> None: ...
```

### Var directory = yes (creates `src/tmpfiles.d/la-toolhive-thv-ui.conf`)

```
# src/tmpfiles.d/la-toolhive-thv-ui.conf — generated
d  /var/lib/la-toolhive-thv-ui  0755  root  root  -
```

Installed to `/usr/lib/tmpfiles.d/la-toolhive-thv-ui.conf`. Processed by
`systemd-tmpfiles --create` on boot.
Also added to `debian/PKG.install`, `rpm/PKG.spec`, and `arch/PKGBUILD`.

### Virtual env = yes

- `.venv/` created via `python3 -m venv .venv`
- PyQt6 installed into `.venv/`
- `.venv/` added to `.gitignore`
- Note printed: `python3-dbus` must be installed system-wide (requires libdbus headers)

---

## Text files processed by scaffold.py

Any file with these extensions is scanned for token replacement:

```
.py  .sh  .md  .txt  .rst  .toml  .ini  .cfg  .conf
.desktop  .service  .spec  .xml  .yml  .yaml  .json
.install  .links  .1  .5  .8
```

Extensionless files scanned by name:
`PKGBUILD  Makefile  VERSION  LICENSE  control  rules  changelog
copyright  watch  conffiles  dirs  postinst  prerm  CONTRIBUTING
CHANGELOG  README`

Directories **skipped** (never scanned):
`.git  .venv  dist  build_rpm  arch/pkg  arch/src  extracted_deb_package`

---

## Validation commands (run after scaffolding)

```bash
# Verify no APP_* tokens remain
grep -rn 'APP_\|MAINTAINER_\|OWNER/la-toolhive-thv-ui\|2026-04-13' \
    --include="*.py" --include="*.desktop" --include="*.service" \
    --include="*.xml" --include="*.spec" --include="PKGBUILD" \
    --include="control" --include="*.install" --include="*.links" .

# Validate desktop file
desktop-file-validate src/desktop/la-toolhive-thv-ui.desktop

# Validate AppStream metainfo
appstreamcli validate src/metainfo/app.metainfo.xml

# Check debian packaging
lintian --no-tag-display-limit dist/*.deb
```
