# Build conditionals (with - OFF, without - ON)...
%bcond_with rlottie
%bcond_with gtk3
# FIXME as of 2.8.1, telegram-desktop crashes on startup with
# an illegal instruction while calling global constructors
# if built with clang.
# It works fine when built with gcc - but we need to figure
# out why at some point.
%bcond_with clang
%bcond_without spellcheck
%bcond_without fonts
%bcond_without ipo
%bcond_without mindbg
%bcond_without gsl

# Telegram Desktop's constants...
%global appname tdesktop
%global launcher telegramdesktop
%global tarsuffix -full

# Telegram API tokens...
%global apiid 208164
%global apihash dfbe1bc42dc9d20507e17d1814cc2f0a

# Applying workaround to RHBZ#1559007...
%if %{with clang}
%global optflags %(echo %{optflags} | sed -e 's/-mcet//g' -e 's/-fcf-protection//g' -e 's/-fstack-clash-protection//g' -e 's/$/ -Qunused-arguments -Wno-unknown-warning-option/') -I%{_includedir}/minizip
%else
%global optflags %{optflags} -I%{_includedir}/minizip -fno-lto
%endif

%global build_ldflags %(echo %{build_ldflags} -Wl,-z,notext)

# Decrease debuginfo verbosity to reduce memory consumption...
%if %{with mindbg}
%global optflags %(echo %{optflags} | sed 's/-g /-g1 /')
%endif

Name: telegram-desktop
# before every upgrade
# try to up tg_owt project first
Version:	4.9.3
Release:	2

# Application and 3rd-party modules licensing:
# * Telegram Desktop - GPLv3+ with OpenSSL exception -- main tarball;
# * rlottie - LGPLv2+ -- static dependency;
# * qt_functions.cpp - LGPLv3 -- build-time dependency.
License: GPLv3+ and LGPLv2+ and LGPLv3
URL: https://github.com/telegramdesktop/%{appname}
Summary: Telegram Desktop official messaging app

# Source files...
# Upstream frequently forgets to make the -full release. When that happens,
# use the package-source.sh script in this repository.
Source0: https://github.com/telegramdesktop/tdesktop/releases/download/v%{version}/%{appname}-%{version}%{tarsuffix}.tar.gz
Patch1: telegram-2.8.6-compile.patch
Patch2: tdesktop-4.6.5-workaround-assert-on-startup.patch
Patch3: tdesktop-4.8.4-compile.patch
# This is a backport of a revert of upstream commit
# 74be75339d474df1a2863028ec146744597bd0bb
Patch4:	telegram-4.8.12-dont-require-unstable-glibmm.patch
Patch5: tdesktop-2.3.2-no-underlinking.patch
Patch6: tdesktop-2.7.9-compile.patch
Patch7: tdesktop-3.3.2-system-minizip.patch
Patch8: tdesktop-4.9.3-compile.patch

Requires: hicolor-icon-theme

# Telegram Desktop require patched version of rlottie since 1.8.0.
# Pull Request pending: https://github.com/Samsung/rlottie/pull/252
%if %{with rlottie}
BuildRequires: pkgconfig(rlottie)
%else
Provides: bundled(rlottie) = 0~git
%endif

# Telegram Desktop require patched version of lxqt-qtplugin.
# Pull Request pending: https://github.com/lxqt/lxqt-qtplugin/pull/52
Provides: bundled(lxqt-qtplugin) = 0.14.0~git

# Compilers and tools...
BuildRequires: desktop-file-utils
BuildRequires: cmake

