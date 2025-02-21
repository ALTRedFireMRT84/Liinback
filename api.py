from flask import Response, jsonify, Flask, request, redirect
import json
import requests
from urllib.parse import quote_plus
class Invidious:
        
    def buildXML(self, json_data, ip, port, lang):
        viewCountLabels = {
            'en': 'views',
            'es': 'visualizaciones',
            'fr': 'vues',
            'de': 'Aufrufe',
            'ja': '回視聴',
            'nl': 'weergaven',
            'it': 'visualizzazioni'
        }
        viewCountLabel = viewCountLabels.get(lang, 'views')
        xml_string = '<?xml version=\'1.0\' encoding=\'UTF-8\'?>'
        xml_string += '<feed xmlns:openSearch=\'http://a9.com/-/spec/opensearch/1.1/\' xmlns:media=\'http://search.yahoo.com/mrss/\' xmlns:yt=\'http://www.youtube.com/xml/schemas/2015\'>'
        xml_string += '<title type=\'text\'>Videos</title>'
        xml_string += '<generator ver=\'1.0\' uri=\'http://kamil.cc/\'>Liinback data API</generator>'
        xml_string += '<openSearch:totalResults>0</openSearch:totalResults>'
        xml_string += '<openSearch:startIndex>1</openSearch:startIndex>'
        xml_string += '<openSearch:itemsPerPage>20</openSearch:itemsPerPage>'
        for item in json_data:
            if 'videoId' not in item:
                continue
            xml_string += '<entry>'
            xml_string += f'<id>http://{ip}:{port}/api/videos/' + self.escape_xml(item['videoId']) + '</id>'
            xml_string += '<published>' + self.escape_xml(item['publishedText']) + '</published>'
            xml_string += '<title type=\'text\'>' + self.escape_xml(item['title']) + '</title>'
            xml_string += f'<link rel=\'http://{ip}:{port}/api/videos/' + self.escape_xml(item['videoId']) + '/related\'/>'
            xml_string += '<author>'
            xml_string += '<name>' + self.escape_xml(item['author']) + '</name>'
            xml_string += f'<uri>http://{ip}:{port}/api/channels/' + self.escape_xml(item.get('channel_id', '')) + '</uri>'
            xml_string += '</author>'
            xml_string += '<media:group>'
            xml_string += '<media:thumbnail yt:name=\'mqdefault\' url=\'http://i.ytimg.com/vi/' + self.escape_xml(item['videoId']) + '/mqdefault.jpg\' height=\'240\' width=\'320\' time=\'00:00:00\'/>'
            xml_string += '<yt:duration seconds=\'' + self.escape_xml(str(item['lengthSeconds'])) + '\'/>'
            xml_string += '<yt:uploaderId id=\'' + self.escape_xml(item['authorId']) + '\'>' + self.escape_xml(item['authorId']) + '</yt:uploaderId>'
            xml_string += '<yt:videoid id=\'' + self.escape_xml(item['videoId']) + '\'>' + self.escape_xml(item['videoId']) + '</yt:videoid>'
            xml_string += '<media:credit role=\'uploader\' name=\'' + self.escape_xml(item['author']) + '\'>' + self.escape_xml(item['author']) + '</media:credit>'
            xml_string += '</media:group>'
            xml_string += f'<yt:statistics favoriteCount="0" viewCount="{item["viewCount"]} {viewCountLabel}"/>'
            xml_string += '</entry>'
        xml_string += '</feed>'
        return xml_string

    def buildPlaylistXML(self, json_data, ip, port, noDateString):
        xml_string = '<?xml version=\'1.0\' encoding=\'UTF-8\'?>'
        xml_string += '<feed xmlns:openSearch=\'http://a9.com/-/spec/opensearch/1.1/\' xmlns:media=\'http://search.yahoo.com/mrss/\' xmlns:yt=\'http://www.youtube.com/xml/schemas/2015\'>'
        xml_string += '<title type=\'text\'>Videos</title>'
        xml_string += '<generator ver=\'1.0\' uri=\'http://kamil.cc/\'>Liinback data API</generator>'
        xml_string += '<openSearch:totalResults>0</openSearch:totalResults>'
        xml_string += '<openSearch:startIndex>1</openSearch:startIndex>'
        xml_string += '<openSearch:itemsPerPage>20</openSearch:itemsPerPage>'
        for item in json_data:
            if 'videoId' not in item:
                continue
            xml_string += '<entry>'
            xml_string += f'<id>http://{ip}:{port}/api/videos/' + self.escape_xml(item['videoId']) + '</id>'
            xml_string += f'<published>{noDateString}</published>'
            xml_string += '<title type=\'text\'>' + self.escape_xml(item['title']) + '</title>'
            xml_string += f'<link rel=\'http://{ip}:{port}/api/videos/' + self.escape_xml(item['videoId']) + '/related\'/>'
            xml_string += '<author>'
            xml_string += '<name>' + self.escape_xml(item['author']) + '</name>'
            xml_string += f'<uri>http://{ip}:{port}/api/channels/' + self.escape_xml(item.get('channel_id', '')) + '</uri>'
            xml_string += '</author>'
            xml_string += '<media:group>'
            xml_string += '<media:thumbnail yt:name=\'mqdefault\' url=\'http://i.ytimg.com/vi/' + self.escape_xml(item['videoId']) + '/mqdefault.jpg\' height=\'240\' width=\'320\' time=\'00:00:00\'/>'
            xml_string += '<yt:duration seconds=\'' + self.escape_xml(str(item['lengthSeconds'])) + '\'/>'
            xml_string += '<yt:uploaderId id=\'' + self.escape_xml(item['authorId']) + '\'>' + self.escape_xml(item['authorId']) + '</yt:uploaderId>'
            xml_string += '<yt:videoid id=\'' + self.escape_xml(item['videoId']) + '\'>' + self.escape_xml(item['videoId']) + '</yt:videoid>'
            xml_string += '<media:credit role=\'uploader\' name=\'' + self.escape_xml(item['author']) + '\'>' + self.escape_xml(item['author']) + '</media:credit>'
            xml_string += '</media:group>'
            xml_string += f'<yt:statistics favoriteCount=\'null\' viewCount=\'\'/>'
            xml_string += '</entry>'
        xml_string += '</feed>'
        return xml_string

    @staticmethod
    def buildM3U(json_data, ip, port):
        m3u_content = "#EXTM3U\n"
        for item in json_data:
            if 'videoId' not in item:
                continue
            video_id = item['videoId']
            title = item['title']
            thumbnail_url = f"http://i.ytimg.com/vi/{video_id}/mqdefault.jpg"
            get_video_url = f"http://{ip}:{port}/api/v2/videos/{video_id}"
            m3u_content += f"#EXTINF:-1,{title}\n{thumbnail_url}\n{get_video_url}\n"
        return m3u_content

    @staticmethod
    def buildV2M3U(json_data, ip, port):
        m3u_content = "#EXTM3U\n"
        for item in json_data:
            if 'videoId' not in item:
                continue
            video_id = item['videoId']
            title = item['title']
            thumbnail_url = f"http://i.ytimg.com/vi/{video_id}/mqdefault.jpg"
            get_video_url = f"http://{ip}:{port}/api/v2/videos/{video_id}"
            m3u_content += f"#EXTINF:-1,{title}\n{thumbnail_url}\n{get_video_url}\n"
        return m3u_content

    @staticmethod
    def buildPlaylistM3U(json_data, ip, port):
        m3u_content = "#EXTM3U\n"
        for item in json_data:
            if 'videoId' not in item:
                continue
            video_id = item['videoId']
            title = item['title']
            thumbnail_url = f"http://i.ytimg.com/vi/{video_id}/mqdefault.jpg"
            get_video_url = f"http://{ip}:{port}/api/v2/videos/{video_id}"
            m3u_content += f"#EXTINF:-1,{title}\n{thumbnail_url}\n{get_video_url}\n"
        return m3u_content
        
    @staticmethod
    def escape_xml(s):
        if s is None:
            return ''
        return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&apos;')

    def search(self, query):
        response = requests.get('https://vid.puffyan.us/api/v1/search?q={}'.format(query))
        response.raise_for_status()
        json_data = response.json()
        xml_data = self.buildM3U(json_data, ip, port)
        return Response(xml_data, mimetype='text/atom+xml')

    def trends(self, ip, port, type_param=None):
        trends_endpoint = "trending"
        if type_param:
            response = requests.get(f"http://vid.puffyan.us/api/v1/{trends_endpoint}?type={type_param}")
        else:
            response = requests.get(f"http://vid.puffyan.us/api/v1/{trends_endpoint}")
        if response.status_code == 200:
            json_data = response.json()
            xml_data = self.buildV2M3U(ip, port, json_data)
            return Response(xml_data, mimetype='text/plain')
        else:
            error_message = {"error": "Invalid response format"}
            return jsonify(error_message), 500

    def popular(self, ip, port):
        popular_endpoint = "popular"
        response = requests.get(f"http://vid.puffyan.us/api/v1/{popular_endpoint}")
        if response.status_code == 200:
            json_data = response.json()
            xml_data = self.buildM3U(json_data, ip, port)
            return Response(xml_data, mimetype='text/atom+xml')
        else:
            error_message = {"error": "Invalid response format"}
            return jsonify(error_message), 500

    def user_uploads(self, ip, port, lang, channel_id=None):
        channels_endpoint = "channels"
        response = requests.get(f"http://vid.puffyan.us/api/v1/{channels_endpoint}/{channel_id}/videos")
        if response.status_code == 200:
            json_data = response.json()
            videos = json_data.get("videos", [])
            xml_data = self.buildXML(videos, ip, port, lang)
            return Response(xml_data, mimetype='text/atom+xml')
        else:
            error_message = {"error": "Invalid response format"}
            return jsonify(error_message), 500
            
    def user_uploads_V2(self, ip, port, channel_id=None):
        channels_endpoint = "channels"
        response = requests.get(f"http://vid.puffyan.us/api/v1/{channels_endpoint}/{channel_id}/videos")
        if response.status_code == 200:
            json_data = response.json()
            videos = json_data.get("videos", [])
            xml_data = self.buildM3U(videos, ip, port)
            return Response(xml_data, mimetype='text/plain')
        else:
            error_message = {"error": "Invalid response format"}
            return jsonify(error_message), 500

    def playlists(self, noDateString, ip, port, playlist_id=None):
        playlists_endpoint = "playlists"
        response = requests.get(f"http://vid.puffyan.us/api/v1/{playlists_endpoint}/{playlist_id}")
        if response.status_code == 200:
            json_data = response.json()
            videos = json_data.get("videos", [])
            xml_data = self.buildPlaylistXML(videos, ip, port, noDateString)
            return Response(xml_data, mimetype='text/atom+xml')
        else:
            error_message = {"error": "Invalid response format"}
            return jsonify(error_message), 500
            
    def playlistV2(self, ip, port, playlist_id=None):
        playlists_endpoint = "playlists"
        response = requests.get(f"http://vid.puffyan.us/api/v1/{playlists_endpoint}/{playlist_id}")
        if response.status_code == 200:
            json_data = response.json()
            videos = json_data.get("videos", [])
            xml_data = self.buildPlaylistM3U(videos, ip, port)
            return Response(xml_data, mimetype='text/plain')
        else:
            error_message = {"error": "Invalid response format"}
            return jsonify(error_message), 500            
            
