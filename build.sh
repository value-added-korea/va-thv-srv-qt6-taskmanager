#!/bin/bash
set -e

# Scaffold the distribution directory exclusively inside the project root
mkdir -p dist

echo "Building Native Standalone CLI Package (Headless)..."
dpkg-deb --build build_cli_deb dist/la-toolhive-thv-ui-cli_1.0.1_all.deb
echo "CLI Package Compiled -> dist/la-toolhive-thv-ui-cli_1.0.1_all.deb"

echo "Building Integrated GUI PyQT Package natively..."
dpkg-buildpackage -us -uc

echo "Routing Debian artifacts directly into local project output natively..."
mv ../la-toolhive-thv-ui_1.0.1_all.deb dist/ 2>/dev/null || true
mv ../la-toolhive-thv-ui_1.0.1.dsc dist/ 2>/dev/null || true
mv ../la-toolhive-thv-ui_1.0.1_amd64.buildinfo dist/ 2>/dev/null || true
mv ../la-toolhive-thv-ui_1.0.1_amd64.changes dist/ 2>/dev/null || true
mv ../la-toolhive-thv-ui_1.0.1.tar.xz dist/ 2>/dev/null || true

echo "Building Native Arch Linux Packages (via makepkg)..."
cd arch
makepkg --nodeps -f
mv ./*.pkg.tar.zst ../dist/ 2>/dev/null || true
cd ..

echo "Compilation execution bounds completed. All packages stored optimally inside ./dist directory."
