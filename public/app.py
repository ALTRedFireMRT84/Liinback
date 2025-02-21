from flask import Flask, request, jsonify, send_file, Response, redirect, abort
import colorama
import requests
import os
import json
import subprocess
import threading
import xml.etree.ElementTree as ET
import re
from datetime import datetime, timedelta
from time import sleep
from debug import request_dump
from api import Invidious, InnerTube, DataAPI
from wiiVideoLoader import GetVideo, GetVideoInfo
from io import BytesIO
app = Flask(__name__)
colorama.init()
accessId = "0bfngonDSa5eSDTA56gZtVNUWtqT9aFGmE4nn302WW7T2ZkzqUkY6IdHZlgvmu7dYAbXh9iVReBveBl78XoVlDSlVC20vKysr2bW"
CACHE_DIR = "./cache_dir/subtitles"
DEFAULTS = [
    "<title>Error 404 (Not Found)!!1</title>",
    """<?xml version="1.0" encoding="utf-8" ?>
    <transcript>
    <text start="0" dur="0.1"> </text>
    </transcript>"""
]
API_KEY = 'AIzaS=yAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8'
DATA_API_KEY = 'AIzaSyDuziy6qTSaKhs0w4SKpLNWivKFNoWjQQA'
processingVideos = []
OAUTH2_DEVICE_CODE_URL = 'https://oauth2.googleapis.com/device/code'
OAUTH2_TOKEN_URL = 'https://oauth2.googleapis.com/token'
CLIENT_ID = '627431331381.apps.googleusercontent.com'
CLIENT_SECRET = 'O_HOjELPNFcHO_n_866hamcO'
REDIRECT_URI = ''
invidious = Invidious()
innerTube = InnerTube()
getVideo = GetVideo()
getVideoInfo = GetVideoInfo()
dataApi = DataAPI()
def installRequirements():
    packages = ['Flask', 'colorama', 'requests', 'yt-dlp']
    for package in packages:
        try:
            subprocess.check_call([os.sys.executable, "-m", "pip", "show", package])
        except subprocess.CalledProcessError:
            print(f"Installing {package}...")
            subprocess.check_call([os.sys.executable, "-m", "pip", "install", package])

    tree.write("configuration.xml")           
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
@app.route('/device_204', methods=['GET'])
def device_204():
    return ''
@app.route('/api/search', methods=['GET'])
def search():
    key = request.args.get('key')
    if key != accessId:
        abort(403)
    oauthToken = request.args.get('access_token')
    lang = request.args.get('lang')
    ip = getIp()
    port = getPort()
    query = request.args.get('q')
    type = request.args.get('type')
    return innerTube.search(query, lang)
@app.route('/api/v3/search', methods=['GET'])
def searchV3():
    ip = getIp()
    port = getPort()
    query = request.args.get('q')
    type = request.args.get('type')
    return innerTube.searchV3(query)
@app.route('/api/v2/trending', methods=['GET'])
def trending():
    key = request.args.get('key')
    if key != accessId:
        abort(403)
    ip = getIp()
    port = getPort()
    type_param = request.args.get('type')
    return invidious.trends(type_param)
@app.route('/api/categories/<type>', methods=['GET'])
def _category(type):
    key = request.args.get('key')
    if key != accessId:
        abort(403)
    ip = getIp()
    port = getPort()
    params = request.args.get('params')
    oauthToken = request.args.get('access_token')
    lang = request.args.get('lang')
    return innerTube.category(type, params, lang)
@app.route('/api/v2/categories/<type>', methods=['GET'])
def _categoryV2(type):
    key = request.args.get('key')
    if key != accessId:
        abort(403)
    ip = getIp()
    port = getPort()
    params = request.args.get('params')
    return innerTube.categoryV2(type, params)
@app.route('/api/categories/v2/<channelId>', methods=['GET'])
def _categoryTwo(channelId):
    key = request.args.get('key')
    if key != accessId:
        abort(403)
    ip = getIp()
    port = getPort()
    oauthToken = request.args.get('access_token')
    lang = request.args.get('lang')
    return innerTube.categoryTwo(channelId, lang)
@app.route('/api/v2/categories/v2/<channelId>', methods=['GET'])
def _categoryTwoV2(channelId):
    key = request.args.get('key')
    if key != accessId:
        abort(403)
    ip = getIp()
    port = getPort()
    return innerTube.categoryTwoV2(channelId)
@app.route('/api/popular', methods=['GET'])
def popular():
    key = request.args.get('key')
    if key != accessId:
        abort(403)
    ip = getIp()
    port = getPort()
    format = request.args.get('format')
    platform = request.args.get('platform')
    return invidious.popular(ip, port)
@app.route('/api/channels/default/uploads', methods=['GET'])
def userUploadsOauthToken():
    oauthToken = request.args.get('access_token')
    userInfoUrl = f"https://www.googleapis.com/youtube/v3/channels?part=snippet&mine=true&key={API_KEY}&access_token={oauthToken}"
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
    key = request.args.get('key')
    if key != accessId:
        abort(403)
    ip = getIp()
    port = getPort()
    lang = request.args.get('lang')
    oauthToken = request.args.get('access_token')
    return innerTube.watchHistory2(lang, oauthToken)
