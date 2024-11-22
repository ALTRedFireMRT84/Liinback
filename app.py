from flask import Flask, request, jsonify, send_file, Response, redirect, send_from_directory, abort
import colorama
import requests
import os
import json
import subprocess
import threading
import yt_dlp
import xml.etree.ElementTree as ET
import re
from time import sleep
from debug import request_dump
from api import Invidious, InnerTube
from io import BytesIO
app = Flask(__name__)
colorama.init()
processingVideos = []
OAUTH2_DEVICE_CODE_URL = 'https://oauth2.googleapis.com/device/code'
OAUTH2_TOKEN_URL = 'https://oauth2.googleapis.com/token'
CLIENT_ID = '627431331381.apps.googleusercontent.com'
CLIENT_SECRET = 'O_HOjELPNFcHO_n_866hamcO'
REDIRECT_URI = ''
invidious = Invidious()
innerTube = InnerTube()
def installRequirements():
    packages = ['Flask', 'colorama', 'requests', 'yt-dlp']
    for package in packages:
        try:
            subprocess.check_call([os.sys.executable, "-m", "pip", "show", package])
        except subprocess.CalledProcessError:
            print(f"Installing {package}...")
            subprocess.check_call([os.sys.executable, "-m", "pip", "install", package])            
def buildConfiguration(ip, port, env):
    configuration = ET.Element("configuration")
    ipElem = ET.SubElement(configuration, "ip")
    ipElem.text = ip
    portElem = ET.SubElement(configuration, "port")
    portElem.text = port
    envElem = ET.SubElement(configuration, "env")
    envElem.text = env
    tree = ET.ElementTree(configuration)
    tree.write("configuration.xml")    
def getIp():
    tree = ET.parse('configuration.xml')
    root = tree.getroot()
    return root.find('ip').text
def getPort():
    tree = ET.parse('configuration.xml')
    root = tree.getroot()
    return root.find('port').text
def replaceToHTTP(url):
    if url.startswith("https://"):
        return url.replace("https://", "http://", 1)
    return url
@app.route('/api/search', methods=['GET'])
def search():
    oauthToken = request.args.get('access_token')
    lang = request.args.get('lang')
    ip = getIp()
    port = getPort()
    query = request.args.get('q')
    return innerTube.search(ip, port, query, lang)    
@app.route('/api/categories/<type>', methods=['GET'])
def _category(type):
    ip = getIp()
    port = getPort()
    oauthToken = request.args.get('access_token')
    lang = request.args.get('lang')
    return innerTube.category(ip, port, type, lang)        
@app.route('/api/categories/v2/<channelId>', methods=['GET'])
def _categoryTwo(channelId):
    ip = getIp()
    port = getPort()
    oauthToken = request.args.get('access_token')
    lang = request.args.get('lang')
    return innerTube.categoryTwo(ip, port, channelId, lang)    
@app.route('/api/popular', methods=['GET'])
def popular():
    ip = getIp()
    port = getPort()
    format = request.args.get('format')
    platform = request.args.get('platform')
    return invidious.popular(ip, port)
@app.route('/api/channels/default/uploads', methods=['GET'])
def userUploadsOauthToken():
    oauthToken = request.args.get('access_token')
    userInfoUrl = f"https://www.googleapis.com/youtube/v3/channels?part=snippet&mine=true&key=AIzaS=yAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8&access_token={oauthToken}"
    response = requests.get(userInfoUrl)
    if response.status_code == 200:
        data = response.json()
        if "items" in data and len(data["items"]) > 0:
            channelId = data["items"][0].get("id", "")
            if channelId:
                return redirect(f'/api/channels/{channelId}/uploads')
        return jsonify({"error": "No channel data found"}), 404
    return jsonify({"error": "Failed to fetch user data"}), response.status_code
@app.route('/api/v2/watch_history', methods=['GET'])
def __watchHistory2():
    ip = getIp()
    port = getPort()
    lang = request.args.get('lang')
    oauthToken = request.args.get('access_token')
    return innerTube.watchHistory2(ip, port, lang, oauthToken)
@app.route('/api/watch_history', methods=['GET'])
def _watchHistory():
    ip = getIp()
    port = getPort()
    lang = request.args.get('lang')
    oauthToken = request.args.get('access_token')
    return innerTube.watchHistory(ip, port, lang, oauthToken)    
@app.route('/api/river', methods=['GET'])
def _river():
    ip = getIp()
    port = getPort()
    lang = request.args.get('lang')
    oauthToken = request.args.get('access_token')
    return innerTube.river(ip, port, oauthToken, lang)    
@app.route('/api/categories/v3/<channelId>', methods=['GET'])
def _categoryThree(channelId):
    ip = getIp()
    port = getPort()
    oauthToken = request.args.get('access_token')
    lang = request.args.get('lang')
    return innerTube.categoryThree(ip, port, channelId, lang)    
@app.route('/api/watch_later', methods=['GET'])
def _watchLater():
    ip = getIp()
    port = getPort()
    lang = request.args.get('lang')
    oauthToken = request.args.get('access_token')
    return innerTube.watchLater(ip, port, lang, oauthToken)    
@app.route('/api/subscriptions', methods=['GET'])
def _subscriptions():
    lang = request.args.get('lang')
    oauthToken = request.args.get('access_token')
    return innerTube.subscriptions(oauthToken)    
@app.route('/api/playlists', methods=['GET'])
def _playlists():
    ip = getIp()
    port = getPort()
    lang = request.args.get('lang')
    oauthToken = request.args.get('access_token')
    return innerTube.playlists(ip, port, oauthToken, lang)
@app.route('/api/videos/<videoId>', methods=['GET'])
def videoInfo(videoId):
    ip = getIp()
    port = getPort()
    lang = request.args.get('lang')
    oauthToken = request.args.get('access_token')
    return innerTube.player(ip, port, videoId, lang)
@app.route('/api/liked_videos', methods=['GET'])
def _likedVideos():
    ip = getIp()
    port = getPort()
    lang = request.args.get('lang')
    oauthToken = request.args.get('access_token')
    return innerTube.likedVideos(ip, port, oauthToken, lang)
@app.route('/api/v2/guide', methods=['GET'])
def guide(oauthToken):
    innerTube = InnerTube()
    url = f'https://www.youtube.com/youtubei/v1/guide?key=AIzaS=yAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8&access_token={oauthToken}'
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
        }
    }    
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        data = response.json()
        return jsonify(data);
