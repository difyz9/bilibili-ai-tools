#!/usr/bin/env python3
"""B站多P视频下载脚本 — 用官方API获取流地址 + ffmpeg下载"""
import json
import os
import subprocess
import sys
import time
import urllib.request

BVID = "BV1N6tt6oE3i"
OUT_DIR = os.path.expanduser("~/Downloads/bilibili/AI导演思维课")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
REFERER = f"https://www.bilibili.com/video/{BVID}"

os.makedirs(OUT_DIR, exist_ok=True)

def fetch(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Referer": REFERER,
        "Accept": "application/json",
    })
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())

def get_video_urls(cid):
    """获取分P的视频流URL（清晰度优先）"""
    api = f"https://api.bilibili.com/x/player/playurl?bvid={BVID}&cid={cid}&qn=64&fnval=4048&fourk=1"
    d = fetch(api)
    if d["code"] != 0:
        return None, None
    data = d["data"]
    # 找最高清晰度的视频+音频
    video_url, audio_url = None, None
    dash = data.get("dash")
    if dash:
        videos = sorted(dash.get("video", []), key=lambda x: x.get("id", 0), reverse=True)
        audios = sorted(dash.get("audio", []), key=lambda x: x.get("id", 0), reverse=True)
        if videos:
            video_url = videos[0]["baseUrl"]
        if audios:
            audio_url = audios[0]["baseUrl"]
    else:
        durl = data.get("durl")
        if durl:
            video_url = durl[0]["url"]
    return video_url, audio_url

def download(url, path):
    """用 ffmpeg 或 curl 下载"""
    if os.path.exists(path) and os.path.getsize(path) > 1024*1024:
        return True
    if url.startswith("http"):
        cmd = ["curl", "-sL", "-o", path, "-H", f"User-Agent: {UA}", "-H", f"Referer: {REFERER}", url]
    else:
        return False
    r = subprocess.run(cmd, timeout=600)
    return r.returncode == 0 and os.path.getsize(path) > 1024*1024

def main():
    # 获取视频信息
    info = fetch(f"https://api.bilibili.com/x/web-interface/view?bvid={BVID}")
    if info["code"] != 0:
        print(f"获取视频信息失败: {info.get('message')}")
        sys.exit(1)
    data = info["data"]
    title = data["title"]
    print(f"系列: {title} ({data['videos']} 集)")

    for page in data["pages"]:
        idx = page["page"]
        cid = page["cid"]
        part = page["part"]
        safe_part = part.replace("/", "_").replace(" ", "_")[:60]
        print(f"\n[{idx}/14] {part} (cid={cid})")

        video_url, audio_url = get_video_urls(cid)
        if not video_url:
            print(f"  ✗ 获取流地址失败")
            continue

        v_path = os.path.join(OUT_DIR, f"p{idx:02d}_{safe_part}.m4s")
        a_path = os.path.join(OUT_DIR, f"p{idx:02d}_{safe_part}.aac")
        out_path = os.path.join(OUT_DIR, f"p{idx:02d}_{safe_part}.mp4")

        if not os.path.exists(out_path) or os.path.getsize(out_path) < 1024*1024:
            if download(video_url, v_path):
                print(f"  ✓ 视频流已下载")
            else:
                print(f"  ✗ 视频流下载失败")
                continue
            if audio_url:
                download(audio_url, a_path)
                print(f"  ✓ 音频流已下载")
            # 合并
            if audio_url and os.path.exists(a_path):
                r = subprocess.run([
                    "ffmpeg", "-y", "-i", v_path, "-i", a_path,
                    "-c", "copy", out_path
                ], capture_output=True, timeout=300)
                if r.returncode == 0:
                    print(f"  ✓ 合并完成")
                else:
                    print(f"  ✗ 合并失败，保留 m4s")
            else:
                os.rename(v_path, out_path)
                print(f"  ✓ 已保存（无音轨）")
            # 清理中间文件
            for p in (v_path, a_path):
                if os.path.exists(p):
                    os.remove(p)
        else:
            print(f"  ✓ 已存在，跳过")
        time.sleep(1)  # 避免限流

    print("\n=== 全部完成 ===")

if __name__ == "__main__":
    main()
