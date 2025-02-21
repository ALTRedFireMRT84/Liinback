import os
import requests
import tempfile
from flask import Flask, request, Response, send_from_directory
import subprocess
processing_content = set()
class GetVideoInfo:
    def build(self, videoId):
        streamUrl = f"https://www.youtube.com/youtubei/v1/player?key=AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8&videoId={videoId}"
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        payload = {
            "context": {
                "client": {
                    "hl": "en",
                    "gl": "US",
                    "clientName": "WEB",
                    "clientVersion": "2.20210714.01.00"
                }
            },
            "videoId": videoId,
            "params": ""
        }
        response = requests.post(streamUrl, json=payload, headers=headers)
        if response.status_code != 200:
            return f"Error retrieving video info: {response.status_code}", response.status_code
        
        try:
            json_data = response.json()
            title = json_data['videoDetails']['title']
            length_seconds = json_data['videoDetails']['lengthSeconds']
            author = json_data['videoDetails']['author']
        except KeyError as e:
            return f"Missing key: {e}", 400
        
        fmtList = "43/854x480/9/0/115"
        fmtStreamMap = f"43|"
        fmtMap = "43/0/7/0/0"    
        thumbnailUrl = f"http://i.ytimg.com/vi/{videoId}/mqdefault.jpg"        
        response_str = (
            f"status=ok&"
            f"length_seconds={length_seconds}&"
            f"keywords=a&"
            f"vq=None&"
            f"muted=0&"
            f"avg_rating=5.0&"
            f"thumbnailUrl={thumbnailUrl}&"
            f"allow_ratings=1&"
            f"hl=en&"
            f"ftoken=&"
            f"allow_embed=1&"
            f"fmtMap={fmtMap}&"
            f"fmt_url_map={fmtStreamMap}&"
            f"token=null&"
            f"plid=null&"
            f"track_embed=0&"
            f"author={author}&"
            f"title={title}&"
            f"videoId={videoId}&"
            f"fmtList={fmtList}&"
            f"fmtStreamMap={fmtStreamMap.split()[0]}"
        )
        return Response(response_str, content_type='text/plain')
class GetVideo:
    def fetch_video_url(self, videoId):
        url = f'https://www.googleapis.com/youtubei/v1/player?key=AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8&videoId={videoId}'
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'com.google.android.youtube/19.02.39 (Linux; U; Android 14) gzip'
        }
        payload = {
            "context": {
                "client": {
                    "hl": "en",
                    "gl": "US",
                    "clientName": "ANDROID",
                    "clientVersion": "19.02.39",
                    "androidSdkVersion": 34,
                    "mainAppWebInfo": {
                        "graftUrl": "/watch?v=" + videoId
                    }
                }
            },
            "videoId": videoId
        }
        
        response = requests.post(url, headers=headers, json=payload)
        data = response.json()
        streamData = data.get('streamingData', {})
        formats = streamData.get('adaptiveFormats', []) + streamData.get('formats', [])
        
        for f in formats:
            if f.get('audioChannels') == 2 and f.get('mimeType').startswith('video/mp4'):
                return f.get('url')
        return None

    def build(self, videoId):
        temp_dir = tempfile.gettempdir()
        output = os.path.join(temp_dir, f"{videoId}.webm")
        
        if os.path.exists(output):
            return send_from_directory(temp_dir, f"{videoId}.webm", as_attachment=True)
        
        stream_url = self.fetch_video_url(videoId)
        if not stream_url:
            return Response("Error fetching video stream", status=500)
        
        ffmpeg_cmd = [
            'ffmpeg', '-i', stream_url,
            '-c:v', 'libvpx', '-b:v', '300k', '-cpu-used', '8',
            '-pix_fmt', 'yuv420p', '-c:a', 'libvorbis', '-b:a', '128k',
            '-r', '30', '-g', '30', output
        ]
        
        process = subprocess.run(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        if process.returncode == 0:
            return send_from_directory(temp_dir, f"{videoId}.webm", as_attachment=True)
        else:
            return Response("Error processing video", status=500)

    def fetch(self, videoId):
        return self.build(videoId)
