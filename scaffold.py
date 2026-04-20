#!/usr/bin/env python3
"""
scaffold.py — Interactive project scaffolding for the Linux package template.

Run directly with the system Python interpreter — no virtual environment needed:

    python3 scaffold.py

Asks a series of questions, then:
  • Replaces all template placeholders in every tracked file
  • Renames debian/*.install, debian/*.links, and rpm/*.spec
  • Removes source files for features you don't need (tray, autostart, etc.)
  • Generates config/data directory helpers in src/ when requested
  • Rewrites debian/changelog with your project identity
  • Creates a .venv and installs runtime dependencies (optional)
  • Updates the git remote origin
"""

import configparser
import os
import re
import shutil
import subprocess
import sys
import textwrap
from datetime import datetime
from email.utils import formatdate
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).parent.resolve()

# ---------------------------------------------------------------------------
# Terminal colours (gracefully degraded if not a TTY)
# ---------------------------------------------------------------------------

if sys.stdout.isatty():
    RESET  = "\033[0m"
    BOLD   = "\033[1m"
    DIM    = "\033[2m"
    GREEN  = "\033[32m"
    YELLOW = "\033[33m"
    CYAN   = "\033[36m"
    RED    = "\033[31m"
else:
    RESET = BOLD = DIM = GREEN = YELLOW = CYAN = RED = ""


def _h(text: str) -> str:
    return f"\n{BOLD}{CYAN}{text}{RESET}"

def _ok(text: str) -> str:
    return f"  {GREEN}✓{RESET} {text}"

def _warn(text: str) -> str:
    return f"  {YELLOW}!{RESET} {text}"

def _err(text: str) -> str:
    return f"  {RED}✗{RESET} {text}"

# ---------------------------------------------------------------------------
# Input helpers
# ---------------------------------------------------------------------------

def prompt(question: str, default: str = "", required: bool = True) -> str:
    hint = f" [{default}]" if default else ""
    while True:
        try:
            value = input(f"  {question}{hint}: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n  Aborted.")
            sys.exit(1)
        if value:
            return value
        if default:
            return default
        if required:
            print(f"  {RED}This field is required.{RESET}")
        else:
            return ""


def yes_no(question: str, default: bool = True) -> bool:
    hint = f"{BOLD}Y{RESET}/n" if default else f"y/{BOLD}N{RESET}"
    while True:
        try:
            value = input(f"  {question} [{hint}]: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\n  Aborted.")
            sys.exit(1)
        if not value:
            return default
        if value in ("y", "yes"):
            return True
        if value in ("n", "no"):
            return False
        print(f"  {RED}Enter y or n.{RESET}")


def choose(question: str, options: list[str], default: int = 1) -> int:
    print(f"\n  {question}")
    for i, opt in enumerate(options, 1):
        marker = f"{BOLD}>{RESET}" if i == default else " "
        print(f"  {marker} {i}. {opt}")
    while True:
        try:
            raw = input(f"  Choice [{default}]: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n  Aborted.")
            sys.exit(1)
        if not raw:
            return default
        try:
            n = int(raw)
            if 1 <= n <= len(options):
                return n
        except ValueError:
            pass
        print(f"  {RED}Enter a number between 1 and {len(options)}.{RESET}")

# ---------------------------------------------------------------------------
# Name derivation helpers
# ---------------------------------------------------------------------------

def kebab_to_title(name: str) -> str:
    """la-toolhive-thv-ui  →  La Toolhive Thv Ui"""
    return " ".join(w.capitalize() for w in name.split("-"))


def kebab_to_snake(name: str) -> str:
    """la-toolhive-thv-ui  →  la_toolhive_thv_ui"""
    return name.replace("-", "_")


def kebab_to_pascal(name: str) -> str:
    """la-toolhive-thv-ui  →  LaToolhiveTHVUI (PascalCase class name)"""
    return "".join(w.capitalize() for w in name.split("-"))


def validate_pkg_name(name: str) -> bool:
    return bool(re.fullmatch(r"[a-z][a-z0-9-]*[a-z0-9]", name))

# ---------------------------------------------------------------------------
# Gather all configuration via interactive questions
# ---------------------------------------------------------------------------

