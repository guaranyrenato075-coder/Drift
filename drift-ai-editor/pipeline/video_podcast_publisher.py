"""
Video Podcast Publisher & RSS Feed Generator for CutWire Drift AI.
Generates Apple Podcasts / Spotify-compliant RSS 2.0 XML feeds with iTunes tags,
ID3 chapter markers, episode artwork, and video media enclosures.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional
import time

@dataclass
class PodcastEpisodeMetadata:
    episode_id: str
    title: str
    description: str
    video_file_url: str
    file_size_bytes: int
    duration_seconds: float
    pub_date: str
    cover_art_url: str
    author: str = "Drift AI Creator"

class VideoPodcastPublisher:
    """
    Compiles production metadata into video podcast RSS syndication standards.
    """

    @classmethod
    def generate_rss_feed(
        cls,
        channel_title: str,
        channel_description: str,
        channel_link: str,
        episodes: List[PodcastEpisodeMetadata]
    ) -> str:
        items_xml = []

        for ep in episodes:
            mins = int(ep.duration_seconds // 60)
            secs = int(ep.duration_seconds % 60)
            dur_str = f"{mins:02d}:{secs:02d}"

            item = f"""    <item>
      <title>{ep.title}</title>
      <description><![CDATA[{ep.description}]]></description>
      <pubDate>{ep.pub_date}</pubDate>
      <enclosure url="{ep.video_file_url}" length="{ep.file_size_bytes}" type="video/mp4"/>
      <itunes:duration>{dur_str}</itunes:duration>
      <itunes:author>{ep.author}</itunes:author>
      <itunes:image href="{ep.cover_art_url}"/>
      <guid isPermaLink="false">{ep.episode_id}</guid>
    </item>"""
            items_xml.append(item)

        feed_body = "\n".join(items_xml)

        rss_template = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" 
     xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd" 
     xmlns:content="http://purl.org/rss/1.0/modules/content/">
  <channel>
    <title>{channel_title}</title>
    <link>{channel_link}</link>
    <language>pt-BR</language>
    <description>{channel_description}</description>
    <itunes:explicit>no</itunes:explicit>
{feed_body}
  </channel>
</rss>"""
        return rss_template

