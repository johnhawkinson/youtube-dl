# coding: utf-8
from __future__ import unicode_literals

import re

from .common import InfoExtractor

from ..utils import (
    extract_attributes,
    orderedSet,
)

class BostonGlobeIE(InfoExtractor):
    _VALID_URL = r'https?(?i)://(?:www\.)?bostonglobe\.com/.*/(?P<id>[^/]+)/\w+(?:\.html)?'
    _TEST = {
            'url': 'http://www.bostonglobe.com/metro/2017/02/11/tree-finally-succumbs-disease-leaving-hole-neighborhood/h1b4lviqzMTIn9sVy8F3gP/story.html',
            'info_dict': {
                'id': 'h1b4lviqzMTIn9sVy8F3gP',
                'title': 'A tree finally succumbs to disease, leaving a hole in a neighborhood - The Boston Globe',
            },
            'playlist': [{
                'md5': '0a62181079c85c2d2b618c9a738aedaf',
                'info_dict': {
                    'id': '5320421710001',
                    'ext': 'mp4',
                    'title': 'A tree finally succumbs to disease, leaving a hole in a neighborhood',
                    'description': 'It arrived as a sapling when the Back Bay was in its infancy, a spindly American elm tamped down into a square of dirt cut into the brick sidewalk of 1880s Marlborough Street, no higher than the first bay window of the new brownstone behind it.',
                    'timestamp': 1486877593,
                    'upload_date': '20170212',
                    'uploader_id': '245991542',
                },
            }],
            # HEAD requests produce 404 :(
            'expected_warnings': ['404'],
        }

    def _real_extract(self, url):
        page_id = self._match_id(url)
        webpage = self._download_webpage(url, page_id)

        # cribbed from generic.py
        page_title = self._og_search_title(
            webpage, default=None) or self._html_search_regex(
            r'(?s)<title>(.*?)</title>', webpage, 'video title',
            default='video')

        # from generic.py
        def _playlist_from_matches(matches, getter=None, ie=None):
            urlrs = orderedSet(
                self.url_result(self._proto_relative_url(getter(m) if getter else m), ie)
                for m in matches)
            return self.playlist_result(
                urlrs, playlist_id=page_id, playlist_title=page_title)

        # 	<video data-brightcove-video-id="5320421710001" data-account="245991542" data-player="SJWAiyYWg" data-embed="default" class="video-js" controls itemscope itemtype="http://schema.org/VideoObject">
        entries = []
        for video in re.findall(r'(?i)(<video[^>]+>)', webpage):
            attrs = extract_attributes(video)

            video_id    = attrs.get('data-brightcove-video-id')
            account_id  = attrs.get('data-account')
            player_id   = attrs.get('data-player')
            embed       = attrs.get('data-embed')

            if video_id and account_id and player_id and embed:
                entries.append(
                    'http://players.brightcove.net/%s/%s_%s/index.html?videoId=%s'
                    % (account_id, player_id, embed, video_id))

        return _playlist_from_matches(entries, ie='BrightcoveNew')