@app.route('/api/v2/next/<videoId>', methods=['GET'])
def next(videoId):
    innerTube = InnerTube()
    url = f'https://www.googleapis.com/youtubei/v1/next?key=AIzaS=yAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8&videoId={videoId}'
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'
    }
    payload = {
        "context": {
            "client": {
                "hl": "en",
                "gl": "US",
                "clientName": "TVHTML5",
                "clientVersion": "7.20211011"
            }
        }
    }    
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        data = response.json()
        return jsonify(data);  
@app.route('/api/v2/player/<videoId>', methods=['GET'])
def _player(videoId):
    innerTube = InnerTube()
    url = f'https://www.googleapis.com/youtubei/v1/player?key=AIzaS=yAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8&videoId={videoId}'
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
        "videoId": videoId,
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()
@app.route('/api/v2/watch_history/<oauthToken>', methods=['GET'])
def _watchHistory2(oauthToken):
    innerTube = InnerTube()
    url = f'https://www.youtube.com/youtubei/v1/browse?browseId=FEhistory&key=AIzaS=yAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8&access_token={oauthToken}'
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
        }
    }    
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        data = response.json()
        return jsonify(data);        
@app.route('/api/v2/search', methods=['GET'])
def _home():
    query = request.args.get('q')
    innerTube = InnerTube()
    url = f'https://www.youtube.com/youtubei/v1/search?query={query}&key=AIzaS=yAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8'
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
        }
    }    
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        data = response.json()
        return jsonify(data);        
@app.route('/api/v2/home', methods=['GET'])
def home():
    query = request.args.get('q')
    innerTube = InnerTube()
    url = f'https://www.youtube.com/youtubei/v1/browse?browseId=VLPLjSlr9-WHh-T5y-OIyVncK2sO2evRly5x&key=AIzaS=yAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8'
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
                "clientVersion": "2.20240814.00.00"
            }
        }
    }    
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        data = response.json()
        return jsonify(data);        
@app.route('/api/v2/playlists/<oauthToken>', methods=['GET'])
def library(oauthToken):
    innerTube = InnerTube()
    url = f'https://www.youtube.com/youtubei/v1/browse?browseId=FElibrary&key=AIzaS=yAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8&access_token={oauthToken}'
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
        }
    }    
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        data = response.json()
        return jsonify(data);
@app.route('/api/v2/liked_videos', methods=['GET'])
def _liked(oauthToken):
    innerTube = InnerTube()
    url = f'https://www.youtube.com/youtubei/v1/browse?browseId=VLLL&key=AIzaS=yAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8&access_token={oauthToken}'
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
        }
    }    
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        data = response.json()
        return jsonify(data);     
@app.route('/api/v2/watch_later/<oauthToken>', methods=['GET'])
def _wl(oauthToken):
    innerTube = InnerTube()
    url = f'https://www.youtube.com/youtubei/v1/browse?browseId=VLWL&key=AIzaS=yAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8&access_token={oauthToken}'
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
        }
    }    
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        data = response.json()
        return jsonify(data);
@app.route('/api/v2/whatToWatch/<oauthToken>', methods=['GET'])
def wtw(oauthToken):
    innerTube = InnerTube()
    url = f'https://www.youtube.com/youtubei/v1/browse?browseId=FEwhat_to_watch&key=AIzaS=yAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8&access_token={oauthToken}'
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
        }
    }    
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        data = response.json()
        return jsonify(data);
@app.route('/api/v2/channels/<oauthToken>', methods=['GET'])
def channels_(oauthToken):
    innerTube = InnerTube()
    url = f'https://www.youtube.com/youtubei/v1/browse?browseId=FEchannels&key=AIzaS=yAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8&access_token={oauthToken}'
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
        }
    }    
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        data = response.json()
        return jsonify(data);    
@app.route('/api/v2/subscriptions/<oauthToken>', methods=['GET'])
def subscriptions(oauthToken):
    innerTube = InnerTube()
    url = f'https://www.youtube.com/youtubei/v1/browse?browseId=FEsubscriptions&key=AIzaS=yAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8&access_token={oauthToken}'
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
        }
    }    
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        data = response.json()
        return jsonify(data);
@app.route('/api/channels/<channelId>/uploads', methods=['GET'])
def userUploads(channelId):
    ip = getIp()
    port = getPort()
    lang = request.args.get('lang', 'en')
    oauthToken = request.args.get('access_token')
    return invidious.user_uploads(ip, port, lang, channelId)
@app.route('/api/_playlists', methods=['GET'])
def playlistId():
    ip = getIp()
    port = getPort()
    lang = request.args.get('lang', 'en')
    playlistId = request.args.get('id')
    oauthToken = request.args.get('access_token')
    if not playlistId:
        return jsonify({"error": "Playlist ID is required"}), 400
    if oauthToken:
        return innerTube.playlist(ip, port, lang, playlistId, oauthToken)
    else:
        return innerTube.playlist(ip, port, lang, playlistId)