def gather_config() -> dict:
    cfg: dict = {}
    today = datetime.today()
    cfg["date"]        = today.strftime("%Y-%m-%d")
    cfg["year"]        = str(today.year)
    cfg["date_rfc2822"] = formatdate(localtime=True)

    # ── Project identity ────────────────────────────────────────────────────
    print(_h("── Project identity ──────────────────────────────────────────"))

    while True:
        pkg = prompt("Package name (lowercase kebab-case, e.g. la-toolhive-thv-ui)")
        if validate_pkg_name(pkg):
            break
        print(f"  {RED}Must be lowercase letters, digits, and hyphens "
              f"(no leading/trailing hyphens).{RESET}")

    cfg["pkg_name"]     = pkg
    cfg["source_name"]  = pkg
    cfg["bin_name"]     = pkg
    cfg["module_name"]  = kebab_to_snake(pkg)
    cfg["class_name"]   = kebab_to_pascal(pkg)
    cfg["display_name"] = prompt("Display name", default=kebab_to_title(pkg))
    cfg["generic_name"] = prompt("Generic category name (e.g. System Monitor)",
                                 default="Utility")
    cfg["description"]  = prompt("Short description (one line, no full stop)")
    cfg["description_long"] = prompt(
        "Long description (one or two sentences)")
    cfg["categories"]   = prompt(
        "XDG application categories (semicolon-separated)",
        default="Utility;")

    print()
    cfg["maintainer_name"]  = prompt("Maintainer full name")
    cfg["maintainer_email"] = prompt("Maintainer email address")

    gh_default = f"OWNER/{pkg}"
    gh_slug = prompt("GitHub owner/repo (e.g. myorg/my-app)", default=gh_default)
    cfg["gh_slug"]  = gh_slug
    cfg["gh_owner"] = gh_slug.split("/")[0] if "/" in gh_slug else "OWNER"
    cfg["gh_repo"]  = gh_slug.split("/")[1] if "/" in gh_slug else pkg

    cfg["app_id"] = prompt(
        "Reverse-domain application ID",
        default=f"com.example.{pkg}")

    # ── Features ────────────────────────────────────────────────────────────
    print(_h("── Features ──────────────────────────────────────────────────"))

    cfg["has_tray"] = yes_no("Include a system tray component?", default=True)

    if cfg["has_tray"]:
        login_choice = choose(
            "Start on user login?",
            [
                "XDG autostart only  (all DEs — simpler, no systemd needed)",
                "systemd user service only  (requires a systemd user session)",
                "Both  (maximum compatibility — recommended)",
                "Neither  (user starts the tray manually)",
            ],
            default=3,
        )
        cfg["login_xdg"]     = login_choice in (1, 3)
        cfg["login_systemd"] = login_choice in (2, 3)
    else:
        cfg["login_xdg"]     = False
        cfg["login_systemd"] = False

    # ── Configuration & data directories ────────────────────────────────────
    print(_h("── Configuration & data directories ──────────────────────────"))

    print(f"\n  {DIM}User configuration (~/.config/{pkg}/){RESET}")
    user_cfg = choose(
        "How will this application store user settings?",
        [
            "None  (no per-user configuration)",
            "Static default  (package installs defaults to /etc/{pkg}/;\n"
            "                 user can copy and override in ~/.config/{pkg}/)",
            "Dynamic  (app creates and manages ~/.config/{pkg}/ at runtime)",
        ],
        default=3,
    )
    cfg["user_config"] = user_cfg          # 1=none  2=static/etc  3=dynamic

    cfg["user_data"] = yes_no(
        f"User data directory  (~/.local/share/{pkg}/)?", default=False)

    cfg["system_config"] = yes_no(
        f"System-wide config installed by the package  (/etc/{pkg}/)?",
        default=False)
    if cfg["system_config"]:
        cfg["etc_path"] = prompt(
            "Path under /etc (without leading slash)",
            default=f"etc/{pkg}").lstrip("/")
    else:
        cfg["etc_path"] = None

    cfg["var_data"] = yes_no(
        "System var directory  (/var/… for shared or persistent data)?",
        default=False)
    if cfg["var_data"]:
        var_choice = choose(
            "Location under /var:",
            [
                f"var/lib/{pkg}    (persistent application state — most common)",
                f"var/cache/{pkg}  (regeneratable cached data)",
                f"var/log/{pkg}    (application log files)",
                "Custom path",
            ],
            default=1,
        )
        if var_choice == 1:
            cfg["var_path"] = f"var/lib/{pkg}"
        elif var_choice == 2:
            cfg["var_path"] = f"var/cache/{pkg}"
        elif var_choice == 3:
            cfg["var_path"] = f"var/log/{pkg}"
        else:
            cfg["var_path"] = prompt(
                "Path under /var (no leading slash)",
                default=f"var/lib/{pkg}").lstrip("/")
    else:
        cfg["var_path"] = None

    # ── Python environment ───────────────────────────────────────────────────
    print(_h("── Python environment ────────────────────────────────────────"))

    cfg["use_venv"] = yes_no(
        "Create a .venv virtual environment for development?", default=False)
    if cfg["use_venv"]:
        default_py = shutil.which("python3") or "python3"
        cfg["python_bin"] = prompt("Python interpreter to use", default=default_py)
    else:
        cfg["python_bin"] = shutil.which("python3") or "python3"

    # ── Git remote ───────────────────────────────────────────────────────────
    print(_h("── Git remote ────────────────────────────────────────────────"))

    current_remote = _git_remote()
    if current_remote:
        print(f"\n  Current origin: {DIM}{current_remote}{RESET}")

    suggested = f"https://github.com/{cfg['gh_slug']}.git"
    cfg["git_remote"] = prompt(
        "New remote URL (leave blank to keep current)",
        default=suggested if current_remote != suggested else "",
        required=False,
    )

    return cfg