@app.route('/api/watch_history', methods=['GET'])
def _watchHistory():
    key = request.args.get('key')
    if key != accessId:
        abort(403)
    ip = getIp()
    port = getPort()
    lang = request.args.get('lang')
    oauthToken = request.args.get('access_token')
    return innerTube.watchHistory(lang, oauthToken)
@app.route('/api/river', methods=['GET'])
def _river():
    key = request.args.get('key')
    if key != accessId:
        abort(403)
    ip = getIp()
    port = getPort()
    lang = request.args.get('lang')
    oauthToken = request.args.get('access_token')
    return innerTube.river(oauthToken, lang)
@app.route('/api/categories/v3/<channelId>', methods=['GET'])
def _categoryThree(channelId):
    key = request.args.get('key')
    if key != accessId:
        abort(403)
    ip = getIp()
    port = getPort()
    oauthToken = request.args.get('access_token')
    lang = request.args.get('lang')
    return innerTube.categoryThree(channelId, lang)
@app.route('/api/explore', methods=['GET'])
def _explore():
    key = request.args.get('key')
    if key != accessId:
        abort(403)
    oauthToken = request.args.get('access_token')
    lang = request.args.get('lang')
    return innerTube.explore(lang, oauthToken)
@app.route('/api/v2/categories/v3/<channelId>', methods=['GET'])
def _categoryThreeV2(channelId):
    key = request.args.get('key')
    if key != accessId:
        abort(403)
    ip = getIp()
    port = getPort()
    return innerTube.categoryThreeV2(channelId)
@app.route('/api/favorites', methods=['GET'])
def _favorites():
    key = request.args.get('key')
    if key != accessId:
        abort(403)
    ip = getIp()
    port = getPort()
    lang = request.args.get('lang')
    oauthToken = request.args.get('access_token')
    return innerTube.favorites(oauthToken, lang)
@app.route('/api/watch_later', methods=['GET'])
def _watchLater():
    key = request.args.get('key')
    if key != accessId:
        abort(403)
    ip = getIp()
    port = getPort()
    lang = request.args.get('lang')
    oauthToken = request.args.get('access_token')
    return innerTube.watchLater(lang, oauthToken)
@app.route('/api/subscriptions', methods=['GET'])
def _subscriptions():
    key = request.args.get('key')
    if key != accessId:
        abort(403)
    lang = request.args.get('lang')
    oauthToken = request.args.get('access_token')
    return innerTube.subscriptions(oauthToken)
@app.route('/api/playlists', methods=['GET'])
def _playlists():
    key = request.args.get('key')
    if key != accessId:
        abort(403)
    ip = getIp()
    port = getPort()
    lang = request.args.get('lang')
    oauthToken = request.args.get('access_token')
    return innerTube.playlists(oauthToken, lang)
@app.route('/api/videos/<videoId>', methods=['GET'])
def videoInfo(videoId):
    key = request.args.get('key')
    if key != accessId:
        abort(403)
    ip = getIp()
    port = getPort()
    lang = request.args.get('lang')
    oauthToken = request.args.get('access_token')
    return innerTube.player(videoId, lang, oauthToken)
@app.route('/api/liked_videos', methods=['GET'])
def _likedVideos():
    key = request.args.get('key')
    if key != accessId:
        abort(403)
    ip = getIp()
    port = getPort()
    lang = request.args.get('lang')
    oauthToken = request.args.get('access_token')
    return innerTube.likedVideos(oauthToken, lang)
@app.route('/api/channels/<channelId>/uploads', methods=['GET'])
def userUploads(channelId):
    key = request.args.get('key')
    if key != accessId:
        abort(403)
    ip = getIp()
    port = getPort()
    lang = request.args.get('lang', 'en')
    oauthToken = request.args.get('access_token')
    return dataApi.userUploads(lang, channelId)
@app.route('/api/v2/channels/<channelId>/uploads', methods=['GET'])
def userUploadsV2(channelId):
    key = request.args.get('key')
    if key != accessId:
        abort(403)
    ip = getIp()
    port = getPort()
    return invidious.user_uploads_V2(channelId)
@app.route('/api/_playlists', methods=['GET'])
def playlistId():
    key = request.args.get('key')
    if key != accessId:
        abort(403)
    ip = getIp()
    port = getPort()
    lang = request.args.get('lang', 'en')
    playlistId = request.args.get('id')
    oauthToken = request.args.get('access_token')
    if not playlistId:
        return jsonify({"error": "Playlist ID is required"}), 400
    if oauthToken:
        return innerTube.playlist(lang, playlistId, oauthToken)
    else:
        return innerTube.playlist(lang, playlistId)
@app.route('/api/v3/playlists/<playlist_id>', methods=['GET'])
def playlist__(playlist_id):
    key = request.args.get('key')
    if key != accessId:
        abort(403)
    ip = getIp()
    port = getPort()
    if not playlist_id:
        return jsonify({"error": "Playlist ID is required"}), 400
    return invidious.playlistV2(playlist_id)