@app.route('/leanback_ajax', methods=['GET'])
def leanback_ajax():
    oauthToken = request.args.get('access_token')
    action_featured = request.args.get('action_featured')
    action_environment = request.args.get('action_environment')
    p = request.args.get('p')
    client = request.args.get('client')
    lang = request.args.get('lang')
    supportedLang = ['en', 'es', 'fr', 'de', 'ja', 'nl', 'it']
    ip = getIp()
    port = getPort()
    response = {
        'sets': [
            {
                'gdata_url': {
                    'en': f'http://{ip}:{port}/api/categories/trending?lang=en',
                    'es': f'http://{ip}:{port}/api/categories/trending?lang=es',
                    'fr': f'http://{ip}:{port}/api/categories/trending?lang=fr',
                    'de': f'http://{ip}:{port}/api/categories/trending?lang=de',
                    'ja': f'http://{ip}:{port}/api/categories/trending?lang=ja',
                    'nl': f'http://{ip}:{port}/api/categories/trending?lang=nl',
                    'it': f'http://{ip}:{port}/api/categories/trending?lang=it'
                }.get(lang, f'http://{ip}:{port}/api/categories/trending?lang=en'),
                'thumbnail': {
                    'en': f'http://{ip}:{port}/api/thumbnails/categories/trending?lang=en',
                    'es': f'http://{ip}:{port}/api/thumbnails/categories/trending?lang=es',
                    'fr': f'http://{ip}:{port}/api/thumbnails/categories/trending?lang=fr',
                    'de': f'http://{ip}:{port}/api/thumbnails/categories/trending?lang=de',
                    'ja': f'http://{ip}:{port}/api/thumbnails/categories/trending?lang=ja',
                    'nl': f'http://{ip}:{port}/api/thumbnails/categories/trending?lang=nl',
                    'it': f'http://{ip}:{port}/api/thumbnails/categories/trending?lang=it'
                }.get(lang, f'http://{ip}:{port}/api/thumbnails/categories/trending?lang=en'),
                'title': {
                    'en': f'Trending',
                    'es': f'Tendencias',
                    'fr': f'Tendance',
                    'de': f'Im Trend',
                    'ja': f'トレンド',
                    'nl': f'Populair',
                    'it': f'Tendenza'
                }.get(lang, f'Trending')
            },
            {
                'gdata_url': {
                    'en': f'http://{ip}:{port}/api/categories/v2/UC-9-kyTW8ZkZNDHQJ6FgpwQ?lang=en',
                    'es': f'http://{ip}:{port}/api/categories/v2/UC-9-kyTW8ZkZNDHQJ6FgpwQ?lang=es',
                    'fr': f'http://{ip}:{port}/api/categories/v2/UC-9-kyTW8ZkZNDHQJ6FgpwQ?lang=fr',
                    'de': f'http://{ip}:{port}/api/categories/v2/UC-9-kyTW8ZkZNDHQJ6FgpwQ?lang=de',
                    'ja': f'http://{ip}:{port}/api/categories/v2/UC-9-kyTW8ZkZNDHQJ6FgpwQ?lang=ja',
                    'nl': f'http://{ip}:{port}/api/categories/v2/UC-9-kyTW8ZkZNDHQJ6FgpwQ?lang=nl',
                    'it': f'http://{ip}:{port}/api/categories/v2/UC-9-kyTW8ZkZNDHQJ6FgpwQ?lang=it'
                }.get(lang, f'http://{ip}:{port}/api/categories/v2/UC-9-kyTW8ZkZNDHQJ6FgpwQ?lang=en'),
                'thumbnail': {
                    'en': f'http://{ip}:{port}/api/thumbnails/categories/v2/music?lang=en',
                    'es': f'http://{ip}:{port}/api/thumbnails/categories/v2/music?lang=es',
                    'fr': f'http://{ip}:{port}/api/thumbnails/categories/v2/music?lang=fr',
                    'de': f'http://{ip}:{port}/api/thumbnails/categories/v2/music?lang=de',
                    'ja': f'http://{ip}:{port}/api/thumbnails/categories/v2/music?lang=ja',
                    'nl': f'http://{ip}:{port}/api/thumbnails/categories/v2/music?lang=nl',
                    'it': f'http://{ip}:{port}/api/thumbnails/categories/v2/music?lang=it'
                }.get(lang, f'http://{ip}:{port}/api/thumbnails/categories/v2/music?lang=en'),
                'title': {
                    'en': f'Music',
                    'es': f'Música',
                    'fr': f'Musique',
                    'de': f'Musik',
                    'ja': f'音楽',
                    'nl': f'Muziek',
                    'it': f'Musica'
                }.get(lang, f'Music')
            },
            {
                'gdata_url': {
                    'en': f'http://{ip}:{port}/api/categories/v3/UCEgdi0XIXXZ-qJOFPf4JSKw?lang=en',
                    'es': f'http://{ip}:{port}/api/categories/v3/UCEgdi0XIXXZ-qJOFPf4JSKw?lang=es',
                    'fr': f'http://{ip}:{port}/api/categories/v3/UCEgdi0XIXXZ-qJOFPf4JSKw?lang=fr',
                    'de': f'http://{ip}:{port}/api/categories/v3/UCEgdi0XIXXZ-qJOFPf4JSKw?lang=de',
                    'ja': f'http://{ip}:{port}/api/categories/v3/UCEgdi0XIXXZ-qJOFPf4JSKw?lang=ja',
                    'nl': f'http://{ip}:{port}/api/categories/v3/UCEgdi0XIXXZ-qJOFPf4JSKw?lang=nl',
                    'it': f'http://{ip}:{port}/api/categories/v3/UCEgdi0XIXXZ-qJOFPf4JSKw?lang=it'
                }.get(lang, f'http://{ip}:{port}/api/categories/v3/UCEgdi0XIXXZ-qJOFPf4JSKw?lang=en'),
                'thumbnail': {
                    'en': f'http://{ip}:{port}/api/thumbnails/categories/v3/sports?lang=en',
                    'es': f'http://{ip}:{port}/api/thumbnails/categories/v3/sports?lang=es',
                    'fr': f'http://{ip}:{port}/api/thumbnails/categories/v3/sports?lang=fr',
                    'de': f'http://{ip}:{port}/api/thumbnails/categories/v3/sports?lang=de',
                    'ja': f'http://{ip}:{port}/api/thumbnails/categories/v3/sports?lang=ja',
                    'nl': f'http://{ip}:{port}/api/thumbnails/categories/v3/sports?lang=nl',
                    'it': f'http://{ip}:{port}/api/thumbnails/categories/v3/sports?lang=it'
                }.get(lang, f'http://{ip}:{port}/api/thumbnails/categories/v3/sports?lang=en'),
                'title': {
                    'en': f'Sports',
                    'es': f'Deportes',
                    'fr': f'Sport',
                    'de': f'Sport',
                    'ja': f'スポーツ',
                    'nl': f'Sport',
                    'it': f'Sport'
                }.get(lang, f'Sports')
            },
            {
                'gdata_url': {
                     'en': f'http://{ip}:{port}/api/categories/v3/UCrpQ4p1Ql_hG8rKXIKM1MOQ?lang=en',
                     'es': f'http://{ip}:{port}/api/categories/v3/UCrpQ4p1Ql_hG8rKXIKM1MOQ?lang=es',
                     'fr': f'http://{ip}:{port}/api/categories/v3/UCrpQ4p1Ql_hG8rKXIKM1MOQ?lang=fr',
                     'de': f'http://{ip}:{port}/api/categories/v3/UCrpQ4p1Ql_hG8rKXIKM1MOQ?lang=de',
                     'ja': f'http://{ip}:{port}/api/categories/v3/UCrpQ4p1Ql_hG8rKXIKM1MOQ?lang=ja',
                     'nl': f'http://{ip}:{port}/api/categories/v3/UCrpQ4p1Ql_hG8rKXIKM1MOQ?lang=nl',
                     'it': f'http://{ip}:{port}/api/categories/v3/UCrpQ4p1Ql_hG8rKXIKM1MOQ?lang=it'
                }.get(lang, f'http://{ip}:{port}/api/categories/v3/UCrpQ4p1Ql_hG8rKXIKM1MOQ?lang=en'),
                'thumbnail': {
                    'en': f'http://{ip}:{port}/api/thumbnails/categories/v3/fb?lang=en',
                    'es': f'http://{ip}:{port}/api/thumbnails/categories/v3/fb?lang=es',
                    'fr': f'http://{ip}:{port}/api/thumbnails/categories/v3/fb?lang=fr',
                    'de': f'http://{ip}:{port}/api/thumbnails/categories/v3/fb?lang=de',
                    'ja': f'http://{ip}:{port}/api/thumbnails/categories/v3/fb?lang=ja',
                    'nl': f'http://{ip}:{port}/api/thumbnails/categories/v3/fb?lang=nl',
                    'it': f'http://{ip}:{port}/api/thumbnails/categories/v3/fb?lang=it'
                }.get(lang, f'http://{ip}:{port}/api/thumbnails/categories/v3/fb?lang=en'),
                'title': {
                    'en': f'Fashion & Beauty',
                    'es': f'Moda y belleza',
                    'fr': f'Mode et beauté',
                    'de': f'Beauty & Fashion',
                    'ja': f'ファッションと美容',
                    'nl': f'Mode en beauty',
                    'it': f'Moda e bellezza'
                }.get(lang, f'Fashion & Beauty')
            },
            {
                'gdata_url': {
                     'en': f'http://{ip}:{port}/api/categories/v3/UCYfdidRxbB8Qhf0Nx7ioOYw?lang=en',
                     'es': f'http://{ip}:{port}/api/categories/v3/UCYfdidRxbB8Qhf0Nx7ioOYw?lang=es',
                     'fr': f'http://{ip}:{port}/api/categories/v3/UCYfdidRxbB8Qhf0Nx7ioOYw?lang=fr',
                     'de': f'http://{ip}:{port}/api/categories/v3/UCYfdidRxbB8Qhf0Nx7ioOYw?lang=de',
                     'ja': f'http://{ip}:{port}/api/categories/v3/UCYfdidRxbB8Qhf0Nx7ioOYw?lang=ja',
                     'nl': f'http://{ip}:{port}/api/categories/v3/UCYfdidRxbB8Qhf0Nx7ioOYw?lang=nl',
                     'it': f'http://{ip}:{port}/api/categories/v3/UCYfdidRxbB8Qhf0Nx7ioOYw?lang=it',
                }.get(lang, f'http://{ip}:{port}/api/categories/v3/UCYfdidRxbB8Qhf0Nx7ioOYw?lang=en'),
                'thumbnail': {
                    'en': f'http://{ip}:{port}/api/thumbnails/categories/v3/news?lang=en',
                    'es': f'http://{ip}:{port}/api/thumbnails/categories/v3/news?lang=es',
                    'fr': f'http://{ip}:{port}/api/thumbnails/categories/v3/news?lang=fr',
                    'de': f'http://{ip}:{port}/api/thumbnails/categories/v3/news?lang=de',
                    'ja': f'http://{ip}:{port}/api/thumbnails/categories/v3/news?lang=ja',
                    'nl': f'http://{ip}:{port}/api/thumbnails/categories/v3/news?lang=nl',
                    'it': f'http://{ip}:{port}/api/thumbnails/categories/v3/news?lang=it'
                }.get(lang, f'http://{ip}:{port}/api/thumbnails/categories/v3/news?lang=en'),
                'title': {
                    'en': f'News',
                    'es': f'Noticias',
                    'fr': f'Actualités',
                    'de': f'Nachrichten',
                    'ja': f'ニュース',
                    'nl': f'Nieuws',
                    'it': f'Notizie'
                }.get(lang, f'News')
            },
            {
                'gdata_url': {
                     'en': f'http://{ip}:{port}/api/_playlists?lang=en&id=PLrEnWoR732-BHrPp_Pm8_VleD68f9s14-',
                     'es': f'http://{ip}:{port}/api/_playlists?lang=es&id=PLrEnWoR732-BHrPp_Pm8_VleD68f9s14-',
                     'fr': f'http://{ip}:{port}/api/_playlists?lang=fr&id=PLrEnWoR732-BHrPp_Pm8_VleD68f9s14-',
                     'de': f'http://{ip}:{port}/api/_playlists?lang=de&id=PLrEnWoR732-BHrPp_Pm8_VleD68f9s14-',
                     'ja': f'http://{ip}:{port}/api/_playlists?lang=ja&id=PLrEnWoR732-BHrPp_Pm8_VleD68f9s14-',
                     'nl': f'http://{ip}:{port}/api/_playlists?lang=nl&id=PLrEnWoR732-BHrPp_Pm8_VleD68f9s14-',
                     'it': f'http://{ip}:{port}/api/_playlists?lang=it&id=PLrEnWoR732-BHrPp_Pm8_VleD68f9s14-',
                }.get(lang, f'http://{ip}:{port}/api/_playlists?lang=en&id=PLrEnWoR732-BHrPp_Pm8_VleD68f9s14-'),
                'thumbnail': {
                    'en': f'http://{ip}:{port}/api/thumbnails/playlists?lang=en&id=PLrEnWoR732-BHrPp_Pm8_VleD68f9s14-',
                    'es': f'http://{ip}:{port}/api/thumbnails/playlists?lang=es&id=PLrEnWoR732-BHrPp_Pm8_VleD68f9s14-',
                    'fr': f'http://{ip}:{port}/api/thumbnails/playlists?lang=fr&id=PLrEnWoR732-BHrPp_Pm8_VleD68f9s14-',
                    'de': f'http://{ip}:{port}/api/thumbnails/playlists?lang=de&id=PLrEnWoR732-BHrPp_Pm8_VleD68f9s14-',
                    'ja': f'http://{ip}:{port}/api/thumbnails/playlists?lang=ja&id=PLrEnWoR732-BHrPp_Pm8_VleD68f9s14-',
                    'nl': f'http://{ip}:{port}/api/thumbnails/playlists?lang=nl&id=PLrEnWoR732-BHrPp_Pm8_VleD68f9s14-',
                    'it': f'http://{ip}:{port}/api/thumbnails/playlists?lang=it&id=PLrEnWoR732-BHrPp_Pm8_VleD68f9s14-'
                }.get(lang, f'http://{ip}:{port}/api/thumbnails/playlists?lang=en&id=PLrEnWoR732-BHrPp_Pm8_VleD68f9s14-'),
                'title': {
                    'en': f'Popular on YouTube',
                    'es': f'Populares en YouTube',
                    'fr': f'Populaire sur YouTube',
                    'de': f'Beliebt auf YouTube',
                    'ja': f'YouTubeで人気',
                    'nl': f'Populair op YouTube',
                    'it': f'Popolare su YouTube'
                }.get(lang, f'Popular on YouTube')
            }
        ]
    }    
    if oauthToken:
        userPlaylistsUrl = f'https://www.youtube.com/youtubei/v1/browse?browseId=FElibrary&key=AIzaS=yAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8&access_token={oauthToken}'
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        payload = {
            "context": {
                "client": {
                    "hl": lang,
                    "gl": "US",
                    "clientName": "WEB",
                    "clientVersion": "2.20210714.01.00"
                }
            }
        }        
        responseData = requests.post(userPlaylistsUrl, json=payload, headers=headers)
        if responseData.status_code == 200:
            data = responseData.json()
            contents = data.get('contents', {}).get('twoColumnBrowseResultsRenderer', {}).get('tabs', [])
            for tab in contents:
                tabRenderer = tab.get('tabRenderer', {})
                sectionList = tabRenderer.get('content', {}).get('sectionListRenderer', {}).get('contents', [])                
                for section in sectionList:
                    itemSection = section.get('itemSectionRenderer', {}).get('contents', [])                    
                    for item in itemSection:
                        shelfRenderer = item.get('shelfRenderer', {})
                        horizontalList = shelfRenderer.get('content', {}).get('horizontalListRenderer', {}).get('items', [])                        
                        for video in horizontalList:
                            lockupViewModel = video.get('lockupViewModel', {})
                            title = lockupViewModel.get('metadata', {}).get('lockupMetadataViewModel', {}).get('title', {}).get('content', '')
                            browseId = lockupViewModel.get('contentId', '')
                            thumbnailUrl = ''                            
                            try:
                                thumbnailUrl = lockupViewModel.get('contentImage', {}).get('collectionThumbnailViewModel', {}).get('primaryThumbnail', {}).get('thumbnailViewModel', {}).get('image', {}).get('sources', [{}])[0].get('url', '')
                                if 'mqdefault' in thumbnailUrl:
                                    thumbnailUrl = thumbnailUrl.replace('mqdefault', 'mqdefault')
                                thumbnailUrl = replaceToHTTP(thumbnailUrl)
                            except (IndexError, KeyError):
                                thumbnailUrl = ''                            
                            if title and browseId:
                                response['sets'].insert(0, {
                                    'gdata_url': f'http://{ip}:{port}/api/_playlists?id={browseId}&access_token={oauthToken}&lang={lang}',
                                    'thumbnail': thumbnailUrl,
                                    'title': title
                                })
        else:
            return Response('Failed to fetch playlists', status=500)
        subscriptionsUrl = f'https://www.youtube.com/youtubei/v1/browse?browseId=FEchannels&key=AIzaS=yAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8&access_token={oauthToken}'
        subscriptionsData = requests.post(subscriptionsUrl, json=payload, headers=headers)
        if subscriptionsData.status_code == 200:
            data = subscriptionsData.json()
            for item in data.get('contents', {}).get('twoColumnBrowseResultsRenderer', {}).get('tabs', []):
                tabs = item.get('tabRenderer', {}).get('content', {}).get('sectionListRenderer', {}).get('contents', [])
                for section in tabs:
                    if 'itemSectionRenderer' in section:
                        channelData = section.get('itemSectionRenderer', {}).get('contents', [])
                        for channel in channelData:
                            if 'shelfRenderer' in channel:
                                channelInfo = channel.get('shelfRenderer', {}).get('content', {}).get('expandedShelfContentsRenderer', {}).get('items', [])
                                for channelItem in channelInfo:
                                    channelRenderer = channelItem.get('channelRenderer', {})
                                    if channelRenderer:
                                        authorName = channelRenderer.get('title', {}).get('simpleText', '')
                                        browseId = channelRenderer.get('channelId', '')
                                        if authorName and browseId:
                                            response['sets'].insert(0, {
                                                'gdata_url': f'http://{ip}:{port}/api/channels/{browseId}/uploads',
                                                'thumbnail': f'http://{ip}:{port}/api/thumbnails/channels/{browseId}/uploads',
                                                'title': f'{authorName}'
                                            })
                return jsonify(response)
        else:
            return Response('Failed to fetch subscriptions', status=500)
    return jsonify(response), 200