def _git_remote() -> Optional[str]:
    try:
        r = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            cwd=ROOT, capture_output=True, text=True,
        )
        return r.stdout.strip() if r.returncode == 0 else None
    except FileNotFoundError:
        return None

# ---------------------------------------------------------------------------
# Summary / confirmation
# ---------------------------------------------------------------------------

def preview(cfg: dict):
    print(_h("══ Summary ═══════════════════════════════════════════════════"))

    tray_txt = "yes" if cfg["has_tray"] else "no"
    if cfg["has_tray"]:
        parts = []
        if cfg["login_xdg"]:
            parts.append("XDG autostart")
        if cfg["login_systemd"]:
            parts.append("systemd user service")
        login_txt = " + ".join(parts) if parts else "manual start only"
    else:
        login_txt = "n/a"

    ucfg = {1: "none", 2: "static (/etc/)", 3: "dynamic (~/.config/)"}[cfg["user_config"]]

    rows = [
        ("Package name",       cfg["pkg_name"]),
        ("Display name",       cfg["display_name"]),
        ("Short description",  cfg["description"]),
        ("Maintainer",         f"{cfg['maintainer_name']} <{cfg['maintainer_email']}>"),
        ("GitHub",             cfg["gh_slug"]),
        ("App ID",             cfg["app_id"]),
        ("System tray",        tray_txt),
        ("Login autostart",    login_txt),
        ("User config",        ucfg),
        ("User data dir",      "yes" if cfg["user_data"] else "no"),
        ("System /etc/ config",f"/{cfg['etc_path']}" if cfg["etc_path"] else "no"),
        ("Var directory",      f"/{cfg['var_path']}" if cfg["var_path"] else "no"),
        ("Virtual env",        ".venv/ (will be created)" if cfg["use_venv"] else "no (system Python)"),
        ("Git remote",         cfg["git_remote"] or "(unchanged)"),
    ]

    col = max(len(r[0]) for r in rows) + 2
    print()
    for label, value in rows:
        print(f"  {BOLD}{label:<{col}}{RESET}{value}")
    print()

    if not yes_no("Proceed with scaffolding?", default=True):
        print("  Aborted.")
        sys.exit(0)

# ---------------------------------------------------------------------------
# Placeholder substitution
# ---------------------------------------------------------------------------

# Ordered list: longer / more-specific strings first to prevent partial matches.
_TEMPLATE_ORIGINALS = [
    # Legacy project-specific strings still present in unchanged files
    "la-toolhive-thv-ui",
    "la-toolhive-thv-ui-cli",
    "la-toolhive-thv-ui",
    "la-toolhive-thv-ui",
    "la_toolhive_thv_ui_tray",
    "la_toolhive_thv_ui",
    # Template placeholder tokens (longest first within each group)
    "thv command line has more features and options than Toolhive UI, additionally it is more stable.  The package is to give simular administrative functions to the user for thv but using the users UI (KDE, Gnome, XFCE) and has a system tray notification to indicate the state of the users thv service and the running mcp servers.  The package is adress short comings with Linux and Podman Rootless use cases.",
    "A user UI to start, stop toolhive mcp-optimizer using thv command line",
    "Utility",
    "la-toolhive-thv-ui",
    "la-toolhive-thv-ui-cli",
    "la-toolhive-thv-ui",
    "la-toolhive-thv-ui",
    "com.vai-int.la-toolhive-thv-ui",
    "value.added.kr@gmail.com",
    "Gerald Staruiala",
    "OWNER/la-toolhive-thv-ui",
    "OWNER",
    "la-toolhive-thv-ui",
    "la-toolhive-thv-ui",
    "2026-04-13",
    "2026",
]


