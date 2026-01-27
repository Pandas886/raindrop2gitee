#!/usr/bin/env python3
"""
AI 总结生成脚本
扫描 Raindrop 生成的 Markdown 文件，对缺失 AI 总结的文件调用接口补充内容。
"""

import os
import sys
import json
import time
import requests
import re
from pathlib import Path
from datetime import datetime, timedelta

class AISummarizer:
    """
    得到/罗辑实验室 AI 总结器
    """
    def __init__(self, api_token: str):
        self.api_token = api_token
        self.url = "https://get-notes.luojilab.com/voicenotes/web/notes/stream"
        
    def summarize(self, target_url: str) -> tuple[str, str]:
        """
        调用 AI 接口生成总结
        返回: (title, content)
        """
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "X-Request-ID": str(int(time.time() * 1000)),
            "Content-Type": "application/json"
        }
        
        payload = {
            "attachments": [
                {
                    "size": 100,
                    "type": "link",
                    "title": "",
                    "url": target_url
                }
            ],
            "content": "",
            "entry_type": "ai",
            "note_type": "link",
            "source": "web",
            "prompt_template_id": ""
        }
        
        full_title = ""
        full_content = ""
        
        try:
            print(f"   🤖 正在请求 AI 总结: {target_url}")
            with requests.post(self.url, headers=headers, json=payload, stream=True) as response:
                if response.status_code != 200:
                    print(f"   ⚠️ AI 请求失败: {response.status_code} - {response.text}")
                    return "", ""
                
                for line in response.iter_lines():
                    if not line:
                        continue
                        
                    decoded_line = line.decode('utf-8')
                    if decoded_line.startswith("data: "):
                        json_str = decoded_line[6:] # Remove 'data: ' prefix
                        try:
                            # 某些心跳包可能是空或者只包含 id
                            if not json_str.strip() or json_str.strip() == "[DONE]":
                                continue
                                
                            data_obj = json.loads(json_str)
                            # Parse inner data
                            if "data" in data_obj and isinstance(data_obj["data"], dict) and "msg" in data_obj["data"]:
                                inner_msg_str = data_obj["data"]["msg"]
                                try:
                                    inner_msg = json.loads(inner_msg_str)
                                    
                                    # Accumulate title
                                    if "summary_title" in inner_msg:
                                        full_title += inner_msg["summary_title"]
                                        
                                    # Accumulate content
                                    if "content" in inner_msg:
                                        full_content += inner_msg["content"]
                                except (json.JSONDecodeError, TypeError):
                                    pass # Ignore non-json inner msg
                        except json.JSONDecodeError:
                            pass
                            
            return full_title, full_content
            
        except Exception as e:
            print(f"   ⚠️ AI 处理异常: {e}")
            return "", ""

def extract_url_from_file(file_path: Path) -> str:
    """
    从 Markdown 文件中提取 URL
    """
    try:
        content = file_path.read_text(encoding='utf-8')
        
        # 1. 尝试从 FrontMatter 提取 url: https://...
        match = re.search(r'^url:\s*(.+)$', content, re.MULTILINE)
        if match:
            return match.group(1).strip()
            
        # 2. 尝试从正文提取 🔗 [url](https://...)
        match = re.search(r'🔗 \[(.*?)\]\((http.*?)\)', content)
        if match:
            return match.group(2).strip()
            
    except Exception as e:
        print(f"   读取文件失败: {e}")
    
    return ""

def has_ai_summary(file_path: Path) -> bool:
    """
    检查文件是否已经包含 AI 总结
    """
    try:
        content = file_path.read_text(encoding='utf-8')
        return "## 🤖 AI 深度总结" in content
    except:
        return False

def process_files(output_dir: str = '30_Resources/Raindrop', days: int = 3):
    """
    扫描并处理文件
    """
    api_token = os.getenv('DEDAO_API_TOKEN')
    if not api_token:
        print("❌ 未找到 DEDAO_API_TOKEN，跳过 AI 总结步骤")
        return

    ai = AISummarizer(api_token)
    directory = Path(output_dir)
    
    if not directory.exists():
        print(f"❌ 目录不存在: {directory}")
        return

    print(f"🔍 开始扫描目录: {directory}")
    print(f"   处理最近 {days} 天修改的文件")

    # 计算时间阈值
    cutoff_time = datetime.now() - timedelta(days=days)
    
    count = 0
    processed = 0
    
    for file_path in directory.glob('*.md'):
        # 过滤修改时间
        mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
        if mtime < cutoff_time:
            continue
            
        count += 1
        
        # 检查是否已有总结
        if has_ai_summary(file_path):
            continue
            
        # 提取 URL
        url = extract_url_from_file(file_path)
        if not url:
            print(f"⏩ 跳过 (无URL): {file_path.name}")
            continue
            
        print(f"👉 处理: {file_path.name}")
        
        # 调用 AI
        title, content = ai.summarize(url)
        
        if content:
            try:
                with open(file_path, 'a', encoding='utf-8') as f:
                    f.write(f"\n\n## 🤖 AI 深度总结\n\n")
                    if title:
                        f.write(f"**{title}**\n\n")
                    f.write(f"{content}\n")
                print(f"   ✅ 已追加总结")
                processed += 1
                # 避免触发频率限制，简单休眠
                time.sleep(2)
            except Exception as e:
                print(f"   ❌ 写入失败: {e}")
        else:
            print(f"   ⏩ 跳过 (AI未返回内容)")

    print(f"\n📊 AI 处理完成: 扫描 {count} 个文件, 处理 {processed} 个")

if __name__ == '__main__':
    # 获取环境变量或使用默认值
    output_dir = os.getenv('OUTPUT_DIR', '30_Resources') + '/Raindrop'
    process_files(output_dir)