def fetchAndServeMusicThumbnail(ip, port, lang):
    if not ip or not port:
        return "Invalid IP or Port configuration", 500
    url = f"http://{ip}:{port}/api/categories/v2/UC-9-kyTW8ZkZNDHQJ6FgpwQ?lang={lang}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.text
        thumbnailMatch = re.search(r"<media:thumbnail yt:name=['\"]mqdefault['\"] url=['\"](.*?)['\"]", data)
        thumbnailUrl = thumbnailMatch.group(1) if thumbnailMatch else None
        if thumbnailUrl:
            return redirect(thumbnailUrl, code=302)
        else:
            default = 'http://i.ytimg.com/vi/e/0.jpg'
            return redirect(default, code=302)
    except Exception as e:
        print("Error processing feed data:", e)
        return "Error processing feed data", 500
def fetchAndServePlaylistThumbnail(ip, port, lang, playlistId):
    if not ip or not port:
        return "Invalid IP or Port configuration", 500
    url = f"http://{ip}:{port}/api/_playlists?lang={lang}&id={playlistId}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.text
        thumbnailMatch = re.search(r"<media:thumbnail yt:name=['\"]mqdefault['\"] url=['\"](.*?)['\"]", data)
        thumbnailUrl = thumbnailMatch.group(1) if thumbnailMatch else None
        if thumbnailUrl:
            return redirect(thumbnailUrl, code=302)
        else:
            default = 'http://i.ytimg.com/vi/e/0.jpg'
            return redirect(default, code=302)
    except Exception as e:
        print("Error processing feed data:", e)
        return "Error processing feed data", 500