class InnerTube:
    def playlist(self, ip, port, lang, playlist_id, oauth_token=None):
        url = f'https://www.youtube.com/youtubei/v1/browse?browseId=VL{playlist_id}&key=AIzaS=yAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8'
        if oauth_token:
            url += f'&access_token={oauth_token}'
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0'
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
        response = requests.post(url, json=payload, headers=headers)        
        if response.status_code == 200:
            data = response.json()
            xml_data = self.buildPlaylistXML(data, ip, port)
            return Response(xml_data, mimetype='text/atom+xml')
        else:
            return jsonify({"error": "Failed to fetch playlist data"}), 500
            
    def buildPlaylistXML(self, json_data, ip, port):
        xml_string = '<?xml version="1.0" encoding="UTF-8"?>'
        xml_string += '<feed xmlns:openSearch="http://a9.com/-/spec/opensearch/1.1/" xmlns:media="http://search.yahoo.com/mrss/" xmlns:yt="http://www.youtube.com/xml/schemas/2015">'
        xml_string += '<title type="text">Playlist</title>'
        xml_string += '<generator ver="1.0" uri="http://kamil.cc/">Liinback data API</generator>'
        xml_string += '<openSearch:totalResults>0</openSearch:totalResults>'
        xml_string += '<openSearch:startIndex>1</openSearch:startIndex>'
        xml_string += '<openSearch:itemsPerPage>20</openSearch:itemsPerPage>'
        for item in json_data.get("contents", {}).get("twoColumnBrowseResultsRenderer", {}).get("tabs", []):
            tab = item.get("tabRenderer", {})
            section_list = tab.get("content", {}).get("sectionListRenderer", {}).get("contents", [])
            for section in section_list:
                if "itemSectionRenderer" in section:
                    for video_item in section["itemSectionRenderer"].get("contents", []):
                        if "playlistVideoListRenderer" in video_item:
                            for video in video_item["playlistVideoListRenderer"].get("contents", []):
                                if "playlistVideoRenderer" in video:
                                    videoData = video["playlistVideoRenderer"]
                                    lengthText = videoData.get("lengthText", {}).get("simpleText", "")
                                    videoId = videoData.get("videoId", "")
                                    authorId = videoData.get("shortBylineText", {}).get("runs", [{}])[0].get("navigationEndpoint", {}).get("browseEndpoint", {}).get("browseId", "")
                                    authorName = videoData.get("shortBylineText", {}).get("runs", [{}])[0].get("text", "")
                                    title = videoData.get("title", {}).get("runs", [{}])[0].get("text", "")
                                    viewCount = videoData.get("videoInfo", {}).get("runs", [{}])[0].get("text", "")
                                    publishedText = videoData.get("videoInfo", {}).get("runs", [{}])[2].get("text", "")
                                    xml_string += '<entry>'
                                    xml_string += f'<id>http://{ip}:{port}/api/videos/{videoId}</id>'
                                    xml_string += f'<published>{self.escape_xml(publishedText)}</published>'
                                    xml_string += f'<title type="text">{self.escape_xml(title)}</title>'
                                    xml_string += f'<link rel="http://{ip}:{port}/api/videos/{videoId}/related"/>'
                                    xml_string += f'<author><name>{self.escape_xml(authorName)}</name><uri>https://www.youtube.com/channel/{authorId}</uri></author>'
                                    xml_string += '<media:group>'
                                    xml_string += f'<media:thumbnail yt:name="mqdefault" url="http://i.ytimg.com/vi/{videoId}/mqdefault.jpg" height="240" width="320" time="00:00:00"/>'
                                    xml_string += f'<yt:duration seconds="{self.escape_xml(lengthText)}"/>'
                                    xml_string += f'<yt:uploaderId id="{authorId}">{authorId}</yt:uploaderId>'
                                    xml_string += f'<yt:videoid id="{videoId}">{videoId}</yt:videoid>'
                                    xml_string += f'<media:credit role="uploader" name="{self.escape_xml(authorName)}">{self.escape_xml(authorName)}</media:credit>'
                                    xml_string += '</media:group>'
                                    xml_string += f'<yt:statistics favoriteCount="0" viewCount="{self.escape_xml(viewCount)}"/>'
                                    xml_string += '</entry>'
        xml_string += '</feed>'
        return xml_string

    def extract_continuation_token(self, json_data):
        # Extract the continuation token from the JSON response
        continuation_data = json_data.get("contents", {}).get("twoColumnBrowseResultsRenderer", {}).get("tabs", [{}])[0].get("tabRenderer", {}).get("content", {}).get("sectionListRenderer", {}).get("contents", [])
        if continuation_data:
            continuation_item = continuation_data[-1].get("continuationItemRenderer", {})
            continuation_token = continuation_item.get("continuationEndpoint", {}).get("continuationCommand", {}).get("token", None)
            return continuation_token
        return None

    @staticmethod
    def escape_xml(s):
        if s is None:
            return ''
        return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&apos;')

    @staticmethod
    def change_https_to_http(url):
        if url.startswith("https://"):
            return url.replace("https://", "http://", 1)
        return url

    def buildPlaylistsXML(self, json_data, ip, port, oauth_token):
        xml_string = '<?xml version="1.0" encoding="UTF-8"?>'
        xml_string += '<feed xmlns:openSearch=\'http://a9.com/-/spec/opensearch/1.1/\' xmlns:media=\'http://search.yahoo.com/mrss/\' xmlns:yt=\'http://www.youtube.com/xml/schemas/2015\'>'
        xml_string += '<title type="text">Playlist</title>'
        xml_string += '<generator ver="1.0" uri="http://kamil.cc/">Liinback data API</generator>'
        xml_string += '<openSearch:totalResults>0</openSearch:totalResults>'
        xml_string += '<openSearch:startIndex>1</openSearch:startIndex>'
        xml_string += '<openSearch:itemsPerPage>20</openSearch:itemsPerPage>'
        
        contents = json_data.get('contents', {}).get('twoColumnBrowseResultsRenderer', {}).get('tabs', [])
        
        for tab in contents:
            tab_renderer = tab.get('tabRenderer', {})
            section_list = tab_renderer.get('content', {}).get('sectionListRenderer', {}).get('contents', [])
            
            for section in section_list:
                item_section = section.get('itemSectionRenderer', {}).get('contents', [])
                
                for item in item_section:
                    shelf_renderer = item.get('shelfRenderer', {})
                    horizontal_list = shelf_renderer.get('content', {}).get('horizontalListRenderer', {}).get('items', [])
                    
                    for video in horizontal_list:
                        lockup_view_model = video.get('lockupViewModel', {})
                        title_metadata = lockup_view_model.get('metadata', {}).get('lockupMetadataViewModel', {}).get('title', {}).get('content', '')
                        browse_id = lockup_view_model.get('contentId', '') 
                        thumbnail_url = ''
                        
                        try:
                            thumbnail_url = lockup_view_model.get('contentImage', {}).get('collectionThumbnailViewModel', {}).get('primaryThumbnail', {}).get('thumbnailViewModel', {}).get('image', {}).get('sources', [{}])[0].get('url', '')
                            if 'mqdefault' in thumbnail_url:
                                thumbnail_url = thumbnail_url.replace('mqdefault', 'mqdefault')
                            thumbnail_url = self.change_https_to_http(thumbnail_url)
                        except (IndexError, KeyError):
                            thumbnail_url = ''
                        if title_metadata and browse_id:
                            xml_string += '<entry>'
                            xml_string += f'<title type=\'text\'>{self.escape_xml(title_metadata)}</title>'
                            xml_string += f'<yt:playlistId>{browse_id}</yt:playlistId>'
                            xml_string += f'<updated>{len(json_data)}</updated>'
                            xml_string += f'<yt:countHint>{len(json_data)}</yt:countHint>'
                            xml_string += f"<link>http://{ip}:{port}/api/_playlists?id={self.escape_xml(browse_id)}&access_token={oauth_token}'</link>"
                            if thumbnail_url:
                                xml_string += '<media:group>'
                                xml_string += f'<media:thumbnail yt:name=\'mqdefault\' url=\'{self.escape_xml(thumbnail_url)}\' height=\'240\' width=\'320\' time=\'00:00:00\'/>'
                                xml_string += '</media:group>'
                            xml_string += '</entry>'        
        xml_string += '</feed>'
        return xml_string    
    def playlists(self, ip, port, oauth_token, lang):
        url = f'https://www.youtube.com/youtubei/v1/browse?browseId=FElibrary&key=AIzaS=yAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8&access_token={oauth_token}'
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0'
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
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            xml_data = self.buildPlaylistsXML(data, ip, port, oauth_token)
            return Response(xml_data, mimetype='text/atom+xml')

        return Response('Failed to fetch playlists', status=500)

    def buildWatchHistory2XML(self, json_data, ip, port, lang):
        viewCountLabels = {
            'en': 'views',
            'es': 'visualizaciones',
            'fr': 'vues',
            'de': 'Aufrufe',
            'ja': '回視聴',
            'nl': 'weergaven',
            'it': 'visualizzazioni'
        }
        viewCountLabel = viewCountLabels.get(lang, 'views')
        xml_string = '<?xml version="1.0" encoding="UTF-8"?>'
        xml_string += '<feed xmlns:openSearch="http://a9.com/-/spec/opensearch/1.1/" xmlns:media="http://search.yahoo.com/mrss/" xmlns:yt="http://www.youtube.com/xml/schemas/2015">'
        xml_string += '<title type="text">Videos</title>'
        xml_string += '<generator ver="1.0" uri="http://kamil.cc/">Liinback data API</generator>'
        xml_string += '<openSearch:totalResults>0</openSearch:totalResults>'
        xml_string += '<openSearch:startIndex>1</openSearch:startIndex>'
        xml_string += '<openSearch:itemsPerPage>20</openSearch:itemsPerPage>'
        for item in json_data.get("contents", {}).get("twoColumnBrowseResultsRenderer", {}).get("tabs", []):
            tab = item.get("tabRenderer", {})
            section_list = tab.get("content", {}).get("sectionListRenderer", {}).get("contents", [])

            for section in section_list:
                if "itemSectionRenderer" in section:
                    for video_item in section["itemSectionRenderer"].get("contents", []):
                        if "videoRenderer" in video_item:
                            videoData = video_item["videoRenderer"]
                            videoId = videoData.get("videoId", "")
                            title = videoData.get("title", {}).get("runs", [{}])[0].get("text", "")
                            lengthText = videoData.get("lengthText", {}).get("simpleText", "")
                            viewCount = videoData.get("viewCountText", {}).get("simpleText", "")
                            authorName = videoData.get("longBylineText", {}).get("runs", [{}])[0].get("text", "")
                            authorId = videoData.get("longBylineText", {}).get("runs", [{}])[0].get("navigationEndpoint", {}).get("browseEndpoint", {}).get("browseId", "")
                            xml_string += '<entry>'
                            xml_string += f'<id>http://{ip}:{port}/api/videos/{videoId}</id>'
                            xml_string += f'<published>null</published>'
                            xml_string += f'<title type="text">{self.escape_xml(title)}</title>'
                            xml_string += f'<link rel="http://{ip}:{port}/api/videos/{videoId}/related"/>'
                            xml_string += f'<author><name>{self.escape_xml(authorName)}</name><uri>https://www.youtube.com/channel/{authorId}</uri></author>'
                            xml_string += '<media:group>'
                            xml_string += f'<media:thumbnail yt:name="mqdefault" url="http://i.ytimg.com/vi/{videoId}/mqdefault.jpg" height="240" width="320" time="00:00:00"/>'
                            xml_string += f'<yt:duration seconds="{lengthText}"/>'
                            xml_string += f'<yt:uploaderId id="{authorId}">{authorId}</yt:uploaderId>'
                            xml_string += f'<yt:videoid id="{videoId}">{videoId}</yt:videoid>'
                            xml_string += f'<media:credit role="uploader" name="{self.escape_xml(authorName)}">{self.escape_xml(authorName)}</media:credit>'
                            xml_string += '</media:group>'
                            xml_string += f'<yt:statistics favoriteCount="0" viewCount="{self.escape_xml(viewCount)}"/>'
                            xml_string += '</entry>'

        xml_string += '</feed>'
        return xml_string

    def buildWatchHistoryXML(self, json_data, ip, port, lang, oauth_token):
        viewCountLabels = {
            'en': 'views',
            'es': 'visualizaciones',
            'fr': 'vues',
            'de': 'Aufrufe',
            'ja': '回視聴',
            'nl': 'weergaven',
            'it': 'visualizzazioni'
        }
        viewCountLabel = viewCountLabels.get(lang, 'views')
        xml_string = '<?xml version="1.0" encoding="UTF-8"?>'
        xml_string += '<feed xmlns:openSearch="http://a9.com/-/spec/opensearch/1.1/" xmlns:media="http://search.yahoo.com/mrss/" xmlns:yt="http://www.youtube.com/xml/schemas/2015">'
        xml_string += '<title type="text">Videos</title>'
        xml_string += '<generator ver="1.0" uri="http://kamil.cc/">Liinback data API</generator>'
        xml_string += '<openSearch:totalResults>0</openSearch:totalResults>'
        xml_string += '<openSearch:startIndex>1</openSearch:startIndex>'
        xml_string += '<openSearch:itemsPerPage>20</openSearch:itemsPerPage>'      
        try:
            video_items = json_data.get("contents", {}).get("twoColumnBrowseResultsRenderer", {}).get("tabs", [])
            video_list = []

            for tab in video_items:
                content = tab.get("tabRenderer", {}).get("content", {})
                section_list_renderer = content.get("sectionListRenderer", {}).get("contents", [])
                
                for section in section_list_renderer:
                    item_section = section.get("itemSectionRenderer", {}).get("contents", [])
                    
                    for item in item_section:
                        video_renderer = item.get("videoRenderer", {})
                        if not video_renderer:
                            return redirect(f'/api/v2/watch_history?access_token={oauth_token}&lang={lang}')
                        videoId = video_renderer.get("videoId", "")
                        title = video_renderer.get("title", {}).get("runs", [{}])[0].get("text", "")
                        lengthText = video_renderer.get("lengthText", {}).get("simpleText", "")
                        viewCount = video_renderer.get("viewCountText", {}).get("simpleText", "").split()[0]
                        authorName = video_renderer.get("longBylineText", {}).get("runs", [{}])[0].get("text", "")
                        authorId = video_renderer.get("channelThumbnailSupportedRenderers", {}).get("channelThumbnailWithLinkRenderer", {}).get("navigationEndpoint", {}).get("browseEndpoint", {}).get("browseId", "")
                        if not videoId or not title:
                            return redirect(f'/api/v2/watch_history?access_token={oauth_token}&lang={lang}')
                        xml_string += '<entry>'
                        xml_string += f'<id>http://{ip}:{port}/api/videos/{videoId}</id>'
                        xml_string += f'<published>null</published>'
                        xml_string += f'<title type="text">{self.escape_xml(title)}</title>'
                        xml_string += f'<link rel="http://{ip}:{port}/api/videos/{videoId}/related"/>'
                        xml_string += f'<author><name>{self.escape_xml(authorName)}</name><uri>https://www.youtube.com/channel/{authorId}</uri></author>'
                        xml_string += '<media:group>'
                        xml_string += f'<media:thumbnail yt:name="mqdefault" url="http://i.ytimg.com/vi/{videoId}/mqdefault.jpg" height="240" width="320" time="00:00:00"/>'
                        xml_string += f'<yt:duration seconds="{lengthText}"/>'
                        xml_string += f'<yt:uploaderId id="{authorId}">{authorId}</yt:uploaderId>'
                        xml_string += f'<yt:videoid id="{videoId}">{videoId}</yt:videoid>'
                        xml_string += f'<media:credit role="uploader" name="{self.escape_xml(authorName)}">{self.escape_xml(authorName)}</media:credit>'
                        xml_string += '</media:group>'
                        xml_string += f'<yt:statistics favoriteCount="0" viewCount="{self.escape_xml(viewCount)} {viewCountLabel}"/>'
                        xml_string += '</entry>'

        except Exception as e:
            print(f"Error processing JSON data: {e}")
            return redirect(f'/api/v2/watch_history?access_token={oauth_token}&lang={lang}')

        return xml_string
    def subscriptions(self, ip, port, oauth_token):
        url = f'https://www.youtube.com/youtubei/v1/browse?browseId=FEchannels&key=AIzaS=yAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8&access_token={oauth_token}'
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0'
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

        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            xml_data = self.buildSubscriptions(ip, port, oauth_token, data)
            return Response(xml_data, mimetype='text/atom+xml')

    def buildExplorerXML(self, json_data, ip, port):
        xml_string = '<?xml version="1.0" encoding="UTF-8"?>'
        xml_string += '<feed xmlns:openSearch="http://a9.com/-/spec/opensearch/1.1/" '
        xml_string += 'xmlns:media="http://search.yahoo.com/mrss/" '
        xml_string += 'xmlns:yt="http://www.youtube.com/xml/schemas/2015">'
        xml_string += f'<link rel="next" type="application/atom+xml" href="http://{ip}:{port}/api/videos"/>'
        xml_string += '<title type="text">Subscriptions</title>'
        xml_string += '<generator ver="1.0" uri="http://kamil.cc/">Liinback data API</generator>'
        xml_string += '<openSearch:totalResults>0</openSearch:totalResults>'
        xml_string += '<openSearch:startIndex>1</openSearch:startIndex>'
        xml_string += '<openSearch:itemsPerPage>20</openSearch:itemsPerPage>'
        tabs = json_data.get('contents', {}).get('twoColumnBrowseResultsRenderer', {}).get('tabs', [])
        for tab in tabs:
            tab_content = tab.get('tabRenderer', {}).get('content', {}).get('sectionListRenderer', {}).get('contents', [])
            for section in tab_content:
                if 'itemSectionRenderer' in section:
                    items = section.get('itemSectionRenderer', {}).get('contents', [])
                    for item in items:
                        if 'shelfRenderer' in item:
                            shelf_content = item.get('shelfRenderer', {}).get('content', {}).get('expandedShelfContentsRenderer', {}).get('items', [])
                            for video_item in shelf_content:
                                video_renderer = video_item.get('videoRenderer', {})
                                if video_renderer:
                                    video_id = video_renderer.get('videoId', '')
                                    title = video_renderer.get('title', {}).get('runs', [{}])[0].get('text', '')
                                    author_name = video_renderer.get('longBylineText', {}).get('runs', [{}])[0].get('text', '')
                                    author_id = video_renderer.get('longBylineText', {}).get('runs', [{}])[0].get('navigationEndpoint', {}).get('browseEndpoint', {}).get('browseId', '')
                                    published_text = video_renderer.get('publishedTimeText', {}).get('simpleText', '')
                                    length_text = video_renderer.get('lengthText', {}).get('simpleText', '')
                                    view_count = video_renderer.get('viewCountText', {}).get('simpleText', '')
                                    xml_string += '<entry>'
                                    xml_string += f'<id>http://{ip}:{port}/api/videos/{video_id}</id>'
                                    xml_string += f'<published>{self.escape_xml(published_text)}</published>'
                                    xml_string += f'<title type="text">{self.escape_xml(title)}</title>'
                                    xml_string += f'<link rel="http://{ip}:{port}/api/videos/{video_id}/related"/>'
                                    xml_string += f'<author><name>{self.escape_xml(author_name)}</name>'
                                    xml_string += f'<uri>http://{ip}:{port}/channels/{author_id}/uploads</uri></author>'
                                    xml_string += '<media:group>'
                                    xml_string += f'<media:thumbnail yt:name="mqdefault" '
                                    xml_string += f'url="http://i.ytimg.com/vi/{video_id}/mqdefault.jpg" height="240" width="320" time="00:00:00"/>'
                                    xml_string += f'<yt:duration>{self.escape_xml(length_text)}</yt:duration>'
                                    xml_string += f'<yt:uploaderId id="{author_id}">{author_id}</yt:uploaderId>'
                                    xml_string += f'<yt:videoid id="{video_id}">{video_id}</yt:videoid>'
                                    xml_string += f'<media:credit role="uploader" name="{self.escape_xml(author_name)}">{self.escape_xml(author_name)}</media:credit>'
                                    xml_string += '</media:group>'
                                    xml_string += f'<yt:statistics favoriteCount="0" viewCount="{self.escape_xml(view_count)}"/>'
                                    xml_string += '</entry>'

        xml_string += '</feed>'
        return xml_string

    def buildSubscriptions(self, ip, port, json_data, oauth_token):
        xml_string = '<?xml version="1.0" encoding="UTF-8"?>'
        xml_string += '<feed xmlns:openSearch="http://a9.com/-/spec/opensearch/1.1/" xmlns:media="http://search.yahoo.com/mrss/" xmlns:yt="http://www.youtube.com/xml/schemas/2015">'
        xml_string += f'<link>f"http://{ip}:{port}/api/subscriptions?access_token={oauth_token}"</link>'
        xml_string += '<title type="text">Subscriptions</title>'
        xml_string += f'<openSearch:totalResults></openSearch:totalResults>'
        xml_string += '<generator ver="1.0" uri="http://kamil.cc/">Liinback data API</generator>'
        xml_string += '<openSearch:startIndex>1</openSearch:startIndex>'
        xml_string += '<openSearch:itemsPerPage>20</openSearch:itemsPerPage>'
        
        for item in json_data.get('contents', {}).get('twoColumnBrowseResultsRenderer', {}).get('tabs', []):
            tab_content = item.get('tabRenderer', {}).get('content', {}).get('sectionListRenderer', {}).get('contents', [])
            for section in tab_content:
                if 'itemSectionRenderer' in section:
                    channel_data = section.get('itemSectionRenderer', {}).get('contents', [])
                    for channel in channel_data:
                        if 'shelfRenderer' in channel:
                            channel_info = channel.get('shelfRenderer', {}).get('content', {}).get('expandedShelfContentsRenderer', {}).get('items', [])
                            for channel_item in channel_info:
                                channel_renderer = channel_item.get('channelRenderer', {})
                                if channel_renderer:
                                    author_name = channel_renderer.get('title', {}).get('simpleText', '')
                                    author_id = channel_renderer.get('channelId', '')
                                    xml_string += '<entry>'
                                    xml_string += f'<yt:username>{self.escape_xml(author_name)}</yt:username>'
                                    xml_string += f'<yt:channelId>{self.escape_xml(author_id)}</yt:channelId>'
                                    xml_string += '</entry>'
        
        xml_string += '</feed>'
        return xml_string

    @staticmethod
    def buildCategoryThreeXML(json_data, ip, port):
        xml_string = '<?xml version="1.0" encoding="UTF-8"?>'
        xml_string += '<feed xmlns:openSearch="http://a9.com/-/spec/opensearch/1.1/" xmlns:media="http://search.yahoo.com/mrss/" xmlns:yt="http://www.youtube.com/xml/schemas/2015">'
        xml_string += '<title type="text">Videos</title>'
        xml_string += '<generator ver="1.0" uri="http://kamil.cc/">Liinback data API</generator>'
        xml_string += '<openSearch:totalResults>0</openSearch:totalResults>'
        xml_string += '<openSearch:startIndex>1</openSearch:startIndex>'
        xml_string += '<openSearch:itemsPerPage>20</openSearch:itemsPerPage>'
        for item in json_data.get("contents", {}).get("twoColumnBrowseResultsRenderer", {}).get("tabs", []):
            tab = item.get("tabRenderer", {})
            section_list = tab.get("content", {}).get("richGridRenderer", {}).get("contents", [])

            for section in section_list:
                if "richSectionRenderer" in section:
                    video_data = section["richSectionRenderer"].get("content", {}).get("richShelfRenderer", {}).get("contents", [{}])[0].get("richItemRenderer", {}).get("content", {}).get("videoRenderer", {})
                    video_id = video_data.get("videoId", "")
                    title = video_data.get("title", {}).get("runs", [{}])[0].get("text", "")
                    length_text = video_data.get("lengthText", {}).get("simpleText", "")
                    author_name = video_data.get("longBylineText", {}).get("runs", [{}])[0].get("text", "")
                    published_text = video_data.get("publishedTimeText", {}).get("simpleText", "")
                    author_id = video_data.get("longBylineText", {}).get("runs", [{}])[0].get("navigationEndpoint", {}).get("browseEndpoint", {}).get("browseId", "")
                    view_count = video_data.get("viewCountText", {}).get("simpleText", "")
                    xml_string += '<entry>'
                    xml_string += f'<id>http://{ip}:{port}/api/videos/{video_id}</id>'
                    xml_string += f'<published>{InnerTube.escape_xml(published_text)}</published>'
                    xml_string += f'<title type="text">{InnerTube.escape_xml(title)}</title>'
                    xml_string += f'<link rel="http://{ip}:{port}/api/videos/{video_id}/related"/>'
                    xml_string += f'<author><name>{InnerTube.escape_xml(author_name)}</name><uri>https://www.youtube.com/channel/{author_id}</uri></author>'
                    xml_string += '<media:group>'
                    xml_string += f'<media:thumbnail yt:name="mqdefault" url="http://i.ytimg.com/vi/{video_id}/mqdefault.jpg" height="240" width="320" time="00:00:00"/>'
                    xml_string += f'<yt:duration>{InnerTube.escape_xml(length_text)}</yt:duration>'
                    xml_string += f'<yt:uploaderId id="{author_id}">{author_id}</yt:uploaderId>'
                    xml_string += f'<yt:videoid id="{video_id}">{video_id}</yt:videoid>'
                    xml_string += f'<media:credit role="uploader" name="{InnerTube.escape_xml(author_name)}">{InnerTube.escape_xml(author_name)}</media:credit>'
                    xml_string += '</media:group>'
                    xml_string += f'<yt:statistics favoriteCount="0" viewCount="{InnerTube.escape_xml(view_count)}"/>'
                    xml_string += '</entry>'

        xml_string += '</feed>'
        return xml_string
        
    @staticmethod
    def buildCategoryThreeM3U(json_data, ip, port):
        m3u_content = "#EXTM3U\n"
        for item in json_data.get("contents", {}).get("twoColumnBrowseResultsRenderer", {}).get("tabs", []):
            tab = item.get("tabRenderer", {})
            section_list = tab.get("content", {}).get("richGridRenderer", {}).get("contents", [])

            for section in section_list:
                if "richSectionRenderer" in section:
                    video_data = section["richSectionRenderer"].get("content", {}).get("richShelfRenderer", {}).get("contents", [{}])[0].get("richItemRenderer", {}).get("content", {}).get("videoRenderer", {})
                    video_id = video_data.get("videoId", "")
                    title = video_data.get("title", {}).get("runs", [{}])[0].get("text", "")
                    thumbnail_url = f"http://i.ytimg.com/vi/{video_id}/mqdefault.jpg"
                    get_video = f"http://{ip}:{port}/api/v2/videos/get/{video_id}"
                    m3u_content += f"#EXTINF:-1,{title}\n{thumbnail_url}\n{get_video}\n"
        return m3u_content

    @staticmethod
    def buildRiverXML(json_data, ip, port):
        xml_string = '<?xml version="1.0" encoding="UTF-8"?>'
        xml_string += '<feed xmlns:openSearch="http://a9.com/-/spec/opensearch/1.1/" xmlns:media="http://search.yahoo.com/mrss/" xmlns:yt="http://www.youtube.com/xml/schemas/2015">'
        xml_string += '<title type="text">Videos</title>'
        xml_string += '<generator ver="1.0" uri="http://kamil.cc/">Liinback data API</generator>'
        xml_string += '<openSearch:totalResults>0</openSearch:totalResults>'
        xml_string += '<openSearch:startIndex>1</openSearch:startIndex>'
        xml_string += '<openSearch:itemsPerPage>20</openSearch:itemsPerPage>'
        
        for item in json_data.get("contents", {}).get("twoColumnBrowseResultsRenderer", {}).get("tabs", []):
            tab = item.get("tabRenderer", {})
            section_list = tab.get("content", {}).get("richGridRenderer", {}).get("contents", [])
            
            for section in section_list:
                if "richItemRenderer" in section:
                    video_data = section["richItemRenderer"].get("content", {}).get("videoRenderer", {})                    
                    video_id = video_data.get("videoId", "")
                    length_text = video_data.get("lengthText", {}).get("simpleText", "")
                    author_name = video_data.get("longBylineText", {}).get("runs", [{}])[0].get("text", "")
                    published_text = video_data.get("publishedTimeText", {}).get("simpleText", "")
                    author_id = video_data.get("longBylineText", {}).get("runs", [{}])[0].get("navigationEndpoint", {}).get("browseEndpoint", {}).get("browseId", "")
                    title = video_data.get("title", {}).get("runs", [{}])[0].get("text", "")
                    view_count = video_data.get("viewCountText", {}).get("simpleText", "")
                    xml_string += '<entry>'
                    xml_string += f'<id>http://{ip}:{port}/api/videos/{video_id}</id>'
                    xml_string += f'<published>{InnerTube.escape_xml(published_text)}</published>'
                    xml_string += f'<title type="text">{InnerTube.escape_xml(title)}</title>'
                    xml_string += f'<link rel="http://{ip}:{port}/api/videos/{video_id}/related"/>'
                    xml_string += f'<author><name>{InnerTube.escape_xml(author_name)}</name><uri>https://www.youtube.com/channel/{author_id}</uri></author>'
                    xml_string += '<media:group>'
                    xml_string += f'<media:thumbnail yt:name="mqdefault" url="http://i.ytimg.com/vi/{video_id}/mqdefault.jpg" height="240" width="320" time="00:00:00"/>'
                    xml_string += f'<yt:duration seconds="{length_text}"/>'
                    xml_string += f'<yt:uploaderId id="{author_id}">{author_id}</yt:uploaderId>'
                    xml_string += f'<yt:videoid id="{video_id}">{video_id}</yt:videoid>'
                    xml_string += f'<media:credit role="uploader" name="{InnerTube.escape_xml(author_name)}">{InnerTube.escape_xml(author_name)}</media:credit>'
                    xml_string += '</media:group>'
                    xml_string += f'<yt:statistics favoriteCount="0" viewCount="{InnerTube.escape_xml(view_count)}"/>'
                    xml_string += '</entry>'        
        xml_string += '</feed>'
        return xml_string
        
    def buildCategoryXML(self, json_data, ip, port):
        xml_string = '<?xml version="1.0" encoding="UTF-8"?>'
        xml_string += '<feed xmlns:openSearch="http://a9.com/-/spec/opensearch/1.1/" xmlns:media="http://search.yahoo.com/mrss/" xmlns:yt="http://www.youtube.com/xml/schemas/2015">'
        xml_string += '<title type="text">Videos</title>'
        xml_string += '<generator ver="1.0" uri="http://kamil.cc/">Liinback data API</generator>'
        xml_string += '<openSearch:totalResults>0</openSearch:totalResults>'
        xml_string += '<openSearch:startIndex>1</openSearch:startIndex>'
        xml_string += '<openSearch:itemsPerPage>20</openSearch:itemsPerPage>'
        for item in json_data.get("contents", {}).get("twoColumnBrowseResultsRenderer", {}).get("tabs", []):
            tab = item.get("tabRenderer", {})
            section_list = tab.get("content", {}).get("sectionListRenderer", {}).get("contents", [])
            for section in section_list:
                if "itemSectionRenderer" in section:
                    for video_item in section["itemSectionRenderer"].get("contents", []):
                        if "shelfRenderer" in video_item:
                            shelf_renderer = video_item['shelfRenderer']
                            horizontal_list = shelf_renderer.get('content', {}).get('expandedShelfContentsRenderer', {}).get('items', [])
                            for horizontal_item in horizontal_list:
                                if "videoRenderer" in horizontal_item:
                                    video_data = horizontal_item["videoRenderer"]
                                    video_id = video_data.get("videoId", "")
                                    title = video_data.get("title", {}).get("runs", [{}])[0].get("text", "")
                                    length_text = video_data.get("lengthText", {}).get("simpleText", "")
                                    view_count = video_data.get("viewCountText", {}).get("simpleText", "")
                                    author_name = video_data.get("longBylineText", {}).get("runs", [{}])[0].get("text", "")
                                    author_id = video_data.get("longBylineText", {}).get("runs", [{}])[0].get("navigationEndpoint", {}).get("browseEndpoint", {}).get("browseId", "")
                                    published_text = video_data.get("publishedTimeText", {}).get("simpleText", "")
                                    xml_string += '<entry>'
                                    xml_string += f'<id>http://{ip}:{port}/api/videos/{video_id}</id>'
                                    xml_string += f'<published>{self.escape_xml(published_text)}</published>'
                                    xml_string += f'<title type="text">{self.escape_xml(title)}</title>'
                                    xml_string += f'<link rel="http://{ip}:{port}/api/videos/{video_id}/related"/>'
                                    xml_string += f'<author><name>{self.escape_xml(author_name)}</name><uri>https://www.youtube.com/channel/{author_id}</uri></author>'
                                    xml_string += '<media:group>'
                                    xml_string += f'<media:thumbnail yt:name="mqdefault" url="http://i.ytimg.com/vi/{video_id}/mqdefault.jpg" height="240" width="320" time="00:00:00"/>'
                                    xml_string += f'<yt:duration seconds="{length_text}"/>'
                                    xml_string += f'<yt:uploaderId id="{author_id}">{author_id}</yt:uploaderId>'
                                    xml_string += f'<yt:videoid id="{video_id}">{video_id}</yt:videoid>'
                                    xml_string += f'<media:credit role="uploader" name="{self.escape_xml(author_name)}">{self.escape_xml(author_name)}</media:credit>'
                                    xml_string += '</media:group>'
                                    xml_string += f'<yt:statistics favoriteCount="0" viewCount="{self.escape_xml(view_count)}"/>'
                                    xml_string += '</entry>'
        xml_string += '</feed>'
        return xml_string
    @staticmethod    
    def buildCategoryM3U(json_data, ip, port):
        m3u_content = "#EXTM3U\n"
        for item in json_data.get("contents", {}).get("twoColumnBrowseResultsRenderer", {}).get("tabs", []):
            tab = item.get("tabRenderer", {})
            section_list = tab.get("content", {}).get("sectionListRenderer", {}).get("contents", [])
            for section in section_list:
                if "itemSectionRenderer" in section:
                    for video_item in section["itemSectionRenderer"].get("contents", []):
                        if "shelfRenderer" in video_item:
                            shelf_renderer = video_item['shelfRenderer']
                            horizontal_list = shelf_renderer.get('content', {}).get('expandedShelfContentsRenderer', {}).get('items', [])
                            for horizontal_item in horizontal_list:
                                if "videoRenderer" in horizontal_item:
                                    video_data = horizontal_item["videoRenderer"]
                                    video_id = video_data.get("videoId", "")
                                    title = video_data.get("title", {}).get("runs", [{}])[0].get("text", "")
                                    thumbnail_url = f"http://i.ytimg.com/vi/{video_id}/mqdefault.jpg"
                                    get_video = f"http://{ip}:{port}/api/v2/videos/{video_id}"
                                    m3u_content += f"#EXTINF:-1,{title}\n{thumbnail_url}\n{get_video}\n"
        return m3u_content        
        
    def buildCategoryTwoXML(self, json_data, ip, port):
        xml_string = '<?xml version="1.0" encoding="UTF-8"?>'
        xml_string += '<feed xmlns:openSearch="http://a9.com/-/spec/opensearch/1.1/" xmlns:media="http://search.yahoo.com/mrss/" xmlns:yt="http://www.youtube.com/xml/schemas/2015">'
        xml_string += '<title type="text">Videos</title>'
        xml_string += '<generator ver="1.0" uri="http://kamil.cc/">Liinback data API</generator>'
        xml_string += '<openSearch:totalResults>0</openSearch:totalResults>'
        xml_string += '<openSearch:startIndex>1</openSearch:startIndex>'
        xml_string += '<openSearch:itemsPerPage>20</openSearch:itemsPerPage>'
        for item in json_data.get("contents", {}).get("twoColumnBrowseResultsRenderer", {}).get("tabs", []):
            tab = item.get("tabRenderer", {})
            section_list = tab.get("content", {}).get("sectionListRenderer", {}).get("contents", [])
            for section in section_list:
                if "itemSectionRenderer" in section:
                    for video_item in section["itemSectionRenderer"].get("contents", []):
                        if "shelfRenderer" in video_item:
                            shelf_renderer = video_item['shelfRenderer']
                            horizontal_list = shelf_renderer.get('content', {}).get('horizontalListRenderer', {}).get('items', [])
                            for horizontal_item in horizontal_list:
                                if "gridVideoRenderer" in horizontal_item:
                                    video_data = horizontal_item["gridVideoRenderer"]
                                    video_id = video_data.get("videoId", "")
                                    title = video_data.get("title", {}).get("simpleText", "")
                                    author_name = video_data.get("shortBylineText", {}).get("runs", [{}])[0].get("text", "")
                                    author_id = video_data.get("shortBylineText", {}).get("runs", [{}])[0].get("navigationEndpoint", {}).get("browseEndpoint", {}).get("browseId", "")
                                    published_text = video_data.get("publishedTimeText", {}).get("simpleText", "")
                                    view_count = video_data.get("viewCountText", {}).get("simpleText", "")
                                    playerUrl = f"https://www.youtube.com/youtubei/v1/player?key=AIzaS=yAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8&videoId={video_id}"
                                    headers = {
                                        'Content-Type': 'application/json',
                                        'User-Agent': 'Mozilla/5.0'
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
                                        "videoId": video_id,
                                        "params": ""
                                    }
                                    response = requests.post(playerUrl, json=payload, headers=headers)
                                    if response.status_code == 200:
                                        _jsonData = response.json()
                                        length_text = _jsonData.get('videoDetails', {}).get('lengthSeconds', '')
                                    xml_string += '<entry>'
                                    xml_string += f'<id>http://{ip}:{port}/api/videos/{video_id}</id>'
                                    xml_string += f'<published>{self.escape_xml(published_text)}</published>'
                                    xml_string += f'<title type="text">{self.escape_xml(title)}</title>'
                                    xml_string += f'<link rel="http://{ip}:{port}/api/videos/{video_id}/related"/>'
                                    xml_string += f'<author><name>{self.escape_xml(author_name)}</name><uri>https://www.youtube.com/channel/{author_id}</uri></author>'
                                    xml_string += '<media:group>'
                                    xml_string += f'<media:thumbnail yt:name="mqdefault" url="http://i.ytimg.com/vi/{video_id}/mqdefault.jpg" height="240" width="320" time="00:00:00"/>'
                                    xml_string += f'<yt:duration>{self.escape_xml(length_text)}</yt:duration>'
                                    xml_string += f'<yt:uploaderId id="{author_id}">{author_id}</yt:uploaderId>'
                                    xml_string += f'<yt:videoid id="{video_id}">{video_id}</yt:videoid>'
                                    xml_string += f'<media:credit role="uploader" name="{self.escape_xml(author_name)}">{self.escape_xml(author_name)}</media:credit>'
                                    xml_string += '</media:group>'
                                    xml_string += f'<yt:statistics favoriteCount="0" viewCount="{self.escape_xml(view_count)}"/>'
                                    xml_string += '</entry>'   
        xml_string += '</feed>'
        return xml_string
        
    @staticmethod
    def buildCategoryTwoM3U(json_data, ip, port):
        m3u_content = "#EXTM3U\n"
        for item in json_data.get("contents", {}).get("twoColumnBrowseResultsRenderer", {}).get("tabs", []):
            tab = item.get("tabRenderer", {})
            section_list = tab.get("content", {}).get("sectionListRenderer", {}).get("contents", [])
            for section in section_list:
                if "itemSectionRenderer" in section:
                    for video_item in section["itemSectionRenderer"].get("contents", []):
                        if "shelfRenderer" in video_item:
                            shelf_renderer = video_item['shelfRenderer']
                            horizontal_list = shelf_renderer.get('content', {}).get('horizontalListRenderer', {}).get('items', [])
                            for horizontal_item in horizontal_list:
                                if "gridVideoRenderer" in horizontal_item:
                                    video_data = horizontal_item["gridVideoRenderer"]
                                    video_id = video_data.get("videoId", "")
                                    title = video_data.get("title", {}).get("simpleText", "")
                                    player_url = f"https://www.youtube.com/youtubei/v1/player?key=AIzaS=yAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8&videoId={video_id}"
                                    headers = {
                                        'Content-Type': 'application/json',
                                        'User-Agent': 'Mozilla/5.0'
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
                                        "videoId": video_id,
                                        "params": ""
                                    }
                                    response = requests.post(player_url, json=payload, headers=headers)
                                    if response.status_code == 200:
                                        _json_data = response.json()
                                        length_text = _json_data.get('videoDetails', {}).get('lengthSeconds', '')
                                    thumbnail_url = f"http://i.ytimg.com/vi/{video_id}/mqdefault.jpg"
                                    get_video = f"http://{ip}:{port}/api/v2/videos/{video_id}"
                                    m3u_content += f"#EXTINF:-1,{title}\n{thumbnail_url}\n{get_video}\n"
        return m3u_content

    def buildUploadsXML(self, json_data, ip, port):
        xml_string = '<?xml version="1.0" encoding="UTF-8"?>'
        xml_string += '<feed xmlns:openSearch="http://a9.com/-/spec/opensearch/1.1/" xmlns:media="http://search.yahoo.com/mrss/" xmlns:yt="http://www.youtube.com/xml/schemas/2015">'
        xml_string += '<title type="text">Videos</title>'
        xml_string += '<generator ver="1.0" uri="http://kamil.cc/">Liinback data API</generator>'
        xml_string += '<openSearch:totalResults>0</openSearch:totalResults>'
        xml_string += '<openSearch:startIndex>1</openSearch:startIndex>'
        xml_string += '<openSearch:itemsPerPage>20</openSearch:itemsPerPage>'

        for item in json_data.get("contents", {}).get("twoColumnBrowseResultsRenderer", {}).get("tabs", []):
            tab = item.get("tabRenderer", {})
            section_list = tab.get("content", {}).get("sectionListRenderer", {}).get("contents", [])

            for section in section_list:
                if "itemSectionRenderer" in section:
                    for video_item in section["itemSectionRenderer"].get("contents", []):
                        if "shelfRenderer" in video_item:
                            # Extract video data from the provided structure
                            grid_video = video_item["shelfRenderer"]["content"].get("horizontalListRenderer", {}).get("items", [])

                            for video_data in grid_video:
                                video = video_data.get("gridVideoRenderer", {})
                                videoId = video.get("videoId", "")
                                title = video.get("title", {}).get("simpleText", "")
                                lengthText = video.get("lengthText", {}).get("simpleText", "")
                                viewCount = video.get("viewCountText", {}).get("simpleText", "")
                                authorName = video.get("ownerBadges", [{}])[0].get("metadataBadgeRenderer", {}).get("accessibilityData", {}).get("label", "")
                                authorId = video.get("navigationEndpoint", {}).get("watchEndpoint", {}).get("videoId", "")

                                xml_string += '<entry>'
                                xml_string += f'<id>http://{ip}:{port}/api/videos/{videoId}</id>'
                                xml_string += '<published></published>'
                                xml_string += f'<title type="text">{self.escape_xml(title)}</title>'
                                xml_string += f'<link rel="http://{ip}:{port}/api/videos/{videoId}/related"/>'
                                xml_string += f'<author><name>{self.escape_xml(authorName)}</name><uri>https://www.youtube.com/channel/{authorId}</uri></author>'
                                xml_string += '<media:group>'
                                xml_string += f'<media:thumbnail yt:name="mqdefault" url="http://i.ytimg.com/vi/{videoId}/mqdefault.jpg" height="240" width="320" time="00:00:00"/>'
                                xml_string += f'<yt:duration seconds="{lengthText}"/>'
                                xml_string += f'<yt:uploaderId id="{authorId}">{authorId}</yt:uploaderId>'
                                xml_string += f'<yt:videoid id="{videoId}">{videoId}</yt:videoid>'
                                xml_string += f'<media:credit role="uploader" name="{self.escape_xml(authorName)}">{self.escape_xml(authorName)}</media:credit>'
                                xml_string += '</media:group>'
                                xml_string += f'<yt:statistics favoriteCount="0" viewCount="{self.escape_xml(viewCount)}"/>'
                                xml_string += '</entry>'

        xml_string += '</feed>'
        return xml_string

    def buildXML(self, json_data, ip, port):
        xml_string = '<?xml version="1.0" encoding="UTF-8"?>'
        xml_string += '<feed xmlns:openSearch="http://a9.com/-/spec/opensearch/1.1/" xmlns:media="http://search.yahoo.com/mrss/" xmlns:yt="http://www.youtube.com/xml/schemas/2015">'
        xml_string += '<title type="text">Videos</title>'
        xml_string += '<generator ver="1.0" uri="http://kamil.cc/">Liinback data API</generator>'
        xml_string += '<openSearch:totalResults>0</openSearch:totalResults>'
        xml_string += '<openSearch:startIndex>1</openSearch:startIndex>'
        xml_string += '<openSearch:itemsPerPage>20</openSearch:itemsPerPage>'

        for item in json_data.get("contents", {}).get("twoColumnBrowseResultsRenderer", {}).get("tabs", []):
            tab = item.get("tabRenderer", {})
            section_list = tab.get("content", {}).get("sectionListRenderer", {}).get("contents", [])

            for section in section_list:
                if "itemSectionRenderer" in section:
                    for video_item in section["itemSectionRenderer"].get("contents", []):
                        if "videoRenderer" in video_item:
                            videoData = video_item["videoRenderer"]
                            videoId = videoData.get("videoId", "")
                            title = videoData.get("title", {}).get("runs", [{}])[0].get("text", "")
                            lengthText = videoData.get("lengthText", {}).get("simpleText", "")
                            viewCount = videoData.get("viewCountText", {}).get("simpleText", "")
                            authorName = videoData.get("longBylineText", {}).get("runs", [{}])[0].get("text", "")
                            authorId = videoData.get("longBylineText", {}).get("runs", [{}])[0].get("navigationEndpoint", {}).get("browseEndpoint", {}).get("browseId", "")
                            xml_string += '<entry>'
                            xml_string += f'<id>http://{ip}:{port}/api/videos/{videoId}</id>'
                            xml_string += '<published></published>'
                            xml_string += f'<title type="text">{self.escape_xml(title)}</title>'
                            xml_string += f'<link rel="http://{ip}:{port}/api/videos/{videoId}/related"/>'
                            xml_string += f'<author><name>{self.escape_xml(authorName)}</name><uri>https://www.youtube.com/channel/{authorId}</uri></author>'
                            xml_string += '<media:group>'
                            xml_string += f'<media:thumbnail yt:name="mqdefault" url="http://i.ytimg.com/vi/{videoId}/mqdefault.jpg" height="240" width="320" time="00:00:00"/>'
                            xml_string += f'<yt:duration seconds="{lengthText}"/>'
                            xml_string += f'<yt:uploaderId id="{authorId}">{authorId}</yt:uploaderId>'
                            xml_string += f'<yt:videoid id="{videoId}">{videoId}</yt:videoid>'
                            xml_string += f'<media:credit role="uploader" name="{self.escape_xml(authorName)}">{self.escape_xml(authorName)}</media:credit>'
                            xml_string += '</media:group>'
                            xml_string += f'<yt:statistics favoriteCount="0" viewCount="{self.escape_xml(viewCount)}"/>'
                            xml_string += '</entry>'

        xml_string += '</feed>'
        return xml_string
        
    def buildSearchXML(self, json_data, ip, port):
        xml_string = '<?xml version="1.0" encoding="UTF-8"?>'
        xml_string += '<feed xmlns:openSearch="http://a9.com/-/spec/opensearch/1.1/" xmlns:media="http://search.yahoo.com/mrss/" xmlns:yt="http://www.youtube.com/xml/schemas/2015">'
        xml_string += '<title type="text">Videos</title>'
        xml_string += '<generator ver="1.0" uri="http://kamil.cc/">Liinback data API</generator>'
        xml_string += '<openSearch:totalResults>0</openSearch:totalResults>'
        xml_string += '<openSearch:startIndex>1</openSearch:startIndex>'
        xml_string += '<openSearch:itemsPerPage>20</openSearch:itemsPerPage>'

        for section in json_data.get("contents", {}).get("twoColumnSearchResultsRenderer", {}).get("primaryContents", {}).get("sectionListRenderer", {}).get("contents", []):
            if "itemSectionRenderer" in section:
                for video_item in section["itemSectionRenderer"].get("contents", []):
                    if "videoRenderer" in video_item:
                        videoData = video_item["videoRenderer"]
                        videoId = videoData.get("videoId", "")
                        title = videoData.get("title", {}).get("runs", [{}])[0].get("text", "")
                        lengthText = videoData.get("lengthText", {}).get("simpleText", "")
                        viewCount = videoData.get("viewCountText", {}).get("simpleText", "")
                        publishedText = videoData.get("publishedTimeText", {}).get("simpleText", "")
                        authorName = videoData.get("longBylineText", {}).get("runs", [{}])[0].get("text", "")
                        authorId = videoData.get("longBylineText", {}).get("runs", [{}])[0].get("navigationEndpoint", {}).get("browseEndpoint", {}).get("browseId", "")
                        
                        xml_string += '<entry>'
                        xml_string += f'<id>http://{ip}:{port}/api/videos/{videoId}</id>'
                        xml_string += f'<published>{self.escape_xml(publishedText)}</published>'
                        xml_string += f'<title type="text">{self.escape_xml(title)}</title>'
                        xml_string += f'<link rel="http://{ip}:{port}/api/videos/{videoId}/related"/>'
                        xml_string += f'<author><name>{self.escape_xml(authorName)}</name><uri>https://www.youtube.com/channel/{authorId}</uri></author>'
                        xml_string += '<media:group>'
                        xml_string += f'<media:thumbnail yt:name="mqdefault" url="http://i.ytimg.com/vi/{videoId}/mqdefault.jpg" height="240" width="320" time="00:00:00"/>'
                        xml_string += f'<yt:duration seconds="{lengthText}"/>'
                        xml_string += f'<yt:uploaderId id="{authorId}">{authorId}</yt:uploaderId>'
                        xml_string += f'<yt:videoid id="{videoId}">{videoId}</yt:videoid>'
                        xml_string += f'<media:credit role="uploader" name="{self.escape_xml(authorName)}">{self.escape_xml(authorName)}</media:credit>'
                        xml_string += '</media:group>'
                        xml_string += f'<yt:statistics favoriteCount="0" viewCount="{self.escape_xml(viewCount)}"/>'
                        xml_string += '</entry>'

        xml_string += '</feed>'
        return xml_string
        
    def buildSearchM3U(self, json_data, ip, port):
        m3u_content = "#EXTM3U\n"
        for section in json_data.get("contents", {}).get("twoColumnSearchResultsRenderer", {}).get("primaryContents", {}).get("sectionListRenderer", {}).get("contents", []):
            if "itemSectionRenderer" in section:
                for video_item in section["itemSectionRenderer"].get("contents", []):
                    if "videoRenderer" in video_item:
                        videoData = video_item["videoRenderer"]
                        videoId = videoData.get("videoId", "")
                        title = videoData.get("title", {}).get("runs", [{}])[0].get("text", "")
                        thumbnailUrl = f"http://i.ytimg.com/vi/{videoId}/mqdefault.jpg"
                        getVideo = f"http://{ip}:{port}/api/v2/videos/get/{videoId}"
                        m3u_content += f"#EXTINF:-1,{title}\n{thumbnailUrl}\n{getVideo}\n"
        return m3u_content

    def buildVideoInfoXML(self, json_data, ip, port, lang):
        viewCountLabels = {
            'en': 'views',
            'es': 'visualizaciones',
            'fr': 'vues',
            'de': 'Aufrufe',
            'ja': '回視聴',
            'nl': 'weergaven',
            'it': 'visualizzazioni'
        }
        xml_string = '<?xml version="1.0" encoding="UTF-8"?>'
        xml_string += '<feed xmlns:openSearch="http://a9.com/-/spec/opensearch/1.1/" xmlns:media="http://search.yahoo.com/mrss/" xmlns:yt="http://www.youtube.com/xml/schemas/2015">'
        xml_string += '<title type="text">Videos</title>'
        xml_string += '<generator ver="1.0" uri="http://kamil.cc/">Liinback data API</generator>'
        xml_string += '<openSearch:totalResults>0</openSearch:totalResults>'
        xml_string += '<openSearch:startIndex>1</openSearch:startIndex>'
        xml_string += '<openSearch:itemsPerPage>20</openSearch:itemsPerPage>'
        viewCountLabel = viewCountLabels.get(lang, 'views')
        title = json_data['videoDetails']['title']
        lengthText = json_data['videoDetails']['lengthSeconds']
        viewCount = json_data['videoDetails']['viewCount']
        authorName = json_data['videoDetails']['author']
        authorId = json_data.get('annotations', [])
        if authorId:
            authorId = authorId[0]['playerAnnotationsExpandedRenderer']['featuredChannel']['navigationEndpoint']['browseEndpoint']['browseId']
        publishedDate = json_data['microformat']['playerMicroformatRenderer']['uploadDate']
        videoId = json_data['videoDetails']['videoId']
        xml_string += '<entry>'
        xml_string += f'<id>http://{ip}:{port}/api/videos/{videoId}</id>'
        xml_string += f'<published>{self.escape_xml(publishedDate)}</published>'
        xml_string += f'<title type="text">{self.escape_xml(title)}</title>'
        xml_string += f'<link rel="http://{ip}:{port}/api/videos/{videoId}/related"/>'
        xml_string += f'<author><name>{self.escape_xml(authorName)}</name><uri>https://www.youtube.com/channel/{authorId}</uri></author>'
        xml_string += '<media:group>'
        xml_string += f'<media:thumbnail yt:name="mqdefault" url="http://i.ytimg.com/vi/{videoId}/mqdefault.jpg" height="240" width="320" time="00:00:00"/>'
        xml_string += f'<yt:duration seconds="{lengthText}"/>'
        xml_string += f'<yt:uploaderId id="{authorId}">{authorId}</yt:uploaderId>'
        xml_string += f'<yt:videoid id="{videoId}">{videoId}</yt:videoid>'
        xml_string += f'<media:credit role="uploader" name="{self.escape_xml(authorName)}">{self.escape_xml(authorName)}</media:credit>'
        xml_string += '</media:group>'
        xml_string += f'<yt:statistics favoriteCount="0" viewCount="{self.escape_xml(viewCount)} {viewCountLabel}"/>'
        xml_string += '</entry>'

        xml_string += '</feed>'
        return xml_string

    def send_response(self, xml_data):
        return Response(xml_data, mimetype='application/xml')



    def watchHistory(self, ip, port, lang, oauth_token):
        url = f'https://www.youtube.com/youtubei/v1/browse?browseId=FEhistory&key=AIzaS=yAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8&access_token={oauth_token}'
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0'
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

        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            xml_data = self.buildWatchHistoryXML(data, ip, port, lang, oauth_token)
            return Response(xml_data, mimetype='text/atom+xml')
            
    def watchHistory2(self, ip, port, lang, oauth_token):
        url = f'https://www.youtube.com/youtubei/v1/browse?browseId=FEhistory&key=AIzaS=yAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8&access_token={oauth_token}'
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0'
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

        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            xml_data = self.buildWatchHistory2XML(data, ip, port, lang)
            return Response(xml_data, mimetype='text/atom+xml')

    def river(self, ip, port, oauth_token, lang):
        url = f'https://www.youtube.com/youtubei/v1/browse?browseId=FEwhat_to_watch&key=AIzaS=yAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8'
        if oauth_token:
            url += f'&access_token={oauth_token}'
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0'
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

        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            xml_data = self.buildRiverXML(data, ip, port)
            return Response(xml_data, mimetype='text/atom+xml')

    def watchLater(self, ip, port, lang, oauth_token):
        url = f'https://www.youtube.com/youtubei/v1/browse?browseId=VLWL&key=AIzaS=yAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8&access_token={oauth_token}'
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0'
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

        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            xml_data = self.buildPlaylistXML(data, ip, port)
            return Response(xml_data, mimetype='text/atom+xml')
            
    def likedVideos(self, ip, port, oauth_token, lang):
        url = f'https://www.youtube.com/youtubei/v1/browse?browseId=VLLL&key=AIzaS=yAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8&access_token={oauth_token}'
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0'
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

        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            xml_data = self.buildPlaylistXML(data, ip, port)
            return Response(xml_data, mimetype='text/atom+xml')

    def player(self, ip, port, video_id, lang, oauth_token):
        url = f'https://www.youtube.com/youtubei/v1/player?key=AIzaS=yAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8&videoId={video_id}'
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0'
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
        
        if oauth_token:
            url += f'&access_token={oauth_token}'
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            xml_data = self.buildVideoInfoXML(data, ip, port, lang)
            return Response(xml_data, mimetype='text/atom+xml')

    def searchV3(self, ip, port, query):
        url = f'https://www.youtube.com/youtubei/v1/search?key=AIzaS=yAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8&query={query}'
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0'
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

        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            m3u_data = self.buildSearchM3U(data, ip, port)
            return Response(m3u_data, mimetype='text/plain')
            
    def search(self, ip, port, query, lang):
        url = f'https://www.youtube.com/youtubei/v1/search?key=AIzaS=yAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8&query={query}'
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0'
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

        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            xml_data = self.buildSearchXML(data, ip, port)
            return Response(xml_data, mimetype='text/atom+xml')
            
    def userUploads(self, ip, port, lang, channelId):
        url = f'https://www.youtube.com/youtubei/v1/browse?browseId={channelId}&key=AIzaS=yAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8'
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0'
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

        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            xml_data = self.buildUploadsXML(data, ip, port)
            return Response(xml_data, mimetype='text/atom+xml')

    def favorites(self, ip, port, lang, oauth_token):
        url = f'https://www.youtube.com/youtubei/v1/browse?browseId=FElibrary&key=AIzaS=yAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8&access_token={oauth_token}'
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0'
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
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            favoritesId = None
            for item in data.get("contents", {}).get("twoColumnBrowseResultsRenderer", {}).get("tabs", []):
                tab = item.get("tabRenderer", {})
                section_list = tab.get("content", {}).get("sectionListRenderer", {}).get("contents", [])                
                for section in section_list:
                    if "itemSectionRenderer" in section:
                        for video_item in section["itemSectionRenderer"].get("contents", []):
                            if "playlistVideoListRenderer" in video_item:
                                for video in video_item["playlistVideoListRenderer"].get("contents", []):
                                    if "playlistVideoRenderer" in video:
                                        videoData = video["playlistVideoRenderer"]
                                        title = videoData.get("title", {}).get("runs", [{}])[0].get("text", "")
                                        if title == "Favorites":
                                            favoritesId = videoData.get("playlistId", "")
                                            break
                                if favoritesId:
                                    break
                        if favoritesId:
                            break
                if favoritesId:
                    break
            if favoritesId:
                xml_data = self.buildPlaylistXML(favoritesId, ip, port)
                return Response(xml_data, mimetype='text/atom+xml')
            else:
                return {"error": "Favorites playlist not found."}, 404
            
    def category(self, ip, port, type, params, lang, oauth_token=None):
        url = f'https://www.youtube.com/youtubei/v1/browse?browseId=FE{type}&key=AIzaS=yAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8'
        if params:
            url += f'&params={params}'
        if oauth_token:
            url += f'&access_token={oauth_token}'
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0'
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

        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            xml_data = self.buildCategoryXML(data, ip, port)
            return Response(xml_data, mimetype='text/atom+xml')
            
    def categoryV2(self, ip, port, type, params):
        url = f'https://www.youtube.com/youtubei/v1/browse?browseId=FE{type}&key=AIzaS=yAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8'
        if params:
            url += f'&params={params}'
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0'
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

        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            m3u_data = self.buildCategoryM3U(data, ip, port)
            return Response(m3u_data, mimetype='text/plain')
            
    def categoryTwo(self, ip, port, channelId, lang, oauth_token=None):
        url = f'https://www.youtube.com/youtubei/v1/browse?browseId={channelId}&key=AIzaS=yAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8'
        if oauth_token:
            url += f'&access_token={oauth_token}'
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0'
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

        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            xml_data = self.buildCategoryTwoXML(data, ip, port)
            return Response(xml_data, mimetype='text/atom+xml')
            
    def categoryTwoV2(self, ip, port, channelId):
        url = f'https://www.youtube.com/youtubei/v1/browse?browseId={channelId}&key=AIzaS=yAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8'
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0'
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

        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            xml_data = self.buildCategoryTwoM3U(data, ip, port)
            return Response(xml_data, mimetype='text/plain')
            
    def categoryThree(self, ip, port, channelId, lang, oauth_token=None):
        url = f'https://www.youtube.com/youtubei/v1/browse?browseId={channelId}&key=AIzaS=yAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8'
        if oauth_token:
            url += f'&access_token={oauth_token}'
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0'
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

        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            xml_data = self.buildCategoryThreeXML(data, ip, port)
            return Response(xml_data, mimetype='text/atom+xml')
            
    def categoryThreeV2(self, ip, port, channelId):
        url = f'https://www.youtube.com/youtubei/v1/browse?browseId={channelId}&key=AIzaS=yAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8'
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0'
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

        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            xml_data = self.buildCategoryThreeM3U(data, ip, port)
            return Response(xml_data, mimetype='text/plain')

    def explore(self, ip, port, lang, oauth_token=None):
        url = f'https://www.youtube.com/youtubei/v1/browse?browseId=FEexplore&key=AIzaS=yAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8'
        if oauth_token:
            url += f'&access_token={oauth_token}'
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0'
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
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            xml_data = self.buildExplorerXML(data, ip, port)
            return Response(xml_data, mimetype='text/atom+xml')
            
