#!/bin/bash
#
# Should be run as: sudo ./dailyrun-bundleonly.sh
#

MAC_VERSION=`sw_vers -productVersion | cut -d '.' -f 2`
ARCH=`perl -MFink::FinkVersion -e 'print Fink::FinkVersion::get_arch'`

defaults write com.apple.desktopservices DSDontWriteNetworkStores true

/Users/ailabc/mount-dirs.sh || { echo "Mounting failed." ; exit 1 ; }

/Users/ailabc/bundle-daily-build.sh &> /private/tmp/bundle-daily-build.log
EXIT_VALUE=$?

/Users/ailabc/mount-dirs.sh || { echo "Mounting failed." ; exit 1 ; }

echo "Orange (bundle $MAC_VERSION) [$EXIT_VALUE]" > "/Volumes/download/buildLogs/osx/bundle-$MAC_VERSION-daily-build.log"
date >> "/Volumes/download/buildLogs/osx/bundle-$MAC_VERSION-daily-build.log"
cat /private/tmp/bundle-daily-build.log >> "/Volumes/download/buildLogs/osx/bundle-$MAC_VERSION-daily-build.log"
(($EXIT_VALUE)) && echo "Running bundle-daily-build.sh failed"

# Zero exit value
true