# Development packages for Telegram Desktop...
BuildRequires: cmake(Microsoft.GSL)
BuildRequires: pkgconfig(protobuf)
BuildRequires: mapbox-variant-devel
BuildRequires: pkgconfig(libavcodec)
BuildRequires: pkgconfig(libavformat)
BuildRequires: pkgconfig(xkbcommon)
BuildRequires: pkgconfig(glibmm-2.68)
BuildRequires: cmake(ECM)
BuildRequires: cmake(tl-expected)
BuildRequires: pkgconfig(libyuv)
BuildRequires: qr-code-generator-devel
BuildRequires: qr-code-generator-c++-devel
BuildRequires: pkgconfig(openal)
BuildRequires: pkgconfig(tgvoip)
BuildRequires: pkgconfig(xcb-keysyms)
BuildRequires: libstdc++-devel
BuildRequires: range-v3-devel
BuildRequires: atomic-devel
BuildRequires: boost-devel
BuildRequires: pkgconfig(openssl)
BuildRequires: pkgconfig(minizip)
BuildRequires: pkgconfig(libxxhash)
BuildRequires: appstream-util
BuildRequires: pkgconfig(opus)
BuildRequires: pkgconfig(liblzma)
BuildRequires: pkgconfig(json11)
BuildRequires: pkgconfig(liblz4)
BuildRequires: pkgconfig(libjpeg)
BuildRequires: pkgconfig(hunspell)
BuildRequires: pkgconfig(alsa)
BuildRequires: pkgconfig(libpulse)
BuildRequires: pkgconfig(openh264)
BuildRequires: pkgconfig(vpx)
BuildRequires: pkgconfig(rnnoise)
BuildRequires: pkgconfig(minizip)
BuildRequires: pkgconfig(libzip)
BuildRequires: pkgconfig(gobject-introspection-1.0)
# FIXME is this really necessary? It's there because
# cppgir forces -lstdc++fs, but that may not actually
# be needed...
BuildRequires: stdc++-static-devel
BuildRequires: cmake(fmt)
BuildRequires: cmake(RapidJSON)
BuildRequires: qmake-qt6
BuildRequires: qt6-qtbase-tools
BuildRequires: cmake(Qt6)
BuildRequires: cmake(Qt6Core)
BuildRequires: cmake(Qt6Core5Compat)
BuildRequires: cmake(Qt6DBus)
BuildRequires: cmake(Qt6Network)
BuildRequires: cmake(Qt6Gui)
BuildRequires: cmake(Qt6Svg)
BuildRequires: cmake(Qt6WaylandClient)
BuildRequires: cmake(Qt6OpenGL)
BuildRequires: cmake(Qt6OpenGLWidgets)
BuildRequires: cmake(Qt6Qml)
BuildRequires: cmake(Qt6Quick)
BuildRequires: cmake(Qt6QuickWidgets)
BuildRequires: cmake(Qt6Widgets)
BuildRequires: cmake(Qt6WaylandClient)
BuildRequires: cmake(Qt6WaylandCompositor)
BuildRequires: cmake(tg_owt)
BuildRequires: wayland-devel
BuildRequires: qt6-qtwayland
BuildRequires: ninja
%ifarch %{x86_64} %{ix86}
BuildRequires: yasm
%endif
# FIXME At some point the cmake files should stop looking
# for libraries that aren't being used
#BuildRequires: cmake(Qt5Svg)
#BuildRequires: cmake(KF5CoreAddons)

%if %{with gtk3}
BuildRequires: pkgconfig(appindicator3-0.1)
BuildRequires: pkgconfig(gtk+-3.0)
BuildRequires: pkgconfig(dee-1.0)
Requires: %{_lib}gtk3_0
%endif

%if %{with spellcheck}
BuildRequires: enchant2-devel
BuildRequires: glib2.0-devel
%endif

%if %{with clang}
BuildRequires: clang
BuildRequires: llvm
%endif

%if %{with fonts}
Requires: open-sans-fonts
%endif

%description
Telegram is a messaging app with a focus on speed and security, it’s super
fast, simple and free. You can use Telegram on all your devices at the same
time — your messages sync seamlessly across any number of your phones,
tablets or computers.

With Telegram, you can send messages, photos, videos and files of any type
(doc, zip, mp3, etc), as well as create groups for up to 50,000 people or
channels for broadcasting to unlimited audiences. You can write to your
phone contacts and find people by their usernames. As a result, Telegram is
like SMS and email combined — and can take care of all your personal or
business messaging needs.

%prep
export LC_ALL=en_US.utf-8
# Unpacking Telegram Desktop source archive...
%autosetup -p1 -n %{appname}-%{version}%{tarsuffix}
# Unbundling libraries...
rm -rf Telegram/ThirdParty/{Catch,GSL,QR,SPMediaKeyTap,expected,libdbusmenu-qt,libtgvoip,lz4,minizip,variant,xxHash,mallocng}

export PATH=%{_libdir}/qt6/bin:$PATH
%cmake -G Ninja \
    -DCMAKE_BUILD_TYPE=Release \
    -DDESKTOP_APP_QT6:BOOL=ON \
    -DQT_VERSION_MAJOR=6 \
    -DDESKTOP_APP_DISABLE_JEMALLOC:BOOL=ON \
