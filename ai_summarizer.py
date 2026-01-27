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


class AITagger:
    """
    智谱 AI 标签生成器
    """
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
        self.model = "glm-4.7-flash"

    def generate_tags(self, content: str) -> list[str]:
        """
        根据内容生成标签
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        prompt = """You are a bot in a read-it-later app and your responsibility is to help with automatic tagging.
Please analyze the text provided below and suggest relevant tags that describe its key themes, topics, and main ideas. The rules are:
- Aim for a variety of tags, including broad categories, specific keywords, and potential sub-genres.
- The tags language must be in chinese.
- If it's a famous website you may also include a tag for the website. If the tag is not generic enough, don't include it.
- The content can include text for cookie consent and privacy policy, ignore those while tagging.
- Aim for 3-5 tags.
- If there are no good tags, leave the array empty.

CONTENT START HERE
{content}
CONTENT END HERE

You must respond in JSON with the key "tags" and the value is an array of string tags.
"""
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "你是一个有用的AI助手。"
                },
                {
                    "role": "user",
                    "content": prompt.replace("{content}", content)
                }
            ],
            "stream": False,
            "temperature": 0.1
        }

        try:
            print(f"   🏷️ 正在请求 AI 标签...")
            response = requests.post(self.url, headers=headers, json=payload, timeout=30)
            if response.status_code != 200:
                print(f"   ⚠️ 标签请求失败: {response.status_code} - {response.text}")
                return []
                
            data = response.json()
            if "choices" in data and len(data["choices"]) > 0:
                content_str = data["choices"][0]["message"]["content"]
                # 尝试提取 JSON
                try:
                    # 某些情况下 AI 可能返回 ```json ... ``` 包裹
                    json_match = re.search(r'\{.*\}', content_str, re.DOTALL)
                    if json_match:
                        json_content = json_match.group(0)
                        tags_obj = json.loads(json_content)
                        return tags_obj.get("tags", [])
                except Exception as e:
                    print(f"   ⚠️ 标签解析失败: {e}")
                    
            return []
            
        except Exception as e:
            print(f"   ⚠️ 标签处理异常: {e}")
            return []


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
    dedao_token = os.getenv('DEDAO_API_TOKEN')
    zhipu_key = os.getenv('ZHIPU_API_KEY')
    
    if not dedao_token:
        print("❌ 未找到 DEDAO_API_TOKEN，跳过 AI 总结步骤")
        return

    ai_summarizer = AISummarizer(dedao_token)
    
    ai_tagger = None
    if zhipu_key:
        ai_tagger = AITagger(zhipu_key)
        print("✨ 已启用 AI 自动标签 (Zhipu)")
    
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
        
def inject_tags_into_frontmatter(content: str, tags: list[str]) -> str:
    """
    将标签插入到 FrontMatter 中
    """
    if not tags:
        return content
        
    # Check for FrontMatter
    fm_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not fm_match:
        # No FM, create one
        fm = "---\n"
        fm += "tags:\n"
        for tag in tags:
            fm += f"  - {tag}\n"
        fm += "---\n\n"
        return fm + content
        
    fm_content = fm_match.group(1)
    
    # Check if tags key exists
    if re.search(r'^tags:', fm_content, re.MULTILINE):
        # Insert after "tags:"
        # We assume standard yaml formatting created by our own script: "tags:\n"
        new_tags_str = ""
        for tag in tags:
            new_tags_str += f"  - {tag}\n"
            
        # Replace "tags:\n" with "tags:\n  - tag1\n..."
        # Use a safe replacement that looks for the line ending
        new_fm_content = re.sub(r'(^tags:\s*\n)', rf'\1{new_tags_str}', fm_content, flags=re.MULTILINE)
        
        # If the regex didn't match (maybe inline tags: []), fallback to appending
        if new_fm_content == fm_content:
             # Try to match tags: without newline
             pass 
    else:
        # Add tags key to end of FM
        new_tags_block = "\ntags:\n"
        for tag in tags:
            new_tags_block += f"  - {tag}\n"
        new_fm_content = fm_content + new_tags_block

    return content.replace(fm_match.group(1), new_fm_content)


def process_files(output_dir: str = '30_Resources/Raindrop', days: int = 3):
    """
    扫描并处理文件
    优先读取 new_files_list.txt，如果不存在则扫描目录
    """
    dedao_token = os.getenv('DEDAO_API_TOKEN')
    zhipu_key = os.getenv('ZHIPU_API_KEY')
    
    if not dedao_token:
        print("❌ 未找到 DEDAO_API_TOKEN，跳过 AI 总结步骤")
        return

    ai_summarizer = AISummarizer(dedao_token)
    
    ai_tagger = None
    if zhipu_key:
        ai_tagger = AITagger(zhipu_key)
        print("✨ 已启用 AI 自动标签 (Zhipu)")
    
    directory = Path(output_dir)
    if not directory.exists():
        print(f"❌ 目录不存在: {directory}")
        return

    # Check for report file
    workspace = os.getenv('GITHUB_WORKSPACE', '.')
    report_file = Path(workspace) / 'new_files_list.txt'
    target_files = []
    
    if report_file.exists():
        print(f"� 发现同步列表: {report_file}")
        try:
            with open(report_file, 'r', encoding='utf-8') as f:
                for line in f:
                    filename = line.strip()
                    if filename:
                        file_path = directory / filename
                        if file_path.exists():
                            target_files.append(file_path)
        except Exception as e:
            print(f"⚠️ 读取列表失败: {e}")
    else:
        print(f"🔍 同步列表不存在，跳过 AI 处理")


    print(f"🎯 待处理文件数: {len(target_files)}")
    
    count = 0
    processed = 0
    
    for file_path in target_files:
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
        
        # 1. 调用 AI 总结
        title, content = ai_summarizer.summarize(url)
        
        if content:
            # 2. 调用 AI 标签 (如果有内容)
            tags = []
            if ai_tagger:
                # 使用生成的总结内容作为输入，节省 Token 且更精准
                tags = ai_tagger.generate_tags(content[:2000]) # 限制长度防止超长
            
            try:
                # 读取原文件内容
                file_content = file_path.read_text(encoding='utf-8')
                
                # 注入标签到 FrontMatter
                if tags:
                    file_content = inject_tags_into_frontmatter(file_content, tags)
                    print(f"   🏷️  注入标签: {tags}")

                # 追加总结内容
                summary_block = f"\n\n## 🤖 AI 深度总结\n\n"
                if title:
                    summary_block += f"**{title}**\n\n"
                summary_block += f"{content}\n"
                
                # 写入更新后的内容
                file_path.write_text(file_content + summary_block, encoding='utf-8')
                        
                print(f"   ✅ 已更新文件")
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