def fetchAndServeSportThumbnail(ip, port, lang):
    if not ip or not port:
        return "Invalid IP or Port configuration", 500
    url = f"http://{ip}:{port}/api/categories/v3/UCEgdi0XIXXZ-qJOFPf4JSKw?lang={lang}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.text
        thumbnailMatch = re.search(r"<media:thumbnail yt:name=['\"]mqdefault['\"] url=['\"](.*?)['\"]", data)
        thumbnailUrl = thumbnailMatch.group(1) if thumbnailMatch else None
        if thumbnailUrl:
            return redirect(thumbnailUrl, code=302)
        else:
            default = 'http://i.ytimg.com/vi/e/0.jpg'
            return redirect(default, code=302)
    except Exception as e:
        print("Error processing feed data:", e)
        return "Error processing feed data", 500        
def fetchAndServeGamingThumbnailThumbnail(ip, port, lang):
    if not ip or not port:
        return "Invalid IP or Port configuration", 500
    url = f"http://{ip}:{port}/api/categories/v2/UCOpNcN46UbXVtpKMrmU4Abg?lang={lang}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.text
        thumbnailMatch = re.search(r"<media:thumbnail yt:name=['\"]mqdefault['\"] url=['\"](.*?)['\"]", data)
        thumbnailUrl = thumbnailMatch.group(1) if thumbnailMatch else None
        if thumbnailUrl:
            return redirect(thumbnailUrl, code=302)
        else:
            default = 'http://i.ytimg.com/vi/e/0.jpg'
            return redirect(default, code=302)
    except Exception as e:
        print("Error processing feed data:", e)
        return "Error processing feed data", 500        