def build_substitutions(cfg: dict) -> list[tuple[str, str]]:
    pkg = cfg["pkg_name"]
    return [
        ("la-toolhive-thv-ui", pkg),
        ("la-toolhive-thv-ui-cli", f"{pkg}-cli"),
        ("la-toolhive-thv-ui",                   pkg),
        ("la-toolhive-thv-ui",                      pkg),
        ("la_toolhive_thv_ui_tray",                f"{cfg['module_name']}_tray"),
        ("la_toolhive_thv_ui",                 cfg["module_name"]),
        ("thv command line has more features and options than Toolhive UI, additionally it is more stable.  The package is to give simular administrative functions to the user for thv but using the users UI (KDE, Gnome, XFCE) and has a system tray notification to indicate the state of the users thv service and the running mcp servers.  The package is adress short comings with Linux and Podman Rootless use cases.",              cfg["description_long"]),
        ("A user UI to start, stop toolhive mcp-optimizer using thv command line",                   cfg["description"]),
        ("Utility",                  cfg["generic_name"]),
        ("la-toolhive-thv-ui",                   cfg["source_name"]),
        ("la-toolhive-thv-ui-cli",              f"{cfg['bin_name']}-cli"),
        ("la-toolhive-thv-ui",                  cfg["bin_name"]),
        ("la-toolhive-thv-ui",                          pkg),
        ("com.vai-int.la-toolhive-thv-ui",                            cfg["app_id"]),
        ("value.added.kr@gmail.com",                  cfg["maintainer_email"]),
        ("Gerald Staruiala",                   cfg["maintainer_name"]),
        ("OWNER/la-toolhive-thv-ui",                        cfg["gh_slug"]),
        ("OWNER",                             cfg["gh_owner"]),
        ("la-toolhive-thv-ui",                              cfg["gh_repo"]),
        ("la-toolhive-thv-ui",                      pkg),
        ("2026-04-13",                        cfg["date"]),
        ("2026",                              cfg["year"]),
        # Inline in Python source files
        (f"com.example.{pkg}",               cfg["app_id"]),
    ]


_TEXT_EXTENSIONS = {
    ".py", ".sh", ".md", ".txt", ".rst",
    ".toml", ".ini", ".cfg", ".conf",
    ".desktop", ".service", ".spec", ".xml",
    ".yml", ".yaml", ".json",
    ".install", ".links",
    ".1", ".5", ".8",
    "",         # extensionless files: PKGBUILD, Makefile, VERSION, control, rules, …
}

_SKIP_ROOTS = {
    ".git", ".venv", "dist", "build_rpm",
    "arch/pkg", "arch/src",
    "extracted_deb_package",
}


def _is_text(path: Path) -> bool:
    if path.suffix in _TEXT_EXTENSIONS:
        return True
    # Extensionless: only known names
    if not path.suffix:
        return path.name in {
            "PKGBUILD", "Makefile", "VERSION", "LICENSE",
            "control", "rules", "changelog", "copyright",
            "watch", "conffiles", "dirs", "postinst", "prerm",
            "CONTRIBUTING", "CHANGELOG", "README",
        }
    return False


def _should_skip(path: Path) -> bool:
    try:
        rel = path.relative_to(ROOT)
    except ValueError:
        return True
    for skip in _SKIP_ROOTS:
        parts = Path(skip).parts
        if rel.parts[: len(parts)] == parts:
            return True
    return False


def replace_in_file(path: Path, subs: list[tuple[str, str]]) -> bool:
    try:
        original = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False
    result = original
    for old, new in subs:
        if old in result:
            result = result.replace(old, new)
    if result != original:
        path.write_text(result, encoding="utf-8")
        return True
    return False


def replace_in_tree(subs: list[tuple[str, str]]) -> int:
    changed = 0
    for path in ROOT.rglob("*"):
        if _should_skip(path) or not path.is_file():
            continue
        if _is_text(path):
            if replace_in_file(path, subs):
                changed += 1
    return changed

