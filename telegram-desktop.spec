# Build conditionals (with - OFF, without - ON)...
%bcond_with rlottie
%bcond_with gtk3
%bcond_without clang
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
%global optflags %(echo %{optflags} | sed -e 's/-mcet//g' -e 's/-fcf-protection//g' -e 's/-fstack-clash-protection//g' -e 's/$/ -Qunused-arguments -Wno-unknown-warning-option/')
%endif

%global build_ldflags %(echo %{build_ldflags} -Wl,-z,notext)

# Decrease debuginfo verbosity to reduce memory consumption...
%if %{with mindbg}
%global optflags %(echo %{optflags} | sed 's/-g /-g1 /')
%endif

Name: telegram-desktop
# before every upgrade
# try to up tg_owt project first
Version:	2.7.4
Release:	1

# Application and 3rd-party modules licensing:
# * Telegram Desktop - GPLv3+ with OpenSSL exception -- main tarball;
# * rlottie - LGPLv2+ -- static dependency;
# * qt_functions.cpp - LGPLv3 -- build-time dependency.
License: GPLv3+ and LGPLv2+ and LGPLv3
URL: https://github.com/telegramdesktop/%{appname}
Summary: Telegram Desktop official messaging app

# Source files...
Source0: %{url}/releases/download/v%{version}/%{appname}-%{version}%{tarsuffix}.tar.gz
Patch4:	tdesktop-2.1.7-openssl3.patch
Patch5: tdesktop-2.3.2-no-underlinking.patch
Patch6: tdesktop-2.7.4-zlib-ng.patch

# Telegram Desktop require exact version of Qt due to Qt private API usage.
%{?_qt5:Requires: %{_qt5}%{?_isa} = %{_qt5_version}}
Requires: qt5-qtimageformats%{?_isa}
Requires: hicolor-icon-theme

# Telegram Desktop require patched version of rlottie since 1.8.0.
# Pull Request pending: https://github.com/Samsung/rlottie/pull/252
%if %{with rlottie}
BuildRequires: rlottie-devel >= 0-7.20200825gitff8ddfc
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
BuildRequires: pkgconfig(glibmm-2.4)
BuildRequires: cmake(tl-expected)
BuildRequires: pkgconfig(libyuv)
BuildRequires: qr-code-generator-devel
BuildRequires: qr-code-generator-c++-devel
BuildRequires: pkgconfig(openal)
BuildRequires: qt5-qtbase-devel
BuildRequires: pkgconfig(tgvoip)
BuildRequires: pkgconfig(xcb-keysyms)
BuildRequires: libstdc++-devel
BuildRequires: range-v3-devel
BuildRequires: atomic-devel
BuildRequires: pkgconfig(openssl)
BuildRequires: pkgconfig(minizip)
BuildRequires: pkgconfig(libxxhash)
BuildRequires: appstream-util
BuildRequires: pkgconfig(opus)
BuildRequires: pkgconfig(liblzma)
BuildRequires: pkgconfig(Qt5Gui)
BuildRequires: pkgconfig(json11)
BuildRequires: pkgconfig(liblz4)
BuildRequires: pkgconfig(libjpeg)
BuildRequires: pkgconfig(hunspell)
BuildRequires: pkgconfig(alsa)
BuildRequires: pkgconfig(libpulse)
BuildRequires: pkgconfig(openh264)
BuildRequires: pkgconfig(vpx)
BuildRequires: cmake(RapidJSON)
BuildRequires: cmake(Qt5Network)
BuildRequires: cmake(Qt5Core)
BuildRequires: cmake(dbusmenu-qt5)
BuildRequires: cmake(Qt5WaylandClient)
BuildRequires: cmake(Qt5XkbCommonSupport)
BuildRequires: cmake(tg_owt)
BuildRequires: cmake(kf5wayland)
BuildRequires: qt5-qtwayland-private-devel
BuildRequires: wayland-devel
BuildRequires: qt5-qtwayland
BuildRequires: ninja
%ifarch %{x86_64} %{ix86}
BuildRequires: yasm
%endif

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
# Unpacking Telegram Desktop source archive...
%autosetup -p1 -n %{appname}-%{version}%{tarsuffix}
# Unbundling libraries...
rm -rf Telegram/ThirdParty/{Catch,GSL,QR,SPMediaKeyTap,expected,libdbusmenu-qt,libtgvoip,lz4,minizip,variant,xxHash}

# Patching default desktop file...
desktop-file-edit --set-key=Exec --set-value="%{_bindir}/%{name} -- %u" --copy-name-to-generic-name lib/xdg/telegramdesktop.desktop

%cmake -G Ninja \
    -DCMAKE_BUILD_TYPE=Release \
%if %{without gtk3}
    -DDESKTOP_APP_DISABLE_GTK_INTEGRATION:BOOL=ON \
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
%ninja_build -C build

%install
%ninja_install -C build

%check
#appstream-util validate-relax --nonet %{buildroot}%{_metainfodir}/%{launcher}.appdata.xml
desktop-file-validate %{buildroot}%{_datadir}/applications/%{launcher}.desktop

%files
%doc README.md changelog.txt
%license LICENSE LEGAL
%{_bindir}/%{name}
%{_datadir}/applications/%{launcher}.desktop
%{_datadir}/icons/hicolor/*/apps/*.png
%{_metainfodir}/%{launcher}.appdata.xml
