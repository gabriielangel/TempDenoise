#!/usr/bin/env bash
set -e
APPNAME=TemporalDenoiser
mkdir -p dist_dmg
DMG=dist_dmg/${APPNAME}_$(date +%s).dmg
if command -v create-dmg >/dev/null 2>&1; then
  create-dmg --overwrite --skip-jenkins --volname "$APPNAME" --window-size 500 300 --icon-size 100 --app-drop-link 250 150 "$DMG" dist
else
  TMPDIR=$(mktemp -d)
  cp -R dist/${APPNAME}.app "$TMPDIR/"
  hdiutil create -volname "$APPNAME" -srcfolder "$TMPDIR" -ov -format UDZO "$DMG"
  rm -rf "$TMPDIR"
fi
echo "Created $DMG"