%if %{without gtk3}
    -DDESKTOP_APP_DISABLE_GTK_INTEGRATION:BOOL=ON \
    -DDESKTOP_APP_DISABLE_WEBKITGTK:BOOL=ON \
%endif
%if %{without spellcheck}
    -DDESKTOP_APP_DISABLE_SPELLCHECK:BOOL=ON \
%endif
%if %{without fonts}
    -DDESKTOP_APP_USE_PACKAGED_FONTS:BOOL=OFF \
%endif
%if %{with ipo} && %{with mindbg} && %{without clang}
    -DDESKTOP_APP_ENABLE_IPO_OPTIMIZATIONS:BOOL=ON \
%endif
%if %{with rlottie}
    -DDESKTOP_APP_USE_PACKAGED_RLOTTIE:BOOL=ON \
    -DDESKTOP_APP_LOTTIE_USE_CACHE:BOOL=OFF \
%else
    -DDESKTOP_APP_USE_PACKAGED_RLOTTIE:BOOL=OFF \
    -Drlottie_DIR=`pwd`/../Telegram/ThirdParty/rlottie \
%endif
%if %{with clang}
    -DCMAKE_C_COMPILER=clang \
    -DCMAKE_CXX_COMPILER=clang++ \
    -DCMAKE_AR=%{_bindir}/llvm-ar \
    -DCMAKE_RANLIB=%{_bindir}/llvm-ranlib \
    -DCMAKE_LINKER=%{_bindir}/llvm-ld \
    -DCMAKE_OBJDUMP=%{_bindir}/llvm-objdump \
    -DCMAKE_NM=%{_bindir}/llvm-nm \
%else
    -DCMAKE_AR=%{_bindir}/gcc-ar \
    -DCMAKE_RANLIB=%{_bindir}/gcc-ranlib \
    -DCMAKE_NM=%{_bindir}/gcc-nm \
    -DCMAKE_C_COMPILER=gcc \
    -DCMAKE_CXX_COMPILER=g++ \
%endif
    -DTDESKTOP_API_ID=%{apiid} \
    -DTDESKTOP_API_HASH=%{apihash} \
    -DDESKTOP_APP_USE_PACKAGED:BOOL=ON \
    -DDESKTOP_APP_USE_PACKAGED_GSL:BOOL=OFF \
    -DDESKTOP_APP_USE_PACKAGED_EXPECTED:BOOL=ON \
    -DDESKTOP_APP_USE_PACKAGED_VARIANT:BOOL=ON \
    -DDESKTOP_APP_USE_PACKAGED_QRCODE:BOOL=ON \
    -DDESKTOP_APP_USE_GLIBC_WRAPS:BOOL=OFF \
    -DDESKTOP_APP_DISABLE_CRASH_REPORTS:BOOL=ON \
    -DTDESKTOP_USE_PACKAGED_TGVOIP:BOOL=OFF \
    -DTDESKTOP_DISABLE_REGISTER_CUSTOM_SCHEME:BOOL=ON \
    -DTDESKTOP_DISABLE_DESKTOP_FILE_GENERATION:BOOL=ON \
    -DTDESKTOP_LAUNCHER_BASENAME=%{launcher}

%build
touch build/changelog.txt

PROCESSES="$(getconf _NPROCESSORS_ONLN)"
# Linking Telegram with LTO enabled is VERY RAM intensive
# and breaks boxes that have loads of CPU cores but not
# terabytes of RAM...
[ "$PROCESSES" -gt 4 ] && PROCESSES=4

%ninja_build -C build -j${PROCESSES}

%install
%ninja_install -C build

%check
appstream-util validate-relax --nonet %{buildroot}%{_metainfodir}/org.telegram.desktop.metainfo.xml
# validate hates "SingleMainWindow"
#desktop-file-validate %{buildroot}%{_datadir}/applications/%{launcher}.desktop

%files
%doc README.md changelog.txt
%license LICENSE LEGAL
%{_bindir}/%{name}
%{_datadir}/applications/org.telegram.desktop.desktop
%{_datadir}/icons/hicolor/*/apps/*.png
%{_datadir}/dbus-1/services/org.telegram.desktop.service
%optional %{_metainfodir}/org.telegram.desktop.metainfo.xml
