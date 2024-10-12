#!/usr/bin/env bash

source ../.venv/bin/activate
mkdir -p .buildozer/android/platform/build-arm64-v8a/dists/wavegen/src/main/res/xml
cp device_filter.xml .buildozer/android/platform/build-arm64-v8a/dists/wavegen/src/main/res/xml/
buildozer android debug
deactivate