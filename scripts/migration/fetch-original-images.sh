#!/usr/bin/env bash
# Fetch original images still hosted on Google Sites (lh3.googleusercontent.com).
#
# These URLs were IP-blocked from some datacenter networks during migration.
# Run this script from any normal connection (home/office) after cloning:
#   bash scripts/migration/fetch-original-images.sh
#
# It replaces the placeholder SVG used for the Mind Buddha Hymn page.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
IMG="$ROOT/public/images"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"

declare -A IMAGES=(
  # home banners (zh)
  ["banner-zh-1.jpg"]="https://lh3.googleusercontent.com/sitesv/AG8ngQUKQLK9vSaqmrL5_6pSx8EXJyR-LdfO1lylbDN1hSzLIqFj6VboXEhbgemxIrA14KIzPuWPeLWsyAsPJx2TvfeflSiF6EK8IKOy01HgMsIxfJK9g_MJIErSyp4zzO5aqCMn3yza-hW_8GWb2GMziL9YzvLpy2DeMpRzawVM2Rotgl588BxdLnxaHpjgV13MplQqcY3KOTKwmDAMpslviaIPedUXrsmnuAiR7OeE=w1280"
  ["banner-zh-2.jpg"]="https://lh3.googleusercontent.com/sitesv/AG8ngQX1-_F2WzvkBwb38LO3KLh2iwktdO718iouzaVQnt2sjTMdEddim1GGIVI7OHx6O8mSUsENxU_KLO7LeK42Sg2xCmHOBcVmdZ6paZWB1"
  # home banners (en)
  ["banner-en-1.jpg"]="https://lh3.googleusercontent.com/sitesv/AG8ngQU1kOXzXskvbESBI6_QwXkJNwQLKsi1z2sfdaMCCS6KGo807e_5E9FQZ8_UHb1I2mWeX8Hz0oZMgj8muxgHnyeC_Nrgp1YvNoVyrbB7u0aFqyGoqYs6MaUqJMwY9LxyGMD0Ua9E2sEzira21tqbw_uQoT8d5Q8Sxbs-lpgKYCSmIZA3nXx2Olz4stlbM1E8o1sQ0Eu9brMBRWeTEeYU0ExG10WheZ8-YdUL9U0XiuA=w1280"
  ["banner-en-2.jpg"]="https://lh3.googleusercontent.com/sitesv/AG8ngQUUoVPf9EP9P1tjK0fMVPcTrDyroqmjz04AuCcwQToSZkze4quuv5dtw0Qq5YkI_VsrvOHCTnskBhuleDXmdaGWiMODG1r3MJu1Eudoz"
  # Mind Buddha Hymn calligraphy (page content)
  ["mind-buddha.jpg"]="https://lh3.googleusercontent.com/sitesv/AG8ngQU4OdjUm5dZ24EAj3oDoKdUDRjt-io-lFl619xX3KZGi5q9qixLDAZ-2c9VQaDA6CIDqCpb7OxXHZ_WOMEHvSxoppp8DrSHFaiasxzoA7AGpQFtUlb8Yl9DEe9xhUCxrtdD_95osjBcs7y6O3azrKRycRc0cRmqyREnwjOgE3ApcXj0jYoIKmov6qyAdhq6BvfESQQUkpFfv6Jn8xg=w1280"
)

mkdir -p "$IMG"
ok=0
for name in "${!IMAGES[@]}"; do
  url="${IMAGES[$name]}"
  echo "Fetching $name ..."
  if curl -fsSL -A "$UA" -o "$IMG/$name" "$url"; then
    ok=$((ok+1))
  else
    echo "  !! failed (blocked network? try another connection)" >&2
    rm -f "$IMG/$name"
  fi
done

echo
echo "Downloaded $ok/${#IMAGES[@]} images."

if [ -f "$IMG/mind-buddha.jpg" ]; then
  # swap placeholder references to the real image
  for f in "$ROOT/src/data/content/mind-buddha.json"; do
    sed -i 's#/images/mind-buddha\.svg#/images/mind-buddha.jpg#' "$f"
  done
  rm -f "$IMG/mind-buddha.svg"
  echo "mind-buddha references updated to .jpg"
fi
