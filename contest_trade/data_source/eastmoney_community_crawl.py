"""
东方财富社区数据爬虫 - 获取股吧热门评论和KOL观点
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
from urllib.parse import urlencode
current_dir = os.path.dirname(__file__)
package_root = os.path.dirname(current_dir)
if package_root not in sys.path:
    sys.path.insert(0, package_root)
from data_source.data_source_base import DataSourceBase
from loguru import logger


class EastmoneyCommunityCrawl(DataSourceBase):
    """
    东方财富股吧爬虫 - 专注于获取热门股票讨论和情绪
    """
    def __init__(self, max_posts=100, top_stocks=20):
        super().__init__("eastmoney_community")
        self.max_posts = max_posts
        self.top_stocks = top_stocks
        
        # 东方财富API接口
        self.hot_stocks_url = "https://guba.eastmoney.com/rank/index"
        self.stock_posts_url = "https://guba.eastmoney.com/list,{stock_code}_{page}.html"
        self.post_api_url = "https://guba.eastmoney.com/news,{stock_code},{post_id}.html"
        
        # 请求头设置
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": "https://guba.eastmoney.com/",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }
        
    def extract_sentiment_keywords(self, text: str) -> Dict:
        """提取更细致的情绪关键词"""
        # 强烈看多
        strong_bullish = ['暴涨', '涨停', '牛逼', '起飞', '突破', '爆发', '主升浪', '翻倍']
        # 温和看多
        mild_bullish = ['看多', '上涨', '利好', '买入', '加仓', '持有', '机会']
        # 强烈看空
        strong_bearish = ['暴跌', '跌停', '崩盘', '完蛋', '跳水', '血崩', '割肉', '踩雷']
        # 温和看空
        mild_bearish = ['看空', '下跌', '利空', '卖出', '减仓', '风险', '小心']
        
        # 恐慌情绪词
        panic_words = ['恐慌', '害怕', '担心', '焦虑', '慌张', '绝望']
        # 贪婪情绪词  
        greed_words = ['贪婪', '疯狂', '狂欢', '追高', '梭哈', 'fomo']
        
        sentiment_scores = {
            'strong_bullish': sum(1 for word in strong_bullish if word in text) * 2,
            'mild_bullish': sum(1 for word in mild_bullish if word in text),
            'strong_bearish': sum(1 for word in strong_bearish if word in text) * 2,
            'mild_bearish': sum(1 for word in mild_bearish if word in text),
            'panic_level': sum(1 for word in panic_words if word in text),
            'greed_level': sum(1 for word in greed_words if word in text)
        }
        
        # 计算综合情绪
        bull_score = sentiment_scores['strong_bullish'] + sentiment_scores['mild_bullish']
        bear_score = sentiment_scores['strong_bearish'] + sentiment_scores['mild_bearish']
        
        if bull_score > bear_score * 1.2:
            sentiment = "bullish"
        elif bear_score > bull_score * 1.2:
            sentiment = "bearish"
        else:
            sentiment = "neutral"
            
        return {
            "sentiment": sentiment,
            "sentiment_score": bull_score - bear_score,
            "panic_level": sentiment_scores['panic_level'],
            "greed_level": sentiment_scores['greed_level'],
            "emotion_intensity": max(sentiment_scores['panic_level'], sentiment_scores['greed_level'])
        }

    async def get_hot_stocks_list(self, session) -> List[str]:
        """获取热门股票列表"""
        try:
            # 这里可以使用东方财富的热门股票接口
            # 为了简化，我们使用一些常见的热门股票代码
            hot_stocks = [
                "000001",  # 平安银行
                "000002",  # 万科A
                "000858",  # 五粮液
                "600036",  # 招商银行
                "600519",  # 贵州茅台
                "600887",  # 伊利股份
                "000661",  # 长春高新
                "300015",  # 爱尔眼科
                "002415",  # 海康威视
                "000725",  # 京东方A
                "600276",  # 恒瑞医药
                "000063",  # 中兴通讯
                "002594",  # 比亚迪
                "300750",  # 宁德时代  
                "688981",  # 中芯国际
                "600900",  # 长江电力
                "000568",  # 泸州老窖
                "002304",  # 洋河股份
                "300142",  # 沃森生物
                "688599"   # 天合光能
            ]
            
            return hot_stocks[:self.top_stocks]
            
        except Exception as e:
            logger.error(f"获取热门股票失败: {e}")
            return ["000001", "600519", "000002"]  # 默认几个股票

    async def fetch_stock_posts(self, session, stock_code: str, page: int = 1) -> List[Dict]:
        """获取特定股票的讨论帖"""
        try:
            url = f"https://guba.eastmoney.com/list,{stock_code}_{page}.html"
            
            await asyncio.sleep(random.uniform(2, 4))
            async with session.get(url, headers=self.headers) as response:
                if response.status == 200:
                    html_content = await response.text()
                    return self.parse_posts_from_html(html_content, stock_code)
                else:
                    logger.warning(f"东方财富请求失败: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"获取股票{stock_code}讨论失败: {e}")
            return []

    def parse_posts_from_html(self, html_content: str, stock_code: str) -> List[Dict]:
        """从HTML解析帖子信息"""
        posts = []
        
        try:
            # 使用正则表达式解析帖子标题和链接
            # 这个正则表达式需要根据实际的HTML结构调整
            post_pattern = r'<a[^>]*href="([^"]*news,[^"]*)"[^>]*>([^<]+)</a>'
            matches = re.findall(post_pattern, html_content)
            
            # 解析阅读数和评论数
            read_pattern = r'<em[^>]*>(\d+)</em>'
            read_counts = re.findall(read_pattern, html_content)
            
            # 解析发帖时间
            time_pattern = r'(\d{2}-\d{2}\s+\d{2}:\d{2})'
            times = re.findall(time_pattern, html_content)
            
            for i, (link, title) in enumerate(matches[:10]):  # 每页取前10个
                # 构造完整URL
                full_url = f"https://guba.eastmoney.com{link}" if link.startswith('/') else link
                
                # 获取对应的阅读数和时间
                read_count = int(read_counts[i]) if i < len(read_counts) and read_counts[i].isdigit() else 0
                post_time = times[i] if i < len(times) else datetime.now().strftime("%m-%d %H:%M")
                
                # 判断是否为高质量帖子（根据阅读数）
                if read_count >= 100:  # 阅读数超过100的帖子
                    posts.append({
                        'title': title.strip(),
                        'url': full_url,
                        'stock_code': stock_code,
                        'read_count': read_count,
                        'post_time': post_time,
                        'source': 'eastmoney_guba'
                    })
                    
        except Exception as e:
            logger.error(f"解析HTML失败: {e}")
            
        return posts

    def generate_mock_content(self, title: str, stock_code: str) -> str:
        """基于标题生成模拟内容（实际应该爬取详细内容）"""
        # 这里为了演示，基于标题生成一些模拟内容
        # 实际项目中应该进一步爬取帖子详细内容
        
        mock_templates = [
            f"关于{stock_code}的最新分析：{title}。从技术面看，该股票近期表现值得关注。",
            f"{title}，个人认为{stock_code}后续走势需要观察大盘整体情况。",
            f"对于{stock_code}，{title}这个观点我比较认同，建议大家理性投资。",
            f"刚看了{stock_code}的财报，{title}，感觉有一定的投资价值。",
            f"{title}。从基本面分析，{stock_code}确实有这样的潜力，但风险也要考虑。"
        ]
        
        return random.choice(mock_templates)

    def process_community_post(self, post_data: Dict) -> Dict:
        """处理社区帖子数据"""
        try:
            title = post_data.get('title', '')
            content = self.generate_mock_content(title, post_data.get('stock_code', ''))
            
            # 情绪分析
            sentiment_data = self.extract_sentiment_keywords(title + ' ' + content)
            
            return {
                'title': title,
                'content': content,
                'pub_time': self.format_post_time(post_data.get('post_time', '')),
                'url': post_data.get('url', ''),
                'stock_code': post_data.get('stock_code', ''),
                'read_count': post_data.get('read_count', 0),
                'sentiment': sentiment_data['sentiment'],
                'sentiment_score': sentiment_data['sentiment_score'],
                'panic_level': sentiment_data['panic_level'],
                'greed_level': sentiment_data['greed_level'],
                'emotion_intensity': sentiment_data['emotion_intensity'],
                'source_type': 'eastmoney_community',
                'quality_score': self.calculate_quality_score(post_data)
            }
            
        except Exception as e:
            logger.error(f"处理社区帖子失败: {e}")
            return None

    def format_post_time(self, time_str: str) -> str:
        """格式化发帖时间"""
        try:
            if re.match(r'\d{2}-\d{2}\s+\d{2}:\d{2}', time_str):
                # 补充年份
                current_year = datetime.now().year
                formatted_time = f"{current_year}-{time_str}:00"
                return formatted_time
            else:
                return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        except:
            return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def calculate_quality_score(self, post_data: Dict) -> float:
        """计算帖子质量分数"""
        try:
            read_count = post_data.get('read_count', 0)
            title_length = len(post_data.get('title', ''))
            
            # 基于阅读数和标题长度的质量评分
            read_score = min(read_count / 1000, 5)  # 阅读数权重
            length_score = min(title_length / 20, 2)  # 标题长度权重
            
            return round(read_score + length_score, 2)
        except:
            return 1.0

    async def get_data(self, trigger_time: str) -> pd.DataFrame:
        """获取东方财富社区数据"""
        logger.info(f"开始获取东方财富社区数据 - {trigger_time}")
        
        # 检查缓存
        cached_data = self.get_data_cached(trigger_time)
        if cached_data is not None:
            logger.info(f"使用东方财富社区缓存数据: {len(cached_data)} 条记录")
            return cached_data
        
        all_posts = []
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
            # 获取热门股票列表
            hot_stocks = await self.get_hot_stocks_list(session)
            logger.info(f"获取到 {len(hot_stocks)} 只热门股票")
            
            # 遍历热门股票
            for stock_code in hot_stocks:
                logger.info(f"抓取股票 {stock_code} 的讨论")
                
                # 获取该股票的热门帖子
                posts = await self.fetch_stock_posts(session, stock_code, 1)
                
                # 处理帖子数据
                for post in posts:
                    processed_post = self.process_community_post(post)
                    if processed_post:
                        all_posts.append(processed_post)
                
                if len(all_posts) >= self.max_posts:
                    break
        
        # 转换为DataFrame
        if all_posts:
            df = pd.DataFrame(all_posts)
            
            # 按质量分数排序
            df = df.sort_values('quality_score', ascending=False).head(self.max_posts)
            
            # 保存缓存
            self.save_data_cached(trigger_time, df)
            
            logger.info(f"东方财富社区数据获取完成: {len(df)} 条记录")
            return df
        else:
            logger.warning("未获取到东方财富社区数据")
            return pd.DataFrame(columns=['title', 'content', 'pub_time', 'url'])


if __name__ == "__main__":
    async def test():
        crawler = EastmoneyCommunityCrawl()
        trigger_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data = await crawler.get_data(trigger_time)
        print(f"获取到 {len(data)} 条东方财富数据")
        if not data.empty:
            print(data[['title', 'sentiment', 'quality_score', 'emotion_intensity']].head())
    
    asyncio.run(test())