@app.route('/leanback_ajax', methods=['GET'])
def leanback_ajax():
    key = request.args.get('key')
    if key != accessId:
        abort(403)
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
                    'en': f'http://liinback.pythonanywhere.com/api/categories/trending?lang=en',
                    'es': f'http://liinback.pythonanywhere.com/api/categories/trending?lang=es',
                    'fr': f'http://liinback.pythonanywhere.com/api/categories/trending?lang=fr',
                    'de': f'http://liinback.pythonanywhere.com/api/categories/trending?lang=de',
                    'ja': f'http://liinback.pythonanywhere.com/api/categories/trending?lang=ja',
                    'nl': f'http://liinback.pythonanywhere.com/api/categories/trending?lang=nl',
                    'it': f'http://liinback.pythonanywhere.com/api/categories/trending?lang=it'
                }.get(lang, f'http://liinback.pythonanywhere.com/api/categories/trending?lang=en'),
                'thumbnail': {
                    'en': f'http://liinback.pythonanywhere.com/api/thumbnails/categories/trending?lang=en',
                    'es': f'http://liinback.pythonanywhere.com/api/thumbnails/categories/trending?lang=es',
                    'fr': f'http://liinback.pythonanywhere.com/api/thumbnails/categories/trending?lang=fr',
                    'de': f'http://liinback.pythonanywhere.com/api/thumbnails/categories/trending?lang=de',
                    'ja': f'http://liinback.pythonanywhere.com/api/thumbnails/categories/trending?lang=ja',
                    'nl': f'http://liinback.pythonanywhere.com/api/thumbnails/categories/trending?lang=nl',
                    'it': f'http://liinback.pythonanywhere.com/api/thumbnails/categories/trending?lang=it'
                }.get(lang, f'http://liinback.pythonanywhere.com/api/thumbnails/categories/trending?lang=en'),
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
                    'en': f'http://liinback.pythonanywhere.com/api/categories/trending?params=4gINGgt5dG1hX2NoYXJ0cw%3D%3D&lang=en',
                    'es': f'http://liinback.pythonanywhere.com/api/categories/trending?params=4gINGgt5dG1hX2NoYXJ0cw%3D%3D&lang=es',
                    'fr': f'http://liinback.pythonanywhere.com/api/categories/trending?params=4gINGgt5dG1hX2NoYXJ0cw%3D%3D&lang=fr',
                    'de': f'http://liinback.pythonanywhere.com/api/categories/trending?params=4gINGgt5dG1hX2NoYXJ0cw%3D%3D&lang=de',
                    'ja': f'http://liinback.pythonanywhere.com/api/categories/trending?params=4gINGgt5dG1hX2NoYXJ0cw%3D%3D&lang=ja',
                    'nl': f'http://liinback.pythonanywhere.com/api/categories/trending?params=4gINGgt5dG1hX2NoYXJ0cw%3D%3D&lang=nl',
                    'it': f'http://liinback.pythonanywhere.com/api/categories/trending?params=4gINGgt5dG1hX2NoYXJ0cw%3D%3D&lang=it'
                }.get(lang, f'http://liinback.pythonanywhere.com/api/categories/trending?params=4gINGgt5dG1hX2NoYXJ0cw%3D%3D&lang=en'),
                'thumbnail': {
                    'en': f'http://liinback.pythonanywhere.com/api/thumbnails/categories/v2/music?lang=en',
                    'es': f'http://liinback.pythonanywhere.com/api/thumbnails/categories/v2/music?lang=es',
                    'fr': f'http://liinback.pythonanywhere.com/api/thumbnails/categories/v2/music?lang=fr',
                    'de': f'http://liinback.pythonanywhere.com/api/thumbnails/categories/v2/music?lang=de',
                    'ja': f'http://liinback.pythonanywhere.com/api/thumbnails/categories/v2/music?lang=ja',
                    'nl': f'http://liinback.pythonanywhere.com/api/thumbnails/categories/v2/music?lang=nl',
                    'it': f'http://liinback.pythonanywhere.com/api/thumbnails/categories/v2/music?lang=it'
                }.get(lang, f'http://liinback.pythonanywhere.com/api/thumbnails/categories/v2/music?lang=en'),
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
                    'en': f'http://liinback.pythonanywhere.com/api/categories/trending?params=4gIcGhpnYW1pbmdfY29ycHVzX21vc3RfcG9wdWxhcg%3D%3D&lang=en',
                    'es': f'http://liinback.pythonanywhere.com/api/categories/trending?params=4gIcGhpnYW1pbmdfY29ycHVzX21vc3RfcG9wdWxhcg%3D%3D&lang=es',
                    'fr': f'http://liinback.pythonanywhere.com/api/categories/trending?params=4gIcGhpnYW1pbmdfY29ycHVzX21vc3RfcG9wdWxhcg%3D%3D&lang=fr',
                    'de': f'http://liinback.pythonanywhere.com/api/categories/trending?params=4gIcGhpnYW1pbmdfY29ycHVzX21vc3RfcG9wdWxhcg%3D%3D&lang=de',
                    'ja': f'http://liinback.pythonanywhere.com/api/categories/trending?params=4gIcGhpnYW1pbmdfY29ycHVzX21vc3RfcG9wdWxhcg%3D%3D&lang=ja',
                    'nl': f'http://liinback.pythonanywhere.com/api/categories/trending?params=4gIcGhpnYW1pbmdfY29ycHVzX21vc3RfcG9wdWxhcg%3D%3D&lang=nl',
                    'it': f'http://liinback.pythonanywhere.com/api/categories/trending?params=4gIcGhpnYW1pbmdfY29ycHVzX21vc3RfcG9wdWxhcg%3D%3D&lang=it'
                }.get(lang, f'http://liinback.pythonanywhere.com/api/categories/trending?params=4gIcGhpnYW1pbmdfY29ycHVzX21vc3RfcG9wdWxhcg%3D%3D&lang=en'),
                'thumbnail': {
                    'en': f'http://liinback.pythonanywhere.com/api/thumbnails/categories/v2/gaming?lang=en',
                    'es': f'http://liinback.pythonanywhere.com/api/thumbnails/categories/v2/gaming?lang=es',
                    'fr': f'http://liinback.pythonanywhere.com/api/thumbnails/categories/v2/gaming?lang=fr',
                    'de': f'http://liinback.pythonanywhere.com/api/thumbnails/categories/v2/gaming?lang=de',
                    'ja': f'http://liinback.pythonanywhere.com/api/thumbnails/categories/v2/gaming?lang=ja',
                    'nl': f'http://liinback.pythonanywhere.com/api/thumbnails/categories/v2/gaming?lang=nl',
                    'it': f'http://liinback.pythonanywhere.com/api/thumbnails/categories/v2/gaming?lang=it'
                }.get(lang, f'http://liinback.pythonanywhere.com/api/thumbnails/categories/v2/gaming?lang=en'),
                'title': {
                    'en': f'Gaming',
                    'es': f'Juegos',
                    'fr': f'Jeux vidéo',
                    'de': f'Gaming',
                    'ja': f'ゲーム',
                    'nl': f'Games',
                    'it': f'Giochi'
                }.get(lang, f'Gaming')
            },
            {
                'gdata_url': {
                    'en': f'http://liinback.pythonanywhere.com/api/categories/v3/UCEgdi0XIXXZ-qJOFPf4JSKw?lang=en',
                    'es': f'http://liinback.pythonanywhere.com/api/categories/v3/UCEgdi0XIXXZ-qJOFPf4JSKw?lang=es',
                    'fr': f'http://liinback.pythonanywhere.com/api/categories/v3/UCEgdi0XIXXZ-qJOFPf4JSKw?lang=fr',
                    'de': f'http://liinback.pythonanywhere.com/api/categories/v3/UCEgdi0XIXXZ-qJOFPf4JSKw?lang=de',
                    'ja': f'http://liinback.pythonanywhere.com/api/categories/v3/UCEgdi0XIXXZ-qJOFPf4JSKw?lang=ja',
                    'nl': f'http://liinback.pythonanywhere.com/api/categories/v3/UCEgdi0XIXXZ-qJOFPf4JSKw?lang=nl',
                    'it': f'http://liinback.pythonanywhere.com/api/categories/v3/UCEgdi0XIXXZ-qJOFPf4JSKw?lang=it'
                }.get(lang, f'http://liinback.pythonanywhere.com/api/categories/v3/UCEgdi0XIXXZ-qJOFPf4JSKw?lang=en'),
                'thumbnail': {
                    'en': f'http://liinback.pythonanywhere.com/api/thumbnails/categories/v3/sports?lang=en',
                    'es': f'http://liinback.pythonanywhere.com/api/thumbnails/categories/v3/sports?lang=es',
                    'fr': f'http://liinback.pythonanywhere.com/api/thumbnails/categories/v3/sports?lang=fr',
                    'de': f'http://liinback.pythonanywhere.com/api/thumbnails/categories/v3/sports?lang=de',
                    'ja': f'http://liinback.pythonanywhere.com/api/thumbnails/categories/v3/sports?lang=ja',
                    'nl': f'http://liinback.pythonanywhere.com/api/thumbnails/categories/v3/sports?lang=nl',
                    'it': f'http://liinback.pythonanywhere.com/api/thumbnails/categories/v3/sports?lang=it'
                }.get(lang, f'http://liinback.pythonanywhere.com/api/thumbnails/categories/v3/sports?lang=en'),
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
                     'en': f'http://liinback.pythonanywhere.com/api/categories/v3/UCrpQ4p1Ql_hG8rKXIKM1MOQ?lang=en',
                     'es': f'http://liinback.pythonanywhere.com/api/categories/v3/UCrpQ4p1Ql_hG8rKXIKM1MOQ?lang=es',
                     'fr': f'http://liinback.pythonanywhere.com/api/categories/v3/UCrpQ4p1Ql_hG8rKXIKM1MOQ?lang=fr',
                     'de': f'http://liinback.pythonanywhere.com/api/categories/v3/UCrpQ4p1Ql_hG8rKXIKM1MOQ?lang=de',
                     'ja': f'http://liinback.pythonanywhere.com/api/categories/v3/UCrpQ4p1Ql_hG8rKXIKM1MOQ?lang=ja',
                     'nl': f'http://liinback.pythonanywhere.com/api/categories/v3/UCrpQ4p1Ql_hG8rKXIKM1MOQ?lang=nl',
                     'it': f'http://liinback.pythonanywhere.com/api/categories/v3/UCrpQ4p1Ql_hG8rKXIKM1MOQ?lang=it'
                }.get(lang, f'http://liinback.pythonanywhere.com/api/categories/v3/UCrpQ4p1Ql_hG8rKXIKM1MOQ?lang=en'),
                'thumbnail': {
                    'en': f'http://liinback.pythonanywhere.com/api/thumbnails/categories/v3/fb?lang=en',
                    'es': f'http://liinback.pythonanywhere.com/api/thumbnails/categories/v3/fb?lang=es',
                    'fr': f'http://liinback.pythonanywhere.com/api/thumbnails/categories/v3/fb?lang=fr',
                    'de': f'http://liinback.pythonanywhere.com/api/thumbnails/categories/v3/fb?lang=de',
                    'ja': f'http://liinback.pythonanywhere.com/api/thumbnails/categories/v3/fb?lang=ja',
                    'nl': f'http://liinback.pythonanywhere.com/api/thumbnails/categories/v3/fb?lang=nl',
                    'it': f'http://liinback.pythonanywhere.com/api/thumbnails/categories/v3/fb?lang=it'
                }.get(lang, f'http://liinback.pythonanywhere.com/api/thumbnails/categories/v3/fb?lang=en'),
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
                     'en': f'http://liinback.pythonanywhere.com/api/categories/v3/UCYfdidRxbB8Qhf0Nx7ioOYw?lang=en',
                     'es': f'http://liinback.pythonanywhere.com/api/categories/v3/UCYfdidRxbB8Qhf0Nx7ioOYw?lang=es',
                     'fr': f'http://liinback.pythonanywhere.com/api/categories/v3/UCYfdidRxbB8Qhf0Nx7ioOYw?lang=fr',
                     'de': f'http://liinback.pythonanywhere.com/api/categories/v3/UCYfdidRxbB8Qhf0Nx7ioOYw?lang=de',
                     'ja': f'http://liinback.pythonanywhere.com/api/categories/v3/UCYfdidRxbB8Qhf0Nx7ioOYw?lang=ja',
                     'nl': f'http://liinback.pythonanywhere.com/api/categories/v3/UCYfdidRxbB8Qhf0Nx7ioOYw?lang=nl',
                     'it': f'http://liinback.pythonanywhere.com/api/categories/v3/UCYfdidRxbB8Qhf0Nx7ioOYw?lang=it',
                }.get(lang, f'http://liinback.pythonanywhere.com/api/categories/v3/UCYfdidRxbB8Qhf0Nx7ioOYw?lang=en'),
                'thumbnail': {
                    'en': f'http://liinback.pythonanywhere.com/api/thumbnails/categories/v3/news?lang=en',
                    'es': f'http://liinback.pythonanywhere.com/api/thumbnails/categories/v3/news?lang=es',
                    'fr': f'http://liinback.pythonanywhere.com/api/thumbnails/categories/v3/news?lang=fr',
                    'de': f'http://liinback.pythonanywhere.com/api/thumbnails/categories/v3/news?lang=de',
                    'ja': f'http://liinback.pythonanywhere.com/api/thumbnails/categories/v3/news?lang=ja',
                    'nl': f'http://liinback.pythonanywhere.com/api/thumbnails/categories/v3/news?lang=nl',
                    'it': f'http://liinback.pythonanywhere.com/api/thumbnails/categories/v3/news?lang=it'
                }.get(lang, f'http://liinback.pythonanywhere.com/api/thumbnails/categories/v3/news?lang=en'),
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
                     'en': f'http://liinback.pythonanywhere.com/api/categories/trending?params=4gIKGgh0cmFpbGVycw%3D%3D&lang=en',
                     'es': f'http://liinback.pythonanywhere.com/api/categories/trending?params=4gIKGgh0cmFpbGVycw%3D%3D&lang=es',
                     'fr': f'http://liinback.pythonanywhere.com/api/categories/trending?params=4gIKGgh0cmFpbGVycw%3D%3D&lang=fr',
                     'de': f'http://liinback.pythonanywhere.com/api/categories/trending?params=4gIKGgh0cmFpbGVycw%3D%3D&lang=de',
                     'ja': f'http://liinback.pythonanywhere.com/api/categories/trending?params=4gIKGgh0cmFpbGVycw%3D%3D&lang=ja',
                     'nl': f'http://liinback.pythonanywhere.com/api/categories/trending?params=4gIKGgh0cmFpbGVycw%3D%3D&lang=nl',
                     'it': f'http://liinback.pythonanywhere.com/api/categories/trending?params=4gIKGgh0cmFpbGVycw%3D%3D&lang=it',
                }.get(lang, f'http://liinback.pythonanywhere.com/api/categories/trending?params=4gIKGgh0cmFpbGVycw%3D%3D&lang=en'),
                'thumbnail': {
                    'en': f'http://liinback.pythonanywhere.com/api/thumbnails/categories/v3/movies?lang=en',
                    'es': f'http://liinback.pythonanywhere.com/api/thumbnails/categories/v3/movies?lang=es',
                    'fr': f'http://liinback.pythonanywhere.com/api/thumbnails/categories/v3/movies?lang=fr',
                    'de': f'http://liinback.pythonanywhere.com/api/thumbnails/categories/v3/movies?lang=de',
                    'ja': f'http://liinback.pythonanywhere.com/api/thumbnails/categories/v3/movies?lang=ja',
                    'nl': f'http://liinback.pythonanywhere.com/api/thumbnails/categories/v3/movies?lang=nl',
                    'it': f'http://liinback.pythonanywhere.com/api/thumbnails/categories/v3/movies?lang=it'
                }.get(lang, f'http://liinback.pythonanywhere.com/api/thumbnails/categories/v3/movies?lang=en'),
                'title': {
                    'en': f'Film & Animation',
                    'es': f'Películas y TV',
                    'fr': f'Films et séries TV',
                    'de': f'Films et séries TV',
                    'ja': f'Films et séries TV',
                    'nl': f'Films et séries TV',
                    'it': f'Films et séries TV'
                }.get(lang, f'Film & Animation')
            },
            {
                'gdata_url': {
                     'en': f'http://liinback.pythonanywhere.com/api/_playlists?lang=en&id=PLrEnWoR732-BHrPp_Pm8_VleD68f9s14-',
                     'es': f'http://liinback.pythonanywhere.com/api/_playlists?lang=es&id=PLrEnWoR732-BHrPp_Pm8_VleD68f9s14-',
                     'fr': f'http://liinback.pythonanywhere.com/api/_playlists?lang=fr&id=PLrEnWoR732-BHrPp_Pm8_VleD68f9s14-',
                     'de': f'http://liinback.pythonanywhere.com/api/_playlists?lang=de&id=PLrEnWoR732-BHrPp_Pm8_VleD68f9s14-',
                     'ja': f'http://liinback.pythonanywhere.com/api/_playlists?lang=ja&id=PLrEnWoR732-BHrPp_Pm8_VleD68f9s14-',
                     'nl': f'http://liinback.pythonanywhere.com/api/_playlists?lang=nl&id=PLrEnWoR732-BHrPp_Pm8_VleD68f9s14-',
                     'it': f'http://liinback.pythonanywhere.com/api/_playlists?lang=it&id=PLrEnWoR732-BHrPp_Pm8_VleD68f9s14-',
                }.get(lang, f'http://liinback.pythonanywhere.com/api/_playlists?lang=en&id=PLrEnWoR732-BHrPp_Pm8_VleD68f9s14-'),
                'thumbnail': {
                    'en': f'http://liinback.pythonanywhere.com/api/thumbnails/playlists?lang=en&id=PLrEnWoR732-BHrPp_Pm8_VleD68f9s14-',
                    'es': f'http://liinback.pythonanywhere.com/api/thumbnails/playlists?lang=es&id=PLrEnWoR732-BHrPp_Pm8_VleD68f9s14-',
                    'fr': f'http://liinback.pythonanywhere.com/api/thumbnails/playlists?lang=fr&id=PLrEnWoR732-BHrPp_Pm8_VleD68f9s14-',
                    'de': f'http://liinback.pythonanywhere.com/api/thumbnails/playlists?lang=de&id=PLrEnWoR732-BHrPp_Pm8_VleD68f9s14-',
                    'ja': f'http://liinback.pythonanywhere.com/api/thumbnails/playlists?lang=ja&id=PLrEnWoR732-BHrPp_Pm8_VleD68f9s14-',
                    'nl': f'http://liinback.pythonanywhere.com/api/thumbnails/playlists?lang=nl&id=PLrEnWoR732-BHrPp_Pm8_VleD68f9s14-',
                    'it': f'http://liinback.pythonanywhere.com/api/thumbnails/playlists?lang=it&id=PLrEnWoR732-BHrPp_Pm8_VleD68f9s14-'
                }.get(lang, f'http://liinback.pythonanywhere.com/api/thumbnails/playlists?lang=en&id=PLrEnWoR732-BHrPp_Pm8_VleD68f9s14-'),
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
        subscriptionsUrl = f'https://www.youtube.com/youtubei/v1/browse?browseId=FEchannels&key={API_KEY}&access_token={oauthToken}'
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
                                                'gdata_url': f'http://liinback.pythonanywhere.com/api/channels/{browseId}/uploads',
                                                'thumbnail': f'http://liinback.pythonanywhere.com/api/thumbnails/channels/{browseId}/uploads',
                                                'title': f'{authorName}'
                                            })
                return jsonify(response)
        else:
            return Response('Failed to fetch subscriptions', status=500)
    return jsonify(response), 200
