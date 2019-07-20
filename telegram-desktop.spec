# Enable or disable build with GTK support...
%bcond_without gtk3

# Enable or disable build using clang instead of gcc...
%bcond_without clang

# Telegram Desktop's constants...
%global appname tdesktop
%global apiid 208164
%global apihash dfbe1bc42dc9d20507e17d1814cc2f0a
%global upstreambase https://github.com/telegramdesktop

# Git revision of crl...
%global commit1 9ea870038a2a667add7f621be6252db909068386
%global shortcommit1 %(c=%{commit1}; echo ${c:0:7})

# Decrease debuginfo verbosity to reduce memory consumption...
%global optflags %(echo %{optflags} | sed 's/-g /-g1 /')

# Applying workaround to RHBZ#1559007...
%if %{with clang}
%global optflags %(echo %{optflags} | sed -e 's/-mcet//g' -e 's/-fcf-protection//g' -e 's/-fstack-clash-protection//g' -e 's/$/ -Qunused-arguments -Wno-unknown-warning-option/')
%endif

Summary: Telegram Desktop official messaging app
Name: telegram-desktop
Version: 1.7.15
Release: 1%{?dist}

# Application and 3rd-party modules licensing:
# * S0 (Telegram Desktop) - GPLv3+ with OpenSSL exception -- main source;
# * S1 (crl) - GPLv3+ -- build-time dependency;
# * S2 (qtlottie) - GPLv3+ -- build-time dependency;
# * P0 (qt_functions.cpp) - LGPLv3 -- build-time dependency.
License: GPLv3+ and LGPLv3
URL: %{upstreambase}/%{appname}
ExclusiveArch: %{ix86} %{x86_64}

# Source files...
Source0: %{url}/archive/v%{version}.tar.gz#/%{appname}-%{version}.tar.gz
Source1: %{upstreambase}/crl/archive/%{commit1}.tar.gz#/crl-%{shortcommit1}.tar.gz

# Downstream patches...
Patch0: %{name}-build-fixes.patch
Patch1: %{name}-system-fonts.patch
Patch2: %{name}-unbundle-minizip.patch
Patch3:	tdesktop_lottie_animation_qtdebug.patch

%{?_qt5:Requires: %{_qt5} = %{_qt5_version}}
Requires: qt5-qtimageformats
Requires: hicolor-icon-theme
#Requires: open-sans-fonts

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
BuildRequires: xxhash-devel
BuildRequires: pkgconfig(opus)
BuildRequires: pkgconfig(liblzma)
BuildRequires: pkgconfig(Qt5Gui)
BuildRequires: pkgconfig(json11)
BuildRequires: pkgconfig(liblz4)
BuildRequires: cmake(RapidJSON)
BuildRequires: python2-pkg-resources
BuildRequires: rlottie-devel

%if %{with gtk3}
BuildRequires: pkgconfig(appindicator3-0.1)
BuildRequires: pkgconfig(gtk+-3.0)
BuildRequires: pkgconfig(dee-1.0)
Requires: %{_lib}gtk3_0
%endif

%if %{with clang}
BuildRequires: clang
BuildRequires: llvm
%endif

BuildRequires: minizip-devel

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
%autosetup -n %{appname}-%{version} -p1

# Unpacking crl...
pushd Telegram/ThirdParty
    rm -rf crl
    tar -xf %{SOURCE1}
    mv crl-%{commit1} crl
popd

%build
# Setting build definitions...
%if %{without gtk3}
TDESKTOP_BUILD_DEFINES+='TDESKTOP_DISABLE_GTK_INTEGRATION,'
%endif
TDESKTOP_BUILD_DEFINES+='TDESKTOP_DISABLE_AUTOUPDATE,'
TDESKTOP_BUILD_DEFINES+='TDESKTOP_DISABLE_REGISTER_CUSTOM_SCHEME,'
TDESKTOP_BUILD_DEFINES+='TDESKTOP_DISABLE_DESKTOP_FILE_GENERATION,'
TDESKTOP_BUILD_DEFINES+='TDESKTOP_DISABLE_CRASH_REPORTS,'
TDESKTOP_BUILD_DEFINES+='TDESKTOP_LAUNCHER_FILENAME=%{name}.desktop,'

# Generating cmake script using GYP...
pushd Telegram/gyp
    gyp --depth=. --generator-output=../.. -Goutput_dir=out -Dapi_id=%{apiid} -Dapi_hash=%{apihash} -Dbuild_defines=$TDESKTOP_BUILD_DEFINES Telegram.gyp --format=cmake
popd

# Patching generated cmake script...
LEN=$(($(wc -l < out/Release/CMakeLists.txt) - 2))
sed -i "$LEN r Telegram/gyp/CMakeLists.inj" out/Release/CMakeLists.txt

# Building Telegram Desktop using cmake...
pushd out/Release
    %cmake \
%if %{with clang}
    -DCMAKE_C_COMPILER=clang \
    -DCMAKE_CXX_COMPILER=clang++ \
    -DCMAKE_AR=%{_bindir}/llvm-ar \
    -DCMAKE_RANLIB=%{_bindir}/llvm-ranlib \
    -DCMAKE_LINKER=%{_bindir}/llvm-ld \
    -DCMAKE_OBJDUMP=%{_bindir}/llvm-objdump \
    -DCMAKE_NM=%{_bindir}/llvm-nm
%else
    -DCMAKE_AR=%{_bindir}/gcc-ar \
    -DCMAKE_RANLIB=%{_bindir}/gcc-ranlib \
    -DCMAKE_NM=%{_bindir}/gcc-nm
%endif
    
    %make_build
popd

%install
# Installing executables...
%{__mkdir_p} "%{buildroot}%{_bindir}"
%{__install} -m 0755 -p out/Release/Telegram "%{buildroot}%{_bindir}/%{name}"

# Installing desktop shortcut...
%{__mv} lib/xdg/telegramdesktop.desktop lib/xdg/%{name}.desktop
desktop-file-install --dir="%{buildroot}%{_datadir}/applications" lib/xdg/%{name}.desktop

# Installing icons...
for size in 16 32 48 64 128 256 512; do
    dir="%{buildroot}%{_datadir}/icons/hicolor/${size}x${size}/apps"
    %{__install} -d "$dir"
    %{__install} -m 0644 -p Telegram/Resources/art/icon${size}.png "$dir/%{name}.png"
done

# Installing appdata for Gnome Software...
%{__install} -d %{buildroot}%{_metainfodir}
%{__install} -m 0644 -p lib/xdg/telegramdesktop.appdata.xml %{buildroot}%{_metainfodir}/%{name}.appdata.xml

%files
%doc README.md changelog.txt
%license LICENSE LEGAL
%{_bindir}/%{name}
%{_datadir}/applications/%{name}.desktop
%{_datadir}/icons/hicolor/*/apps/%{name}.png
%{_metainfodir}/%{name}.appdata.xml
