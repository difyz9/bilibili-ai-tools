#!/usr/bin/env bash
# 批量转写 14 集视频 → 字幕（srt + txt）
set -e

DIR="$HOME/Downloads/bilibili/AI导演思维课"
OUT="$HOME/Downloads/bilibili/subtitles"
MODEL="$HOME/.biliup/models/ggml-base.bin"
mkdir -p "$OUT"

cd "$DIR"
count=0
for f in *.mp4; do
  count=$((count+1))
  base="${f%.mp4}"
  echo "=== [$count/14] $base ==="
  
  # 提取音频
  ffmpeg -y -i "$f" -vn -acodec pcm_s16le -ar 16000 -ac 1 "/tmp/audio_$$.wav" 2>/dev/null
  
  # 转写（输出 srt + txt）
  whisper-cli -m "$MODEL" -l zh -osrt -otxt -of "$OUT/$base" "/tmp/audio_$$.wav" 2>/dev/null
  
  echo "  ✓ 完成: $OUT/$base.srt"
done
rm -f "/tmp/audio_$$.wav"
echo ""
echo "=== 全部转写完成，共 $count 集 ==="