def fetchAndServeFashionBeautyThumbnail(ip, port, lang):
    if not ip or not port:
        return "Invalid IP or Port configuration", 500
    url = f"http://{ip}:{port}/api/categories/v3/UCrpQ4p1Ql_hG8rKXIKM1MOQ?lang={lang}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.text
        thumbnailMatch = re.search(r"<media:thumbnail yt:name=['\"]mqdefault['\"] url=['\"](.*?)['\"]", data)
        thumbnailUrl = thumbnailMatch.group(1) if thumbnailMatch else None
        if thumbnailUrl:
            return redirect(thumbnailUrl, code=302)
        else:
            default = 'http://i.ytimg.com/vi/e/0.jpg'
            return redirect(default, code=302)
    except Exception as e:
        print("Error processing feed data:", e)
        return "Error processing feed data", 500        
def fetchAndServeNewsThumbnail(ip, port, lang):
    if not ip or not port:
        return "Invalid IP or Port configuration", 500
    url = f"http://{ip}:{port}/api/categories/v3/UCYfdidRxbB8Qhf0Nx7ioOYw?lang={lang}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.text
        thumbnailMatch = re.search(r"<media:thumbnail yt:name=['\"]mqdefault['\"] url=['\"](.*?)['\"]", data)
        thumbnailUrl = thumbnailMatch.group(1) if thumbnailMatch else None
        if thumbnailUrl:
            return redirect(thumbnailUrl, code=302)
        else:
            default = 'http://i.ytimg.com/vi/e/0.jpg'
            return redirect(default, code=302)
    except Exception as e:
        print("Error processing feed data:", e)
        return "Error processing feed data", 500    
def fetchAndServeTrendsThumbnail(ip, port, lang):
    if not ip or not port:
        return "Invalid IP or Port configuration", 500
    url = f"http://{ip}:{port}/api/categories/trending?lang={lang}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.text
        thumbnailMatch = re.search(r"<media:thumbnail yt:name=['\"]mqdefault['\"] url=['\"](.*?)['\"]", data)
        thumbnailUrl = thumbnailMatch.group(1) if thumbnailMatch else None
        if thumbnailUrl:
            return redirect(thumbnailUrl, code=302)
        else:
            default = 'http://i.ytimg.com/vi/e/0.jpg'
            return redirect(default, code=302)
    except Exception as e:
        print("Error processing feed data:", e)
        return "Error processing feed data", 500        
def fetchAndServeLikesThumbnail(ip, port, lang, oauthToken):
    _url = f'http://{ip}:{port}/api/liked_videos?lang={lang}&access_token={oauthToken}'
    try:
        response = requests.get(_url)
        response.raise_for_status()
        data = response.text
        print("Response Data:", data[:500])
        thumbnailMatch = re.search(r"<media:thumbnail yt:name=['\"]mqdefault['\"] url=['\"](.*?)['\"]", data)
        if thumbnailMatch:
            thumbnailUrl = thumbnailMatch.group(1)
            print("Found Thumbnail URL:", thumbnailUrl)
        else:
            print("No thumbnail found, using default image.")
            thumbnailUrl = None
        if thumbnailUrl:
            return redirect(thumbnailUrl, code=302)
        else:
            default = 'http://i.ytimg.com/vi/e/0.jpg'
            return redirect(default, code=302)    
    except requests.exceptions.RequestException as e:
        print("Error processing feed data:", e)
        return "Error processing feed data", 500
@app.route('/api/thumbnails/categories/trending', methods=['GET'])
def trendingThumbnail():
    ip = getIp()
    port = getPort()
    lang = request.args.get('lang', 'en')  
    return fetchAndServeTrendsThumbnail(ip, port, lang)    
def fetchAndServePopularThumbnail(ip, port, type=None):
    url = "http://{ip}:{port}/api/popular"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.text
        thumbnailMatch = re.search(r"<media:thumbnail yt:name='mqdefault' url='(.*?)'", data)
        thumbnailUrl = thumbnailMatch.group(1) if thumbnailMatch else None
        if thumbnailUrl:
            return redirect(thumbnailUrl, code=302)
        else:
            default = 'http://i.ytimg.com/vi/e/0.jpg'
            return redirect(default, code=302)
    except Exception as e:
        print("Error processing feed data:", e)
        return "Error processing feed data", 500