# ---------------------------------------------------------------------------
# Rename package-specific files
# ---------------------------------------------------------------------------

def rename_package_files(cfg: dict):
    pkg = cfg["pkg_name"]
    renames = [
        (ROOT / "debian" / "la-toolhive-thv-ui.install",
         ROOT / "debian" / f"{pkg}.install"),
        (ROOT / "debian" / "la-toolhive-thv-ui.links",
         ROOT / "debian" / f"{pkg}.links"),
        (ROOT / "rpm" / "la-toolhive-thv-ui.spec",
         ROOT / "rpm" / f"{pkg}.spec"),
    ]
    for src, dst in renames:
        if src.exists():
            src.rename(dst)
            print(_ok(f"Renamed  {src.name}  →  {dst.name}"))
        elif dst.exists():
            print(f"    {DIM}(already: {dst.name}){RESET}")
        else:
            print(_warn(f"Not found, skipping: {src.name}"))

# ---------------------------------------------------------------------------
# Remove unused feature files and patch packaging references
# ---------------------------------------------------------------------------

def _remove(path: Path):
    if path.is_file():
        path.unlink()
        print(_ok(f"Removed  {path.relative_to(ROOT)}"))


def _remove_lines_containing(path: Path, fragments: list[str]):
    """Remove lines from a text file that contain any of the given fragments."""
    if not path.exists():
        return
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    kept = [l for l in lines if not any(f in l for f in fragments)]
    if len(kept) != len(lines):
        path.write_text("".join(kept), encoding="utf-8")


def remove_unused_components(cfg: dict):
    pkg = cfg["pkg_name"]
    install_file = ROOT / "debian" / f"{pkg}.install"

    if not cfg["has_tray"]:
        _remove(ROOT / "src" / "tray.py")
        _remove(ROOT / "src" / "desktop" / "app-autostart.desktop")
        _remove(ROOT / "src" / "systemd" / "app.service")
        _rmdir_if_empty(ROOT / "src" / "systemd")
        # Patch packaging
        _remove_lines_containing(install_file, ["tray.py", "autostart", "systemd"])
        _patch_spec_remove(ROOT / "rpm" / f"{pkg}.spec",
                           ["tray.py", "autostart", "systemd", "la-toolhive-thv-ui-tray"])
        _patch_pkgbuild_remove(["tray.py", "autostart", "systemd", "la-toolhive-thv-ui-tray"])
        print(_ok("Removed tray, autostart, and systemd references from packaging"))
    else:
        if not cfg["login_xdg"]:
            _remove(ROOT / "src" / "desktop" / "app-autostart.desktop")
            _remove_lines_containing(install_file, ["autostart"])
            _patch_spec_remove(ROOT / "rpm" / f"{pkg}.spec", ["autostart"])
            _patch_pkgbuild_remove(["autostart"])

        if not cfg["login_systemd"]:
            _remove(ROOT / "src" / "systemd" / "app.service")
            _rmdir_if_empty(ROOT / "src" / "systemd")
            _remove_lines_containing(install_file, ["systemd"])
            _patch_spec_remove(ROOT / "rpm" / f"{pkg}.spec", ["systemd"])
            _patch_pkgbuild_remove(["systemd"])


def _rmdir_if_empty(path: Path):
    if path.is_dir() and not any(path.iterdir()):
        path.rmdir()
        print(_ok(f"Removed empty directory  {path.relative_to(ROOT)}"))


def _patch_spec_remove(spec: Path, fragments: list[str]):
    if spec.exists():
        _remove_lines_containing(spec, fragments)


def _patch_pkgbuild_remove(fragments: list[str]):
    pkgbuild = ROOT / "arch" / "PKGBUILD"
    if pkgbuild.exists():
        _remove_lines_containing(pkgbuild, fragments)

# ---------------------------------------------------------------------------
# Rewrite debian/changelog
# ---------------------------------------------------------------------------

def rewrite_changelog(cfg: dict):
    pkg = cfg["pkg_name"]
    maintainer = f"{cfg['maintainer_name']} <{cfg['maintainer_email']}>"
    content = (
        f"{pkg} (1.0.0) unstable; urgency=low\n\n"
        f"  * Initial release.\n\n"
        f" -- {maintainer}  {cfg['date_rfc2822']}\n"
    )
    (ROOT / "debian" / "changelog").write_text(content, encoding="utf-8")
    print(_ok("Rewrote  debian/changelog"))

