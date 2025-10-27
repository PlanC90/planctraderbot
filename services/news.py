"""
Kripto Haber Servisi - RSS Feeds
Kaynaklar: RSS Feeds (CoinDesk, CoinTelegraph, CoinTürk vb.)
"""
import requests
from typing import List, Dict
from datetime import datetime
import xml.etree.ElementTree as ET


class NewsService:
    def __init__(self):
        # RSS Feed kaynakları (dil bazlı)
        self.rss_feeds = {
            'en': [
                'https://cointelegraph.com/rss',
                'https://www.coindesk.com/arc/outboundfeeds/rss/',
                'https://cryptonews.com/news/feed/',
            ],
            'tr': [
                'https://tr.cointelegraph.com/rss',
                # Türkçe kaynaklar RSS desteği sınırlı, CryptoPanic fallback kullanacak
            ],
            'de': [
                'https://de.cointelegraph.com/rss',
            ],
            'es': [
                'https://es.cointelegraph.com/rss',
            ],
            'fr': [
                'https://fr.cointelegraph.com/rss',
            ],
            'it': [
                'https://it.cointelegraph.com/rss',
            ],
            'pt': [
                'https://pt.cointelegraph.com/rss',
            ],
            'ru': [
                'https://ru.cointelegraph.com/rss',
            ],
            'ja': [
                'https://jp.cointelegraph.com/rss',
            ],
            'ko': [
                'https://kr.cointelegraph.com/rss',
            ],
            'zh': [
                'https://cn.cointelegraph.com/rss',
            ],
        }
        
    def fetch_latest_news(self, limit: int = 10, filter_type: str = "hot", language: str = "en") -> List[Dict]:
        """
        RSS feeds'den haber çekme
        
        Args:
            limit: Kaç haber getirileceği
            filter_type: Kullanılmıyor (uyumluluk için)
            language: Dil kodu ("en", "tr", "de", "es", "fr", "it", "pt", "ru", "ko", "zh", "ja")
            
        Returns:
            Haber listesi: [{title, url, source, published_at}, ...]
        """
        all_news = []
        
        # RSS Feeds'den çek (seçilen dilde)
        if language in self.rss_feeds:
            for feed_url in self.rss_feeds[language]:
                try:
                    rss_news = self._fetch_rss_feed(feed_url, limit=limit)
                    all_news.extend(rss_news)
                except Exception as e:
                    print(f"RSS feed hatası ({feed_url}): {e}")
                    continue
        
        # Tarihe göre sırala ve limit uygula
        all_news.sort(key=lambda x: x.get('published_at', ''), reverse=True)
        return all_news[:limit]
    
    def _fetch_rss_feed(self, feed_url: str, limit: int = 5) -> List[Dict]:
        """RSS feed'den haber çeker"""
        try:
            response = requests.get(feed_url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            response.raise_for_status()
            
            # XML parse - encoding sorunlarını çöz
            content = response.content
            # UTF-8 BOM'u temizle
            if content.startswith(b'\xef\xbb\xbf'):
                content = content[3:]
            
            root = ET.fromstring(content)
            news_list = []
            
            # RSS formatı: <channel><item>...</item></channel>
            items = root.findall('.//item')[:limit]
            
            for item in items:
                title_elem = item.find('title')
                link_elem = item.find('link')
                pub_date_elem = item.find('pubDate')
                
                # Kaynak ismini URL'den çıkar
                source_name = feed_url.split('/')[2].replace('www.', '').split('.')[0].title()
                
                news_item = {
                    'title': title_elem.text if title_elem is not None else 'No Title',
                    'url': link_elem.text if link_elem is not None else feed_url,
                    'source': source_name,
                    'published_at': self._parse_rss_date(pub_date_elem.text if pub_date_elem is not None else ''),
                }
                news_list.append(news_item)
            
            return news_list
            
        except Exception as e:
            print(f"RSS parse hatası: {e}")
            return []
    
    def _parse_rss_date(self, date_str: str) -> str:
        """RSS tarihini ISO formatına çevirir"""
        if not date_str:
            return datetime.now().isoformat()
        
        try:
            # RSS date format: "Mon, 01 Jan 2024 10:30:00 +0000"
            from email.utils import parsedate_to_datetime
            dt = parsedate_to_datetime(date_str)
            return dt.isoformat()
        except Exception:
            return datetime.now().isoformat()
    
    def format_time_ago(self, published_at: str) -> str:
        """Zaman farkını hesaplar: '2 saat önce', '1 gün önce' gibi"""
        try:
            # ISO format: 2024-01-23T10:30:00Z veya 2024-01-23T10:30:00+00:00
            if 'Z' in published_at:
                published_time = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
            else:
                published_time = datetime.fromisoformat(published_at)
            
            now = datetime.now(published_time.tzinfo) if published_time.tzinfo else datetime.now()
            diff = now - published_time
            
            seconds = diff.total_seconds()
            
            if seconds < 60:
                return "Az önce"
            elif seconds < 3600:
                minutes = int(seconds / 60)
                return f"{minutes} dakika önce"
            elif seconds < 86400:
                hours = int(seconds / 3600)
                return f"{hours} saat önce"
            else:
                days = int(seconds / 86400)
                return f"{days} gün önce"
                
        except Exception:
            return "Bilinmeyen"


# Test kodu
if __name__ == "__main__":
    service = NewsService()
    
    print("=" * 60)
    print("📰 TÜRKÇE HABERLER")
    print("=" * 60)
    tr_news = service.fetch_latest_news(limit=5, language="tr")
    for item in tr_news:
        print(f"\n📰 {item['title'][:60]}...")
        print(f"   📅 {item['source']} - {service.format_time_ago(item['published_at'])}")
        print(f"   🔗 {item['url'][:60]}...")
    
    print("\n" + "=" * 60)
    print("📰 İNGİLİZCE HABERLER")
    print("=" * 60)
    en_news = service.fetch_latest_news(limit=5, language="en")
    for item in en_news:
        print(f"\n📰 {item['title'][:60]}...")
        print(f"   📅 {item['source']} - {service.format_time_ago(item['published_at'])}")
        print(f"   🔗 {item['url'][:60]}...")
