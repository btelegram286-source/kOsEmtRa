#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
🚀 Naofumi Bot Gelişmiş Özellikler Modülü
TikTok, Twitter ve diğer platform desteği
"""

import os
import re
import asyncio
import logging
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse, parse_qs
import requests
from yt_dlp import YoutubeDL

logger = logging.getLogger(__name__)

class AdvancedFeatures:
    def __init__(self):
        """Gelişmiş özellikler sınıfını başlat"""
        self.supported_platforms = {
            'youtube': {
                'domains': ['youtube.com', 'youtu.be', 'm.youtube.com'],
                'enabled': True,
                'priority': 1
            },
            'instagram': {
                'domains': ['instagram.com', 'www.instagram.com'],
                'enabled': False,  # Geçici olarak devre dışı
                'priority': 2
            },
            'tiktok': {
                'domains': ['tiktok.com', 'vm.tiktok.com', 'vt.tiktok.com'],
                'enabled': True,
                'priority': 3
            },
            'twitter': {
                'domains': ['twitter.com', 'x.com', 't.co'],
                'enabled': True,
                'priority': 4
            },
            'facebook': {
                'domains': ['facebook.com', 'fb.watch', 'fb.com'],
                'enabled': True,
                'priority': 5
            }
        }
        
        # Platform-specific ayarlar
        self.platform_configs = {
            'tiktok': {
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                }
            },
            'twitter': {
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
                }
            }
        }
    
    def detect_platform(self, url: str) -> Optional[str]:
        """URL'den platform tespit et"""
        try:
            parsed_url = urlparse(url)
            domain = parsed_url.netloc.lower()
            
            # www. kısmını kaldır
            if domain.startswith('www.'):
                domain = domain[4:]
            
            for platform, config in self.supported_platforms.items():
                if config['enabled']:
                    for supported_domain in config['domains']:
                        if supported_domain in domain:
                            logger.info(f"Platform tespit edildi: {platform} - {url}")
                            return platform
            
            logger.warning(f"Desteklenmeyen platform: {domain}")
            return None
            
        except Exception as e:
            logger.error(f"Platform tespit hatası: {e}")
            return None
    
    def is_valid_url(self, url: str) -> bool:
        """URL geçerliliğini kontrol et"""
        try:
            parsed = urlparse(url)
            return bool(parsed.netloc) and bool(parsed.scheme)
        except:
            return False
    
    def clean_url(self, url: str) -> str:
        """URL'yi temizle ve normalize et"""
        # Boşlukları kaldır
        url = url.strip()
        
        # http/https kontrolü
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # URL parametrelerini temizle
        if '?' in url:
            base_url, params = url.split('?', 1)
            # Önemli parametreleri koru
            important_params = ['v', 't', 'list', 'index']
            parsed_params = parse_qs(params)
            clean_params = {}
            
            for param in important_params:
                if param in parsed_params:
                    clean_params[param] = parsed_params[param][0]
            
            if clean_params:
                param_string = '&'.join([f"{k}={v}" for k, v in clean_params.items()])
                url = f"{base_url}?{param_string}"
            else:
                url = base_url
        
        return url
    
    def get_platform_info(self, url: str) -> Dict:
        """Platform bilgilerini al"""
        platform = self.detect_platform(url)
        if not platform:
            return {'error': 'Desteklenmeyen platform'}
        
        config = self.supported_platforms[platform]
        return {
            'platform': platform,
            'enabled': config['enabled'],
            'priority': config['priority'],
            'domains': config['domains']
        }
    
    async def get_video_info(self, url: str) -> Dict:
        """Video bilgilerini al"""
        try:
            platform = self.detect_platform(url)
            if not platform:
                return {'error': 'Desteklenmeyen platform'}
            
            # Platform-specific bilgi alma
            if platform == 'tiktok':
                return await self._get_tiktok_info(url)
            elif platform == 'twitter':
                return await self._get_twitter_info(url)
            elif platform == 'facebook':
                return await self._get_facebook_info(url)
            elif platform == 'instagram':
                # Instagram için özel çözüm
                return await self._get_instagram_info(url)
            else:
                # YouTube için yt-dlp kullan
                return await self._get_ytdlp_info(url)
                
        except Exception as e:
            logger.error(f"Video bilgi alma hatası: {e}")
            return {'error': str(e)}
    
    async def _get_tiktok_info(self, url: str) -> Dict:
        """TikTok video bilgilerini al"""
        try:
            # TikTok için özel yt-dlp ayarları
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
                'user_agent': self.platform_configs['tiktok']['user_agent'],
                'headers': self.platform_configs['tiktok']['headers']
            }
            
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                return {
                    'title': info.get('title', 'TikTok Video'),
                    'duration': info.get('duration', 0),
                    'uploader': info.get('uploader', 'TikTok User'),
                    'view_count': info.get('view_count', 0),
                    'like_count': info.get('like_count', 0),
                    'thumbnail': info.get('thumbnail', ''),
                    'formats': info.get('formats', []),
                    'platform': 'tiktok'
                }
                
        except Exception as e:
            logger.error(f"TikTok bilgi alma hatası: {e}")
            return {'error': f'TikTok bilgi alınamadı: {e}'}
    
    async def _get_twitter_info(self, url: str) -> Dict:
        """Twitter video bilgilerini al"""
        try:
            # Twitter için özel yt-dlp ayarları
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
                'user_agent': self.platform_configs['twitter']['user_agent'],
                'headers': self.platform_configs['twitter']['headers']
            }
            
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                return {
                    'title': info.get('title', 'Twitter Video'),
                    'duration': info.get('duration', 0),
                    'uploader': info.get('uploader', 'Twitter User'),
                    'view_count': info.get('view_count', 0),
                    'thumbnail': info.get('thumbnail', ''),
                    'formats': info.get('formats', []),
                    'platform': 'twitter'
                }
                
        except Exception as e:
            logger.error(f"Twitter bilgi alma hatası: {e}")
            return {'error': f'Twitter bilgi alınamadı: {e}'}
    
    async def _get_facebook_info(self, url: str) -> Dict:
        """Facebook video bilgilerini al"""
        try:
            # Facebook için özel yt-dlp ayarları
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                return {
                    'title': info.get('title', 'Facebook Video'),
                    'duration': info.get('duration', 0),
                    'uploader': info.get('uploader', 'Facebook User'),
                    'view_count': info.get('view_count', 0),
                    'thumbnail': info.get('thumbnail', ''),
                    'formats': info.get('formats', []),
                    'platform': 'facebook'
                }
                
        except Exception as e:
            logger.error(f"Facebook bilgi alma hatası: {e}")
            return {'error': f'Facebook bilgi alınamadı: {e}'}
    
    async def _get_instagram_info(self, url: str) -> Dict:
        """Instagram video bilgilerini al - özel çözüm"""
        try:
            # Instagram için basit yt-dlp ayarları
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
                'noplaylist': True,
                'user_agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1',
                'extractor_retries': 1,
                'fragment_retries': 1,
                'retries': 1,
                'socket_timeout': 15
            }
            
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                return {
                    'title': info.get('title', 'Instagram Video'),
                    'duration': info.get('duration', 0),
                    'uploader': info.get('uploader', 'Instagram User'),
                    'view_count': info.get('view_count', 0),
                    'like_count': info.get('like_count', 0),
                    'thumbnail': info.get('thumbnail', ''),
                    'formats': info.get('formats', []),
                    'platform': 'instagram'
                }
                
        except Exception as e:
            logger.error(f"Instagram bilgi alma hatası: {e}")
            # Fallback: Basit bilgi döndür
            return {
                'title': 'Instagram Video',
                'duration': 0,
                'uploader': 'Instagram User',
                'view_count': 0,
                'like_count': 0,
                'thumbnail': '',
                'formats': [],
                'platform': 'instagram',
                'warning': 'Instagram içeriği için sınırlı bilgi mevcut'
            }
    
    async def _get_ytdlp_info(self, url: str) -> Dict:
        """yt-dlp ile video bilgilerini al"""
        try:
            platform = self.detect_platform(url)
            
            # Platform-specific ayarlar
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
                'noplaylist': True
            }
            
            # Instagram için özel ayarlar
            if platform == 'instagram':
                ydl_opts.update({
                    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'headers': {
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.5',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'DNT': '1',
                        'Connection': 'keep-alive',
                        'Upgrade-Insecure-Requests': '1',
                    },
                    'extractor_retries': 2,
                    'fragment_retries': 2,
                    'retries': 2,
                    'socket_timeout': 30,
                    'sleep_interval': 1,
                    'max_sleep_interval': 5
                })
            
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                return {
                    'title': info.get('title', 'Video'),
                    'duration': info.get('duration', 0),
                    'uploader': info.get('uploader', 'Unknown'),
                    'view_count': info.get('view_count', 0),
                    'like_count': info.get('like_count', 0),
                    'thumbnail': info.get('thumbnail', ''),
                    'formats': info.get('formats', []),
                    'platform': platform
                }
                
        except Exception as e:
            logger.error(f"yt-dlp bilgi alma hatası: {e}")
            return {'error': f'Video bilgi alınamadı: {e}'}
    
    def get_available_formats(self, video_info: Dict) -> List[Dict]:
        """Mevcut formatları al"""
        if 'error' in video_info:
            return []
        
        formats = video_info.get('formats', [])
        available_formats = []
        
        for fmt in formats:
            if fmt.get('vcodec') != 'none':  # Video formatı
                available_formats.append({
                    'format_id': fmt.get('format_id'),
                    'ext': fmt.get('ext'),
                    'height': fmt.get('height'),
                    'width': fmt.get('width'),
                    'filesize': fmt.get('filesize'),
                    'quality': f"{fmt.get('height', '?')}p" if fmt.get('height') else 'Unknown'
                })
            elif fmt.get('acodec') != 'none':  # Audio formatı
                available_formats.append({
                    'format_id': fmt.get('format_id'),
                    'ext': fmt.get('ext'),
                    'bitrate': fmt.get('abr'),
                    'filesize': fmt.get('filesize'),
                    'quality': f"{fmt.get('abr', '?')}kbps" if fmt.get('abr') else 'Unknown'
                })
        
        return available_formats
    
    def get_best_format(self, video_info: Dict, preferred_quality: str = '720p') -> Optional[Dict]:
        """En iyi formatı seç"""
        formats = self.get_available_formats(video_info)
        if not formats:
            return None
        
        # Kaliteye göre sırala
        quality_order = ['2160p', '1440p', '1080p', '720p', '480p', '360p', '240p']
        
        try:
            preferred_index = quality_order.index(preferred_quality)
        except ValueError:
            preferred_index = 3  # 720p varsayılan
        
        # Tercih edilen kaliteyi bul
        for quality in quality_order[preferred_index:]:
            for fmt in formats:
                if fmt.get('quality') == quality:
                    return fmt
        
        # Tercih edilen kalite bulunamazsa en yüksek kaliteyi döndür
        return formats[0] if formats else None
    
    def create_download_options(self, platform: str, format_type: str, quality: str) -> Dict:
        """İndirme seçeneklerini oluştur"""
        options = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'noplaylist': True
        }
        
        if platform == 'tiktok':
            options.update({
                'user_agent': self.platform_configs['tiktok']['user_agent'],
                'headers': self.platform_configs['tiktok']['headers']
            })
        elif platform == 'twitter':
            options.update({
                'user_agent': self.platform_configs['twitter']['user_agent'],
                'headers': self.platform_configs['twitter']['headers']
            })
        
        if format_type == 'mp3':
            options.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': quality.replace('kbps', ''),
                }],
                'outtmpl': '%(title)s.%(ext)s'
            })
        else:  # mp4
            height = quality.replace('p', '')
            options.update({
                'format': f'bestvideo[height<={height}]+bestaudio/best[height<={height}]',
                'postprocessors': [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4'
                }],
                'ffmpeg_args': ['-c:v', 'libx264', '-c:a', 'aac', '-b:a', '192k'],
                'outtmpl': '%(title)s.%(ext)s',
                'merge_output_format': 'mp4'
            })
        
        return options
    
    def get_platform_emoji(self, platform: str) -> str:
        """Platform emojisini al"""
        emojis = {
            'youtube': '📺',
            'instagram': '📸',
            'tiktok': '🎵',
            'twitter': '🐦',
            'facebook': '👥'
        }
        return emojis.get(platform, '🎬')
    
    def get_platform_name(self, platform: str) -> str:
        """Platform adını al"""
        names = {
            'youtube': 'YouTube',
            'instagram': 'Instagram',
            'tiktok': 'TikTok',
            'twitter': 'Twitter',
            'facebook': 'Facebook'
        }
        return names.get(platform, 'Unknown')

# Global instance
advanced_features = AdvancedFeatures()

# Test fonksiyonu
async def test_advanced_features():
    """Gelişmiş özellikleri test et"""
    test_urls = [
        'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
        'https://www.instagram.com/p/ABC123/',
        'https://www.tiktok.com/@user/video/1234567890',
        'https://twitter.com/user/status/1234567890'
    ]
    
    for url in test_urls:
        print(f"\n🔍 Test URL: {url}")
        platform = advanced_features.detect_platform(url)
        print(f"Platform: {platform}")
        
        if platform:
            info = await advanced_features.get_video_info(url)
            print(f"Video Info: {info.get('title', 'N/A')}")

if __name__ == "__main__":
    asyncio.run(test_advanced_features())
