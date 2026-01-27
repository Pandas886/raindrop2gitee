#!/usr/bin/env python3
"""
Raindrop.io API 同步脚本
通过 API 获取最新的书签并转换为 Obsidian Markdown
"""

import os
import sys
import json
import requests
from datetime import datetime, timedelta
from pathlib import Path
import hashlib
import re


class RaindropSync:
    """
    Raindrop API 同步器
    """
    
    def __init__(self, api_token: str, output_dir: str = '30_Resources'):
        self.api_token = api_token
        self.base_url = 'https://api.raindrop.io/rest/v1'
        self.headers = {
            'Authorization': f'Bearer {api_token}',
            'Content-Type': 'application/json'
        }
        self.output_dir = Path(output_dir) / 'Raindrop'
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.created_files = []
    

    
    def sanitize_filename(self, text: str, max_length: int = 80) -> str:
        """
        清理文件名
        """
        text = re.sub(r'[<>:"/\\|?*]', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        text = text.strip('. ')
        if len(text) > max_length:
            text = text[:max_length].rsplit(' ', 1)[0]
        return text or 'untitled'
    
    
    def get_raindrops(self, days: int = 7) -> list:
        """
        获取最近 N 天的书签
        """
        all_raindrops = []
        page = 0
        per_page = 50
        
        # 计算时间范围
        since_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        while True:
            url = f"{self.base_url}/raindrops/0"
            params = {
                'page': page,
                'perpage': per_page,
                'sort': '-created'
            }
            
            try:
                response = requests.get(url, headers=self.headers, params=params)
                response.raise_for_status()
                data = response.json()
                
                items = data.get('items', [])
                if not items:
                    break
                
                # 过滤最近的书签
                for item in items:
                    created = item.get('created', '')
                    if created >= since_date:
                        all_raindrops.append(item)
                    else:
                        return all_raindrops  # 已经到达时间范围外
                
                page += 1
                
            except requests.exceptions.RequestException as e:
                print(f"❌ API 请求失败: {e}")
                break
        
        return all_raindrops
    
    def create_markdown(self, raindrop: dict) -> str:
        """
        创建 Markdown 内容
        """
        title = raindrop.get('title', 'Untitled')
        url = raindrop.get('link', '')
        excerpt = raindrop.get('excerpt', '').strip()
        note = raindrop.get('note', '').strip()
        highlights = raindrop.get('highlights', [])
        tags = raindrop.get('tags', [])
        created = raindrop.get('created', '')
        cover = raindrop.get('cover', '').strip()
        domain = raindrop.get('domain', '')
        collection = raindrop.get('collection', {})
        collection_title = collection.get('title', 'Unsorted') if isinstance(collection, dict) else 'Unsorted'
        important = raindrop.get('important', False)
        
        # 格式化日期
        try:
            dt = datetime.fromisoformat(created.replace('Z', '+00:00'))
            created_date = dt.strftime('%Y-%m-%d')
        except:
            created_date = created
        
        # 构建内容
        content = []
        
        # Front Matter
        content.append('---')
        content.append(f'title: "{title}"')
        content.append(f'url: {url}')
        content.append(f'domain: {domain}')
        content.append(f'created: {created_date}')
        content.append(f'source: raindrop')
        content.append(f'folder: {collection_title}')
        if tags:
            content.append('tags:')
            for tag in tags:
                content.append(f'  - {tag}')
        if important:
            content.append('favorite: true')
        content.append('---')
        content.append('')
        
        # 主要内容
        content.append(f'# {title}')
        content.append('')
        content.append(f'🔗 [{url}]({url})')
        content.append(f'📁 **分类**: {collection_title}')
        content.append(f'📅 **创建**: {created_date}')
        content.append('')
        
        if excerpt:
            content.append('## 📝 摘要')
            content.append('')
            content.append(excerpt)
            content.append('')
        
        if note:
            content.append('## 💡 我的笔记')
            content.append('')
            content.append(note)
            content.append('')
        
        # 处理高亮（API 返回的是数组）
        if highlights and len(highlights) > 0:
            content.append('## ✨ 高亮标注')
            content.append('')
            for highlight in highlights:
                if isinstance(highlight, dict):
                    text = highlight.get('text', '')
                    if text:
                        content.append(f'> {text}')
                        content.append('')
                elif isinstance(highlight, str):
                    content.append(f'> {highlight}')
                    content.append('')
        
        if cover:
            content.append('## 🖼️ 封面')
            content.append('')
            content.append(f'![cover]({cover})')
            content.append('')
        
        return '\n'.join(content)
    
    def sync(self, days: int = 7):
        """
        执行同步
        """
        print(f"🚀 开始同步最近 {days} 天的 Raindrop 书签...")
        
        # 获取书签
        raindrops = self.get_raindrops(days)
        print(f"📥 获取到 {len(raindrops)} 个书签")
        
        new_count = 0
        skipped_count = 0
        
        for raindrop in raindrops:
            raindrop_id = str(raindrop.get('_id', ''))
            
            try:
                title = raindrop.get('title', 'Untitled')
                url = raindrop.get('link', '')
                created = raindrop.get('created', '')
                collection = raindrop.get('collection', {})
                collection_title = collection.get('title', 'Unsorted') if isinstance(collection, dict) else 'Unsorted'
                
                # 格式化日期
                try:
                    dt = datetime.fromisoformat(created.replace('Z', '+00:00'))
                    created_date = dt.strftime('%Y-%m-%d')
                except:
                    created_date = datetime.now().strftime('%Y-%m-%d')
                
                # 生成文件名（扁平化存储）
                safe_title = self.sanitize_filename(title, max_length=60)
                base_filename = f"{created_date}-{safe_title}.md"
                
                # 检查文件是否存在，如果存在则跳过
                file_path = self.output_dir / base_filename
                if file_path.exists():
                    skipped_count += 1
                    print(f"⏩ 跳过 (文件已存在): {base_filename}")
                    continue
                
                filename = base_filename
                
                # 生成 Markdown
                markdown_content = self.create_markdown(raindrop)
                
                # 写入文件（扁平化存储）
                file_path = self.output_dir / filename
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(markdown_content)
                
                new_count += 1
                self.created_files.append(filename)
                print(f"✅ 新增: {filename}")
            
            except Exception as e:
                print(f"❌ 处理书签出错 ({raindrop_id}): {e}")
                continue
        
        # Write report file
        if self.created_files:
            workspace = os.getenv('GITHUB_WORKSPACE', '.')
            report_path = Path(workspace) / 'new_files_list.txt'
            
            try:
                with open(report_path, 'w', encoding='utf-8') as f:
                    for filename in self.created_files:
                        f.write(f"{filename}\n")
                print(f"📝 已生成文件列表: {report_path} ({len(self.created_files)} 个文件)")
            except Exception as e:
                print(f"❌ 写入列表失败: {e}")

        print(f"\n📊 同步完成:")
        print(f"   - 新增: {new_count} 个文件")
        print(f"   - 跳过: {skipped_count} 个文件")
        print(f"   - 输出目录: {self.output_dir}")


def main():
    """
    主函数
    """
    # 从环境变量获取 API Token
    api_token = os.getenv('RAINDROP_API_TOKEN')
    
    if not api_token:
        print("❌ 错误: 请设置环境变量 RAINDROP_API_TOKEN")
        print("   获取 Token: https://app.raindrop.io/settings/integrations")
        sys.exit(1)
    
    # 获取同步天数（默认 7 天）
    days = int(os.getenv('SYNC_DAYS', '7'))
    
    # 获取输出目录
    output_dir = os.getenv('OUTPUT_DIR', '30_Resources')
    
    # 执行同步
    syncer = RaindropSync(api_token, output_dir)
    syncer.sync(days)


if __name__ == '__main__':
    main()
