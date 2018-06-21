# Telegram Desktop's constants...
%global appname tdesktop

# Git revision of crl...
%global commit1 c739b14bc04ca3ce740893fef9bffe2bcca99629
%global shortcommit1 %(c=%{commit1}; echo ${c:0:7})

# Decrease debuginfo verbosity to reduce memory consumption...
%global optflags %(echo %{optflags} | sed 's/-g /-g1 /')

Summary: Telegram Desktop official messaging app
Name: telegram-desktop
Version: 1.3.7
Release: 1

# Application and 3rd-party modules licensing:
# * S0 (Telegram Desktop) - GPLv3+ with OpenSSL exception -- main source;
# * S1 (crl) - GPLv3+ -- build-time dependency;
# * P0 (qt_functions.cpp) - LGPLv3 -- build-time dependency.
License: GPLv3+ and LGPLv3
URL: https://github.com/telegramdesktop/%{appname}

Source0: %{url}/archive/v%{version}.tar.gz
Source1: https://github.com/telegramdesktop/crl/archive/%{commit1}.tar.gz
Patch0: %{name}-build-fixes.patch
Patch2: %{name}-system-fonts.patch
#Patch1: %{name}-api-tokens.patch

Requires: qt5-qtimageformats
Requires: hicolor-icon-theme

# Compilers and tools...
BuildRequires: desktop-file-utils
BuildRequires: cmake
BuildRequires: gyp

# Development packages for Telegram Desktop...
BuildRequires: guidelines-support-library-devel
BuildRequires: mapbox-variant-devel
BuildRequires: ffmpeg-devel
BuildRequires: openal-soft-devel
BuildRequires: qt5-qtbase-devel
BuildRequires: tgvoip-devel
BuildRequires: libstdc++-devel
BuildRequires: range-v3-devel
BuildRequires: openssl-devel
BuildRequires: minizip-devel
BuildRequires: pkgconfig(opus)
BuildRequires: pkgconfig(gtk+-3.0)
BuildRequires: pkgconfig(dee-1.0)
BuildRequires: pkgconfig(liblzma)
BuildRequires: pkgconfig(appindicator3-0.1)
BuildRequires: pkgconfig(Qt5Gui)
BuildRequires: python2

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
%setup -n %{appname}-%{version}
%apply_patches

# Unpacking crl...
pushd Telegram/ThirdParty
    rm -rf crl
    tar -xf %{SOURCE1}
    mv crl-%{commit1} crl
popd
sed -i 's!appindicator-0.1!appindicator3-0.1!g' Telegram/gyp/telegram_linux.gypi

%build
export CC=/usr/bin/gcc
export CXX=/usr/bin/g++
# Generating cmake script using GYP...
pushd Telegram/gyp
    gyp --depth=. --generator-output=../.. -Goutput_dir=out Telegram.gyp --format=cmake
popd

# Patching generated cmake script...
LEN=$(($(wc -l < out/Release/CMakeLists.txt) - 2))
sed -i "$LEN r Telegram/gyp/CMakeLists.inj" out/Release/CMakeLists.txt

# Building Telegram Desktop using cmake...
pushd out/Release
    %cmake
    %make
popd

%install
# Installing executables...
mkdir -p "%{buildroot}%{_bindir}"
install -m 0755 -p out/Release/build/Telegram "%{buildroot}%{_bindir}/%{name}"

# Installing desktop shortcut...
mv lib/xdg/telegramdesktop.desktop lib/xdg/%{name}.desktop
desktop-file-install --dir="%{buildroot}%{_datadir}/applications" lib/xdg/%{name}.desktop

# Installing icons...
for size in 16 32 48 64 128 256 512; do
    dir="%{buildroot}%{_datadir}/icons/hicolor/${size}x${size}/apps"
    install -d "$dir"
    install -m 0644 -p Telegram/Resources/art/icon${size}.png "$dir/%{name}.png"
done

# Installing tg protocol handler...
install -d "%{buildroot}%{_datadir}/kde4/services"
install -m 0644 -p lib/xdg/tg.protocol "%{buildroot}%{_datadir}/kde4/services/tg.protocol"

# Installing appdata for Gnome Software...
install -d "%{buildroot}%{_datadir}/metainfo"
install -m 0644 -p lib/xdg/telegramdesktop.appdata.xml "%{buildroot}%{_datadir}/metainfo/%{name}.appdata.xml"

%files
%doc README.md changelog.txt
%{_bindir}/%{name}
%{_datadir}/applications/%{name}.desktop
%{_datadir}/kde4/services/tg.protocol
%{_datadir}/icons/hicolor/*/apps/%{name}.png
%{_datadir}/metainfo/%{name}.appdata.xml
