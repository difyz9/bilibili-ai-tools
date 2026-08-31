# Bilibili AI 工具集

B 站视频批量下载 + 听录转写 + AI 影视制作 Skill

## 目录

- `scripts/` — B站多P视频下载脚本（B站官方API + ffmpeg）、批量听录转写脚本（whisper.cpp）
- `skill/ai-film-director/` — AI 影视导演工作流 Skill（源自《AI导演思维课》14集课程听录提炼）

## 使用

### 下载 B 站多P系列
```bash
python3 scripts/download_series.py   # 修改脚本顶部的 BVID
```

### 批量听录生成字幕
```bash
bash scripts/transcribe_all.sh       # 需先安装 whisper.cpp 和 ffmpeg
```