def fetchAndServeChannelUploadsThumbnail2(ip, port, browseId):
    url = f"http://{ip}:{port}/api/channels/{browseId}/uploads"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.text
        thumbnailMatch = re.search(r"<media:thumbnail yt:name='mqdefault' url='(.*?)'", data)
        thumbnailUrl = thumbnailMatch.group(1) if thumbnailMatch else None
        if thumbnailUrl:
            return redirect(thumbnailUrl, code=302)
        else:
            default = 'http://i.ytimg.com/vi/e/0.jpg'
            return redirect(default, code=302)
    except Exception as e:
        print("Error processing feed data:", e)
        return "Error processing feed data", 500    
def fetchAndServeChannelUploadsThumbnail(ip, port, channelId):
    url = f"http://{ip}:{port}/api/channels/{channelId}/uploads"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.text
        thumbnailMatch = re.search(r"<media:thumbnail yt:name='mqdefault' url='(.*?)'", data)
        thumbnailUrl = thumbnailMatch.group(1) if thumbnailMatch else None
        if thumbnailUrl:
            return redirect(thumbnailUrl, code=302)
        else:
            default = 'http://i.ytimg.com/vi/e/0.jpg'
            return redirect(default, code=302)
    except Exception as e:
        print("Error processing feed data:", e)
        return "Error processing feed data", 500        
def getAuthorName(ip, port, channelId):
    try:
        url = f"http://{ip}:{port}/api/channels/{channelId}/uploads"
        response = requests.get(url)
        response.raise_for_status()
        data = response.text
        authorMatch = re.search(r"<author><name>(.*?)</name>", data)
        authorName = authorMatch.group(1) if authorMatch else None       
        return authorName
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None
@app.route('/api/thumbnails/channels/<browseId>/uploads', methods=['GET'])
def _uploadsThumbnail(browseId):
    ip = getIp()
    port = getPort()
    return fetchAndServeChannelUploadsThumbnail2(ip, port, browseId)        
@app.route('/api/thumbnails/channels/<channelId>/uploads', methods=['GET'])
def uploadsThumbnail(channelId):
    ip = getIp()
    port = getPort()
    return fetchAndServeChannelUploadsThumbnail(ip, port, channelId)    
@app.route('/api/thumbnails/playlists', methods=['GET'])
def playlistThumbnail():
    ip = getIp()
    port = getPort()
    lang = request.args.get('lang', 'en')  
    playlistId = request.args.get('id')
    return fetchAndServePlaylistThumbnail(ip, port, lang, playlistId)    
@app.route('/api/thumbnails/popular', methods=['GET'])
def popularThumbnail():
    ip = getIp()
    port = getPort()
    type = request.args.get('type')
    return fetchAndServePopularThumbnail(ip, port, type)    
@app.route('/api/thumbnails/liked_videos', methods=['GET'])
def likedVideosThumbnail():
    ip = getIp()
    port = getPort()
    lang = request.args.get('lang', 'en')  
    oauthToken = request.args.get('access_token')
    if oauthToken:
        return fetchAndServeLikesThumbnail(ip, port, lang, oauthToken)
    else:
        return "Access token missing", 400        
@app.route('/api/thumbnails/categories/v2/music', methods=['GET'])
def musicThumbnail():
    ip = getIp()
    port = getPort()
    lang = request.args.get('lang', 'en')  
    return fetchAndServeMusicThumbnail(ip, port, lang)    
@app.route('/api/thumbnails/categories/v2/gaming', methods=['GET'])
def gamingThumbnail():
    ip = getIp()
    port = getPort()
    lang = request.args.get('lang', 'en')  
    return fetchAndServeGamingThumbnail(ip, port, lang)    
@app.route('/api/thumbnails/categories/v3/sports', methods=['GET'])
def sportsThumbnail():
    ip = getIp()
    port = getPort()
    lang = request.args.get('lang', 'en')  
    return fetchAndServeSportThumbnail(ip, port, lang)    
@app.route('/api/thumbnails/categories/v3/fb', methods=['GET'])
def fashionAndBeautyThumbnail():
    ip = getIp()
    port = getPort()
    lang = request.args.get('lang', 'en')  
    return fetchAndServeFashionBeautyThumbnail(ip, port, lang)    
@app.route('/api/thumbnails/categories/v3/news', methods=['GET'])
def newsThumbnail():
    ip = getIp()
    port = getPort()
    lang = request.args.get('lang', 'en')  
    return fetchAndServeNewsThumbnail(ip, port, lang)
@app.route('/api/videos/get/<videoId>', methods=['GET'])
def getVideo(videoId):
    try:
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]',
            'outtmpl': f'assets/{videoId}.%(ext)s',
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([f'https://www.youtube.com/watch?v={videoId}'])

        _input = f"assets/{videoId}.mp4"
        if not os.path.exists(_input):
            abort(404, description="Downloaded video not found.")
        output = f"assets/{videoId}.webm"
        if os.path.exists(output):
            return send_from_directory(os.getcwd(), output, as_attachment=True)
        command = [
            'ffmpeg', '-v', 'verbose', '-i', _input, 
            '-c:v', 'libvpx', '-b:v', '500k', '-cpu-used', '8', 
            '-vf', 'scale=-1:360', '-pix_fmt', 'yuv420p',
            '-c:a', 'libvorbis', '-b:a', '128k', '-r', '30', '-g', '30', 
            output
        ]
        subprocess.run(command)
        return send_from_directory(os.getcwd(), output, as_attachment=True)
    except Exception as e:
        print(f"Error: {e}")
        abort(500, description="An error occurred while processing the video.")
