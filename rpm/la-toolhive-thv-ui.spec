# ---------------------------------------------------------------------------
# RPM spec file template
# TODO: Rename this file: mv rpm/la-toolhive-thv-ui.spec rpm/la-toolhive-thv-ui.spec
# TODO: Replace all APP_* and OWNER/la-toolhive-thv-ui placeholders.
# ---------------------------------------------------------------------------

Name:           la-toolhive-thv-ui
Version:        1.0.0
Release:        1%{?dist}
Summary:        A user UI to start, stop toolhive mcp-optimizer using thv command line
License:        MIT
URL:            https://github.com/OWNER/la-toolhive-thv-ui
Source0:        %{name}-%{version}.tar.gz
BuildArch:      noarch

# Ensure icon and desktop caches are refreshed on install/removal
BuildRequires:  desktop-file-utils
BuildRequires:  libappstream-glib

# ---------------------------------------------------------------------------
# GUI subpackage
# ---------------------------------------------------------------------------
%package -n la-toolhive-thv-ui
Summary:        A user UI to start, stop toolhive mcp-optimizer using thv command line
Requires:       python3
Requires:       python3-pyqt6
Requires:       python3-dbus
# GNOME users need the AppIndicator extension for the system tray icon.
# It is not listed as a hard dependency because it is optional on non-GNOME.
Recommends:     la-toolhive-thv-ui-cli = %{version}-%{release}

# ---------------------------------------------------------------------------
# CLI subpackage
# ---------------------------------------------------------------------------
%package -n la-toolhive-thv-ui-cli
Summary:        A user UI to start, stop toolhive mcp-optimizer using thv command line (CLI only)
Requires:       python3

# ---------------------------------------------------------------------------
%description -n la-toolhive-thv-ui
thv command line has more features and options than Toolhive UI, additionally it is more stable.  The package is to give simular administrative functions to the user for thv but using the users UI (KDE, Gnome, XFCE) and has a system tray notification to indicate the state of the users thv service and the running mcp servers.  The package is adress short comings with Linux and Podman Rootless use cases.

The system tray component supports GNOME (with AppIndicator extension),
Xfce, and KDE. It can be autostarted on login via XDG autostart or a
user systemd service.

%description -n la-toolhive-thv-ui-cli
Command-line component of %{name}. Suitable for headless servers and
environments without a desktop session.

%description
thv command line has more features and options than Toolhive UI, additionally it is more stable.  The package is to give simular administrative functions to the user for thv but using the users UI (KDE, Gnome, XFCE) and has a system tray notification to indicate the state of the users thv service and the running mcp servers.  The package is adress short comings with Linux and Podman Rootless use cases.

# ---------------------------------------------------------------------------
%prep
%setup -q -c

# ---------------------------------------------------------------------------
%install
# Application data
install -d %{buildroot}/usr/share/%{name}
install -Dm755 src/app.py   %{buildroot}/usr/share/%{name}/app.py
install -Dm755 src/tray.py  %{buildroot}/usr/share/%{name}/tray.py

# /usr/bin entry points (symlinks)
install -d %{buildroot}/usr/bin
ln -sf ../share/%{name}/app.py  %{buildroot}/usr/bin/la-toolhive-thv-ui
ln -sf ../share/%{name}/tray.py %{buildroot}/usr/bin/la-toolhive-thv-ui-tray

# XDG desktop entry
install -Dm644 src/desktop/app.desktop \
    %{buildroot}/usr/share/applications/la-toolhive-thv-ui.desktop

# XDG autostart entry
install -Dm644 src/desktop/app-autostart.desktop \
    %{buildroot}/etc/xdg/autostart/la-toolhive-thv-ui-tray.desktop

# Icons → hicolor theme (GNOME, Xfce, KDE all search here)
find src/icons/ -maxdepth 1 -name "*.svg" -exec install -Dm644 {} \
    %{buildroot}/usr/share/icons/hicolor/scalable/apps/ \;
find src/icons/ -maxdepth 1 -name "*.png" -exec install -Dm644 {} \
    %{buildroot}/usr/share/icons/hicolor/256x256/apps/ \;

# Tray-specific icons → app data directory
install -d %{buildroot}/usr/share/%{name}/icons
find src/icons/ -maxdepth 1 \( -name "tray-*.svg" -o -name "tray-*.png" \
    -o -name "tray-*.ico" \) -exec cp -p {} \
    %{buildroot}/usr/share/%{name}/icons/ \; || true

# User systemd service
install -Dm644 src/systemd/app.service \
    %{buildroot}/usr/lib/systemd/user/la-toolhive-thv-ui.service

# AppStream metainfo
install -Dm644 src/metainfo/app.metainfo.xml \
    %{buildroot}/usr/share/metainfo/com.vai-int.la-toolhive-thv-ui.metainfo.xml

# Man page
install -d %{buildroot}/usr/share/man/man1
install -m644 src/*.1 %{buildroot}/usr/share/man/man1/

# ---------------------------------------------------------------------------
%post -n la-toolhive-thv-ui
/usr/bin/update-desktop-database &>/dev/null || true
/usr/bin/gtk-update-icon-cache /usr/share/icons/hicolor &>/dev/null || true

%postun -n la-toolhive-thv-ui
/usr/bin/update-desktop-database &>/dev/null || true
/usr/bin/gtk-update-icon-cache /usr/share/icons/hicolor &>/dev/null || true

# ---------------------------------------------------------------------------
%files -n la-toolhive-thv-ui
/usr/bin/la-toolhive-thv-ui
/usr/bin/la-toolhive-thv-ui-tray
%dir /usr/share/%{name}/
/usr/share/%{name}/app.py
/usr/share/%{name}/tray.py
%dir /usr/share/%{name}/icons/
/usr/share/%{name}/icons/
/usr/share/applications/la-toolhive-thv-ui.desktop
/etc/xdg/autostart/la-toolhive-thv-ui-tray.desktop
/usr/share/icons/hicolor/scalable/apps/
/usr/share/icons/hicolor/256x256/apps/
/usr/lib/systemd/user/la-toolhive-thv-ui.service
/usr/share/metainfo/com.vai-int.la-toolhive-thv-ui.metainfo.xml

%files -n la-toolhive-thv-ui-cli
/usr/bin/la-toolhive-thv-ui
%dir /usr/share/%{name}/
/usr/share/%{name}/app.py
/usr/share/man/man1/
