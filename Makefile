VERSION  := $(shell cat VERSION)
PKG_NAME := $(shell awk '/^Source:/{print $$2}' debian/control)

.PHONY: all deb rpm arch clean

all: deb rpm arch

deb:
	@echo "==> Building CLI .deb (dpkg-deb)..."
	mkdir -p dist
	dpkg-deb --build build_cli_deb dist/$(PKG_NAME)-cli_$(VERSION)_all.deb
	@echo "==> Building full .deb (debhelper)..."
	dpkg-buildpackage -us -uc
	mv ../$(PKG_NAME)_$(VERSION)_all.deb dist/ 2>/dev/null || true
	mv ../$(PKG_NAME)_$(VERSION).dsc dist/ 2>/dev/null || true
	mv ../$(PKG_NAME)_$(VERSION)_amd64.buildinfo dist/ 2>/dev/null || true
	mv ../$(PKG_NAME)_$(VERSION)_amd64.changes dist/ 2>/dev/null || true
	mv ../$(PKG_NAME)_$(VERSION).tar.xz dist/ 2>/dev/null || true

rpm:
	@echo "==> Building RPM..."
	mkdir -p build_rpm/{SPECS,SOURCES,BUILD,RPMS,SRPMS}
	cp rpm/*.spec build_rpm/SPECS/
	tar czf build_rpm/SOURCES/$(PKG_NAME)-$(VERSION).tar.gz \
		--transform 's|^\./|$(PKG_NAME)-$(VERSION)/|' ./src
	rpmbuild --define "_topdir $(CURDIR)/build_rpm" -ba build_rpm/SPECS/$(PKG_NAME).spec
	mkdir -p dist
	find build_rpm/RPMS -name '*.rpm' -exec cp {} dist/ \;

arch:
	@echo "==> Building Arch package..."
	cd arch && makepkg --nodeps -f
	mkdir -p dist
	mv arch/*.pkg.tar.zst dist/ 2>/dev/null || true
	mv arch/*.pkg.tar.gz dist/ 2>/dev/null || true

clean:
	rm -rf dist/ build_rpm/ arch/pkg/ arch/src/
	rm -f arch/*.pkg.tar.zst arch/*.pkg.tar.gz arch/*.tar.xz
	rm -rf debian/.debhelper debian/debhelper-build-stamp debian/files
	rm -f debian/*.substvars debian/*.log debian/*.debhelper.log
	find debian/ -mindepth 1 -maxdepth 1 -type d -exec rm -rf {} +
