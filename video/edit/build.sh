#!/bin/bash
# usage: [EDL=edl_song2.py] ./build.sh WIDE.mov HAND.mov OUT_DIR [SCALE] [CRF]
#   EDL   : 編集データ（省略時 edl.py = 1曲目）
#   WIDE  : 全体カメラ（音源もここから抽出）
#   HAND  : 手持ちカメラ（映像のみ使用）
#   SCALE : 1 = 1920x1080 / 0.5 = 確認用プレビュー
set -euo pipefail
WIDE=$1; HAND=$2; OUT=$3; SC=${4:-1}; CRF=${5:-18}
HERE=$(cd "$(dirname "$0")" && pwd)
export EDL=${EDL:-edl.py}
LOAD="import runpy; edl = type('E', (), runpy.run_path('$HERE/$EDL'))"
DUR=$(python3 -c "$LOAD; print(edl.DURATION)")
NAME=$(python3 -c "$LOAD; print(getattr(edl, 'OUTPUT_NAME', 'f_it_up_edit'))")
mkdir -p "$OUT"
# 4 並列でチャンクごとにレンダリング
B=($(python3 -c "d=$DUR; print(' '.join(str(round(d*i/4/ (1/30))*(1/30)) for i in range(5)))"))
for i in 0 1 2 3; do
  python3 "$HERE/render.py" "$WIDE" "$HAND" "$OUT" --start "${B[$i]}" --end "${B[$((i+1))]}" \
    --scale "$SC" --crf "$CRF" > "$OUT/log_$i.txt" 2>&1 &
done
wait
ls "$OUT"/chunk_*.mp4 | sed "s/^/file '/;s/$/'/" > "$OUT/list.txt"
# edl.MUTE の区間だけ音を消す（前後 0.05 秒でフェード）
AF=$(python3 -c "
$LOAD
g = ['min(1,max(0,max((%s-t)/0.05,(t-%s)/0.05)))' % (a, b) for a, b in getattr(edl, 'MUTE', [])]
print('volume=' + chr(39) + ('*'.join(g) or '1') + chr(39) + ':eval=frame')")
ffmpeg -v error -y -f concat -safe 0 -i "$OUT/list.txt" -i "$WIDE" -map 0:v -map 1:a \
  -c:v copy -af "$AF" -c:a aac -b:a 256k -t "$DUR" -movflags +faststart "$OUT/$NAME.mp4"
echo "done: $OUT/$NAME.mp4"