# ---------------------------------------------------------------------------
# Configuration & data directory stubs
# ---------------------------------------------------------------------------

def create_config_stubs(cfg: dict):
    pkg = cfg["pkg_name"]

    # ── Dynamic user config (~/.config/la-toolhive-thv-ui/) ───────────────────────────
    if cfg["user_config"] == 3:
        _write_user_config_module(cfg)

    # ── Static system config (/etc/la-toolhive-thv-ui/) ───────────────────────────────
    if cfg["user_config"] == 2 or cfg["system_config"]:
        etc_path = cfg.get("etc_path") or f"etc/{pkg}"
        _write_static_config(cfg, etc_path)

    # ── User data dir (~/.local/share/la-toolhive-thv-ui/) ─────────────────────────────
    if cfg["user_data"]:
        _write_data_module(cfg)

    # ── System var directory ──────────────────────────────────────────────────
    if cfg["var_path"]:
        _write_tmpfiles(cfg)


def _write_user_config_module(cfg: dict):
    pkg = cfg["pkg_name"]
    path = ROOT / "src" / "config.py"
    path.write_text(textwrap.dedent(f'''\
        #!/usr/bin/env python3
        """User configuration loader for {cfg["display_name"]}.

        Config file location: ~/.config/{pkg}/config.ini
        A default config is written on first run if absent.
        Edit DEFAULTS to add application-specific settings.
        """
        import configparser
        import os
        from pathlib import Path

        la-toolhive-thv-ui = "{pkg}"

        CONFIG_DIR  = Path(os.environ.get("XDG_CONFIG_HOME",
                           Path.home() / ".config")) / la-toolhive-thv-ui
        CONFIG_FILE = CONFIG_DIR / "config.ini"

        DEFAULTS: dict[str, dict[str, str]] = {{
            "general": {{
                "autostart": "true",
            }},
            # TODO: Add your application-specific config sections and keys here.
        }}


        def load() -> configparser.ConfigParser:
            """Return a ConfigParser populated from disk (or defaults if absent)."""
            parser = configparser.ConfigParser()
            for section, values in DEFAULTS.items():
                parser[section] = values
            if CONFIG_FILE.exists():
                parser.read(CONFIG_FILE, encoding="utf-8")
            else:
                _write(parser)
            return parser


        def save(parser: configparser.ConfigParser) -> None:
            """Persist *parser* to ~/.config/{pkg}/config.ini."""
            _write(parser)


        def _write(parser: configparser.ConfigParser) -> None:
            CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            with open(CONFIG_FILE, "w", encoding="utf-8") as fh:
                parser.write(fh)
    '''), encoding="utf-8")
    print(_ok("Created  src/config.py  (dynamic user config loader)"))


def _write_static_config(cfg: dict, etc_path: str):
    pkg = cfg["pkg_name"]
    src_cfg_dir = ROOT / "src" / "config"
    src_cfg_dir.mkdir(exist_ok=True)
    ini = src_cfg_dir / "config.ini"
    ini.write_text(textwrap.dedent(f"""\
        ; Default system configuration for {cfg['display_name']}
        ; Installed to /{etc_path}/config.ini by the package.
        ;
        ; To override per-user, copy this file to:
        ;   ~/.config/{pkg}/config.ini
        ; and edit the relevant values.

        [general]
        autostart = true

        ; TODO: Add your application-specific sections and keys here.
    """), encoding="utf-8")
    print(_ok(f"Created  src/config/config.ini  (static system config — /{etc_path}/)"))

    # Add install line to debian .install
    install_file = ROOT / "debian" / f"{pkg}.install"
    if install_file.exists():
        content = install_file.read_text(encoding="utf-8")
        entry = f"src/config/config.ini              {etc_path}/\n"
        if "src/config/config.ini" not in content:
            install_file.write_text(content + entry, encoding="utf-8")
            print(_ok(f"Updated  debian/{pkg}.install  with /etc config path"))

    # Arch: add backup= array so pacman asks before overwriting on upgrade
    pkgbuild = ROOT / "arch" / "PKGBUILD"
    if pkgbuild.exists():
        content = pkgbuild.read_text(encoding="utf-8")
        if "backup=" not in content:
            content = content.replace(
                "source=()",
                f"backup=('{etc_path}/config.ini')\nsource=()")
            pkgbuild.write_text(content, encoding="utf-8")
            print(_ok("Updated  arch/PKGBUILD  with backup= array"))


