#!/bin/bash

TYPE="icon"
if [[ "$TYPE" == "" ]]; then
    echo "Error: empty name!"
    exit 1
fi

mkdir $TYPE".iconset"
cp $TYPE"_32.png" $TYPE".iconset/icon_32x32.png"
convert $TYPE".iconset/icon_32x32.png" -interpolate Nearest -filter point -resize 16x16 $TYPE".iconset/icon_16x16.png"
cp $TYPE".iconset/icon_32x32.png" $TYPE".iconset/icon_16x16@2x.png"
convert $TYPE".iconset/icon_32x32.png" -interpolate Nearest -filter point -resize 64x64 $TYPE".iconset/icon_32x32@2x.png"
convert $TYPE".iconset/icon_32x32.png" -interpolate Nearest -filter point -resize 48x48 $TYPE".iconset/icon_48x48.png"
convert $TYPE".iconset/icon_48x48.png" -interpolate Nearest -filter point -resize 96x96 $TYPE".iconset/icon_48x48@2x.png"
convert $TYPE".iconset/icon_32x32.png" -interpolate Nearest -filter point -resize 128x128 $TYPE".iconset/icon_128x128.png"
convert $TYPE".iconset/icon_32x32.png" -interpolate Nearest -filter point -resize 256x256 $TYPE".iconset/icon_256x256.png"
convert $TYPE".iconset/icon_32x32.png" -interpolate Nearest -filter point -resize 256x256 $TYPE".iconset/icon_128x128@2x.png"
convert $TYPE".iconset/icon_32x32.png" -interpolate Nearest -filter point -resize 512x512 $TYPE".iconset/icon_256x256@2x.png"

echo "makeIcon..."

iconutil -c icns $TYPE".iconset"

rm -Rf $TYPE".iconset"