def fetchAndServeMusicThumbnail(lang):
    if not ip or not port:
        return "Invalid IP or Port configuration", 500
    url = f"http://liinback.pythonanywhere.com/api/categories/trending?params=4gINGgt5dG1hX2NoYXJ0cw%3D%3D&lang={lang}&key={accessId}"
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
def fetchAndServePlaylistThumbnail(lang, playlistId):
    if not ip or not port:
        return "Invalid IP or Port configuration", 500
    url = f"http://liinback.pythonanywhere.com/api/_playlists?lang={lang}&id={playlistId}&key={accessId}"
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
def fetchAndServeSportThumbnail(lang):
    if not ip or not port:
        return "Invalid IP or Port configuration", 500
    url = f"http://liinback.pythonanywhere.com/api/categories/v3/UCEgdi0XIXXZ-qJOFPf4JSKw?lang={lang}&key={accessId}"
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
def fetchAndServeMoviesThumbnail(lang):
    if not ip or not port:
        return "Invalid IP or Port configuration", 500
    url = f"http://liinback.pythonanywhere.com/api/categories/trending?params=4gIKGgh0cmFpbGVycw%3D%3D&lang={lang}&key={accessId}"
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
def fetchAndServeGamingThumbnail(lang):
    if not ip or not port:
        return "Invalid IP or Port configuration", 500
    url = f"http://liinback.pythonanywhere.com/api/categories/trending?params=4gIcGhpnYW1pbmdfY29ycHVzX21vc3RfcG9wdWxhcg%3D%3D&lang={lang}&key={accessId}"
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
def fetchAndServeFashionBeautyThumbnail(lang):
    if not ip or not port:
        return "Invalid IP or Port configuration", 500
    url = f"http://liinback.pythonanywhere.com/api/categories/v3/UCrpQ4p1Ql_hG8rKXIKM1MOQ?lang={lang}&key={accessId}"
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
def fetchAndServeNewsThumbnail(lang):
    if not ip or not port:
        return "Invalid IP or Port configuration", 500
    url = f"http://liinback.pythonanywhere.com/api/categories/v3/UCYfdidRxbB8Qhf0Nx7ioOYw?lang={lang}&key={accessId}"
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
def fetchAndServeTrendsThumbnail(lang):
    if not ip or not port:
        return "Invalid IP or Port configuration", 500
    url = f"http://liinback.pythonanywhere.com/api/categories/trending?lang={lang}&key={accessId}"
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
def fetchAndServeLikesThumbnail(lang, oauthToken):
    _url = f'http://liinback.pythonanywhere.com/api/liked_videos?lang={lang}&access_token={oauthToken}&key={accessId}'
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
    return fetchAndServeTrendsThumbnail(lang)
