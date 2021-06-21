#!/bin/sh
# Telegram maintainers frequently forget to make the "full" tarball,
# and the github tarball doesn't include submodules
V="$1"
if [ -z "$V" ]; then
	echo "Required argument: Version number"
	exit 1
fi
D="$(realpath $(dirname $0))"
T="$(mktemp -d /tmp/telegramXXXXXX)"
cd "$T"
git clone -b v$V --depth 1 https://github.com/telegramdesktop/tdesktop
cd tdesktop
git submodule update --init --recursive
find . -name .git |xargs rm -rf
cd ..
mv tdesktop tdesktop-$V-full
tar czf "$D/tdesktop-$V-full.tar.gz" tdesktop-$V-full
rm -rf "$T"