def _write_data_module(cfg: dict):
    pkg = cfg["pkg_name"]
    path = ROOT / "src" / "data.py"
    path.write_text(textwrap.dedent(f'''\
        #!/usr/bin/env python3
        """XDG user data and cache directory helpers for {cfg["display_name"]}."""
        import os
        from pathlib import Path

        la-toolhive-thv-ui = "{pkg}"

        DATA_DIR  = Path(os.environ.get("XDG_DATA_HOME",
                         Path.home() / ".local" / "share")) / la-toolhive-thv-ui
        CACHE_DIR = Path(os.environ.get("XDG_CACHE_HOME",
                         Path.home() / ".cache")) / la-toolhive-thv-ui


        def ensure_dirs() -> None:
            """Create user data and cache directories on first run."""
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            CACHE_DIR.mkdir(parents=True, exist_ok=True)
    '''), encoding="utf-8")
    print(_ok("Created  src/data.py  (XDG user data/cache directory helpers)"))


def _write_tmpfiles(cfg: dict):
    pkg  = cfg["pkg_name"]
    var  = cfg["var_path"]
    tdir = ROOT / "src" / "tmpfiles.d"
    tdir.mkdir(exist_ok=True)
    conf = tdir / f"{pkg}.conf"
    conf.write_text(textwrap.dedent(f"""\
        # systemd-tmpfiles configuration for {cfg['display_name']}
        # Ensures /{var} exists on every boot (created if absent, never deleted).
        # Installed to /usr/lib/tmpfiles.d/{pkg}.conf by the package.
        #
        # Type  Path          Mode  UID   GID   Age  Argument
        d       /{var}        0755  root  root  -
    """), encoding="utf-8")
    print(_ok(f"Created  src/tmpfiles.d/{pkg}.conf  (ensures /{var} on boot)"))

    # Add to debian .install
    install_file = ROOT / "debian" / f"{pkg}.install"
    if install_file.exists():
        content = install_file.read_text(encoding="utf-8")
        entry = f"src/tmpfiles.d/{pkg}.conf        usr/lib/tmpfiles.d/\n"
        if "tmpfiles.d" not in content:
            install_file.write_text(content + entry, encoding="utf-8")
            print(_ok(f"Updated  debian/{pkg}.install  with tmpfiles.d entry"))

    # Add to RPM spec %files
    spec = ROOT / "rpm" / f"{pkg}.spec"
    if spec.exists():
        content = spec.read_text(encoding="utf-8")
        entry = f"/usr/lib/tmpfiles.d/{pkg}.conf\n"
        if "tmpfiles.d" not in content:
            # Insert before last %files block end
            content = content.replace(
                "/usr/share/man/man1/",
                f"/usr/share/man/man1/\n{entry}")
            spec.write_text(content, encoding="utf-8")

    # Add to PKGBUILD
    pkgbuild = ROOT / "arch" / "PKGBUILD"
    if pkgbuild.exists():
        content = pkgbuild.read_text(encoding="utf-8")
        if "tmpfiles.d" not in content:
            snippet = (
                f'\n    # System var directory (created on boot via tmpfiles.d)\n'
                f'    install -Dm644 "${{startdir}}/../src/tmpfiles.d/{pkg}.conf" \\\n'
                f'        "${{pkgdir}}/usr/lib/tmpfiles.d/{pkg}.conf"\n'
            )
            # Insert before the closing brace of the first package function
            content = content.replace(
                "}\n\n# -----------",
                snippet + "}\n\n# -----------",
                1,
            )
            pkgbuild.write_text(content, encoding="utf-8")

# ---------------------------------------------------------------------------
# Virtual environment
# ---------------------------------------------------------------------------

