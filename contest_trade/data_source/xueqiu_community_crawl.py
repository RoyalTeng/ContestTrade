"""
雪球社区数据爬虫 - 获取KOL观点和高热度评论
"""
import asyncio
import aiohttp
import re
import json
import os
import time
from datetime import datetime, timedelta
import random
import pandas as pd
import sys
from typing import List, Dict
current_dir = os.path.dirname(__file__)
package_root = os.path.dirname(current_dir)
if package_root not in sys.path:
    sys.path.insert(0, package_root)
from data_source.data_source_base import DataSourceBase
from loguru import logger


class XueqiuCommunityCrawl(DataSourceBase):
    """
    雪球社区爬虫 - 专注于获取市场情绪和KOL观点
    """
    def __init__(self, max_posts=100, min_follower_count=1000, min_like_count=50):
        super().__init__("xueqiu_community")
        self.max_posts = max_posts
        self.min_follower_count = min_follower_count  # KOL最低粉丝数
        self.min_like_count = min_like_count  # 最低点赞数
        
        # 雪球API接口
        self.timeline_url = "https://xueqiu.com/v4/statuses/public_timeline_by_category.json"
        self.user_url = "https://xueqiu.com/u/{user_id}"
        self.post_detail_url = "https://xueqiu.com/statuses/show.json"
        
        # 请求头设置
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Referer": "https://xueqiu.com/",
            "X-Requested-With": "XMLHttpRequest"
        }
        
        # 关注的话题类别
        self.categories = [
            102,  # 热门
            105,  # 沪深
            104,  # 港股  
            103,  # 美股
        ]
        
    async def get_session_token(self, session):
        """获取雪球访问token"""
        try:
            async with session.get("https://xueqiu.com", headers=self.headers) as response:
                cookies = response.cookies
                token = cookies.get('xq_a_token')
                if token:
                    self.headers['Cookie'] = f'xq_a_token={token.value}'
                await asyncio.sleep(random.uniform(1, 2))
        except Exception as e:
            logger.warning(f"获取雪球token失败: {e}")

    async def fetch_timeline_posts(self, session, category=102, page=1):
        """获取时间线帖子"""
        params = {
            'since_id': -1,
            'max_id': -1,
            'count': 20,
            'category': category,
            'page': page
        }
        
        try:
            await asyncio.sleep(random.uniform(2, 4))  # 增加延迟避免被封
            async with session.get(self.timeline_url, headers=self.headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('statuses', [])
                else:
                    logger.warning(f"雪球API返回状态码: {response.status}")
                    return []
        except Exception as e:
            logger.error(f"获取雪球时间线失败: {e}")
            return []

    def extract_sentiment_signals(self, text: str) -> Dict:
        """提取情绪信号"""
        # 情绪关键词
        bullish_keywords = ['看多', '上涨', '牛市', '买入', '加仓', '利好', '突破', '涨停']
        bearish_keywords = ['看空', '下跌', '熊市', '卖出', '减仓', '利空', '跌破', '跌停']
        
        bullish_count = sum(1 for word in bullish_keywords if word in text)
        bearish_count = sum(1 for word in bearish_keywords if word in text)
        
        sentiment = "neutral"
        if bullish_count > bearish_count:
            sentiment = "bullish"
        elif bearish_count > bullish_count:
            sentiment = "bearish"
            
        return {
            "sentiment": sentiment,
            "bullish_signals": bullish_count,
            "bearish_signals": bearish_count,
            "confidence": abs(bullish_count - bearish_count) / max(len(text) / 100, 1)
        }

    def extract_stock_mentions(self, text: str) -> List[str]:
        """提取股票代码"""
        # 匹配股票代码格式 $SH600000 或 SH600000 或 600000
        patterns = [
            r'\$([A-Z]{2}\d{6})',  # $SH600000
            r'\$(\d{6})',          # $600000
            r'([A-Z]{2}\d{6})',    # SH600000
            r'(\d{6})',            # 600000 (需要更严格的上下文判断)
        ]
        
        stocks = []
        for pattern in patterns:
            stocks.extend(re.findall(pattern, text))
            
        # 去重并标准化
        return list(set(stocks))

    def is_high_quality_post(self, post_data: Dict) -> bool:
        """判断是否为高质量帖子"""
        try:
            user = post_data.get('user', {})
            followers_count = user.get('followers_count', 0)
            like_count = post_data.get('like_count', 0)
            comment_count = post_data.get('comment_count', 0)
            text_length = len(post_data.get('text', ''))
            
            # 高质量判断标准
            is_kol = followers_count >= self.min_follower_count
            is_popular = (like_count + comment_count * 2) >= self.min_like_count
            is_substantial = text_length >= 50  # 内容不能太短
            
            return is_kol or is_popular or is_substantial
            
        except Exception as e:
            logger.warning(f"评估帖子质量失败: {e}")
            return False

    def process_post(self, post_data: Dict) -> Dict:
        """处理单个帖子数据"""
        try:
            user = post_data.get('user', {})
            text = post_data.get('text', '')
            
            # 清理HTML标签
            clean_text = re.sub(r'<[^>]+>', '', text)
            clean_text = re.sub(r'&[a-zA-Z]+;', '', clean_text)
            
            # 提取关键信息
            sentiment_data = self.extract_sentiment_signals(clean_text)
            stock_mentions = self.extract_stock_mentions(clean_text)
            
            return {
                'title': clean_text[:100] + '...' if len(clean_text) > 100 else clean_text,
                'content': clean_text,
                'pub_time': datetime.fromtimestamp(post_data.get('created_at', 0) / 1000).strftime('%Y-%m-%d %H:%M:%S'),
                'url': f"https://xueqiu.com/{post_data.get('id', '')}",
                'author_name': user.get('screen_name', ''),
                'author_followers': user.get('followers_count', 0),
                'like_count': post_data.get('like_count', 0),
                'comment_count': post_data.get('comment_count', 0),
                'repost_count': post_data.get('retweet_count', 0),
                'sentiment': sentiment_data['sentiment'],
                'sentiment_confidence': sentiment_data['confidence'],
                'stock_mentions': ','.join(stock_mentions),
                'source_type': 'xueqiu_community',
                'influence_score': self.calculate_influence_score(post_data)
            }
        except Exception as e:
            logger.error(f"处理帖子数据失败: {e}")
            return None

    def calculate_influence_score(self, post_data: Dict) -> float:
        """计算影响力分数"""
        try:
            user = post_data.get('user', {})
            followers = user.get('followers_count', 0)
            likes = post_data.get('like_count', 0)
            comments = post_data.get('comment_count', 0)
            reposts = post_data.get('retweet_count', 0)
            
            # 影响力计算公式
            follower_score = min(followers / 10000, 5)  # 粉丝数权重，最高5分
            engagement_score = (likes * 1 + comments * 3 + reposts * 2) / 100  # 互动权重
            
            return round(follower_score + engagement_score, 2)
        except:
            return 0.0

    async def get_data(self, trigger_time: str) -> pd.DataFrame:
        """获取雪球社区数据"""
        logger.info(f"开始获取雪球社区数据 - {trigger_time}")
        
        # 检查缓存
        cached_data = self.get_data_cached(trigger_time)
        if cached_data is not None:
            logger.info(f"使用雪球社区缓存数据: {len(cached_data)} 条记录")
            return cached_data
        
        all_posts = []
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
            # 获取访问token
            await self.get_session_token(session)
            
            # 获取各类别的帖子
            for category in self.categories:
                logger.info(f"抓取雪球类别 {category} 的帖子")
                
                for page in range(1, 6):  # 前5页
                    posts = await self.fetch_timeline_posts(session, category, page)
                    
                    if not posts:
                        break
                    
                    # 过滤和处理帖子
                    for post in posts:
                        if self.is_high_quality_post(post):
                            processed_post = self.process_post(post)
                            if processed_post:
                                all_posts.append(processed_post)
                    
                    if len(all_posts) >= self.max_posts:
                        break
                
                if len(all_posts) >= self.max_posts:
                    break
        
        # 转换为DataFrame
        if all_posts:
            df = pd.DataFrame(all_posts)
            
            # 按影响力分数排序
            df = df.sort_values('influence_score', ascending=False).head(self.max_posts)
            
            # 保存缓存
            self.save_data_cached(trigger_time, df)
            
            logger.info(f"雪球社区数据获取完成: {len(df)} 条记录")
            return df
        else:
            logger.warning("未获取到雪球社区数据")
            return pd.DataFrame(columns=['title', 'content', 'pub_time', 'url'])


if __name__ == "__main__":
    async def test():
        crawler = XueqiuCommunityCrawl()
        trigger_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data = await crawler.get_data(trigger_time)
        print(f"获取到 {len(data)} 条雪球数据")
        if not data.empty:
            print(data[['title', 'sentiment', 'influence_score', 'author_followers']].head())
    
    asyncio.run(test())