def fetchAndServePopularThumbnail(type=None):
    url = "http://liinback.pythonanywhere.com/api/popular&key={accessId}"
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
def fetchAndServeChannelUploadsThumbnail2(browseId):
    url = f"http://liinback.pythonanywhere.com/api/channels/{browseId}/uploads&key={accessId}"
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
def fetchAndServeChannelUploadsThumbnail2(channelId):
    url = f'https://www.googleapis.com/youtube/v3/channels?part=contentDetails&id={channelId}&key={DATA_API_KEY}'
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        uploads_playlist_id = data['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        playlist_url = f'https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&maxResults=1&playlistId={uploads_playlist_id}&key={DATA_API_KEY}'
        playlist_response = requests.get(playlist_url)
        playlist_response.raise_for_status()
        playlist_data = playlist_response.json()
        if 'items' in playlist_data:
            video = playlist_data['items'][0]['snippet']
            video_id = video['resourceId']['videoId']
            thumbnail_url = f'http://i.ytimg.com/vi/{video_id}/mqdefault.jpg'
            return redirect(thumbnail_url, code=302)
        else:
            return 'No videos found in the uploads playlist', 404
    except Exception as e:
        print("Error fetching or processing data:", e)
        return "Error fetching channel data", 500
def getAuthorName(channelId):
    try:
        url = f"http://liinback.pythonanywhere.com/api/channels/{channelId}/uploads&key={accessId}"
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
    return fetchAndServeChannelUploadsThumbnail2(browseId)
@app.route('/api/thumbnails/channels/<channelId>/uploads', methods=['GET'])
def uploadsThumbnail(channelId):
    ip = getIp()
    port = getPort()
    return fetchAndServeChannelUploadsThumbnail(channelId)
@app.route('/api/thumbnails/playlists', methods=['GET'])
def playlistThumbnail():
    ip = getIp()
    port = getPort()
    lang = request.args.get('lang', 'en')
    playlistId = request.args.get('id')
    return fetchAndServePlaylistThumbnail(lang, playlistId)
@app.route('/api/thumbnails/popular', methods=['GET'])
def popularThumbnail():
    ip = getIp()
    port = getPort()
    type = request.args.get('type')
    return fetchAndServePopularThumbnail(type)
@app.route('/api/thumbnails/liked_videos', methods=['GET'])
def likedVideosThumbnail():
    ip = getIp()
    port = getPort()
    lang = request.args.get('lang', 'en')
    oauthToken = request.args.get('access_token')
    if oauthToken:
        return fetchAndServeLikesThumbnail(lang, oauthToken)
    else:
        return "Access token missing", 400
@app.route('/api/thumbnails/categories/v2/music', methods=['GET'])
def musicThumbnail():
    ip = getIp()
    port = getPort()
    lang = request.args.get('lang', 'en')
    return fetchAndServeMusicThumbnail(lang)
@app.route('/api/thumbnails/categories/v3/movies', methods=['GET'])
def moviesThumbnail():
    ip = getIp()
    port = getPort()
    lang = request.args.get('lang', 'en')
    return fetchAndServeMoviesThumbnail(lang)
@app.route('/api/thumbnails/categories/v2/gaming', methods=['GET'])
def gamingThumbnail():
    ip = getIp()
    port = getPort()
    lang = request.args.get('lang', 'en')
    return fetchAndServeGamingThumbnail(lang)
@app.route('/api/thumbnails/categories/v3/sports', methods=['GET'])
def sportsThumbnail():
    ip = getIp()
    port = getPort()
    lang = request.args.get('lang', 'en')
    return fetchAndServeSportThumbnail(lang)
@app.route('/api/thumbnails/categories/v3/fb', methods=['GET'])
def fashionAndBeautyThumbnail():
    ip = getIp()
    port = getPort()
    lang = request.args.get('lang', 'en')
    return fetchAndServeFashionBeautyThumbnail(lang)
@app.route('/api/thumbnails/categories/v3/news', methods=['GET'])
def newsThumbnail():
    ip = getIp()
    port = getPort()
    lang = request.args.get('lang', 'en')
    return fetchAndServeNewsThumbnail(lang)
def file_expired(file_path):
    if not os.path.exists(file_path):
        return True
    file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
    expiration_time = file_mtime + timedelta(hours=48)
    return datetime.now() > expiration_time
@app.route('/video/get/<videoId>', methods=['GET'])
def get_video(videoId):
    return getVideo.fetch(videoId)
@app.route('/video/info/<videoId>', methods=['GET'])
def _getVideoInfo(videoId):
    return getVideoInfo.build(videoId)
@app.route("/timedtext")
def timedtext():
    video_id = request.args.get("v", "")
    type_ = request.args.get("type")
    use_json = "json" in request.args
    reset_cache = "resetcache=1" in (request.headers.get("Referer", ""))
    if type_ == "list":
        data = get_languages(video_id, reset_cache)
        return jsonify(data) if use_json else generateXMLList(data)
    elif type_ == "track":
        lang = request.args.get("lang", "")
        xml = getCaption(video_id, lang)
        return jsonify(parseCaptionsInJSONFormat(xml)) if use_json else xml
    return "Invalid request", 400
def get_languages(video_id, reset_cache=False):
    cache_file = os.path.join(CACHE_DIR, f"{video_id}_langs.json")
    if not reset_cache and os.path.exists(cache_file):
        with open(cache_file, "r", encoding="utf-8") as f:
            return json.load(f)
    data = {}
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(data, f)
    return data
def getCaption(video_id, language):
    filename = os.path.join(CACHE_DIR, f"{video_id}-{language}.xml")
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            return f.read()

    languages = get_languages(video_id)
    if language in languages:
        try:
            response = requests.get(languages[language]["url"])
            if response.status_code == 404 or DEFAULTS[0] in response.text:
                return DEFAULTS[1]
            with open(filename, "w", encoding="utf-8") as f:
                f.write(response.text)
            return response.text
        except requests.RequestException:
            return ""
    return ""
def parseCaptionsInJSONFormat(xml_data):
    def b_float(value):
        return round(float(value), 1)

    json_data = {}
    root = ET.fromstring(xml_data)
    for text in root.findall("text"):
        start_time = b_float(text.attrib.get("start", "0"))
        while start_time in json_data:
            start_time += 0.1
        json_data[start_time] = {
            "text": text.text or "",
            "start": start_time,
            "duration": b_float(text.attrib.get("dur", "0")),
            "end": b_float(start_time + b_float(text.attrib.get("dur", "0")))
        }
    return json_data
def generateXMLList(data):
    xml = "<subList>"
    for index, (lang, info) in enumerate(data.items()):
        xml += f'<track id="{index}" lang_code="{lang}" lang_name="{info["name"]}" />'
    xml += "</subList>"
    return xml
@app.route('/apiplayer', methods=['GET'])
def apiplayer():
    key = request.args.get('key')
    if key != accessId:
        abort(403)
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
@app.route('/subtitle_module',methods=['GET'])
def subtitle_module():
    request_dump(request)
    return send_file(r"swf\subtitle_module.swf",mimetype="application/x-shockwave-flash")
@app.route('/iv_module',methods=['GET'])
def iv_module():
    request_dump(request)
    return send_file(r"swf\iv_module.swf",mimetype="application/x-shockwave-flash")
@app.route('/wiitv', methods=['GET'])
def lblWii():
    key = request.args.get('key')
    if key != accessId:
        abort(403)
    lang = request.args.get('lang', 'en')
    lang_map = {'en', 'es', 'fr', 'it', 'de', 'nl', 'ja'}
    if lang not in lang_map:
        lang = 'en'
    return send_file(f"swf/{lang}/leanbacklite_wii.swf", mimetype="application/x-shockwave-flash")
@app.route('/api/users/<channelId>/icon', methods=['GET'])
def getUserIcon(channelId):
    url = f'https://www.googleapis.com/youtube/v3/channels/?part=snippet&id={channelId}&key={DATA_API_KEY}'
    response = requests.get(url)
    if response.status_code != 200:
        return "Error fetching channel data", 500
    channelData = response.json()
    items = channelData.get('items', [])
    if not items:
        return 'Channel is undefined', 404
    thumbnails = items[0]['snippet']['thumbnails']
    thumbnail_url = thumbnails.get('default', {}).get('url')
    if thumbnail_url:
        thumbnail_response = requests.get(thumbnail_url)
        if thumbnail_response.status_code == 200:
            return Response(thumbnail_response.content, content_type='image/jpeg')
        else:
            return 'Failed to load thumbnail', 500
    else:
        return 'Thumbnail is undefined', 404
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
                customThumbnailUrl = f"http://liinback.pythonanywhere.com/api/users/{channelId}/icon"
                channelData["thumbnails"]["default"]["url"] = customThumbnailUrl
        return jsonify(data)
    return jsonify({"error": f"Failed to fetch user data: {response.text}"}), response.status_code
@app.route('/api/authentication/token', methods=['POST'])
def _access_token():
    return accessId
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)