def create_venv(cfg: dict):
    print(_h("── Creating virtual environment ──────────────────────────────"))

    venv_dir = ROOT / ".venv"
    python   = cfg["python_bin"]

    print(f"\n  Creating {venv_dir.relative_to(ROOT)}/ using {python} …")
    try:
        subprocess.run([python, "-m", "venv", str(venv_dir)], check=True, cwd=ROOT)
        print(_ok(f".venv created at {venv_dir}"))
    except subprocess.CalledProcessError as exc:
        print(_err(f"python -m venv failed: {exc}"))
        return

    pip = venv_dir / "bin" / "pip"
    packages = ["PyQt6"]

    print(f"\n  Installing into .venv: {' '.join(packages)} …")
    try:
        subprocess.run([str(pip), "install", "--quiet"] + packages,
                       check=True, cwd=ROOT)
        print(_ok(f"Installed: {', '.join(packages)}"))
    except subprocess.CalledProcessError as exc:
        print(_err(f"pip install failed: {exc}"))

    print(_warn(
        "python3-dbus requires system build headers.\n"
        "    Install system-wide instead:  sudo apt install python3-dbus  "
        "(Debian/Ubuntu)\n"
        "                                  sudo dnf install python3-dbus  "
        "(Fedora/RHEL)\n"
        "                                  sudo pacman -S python-dbus  "
        "(Arch)"))

    # Ensure .venv/ is in .gitignore
    gitignore = ROOT / ".gitignore"
    if gitignore.exists():
        text = gitignore.read_text(encoding="utf-8")
        if ".venv" not in text:
            gitignore.write_text(text + "\n# Virtual environment\n.venv/\n",
                                 encoding="utf-8")
            print(_ok("Added .venv/ to .gitignore"))

# ---------------------------------------------------------------------------
# Git remote
# ---------------------------------------------------------------------------

def setup_git(cfg: dict):
    remote = cfg.get("git_remote", "")
    if not remote:
        return
    print(_h("── Git remote ────────────────────────────────────────────────"))
    try:
        existing = _git_remote()
        if existing:
            subprocess.run(
                ["git", "remote", "set-url", "origin", remote],
                cwd=ROOT, check=True,
            )
            print(_ok(f"Remote 'origin' updated  →  {remote}"))
        else:
            subprocess.run(
                ["git", "remote", "add", "origin", remote],
                cwd=ROOT, check=True,
            )
            print(_ok(f"Remote 'origin' added  →  {remote}"))
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        print(_warn(f"Could not update git remote: {exc}"))

# ---------------------------------------------------------------------------
# Next steps
# ---------------------------------------------------------------------------

def print_next_steps(cfg: dict):
    pkg       = cfg["pkg_name"]
    venv_note = "\n    source .venv/bin/activate" if cfg["use_venv"] else ""
    tray_line = (
        f"\n    src/tray.py          (system tray)"
        if cfg["has_tray"] else ""
    )
    push_line = (
        f"\n    git push -u origin main"
        if cfg.get("git_remote") else ""
    )

    print(_h("══ Done! ═════════════════════════════════════════════════════"))
    print(f"""
  ① Review remaining TODOs:
      grep -rn 'TODO' src/ debian/ rpm/ arch/

  ② Add your application icons to src/icons/:
      {pkg}.svg           main app icon  (→ hicolor theme, shown in launchers)
      tray-active.svg     tray icon active state
      tray-inactive.svg   tray icon inactive state

  ③ Implement your application logic:
      src/app.py           (main window){tray_line}

  ④ Validate the desktop entry:
      desktop-file-validate src/desktop/app.desktop

  ⑤ Build packages:{venv_note}
      make deb             (requires: debhelper devscripts)
      make rpm             (requires: rpm-build)
      make arch            (requires: base-devel makepkg)

  ⑥ Commit:
      git add -A
      git commit -m "feat: initialise {pkg} from template"{push_line}
""")

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    print(f"\n{BOLD}{CYAN}"
          "╔══════════════════════════════════════════════╗\n"
          "║   Linux Package Scaffolding Tool             ║\n"
          "╚══════════════════════════════════════════════╝"
          f"{RESET}")
    print(f"  Working directory: {DIM}{ROOT}{RESET}\n")

    cfg  = gather_config()
    preview(cfg)
    subs = build_substitutions(cfg)

    print(_h("── Applying changes ──────────────────────────────────────────"))
    print()

    # 1. Replace all placeholder strings in every text file in the tree
    changed = replace_in_tree(subs)
    print(_ok(f"Updated placeholders in {changed} file(s)"))

    # 2. Rename packaging files to match the project name
    rename_package_files(cfg)

    # 3. Remove source files for unneeded features; patch packaging references
    remove_unused_components(cfg)

    # 4. Rewrite debian/changelog with correct package name and maintainer
    rewrite_changelog(cfg)

    # 5. Generate config/data stubs based on selected options
    create_config_stubs(cfg)

    # 6. Virtual environment
    if cfg["use_venv"]:
        create_venv(cfg)

    # 7. Git remote
    setup_git(cfg)

    print_next_steps(cfg)


if __name__ == "__main__":
    main()
