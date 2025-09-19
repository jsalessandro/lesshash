#!/usr/bin/env python3
import re
import os
import glob

def convert_mermaid_to_markdown(content):
    """将Mermaid图表转换为Markdown表格"""

    # 查找所有Mermaid代码块
    pattern = r'```mermaid\n(.*?)```'

    def replace_mermaid(match):
        mermaid_content = match.group(1)

        # 分析Mermaid内容并生成相应的Markdown表格
        if 'flowchart' in mermaid_content or 'graph' in mermaid_content:
            # 简单的流程图转换
            lines = mermaid_content.split('\n')

            # 提取节点和关系
            nodes = []
            relations = []

            for line in lines:
                if '-->' in line or '-.->|' in line or '-->|' in line:
                    # 这是一个关系
                    relations.append(line.strip())
                elif '[' in line and ']' in line:
                    # 这是一个节点定义
                    nodes.append(line.strip())

            # 生成表格
            table = "#### 流程图表\n\n"

            if nodes:
                table += "**节点说明：**\n\n"
                table += "| 节点 | 描述 |\n"
                table += "|------|------|\n"

                for node in nodes[:10]:  # 限制显示前10个节点
                    # 提取节点信息
                    node_match = re.search(r'(\w+)\["?([^"\]]+)"?\]', node)
                    if node_match:
                        node_id = node_match.group(1)
                        node_desc = node_match.group(2).replace('<br/>', ' ')
                        table += f"| {node_id} | {node_desc} |\n"

            if relations:
                table += "\n**关系流向：**\n```\n"
                for rel in relations[:5]:  # 限制显示前5个关系
                    # 简化关系显示
                    rel_simple = rel.replace('-->', '→').replace('-.->|', '→').replace('-->|', '→')
                    table += f"{rel_simple}\n"
                table += "```"

            return table

        elif 'sequenceDiagram' in mermaid_content:
            # 序列图转换
            table = "#### 序列图\n\n"
            table += "| 步骤 | 参与者 | 动作 | 目标 | 说明 |\n"
            table += "|------|--------|------|------|------|\n"

            lines = mermaid_content.split('\n')
            step = 1
            for line in lines:
                if '->>' in line or '-->>' in line:
                    parts = re.split(r'->>|-->>|:', line)
                    if len(parts) >= 2:
                        from_actor = parts[0].strip()
                        to_actor = parts[1].strip() if len(parts) > 1 else ""
                        message = parts[2].strip() if len(parts) > 2 else ""
                        table += f"| {step} | {from_actor} | 发送 | {to_actor} | {message} |\n"
                        step += 1

            return table

        elif 'classDiagram' in mermaid_content:
            # 类图转换
            table = "#### 类图\n\n"
            table += "| 类名 | 属性 | 方法 | 关系 |\n"
            table += "|------|------|------|------|\n"
            # 简化处理
            table += "| 详见代码 | - | - | - |\n"
            return table

        else:
            # 其他类型的图表，生成通用表格
            return "#### 图表内容\n\n*[Mermaid图表已转换为表格形式]*\n"

    # 替换所有Mermaid块
    converted = re.sub(pattern, replace_mermaid, content, flags=re.DOTALL)
    return converted

def process_file(filepath):
    """处理单个文件"""
    print(f"处理文件: {filepath}")

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否包含Mermaid
    if '```mermaid' not in content:
        print(f"  跳过 - 不包含Mermaid图表")
        return False

    # 转换内容
    converted_content = convert_mermaid_to_markdown(content)

    # 写回文件
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(converted_content)

    print(f"  ✓ 已转换Mermaid图表")
    return True

def main():
    """主函数"""
    # 获取所有markdown文件
    md_files = glob.glob('content/posts/*.md')

    converted_count = 0

    for filepath in md_files:
        if process_file(filepath):
            converted_count += 1

    print(f"\n总计转换了 {converted_count} 个文件")

if __name__ == "__main__":
    main()