@app.route('/api/videos/info/<videoId>', methods=['GET'])
def getVideoInfo(videoId):
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
    response = (
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
    return Response(response, content_type='text/plain')
@app.route('/apiplayer', methods=['GET'])
def apiplayer():
    version = request.args.get('version')
    _id = request.args.get('id')
    ps = request.args.get('ps')
    el = request.args.get('el')
    ccAutoCaps = request.args.get('cc_auto_caps')
    cos = request.args.get('cos')
    cplatform = request.args.get('cplatform')
    if version == '2' and _id == 'vflZLm5Vu' and ps == 'lbl' and el == 'leanback' and ccAutoCaps == '1' and cos == 'vodf' and cplatform == 'game_console':
        request_dump(request)
        return send_file(r"swf\apiplayer-vflZLm5Vu.swf", mimetype="application/x-shockwave-flash")
    return send_file(r"swf\apiplayer.swf", mimetype="application/x-shockwave-flash")    
@app.route('/wiitv', methods=['GET'])
def lblWii():
    request_dump(request)
    oauthToken = request.args.get('access_token')
    return send_file(r"swf\leanbacklite_wii.swf", mimetype="application/x-shockwave-flash")    
@app.route('/api/users/<channelId>/icon', methods=['GET'])
def getUserIcon(channelId):
    url = f'https://inv.nadeko.net/api/v1/channels/{channelId}'
    response = requests.get(url)
    if response.status_code != 200:
        return "Error fetching channel data", 500
    channelData = response.json()
    authorThumbnails = channelData.get('authorThumbnails', [])
    thumbnailUrl = None
    for thumbnail in authorThumbnails:
        if thumbnail['width'] == 48 and thumbnail['height'] == 48:
            thumbnailUrl = thumbnail['url']
            break
    if thumbnailUrl:
        thumbnailUrl = thumbnailUrl.replace('https://', 'http://', 1)
        return redirect(thumbnailUrl)
    else:
        return "Thumbnail not found", 404        
@app.route('/o/oauth2/device/code', methods=['POST'])
def deviceCode():
    response = requests.post(
        OAUTH2_DEVICE_CODE_URL,
        data={
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'scope': 'https://www.googleapis.com/auth/youtube',
        }
    )
    if response.status_code != 200:
        return jsonify({"error": "Failed to get device code"}), 400
    data = response.json()
    device_code = data['device_code']
    user_code = data['user_code']
    verification_url = data['verification_url']
    expires_in = data['expires_in']
    message = f"Please visit {verification_url} and enter the user code: {user_code}"
    return jsonify({
        'device_code': device_code,
        'user_code': user_code,
        'verification_url': verification_url,
        'expires_in': expires_in,
        'message': message
    })
    print(message)
@app.route('/o/oauth2/device/code/status', methods=['POST'])
def checkStatus():
    device_code = request.json.get('device_code')
    if not device_code:
        return jsonify({"error": "Device code is required"}), 400
    response = requests.post(
        OAUTH2_TOKEN_URL,
        data={
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'device_code': device_code,
            'grant_type': 'urn:ietf:params:oauth:grant-type:device_code',
        }
    )
    if response.status_code == 200:
        data = response.json()
        return jsonify({
            'access_token': data['access_token'],
            'refresh_token': data.get('refresh_token'),
            'expires_in': data['expires_in']
        })
    elif response.status_code == 400:
        data = response.json()
        if data.get('error') == 'authorization_pending':
            return jsonify({"status": "pending", "message": "User hasn't authorized yet."}), 200
        elif data.get('error') == 'slow_down':
            return jsonify({"status": "slow_down", "message": "Too many requests, try again later."}), 429
        return jsonify({"error": "Authorization failed."}), 400
    return jsonify({"error": "Unknown error occurred."}), 500
@app.route('/o/oauth2/token', methods=['POST'])
def oauth2_token():
    youtube_oauth_url = 'https://www.youtube.com/o/oauth2/token'
    response = requests.post(youtube_oauth_url, data=request.form)
    if response.status_code == 200:
        return jsonify(response.json())
@app.route('/auth/youtube', methods=['POST'])
def youtubeAuth():
    code = request.json.get('code')
    if not code:
        return jsonify({"error": "Authorization code is required"}), 400
    response = requests.post(
        'https://www.googleapis.com/oauth2/v4/token',
        data={
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'code': code,
            'grant_type': 'http://oauth.net/grant_type/device/1.0',
            'redirect_uri': REDIRECT_URI,
        }
    )
    if response.status_code == 200:
        data = response.json()
        return jsonify({
            'access_token': data['access_token'],
            'refresh_token': data.get('refresh_token'),
            'expires_in': data['expires_in']
        })
    return jsonify({"error": "Failed to obtain token"}), 400    
@app.route('/api/users/default', methods=['GET'])
def defaultUser():
    access_token = request.args.get('access_token')
    if not access_token:
        return jsonify({"error": "access_token is required"}), 400    
    userInfoUrl = f"https://www.googleapis.com/youtube/v3/channels?part=snippet&mine=true&access_token={access_token}"    
    response = requests.get(userInfoUrl)
    if response.status_code == 200:
        data = response.json()
        if "items" in data and len(data["items"]) > 0:
            channelData = data["items"][0].get("snippet", {})
            channelId = data["items"][0].get("id", "")
            thumbnails = channelData.get("thumbnails", {})
            defaultThumbnail = thumbnails.get("default", {}).get("url", "")
            if defaultThumbnail and channelId:
                customThumbnailUrl = f"http://{ip}:{port}/api/users/{channelId}/icon"
                channelData["thumbnails"]["default"]["url"] = customThumbnailUrl        
        return jsonify(data)    
    return jsonify({"error": f"Failed to fetch user data: {response.text}"}), response.status_code
if __name__ == '__main__':
    if not os.path.exists('configuration.xml'):
        port = input("What port should Liinback run on?\nCAUTION: The maximum number port the Wii runs is port 443: ")
        while int(port) > 443:
            port = input("I'm sorry but this port is not compatible on the Wii. Please enter a different port number. Again, the maximum number port is 443: ")
        env = input("Are you using [dev] or [prod]? ")
        while env not in ['dev', 'prod']:
            env = input("Please enter either 'dev' or 'prod': ")
        if env == 'prod':
            input("Please paste in your SSL tokens in this directory of your Liinback, then press enter when you have done that.")
            if os.path.exists('cert.pem') and os.path.exists('key.pem'):
                print(f"I found your {os.path.abspath('cert.pem')} and {os.path.abspath('key.pem')} certificates. Press enter to see the next step/guide.")
                input()
            else:
                print("SSL tokens are missing, continuing without SSL.")        
        ip = input("Please enter your IP address: ")
        print("Building your configuration file")
        buildConfiguration(ip, port, env)
        installRequirements()
    tree = ET.parse('configuration.xml')
    root = tree.getroot()
    ip = root.find('ip').text
    port = root.find('port').text
    env = root.find('env').text
    app.run(debug=True, host=ip, port=int(port))