class DataAPI:
    DATA_API_KEY = 'AIzaSyDuziy6qTSaKhs0w4SKpLNWivKFNoWjQQA'    
    BASE_URL = "https://www.googleapis.com/youtube/v3"

    def userUploads(self, ip, port, lang, channelId):
        uploads_playlist_id = self.getUploadsPlaylistId(channelId)
        if not uploads_playlist_id:
            return Response("<error>Channel not found</error>", mimetype='text/xml')
        
        videos = self.getAllVideosFromPlaylist(uploads_playlist_id)
        xml_data = self.buildUploadsXML(videos, ip, port)
        return Response(xml_data, mimetype='text/atom+xml')
    
    def getUploadsPlaylistId(self, channelId):
        url = f"{self.BASE_URL}/channels?part=contentDetails&id={channelId}&key={self.DATA_API_KEY}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if "items" in data and len(data["items"]) > 0:
                return data["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
        return None
    
    def getAllVideosFromPlaylist(self, playlistId):
        videos = []
        url = f"{self.BASE_URL}/playlistItems?part=snippet,contentDetails&maxResults=50&playlistId={playlistId}&key={self.DATA_API_KEY}"
        while url:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                videos.extend(data.get("items", []))
                url = data.get("nextPageToken")
                if url:
                    url = f"{self.BASE_URL}/playlistItems?part=snippet,contentDetails&maxResults=50&pageToken={url}&playlistId={playlistId}&key={self.DATA_API_KEY}"
                else:
                    break
        return videos

    def playlist(self, ip, port, playlistId, oauthToken=None):
        if oauthToken:
            videos = self.getAllVideosFromPlaylistWithOAuth(playlistId, oauthToken)
        else:
            videos = self.getAllVideosFromPlaylist(playlistId)        
        if not videos:
            return Response("<error>Playlist not found</error>", mimetype='text/xml')        
        xml_data = self.buildPlaylistXML(videos, ip, port)
        return Response(xml_data, mimetype='text/atom+xml')

    def getAllVideosFromPlaylistWithOAuth(self, playlistId, oauthToken):
        videos = []
        url = f"https://www.googleapis.com/youtube/v3/playlistItems?part=snippet,contentDetails&maxResults=50&playlistId={playlistId}&access_token={oauthToken}"
        
        while url:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                videos.extend(data.get("items", []))
                url = data.get("nextPageToken")
                if url:
                    url = f"https://www.googleapis.com/youtube/v3/playlistItems?part=snippet,contentDetails&maxResults=50&pageToken={url}&playlistId={playlistId}&access_token={oauthToken}"
                else:
                    break
        return videos

    def buildPlaylistXML(self, videos, ip, port):
        xml_string = '<?xml version="1.0" encoding="UTF-8"?>'
        xml_string += '<feed xmlns:openSearch="http://a9.com/-/spec/opensearch/1.1/" xmlns:media="http://search.yahoo.com/mrss/" xmlns:yt="http://www.youtube.com/xml/schemas/2015">'
        xml_string += '<title type="text">Playlist</title>'
        xml_string += '<generator ver="1.0" uri="http://kamil.cc/">Liinback data API</generator>'
        xml_string += f'<openSearch:totalResults>{len(videos)}</openSearch:totalResults>'
        xml_string += '<openSearch:startIndex>1</openSearch:startIndex>'
        xml_string += '<openSearch:itemsPerPage>50</openSearch:itemsPerPage>'        
        for video in videos:
            snippet = video.get("snippet", {})
            content = video.get("contentDetails", {})
            videoId = content.get("videoId", "")
            title = snippet.get("title", "")
            publishedAt = snippet.get("publishedAt", "")
            authorName = snippet.get("channelTitle", "")
            authorId = snippet.get("channelId", "")
            thumbnailUrl = snippet.get("thumbnails", {}).get("medium", {}).get("url", "")
            viewCount = snippet.get("viewCount", "0")
            duration = content.get("duration", "")
            xml_string += '<entry>'
            xml_string += f'<id>http://{ip}:{port}/api/videos/{videoId}</id>'
            xml_string += f'<published>{publishedAt}</published>'
            xml_string += f'<title type="text">{self.escape_xml(title)}</title>'
            xml_string += f'<link rel="http://{ip}:{port}/api/videos/{videoId}/related"/>' 
            xml_string += f'<author><name>{self.escape_xml(authorName)}</name><uri>https://www.youtube.com/channel/{authorId}</uri></author>'
            xml_string += '<media:group>'
            xml_string += f'<media:thumbnail yt:name="mqdefault" url="http://i.ytimg.com/vi/{videoId}/mqdefault.jpg" height="240" width="320"/>'
            xml_string += f'<yt:videoid id="{videoId}">{videoId}</yt:videoid>'
            xml_string += f'<yt:duration seconds="{duration}"/>'  
            xml_string += f'<media:credit role="uploader" name="{self.escape_xml(authorName)}">{self.escape_xml(authorName)}</media:credit>'
            xml_string += '</media:group>'
            xml_string += f'<yt:statistics favoriteCount="0" viewCount="{viewCount}"/>'
            xml_string += '</entry>'        
        xml_string += '</feed>'
        return xml_string 

    def buildUploadsXML(self, videos, ip, port):
        xml_string = '<?xml version="1.0" encoding="UTF-8"?>'
        xml_string += '<feed xmlns:openSearch="http://a9.com/-/spec/opensearch/1.1/" xmlns:media="http://search.yahoo.com/mrss/" xmlns:yt="http://www.youtube.com/xml/schemas/2015">'
        xml_string += '<title type="text">Videos</title>'
        xml_string += '<generator ver="1.0" uri="http://kamil.cc/">Liinback data API</generator>'
        xml_string += f'<openSearch:totalResults>{len(videos)}</openSearch:totalResults>'
        xml_string += '<openSearch:startIndex>1</openSearch:startIndex>'
        xml_string += '<openSearch:itemsPerPage>50</openSearch:itemsPerPage>'        
        for video in videos:
            snippet = video.get("snippet", {})
            content = video.get("contentDetails", {})
            videoId = content.get("videoId", "")
            title = snippet.get("title", "")
            publishedAt = snippet.get("publishedAt", "")
            authorName = snippet.get("channelTitle", "")
            authorId = snippet.get("channelId", "")
            thumbnailUrl = snippet.get("thumbnails", {}).get("medium", {}).get("url", "")
            viewCount = snippet.get("viewCount", "0")
            duration = content.get("duration", "")  
            xml_string += '<entry>'
            xml_string += f'<id>http://{ip}:{port}/api/videos/{videoId}</id>'
            xml_string += f'<published>{publishedAt}</published>'
            xml_string += f'<title type="text">{self.escape_xml(title)}</title>'
            xml_string += f'<link rel="http://{ip}:{port}/api/videos/{videoId}/related"/>'
            xml_string += f'<author><name>{self.escape_xml(authorName)}</name><uri>https://www.youtube.com/channel/{authorId}</uri></author>'
            xml_string += '<media:group>'
            xml_string += f'<media:thumbnail yt:name="mqdefault" url="http://i.ytimg.com/vi/{videoId}/mqdefault.jpg" height="240" width="320"/>'
            xml_string += f'<yt:videoid id="{videoId}">{videoId}</yt:videoid>'
            xml_string += f'<yt:duration seconds="{duration}"/>'
            xml_string += f'<media:credit role="uploader" name="{self.escape_xml(authorName)}">{self.escape_xml(authorName)}</media:credit>'
            xml_string += '</media:group>'
            xml_string += f'<yt:statistics favoriteCount="0" viewCount="{viewCount}"/>'
            xml_string += '</entry>'        
        xml_string += '</feed>'
        return xml_string    
    @staticmethod
    def escape_xml(s):
        if s is None:
            return ''
        return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\"", "&quot;").replace("'", "&apos;")