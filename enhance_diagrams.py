#!/usr/bin/env python3
import re
import os
import glob

def create_enhanced_flowchart(title, description, nodes, relationships, color_scheme="blue"):
    """创建增强的流程图HTML"""

    color_schemes = {
        "blue": {
            "gradient": "linear-gradient(135deg, #74b9ff 0%, #0984e3 100%)",
            "node_bg": "#6c5ce7",
            "data_bg": "#00b894",
            "pointer_bg": "#6c5ce7"
        },
        "purple": {
            "gradient": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
            "node_bg": "#a29bfe",
            "data_bg": "#fd79a8",
            "pointer_bg": "#6c5ce7"
        },
        "green": {
            "gradient": "linear-gradient(135deg, #00b894 0%, #00cec9 100%)",
            "node_bg": "#00b894",
            "data_bg": "#74b9ff",
            "pointer_bg": "#fd79a8"
        },
        "orange": {
            "gradient": "linear-gradient(135deg, #fdcb6e 0%, #e17055 100%)",
            "node_bg": "#fd79a8",
            "data_bg": "#6c5ce7",
            "pointer_bg": "#74b9ff"
        }
    }

    scheme = color_schemes.get(color_scheme, color_schemes["blue"])

    html = f'''#### 🎯 {title}

<div style="background: {scheme['gradient']}; padding: 25px; border-radius: 15px; margin: 20px 0; color: white; box-shadow: 0 8px 32px rgba(0,0,0,0.3);">

<div style="text-align: center; margin-bottom: 20px;">
<div style="font-size: 20px; font-weight: bold; margin-bottom: 10px;">📊 {title}</div>
<div style="font-size: 14px; opacity: 0.9;">{description}</div>
</div>

<div style="display: flex; justify-content: center; align-items: center; gap: 15px; flex-wrap: wrap; margin: 25px 0;">
'''

    # 添加节点
    for i, node in enumerate(nodes):
        node_id = node.get('id', f'节点{i+1}')
        node_desc = node.get('desc', node_id)
        node_data = node.get('data', '')

        html += f'''
<!-- {node_id} -->
<div style="background: rgba(255,255,255,0.15); backdrop-filter: blur(10px); border-radius: 12px; padding: 15px; text-align: center; min-width: 120px; border: 2px solid rgba(255,255,255,0.3);">
<div style="font-weight: bold; color: #FFD700; margin-bottom: 8px;">{node_id}</div>
'''
        if node_data:
            html += f'''<div style="background: {scheme['data_bg']}; padding: 8px; border-radius: 8px; margin-bottom: 8px;">
<div style="font-size: 12px; opacity: 0.8;">数据</div>
<div style="font-size: 18px; font-weight: bold;">{node_data}</div>
</div>'''

        html += f'''<div style="font-size: 14px; margin-top: 5px;">{node_desc}</div>
</div>'''

        # 添加箭头（除了最后一个节点）
        if i < len(nodes) - 1:
            html += '\n<div style="font-size: 24px; color: #FFD700;">➡️</div>'

    html += '''
</div>

<div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; text-align: center;">
<div style="font-size: 16px; font-weight: bold; margin-bottom: 10px;">🔄 处理流程</div>
<div style="display: flex; justify-content: center; gap: 15px; flex-wrap: wrap;">
'''

    # 添加关系流程
    for rel in relationships:
        html += f'<span style="background: rgba(255,255,255,0.2); padding: 8px 12px; border-radius: 8px; font-size: 14px;">{rel}</span>'

    html += '''
</div>
</div>

</div>'''

    return html

def create_enhanced_sequence_diagram(title, description, steps, color_scheme="pink"):
    """创建增强的序列图HTML"""

    color_schemes = {
        "pink": {
            "gradient": "linear-gradient(135deg, #fd79a8 0%, #e84393 100%)",
            "step_bg": "#6c5ce7"
        },
        "blue": {
            "gradient": "linear-gradient(135deg, #74b9ff 0%, #0984e3 100%)",
            "step_bg": "#00b894"
        }
    }

    scheme = color_schemes.get(color_scheme, color_schemes["pink"])

    html = f'''#### 🎬 {title}

<div style="background: {scheme['gradient']}; padding: 25px; border-radius: 15px; margin: 20px 0; color: white; box-shadow: 0 8px 32px rgba(0,0,0,0.3);">

<div style="text-align: center; margin-bottom: 20px;">
<div style="font-size: 20px; font-weight: bold; margin-bottom: 10px;">📋 {title}</div>
<div style="font-size: 14px; opacity: 0.9;">{description}</div>
</div>

<div style="background: rgba(255,255,255,0.1); padding: 20px; border-radius: 12px;">
<div style="display: grid; grid-template-columns: auto 1fr auto 1fr auto; gap: 15px; align-items: center;">
<div style="font-weight: bold; text-align: center; color: #FFD700;">步骤</div>
<div style="font-weight: bold; text-align: center; color: #FFD700;">参与者</div>
<div style="font-weight: bold; text-align: center; color: #FFD700;">操作</div>
<div style="font-weight: bold; text-align: center; color: #FFD700;">目标</div>
<div style="font-weight: bold; text-align: center; color: #FFD700;">说明</div>
'''

    for i, step in enumerate(steps, 1):
        participant = step.get('participant', '')
        action = step.get('action', '发送')
        target = step.get('target', '')
        desc = step.get('desc', '')

        html += f'''
<div style="background: {scheme['step_bg']}; padding: 8px; border-radius: 8px; text-align: center; font-weight: bold;">{i}</div>
<div style="background: rgba(255,255,255,0.1); padding: 8px; border-radius: 8px; text-align: center;">{participant}</div>
<div style="background: rgba(255,255,255,0.1); padding: 8px; border-radius: 8px; text-align: center;">{action}</div>
<div style="background: rgba(255,255,255,0.1); padding: 8px; border-radius: 8px; text-align: center;">{target}</div>
<div style="background: rgba(255,255,255,0.1); padding: 8px; border-radius: 8px; text-align: center;">{desc}</div>
'''

    html += '''
</div>
</div>

</div>'''

    return html

def enhance_specific_articles():
    """增强特定文章的图表"""

    enhancements = {
        "data-structure-05-stack.md": {
            "patterns": [
                {
                    "old": r"#### 流程图表\n\n\*\[Mermaid图表已转换为表格形式\]\*",
                    "new": create_enhanced_flowchart(
                        "栈结构可视化",
                        "后进先出（LIFO）：最后放入的元素最先取出",
                        [
                            {"id": "栈顶", "desc": "Top指针", "data": "30"},
                            {"id": "中间", "desc": "栈元素", "data": "20"},
                            {"id": "栈底", "desc": "Bottom", "data": "10"}
                        ],
                        ["元素入栈 ➡️ 栈顶", "元素出栈 ⬅️ 栈顶", "后进先出原则"],
                        "orange"
                    )
                }
            ]
        },

        "algorithm-02-trie.md": {
            "patterns": [
                {
                    "old": r"#### 流程图表\n\n\*\[Mermaid图表已转换为表格形式\]\*",
                    "new": create_enhanced_flowchart(
                        "Trie树结构可视化",
                        "字典树：高效的字符串搜索数据结构",
                        [
                            {"id": "根节点", "desc": "Root", "data": "''"},
                            {"id": "第一层", "desc": "字符节点", "data": "a,b,c"},
                            {"id": "叶子节点", "desc": "单词结束", "data": "word"}
                        ],
                        ["插入字符串", "逐字符建立路径", "标记单词结束"],
                        "green"
                    )
                }
            ]
        },

        "distributed-02-cap-theorem.md": {
            "patterns": [
                {
                    "old": r"#### 流程图表\n\n\*\[Mermaid图表已转换为表格形式\]\*",
                    "new": create_enhanced_flowchart(
                        "CAP定理三角关系",
                        "分布式系统只能同时满足其中两个特性",
                        [
                            {"id": "一致性", "desc": "Consistency", "data": "C"},
                            {"id": "可用性", "desc": "Availability", "data": "A"},
                            {"id": "分区容错", "desc": "Partition", "data": "P"}
                        ],
                        ["CA: 传统数据库", "CP: 强一致系统", "AP: 高可用系统"],
                        "purple"
                    )
                }
            ]
        }
    }

    return enhancements

def process_file(filepath, enhancements):
    """处理单个文件"""
    print(f"处理文件: {filepath}")

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    modified = False

    # 通用替换：将所有简单的流程图表转换为增强版本
    simple_pattern = r'#### 流程图表\n\n\*\[Mermaid图表已转换为表格形式\]\*'
    if re.search(simple_pattern, content):
        # 根据文件名确定主题
        filename = os.path.basename(filepath)
        if "data-structure" in filename:
            title = "数据结构可视化"
            desc = "直观展示数据结构的组织方式和操作过程"
            color = "blue"
        elif "algorithm" in filename:
            title = "算法流程可视化"
            desc = "展示算法的执行步骤和处理逻辑"
            color = "green"
        elif "distributed" in filename:
            title = "分布式系统架构图"
            desc = "展示分布式系统的组件和交互关系"
            color = "purple"
        else:
            title = "流程图表"
            desc = "系统流程和数据流向展示"
            color = "blue"

        enhanced_chart = f'''#### 🎯 {title}

<div style="background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%); padding: 25px; border-radius: 15px; margin: 20px 0; color: white; box-shadow: 0 8px 32px rgba(0,0,0,0.3);">

<div style="text-align: center; margin-bottom: 20px;">
<div style="font-size: 20px; font-weight: bold; margin-bottom: 10px;">📊 {title}</div>
<div style="font-size: 14px; opacity: 0.9;">{desc}</div>
</div>

<div style="background: rgba(255,255,255,0.1); padding: 20px; border-radius: 12px; text-align: center;">
<div style="font-size: 18px; font-weight: bold; margin-bottom: 15px;">🔍 详细内容</div>
<div style="font-size: 16px; line-height: 1.6;">
此图表展示了相关概念的核心要点和处理流程。<br/>
通过可视化的方式帮助理解复杂的技术概念，<br/>
让学习过程更加直观和高效。
</div>
</div>

<div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; text-align: center; margin-top: 15px;">
<div style="font-size: 16px; font-weight: bold; margin-bottom: 8px;">💡 学习建议</div>
<div style="font-size: 14px; opacity: 0.9;">结合代码实例和实际应用场景来理解概念</div>
</div>

</div>'''

        content = re.sub(simple_pattern, enhanced_chart, content)
        modified = True

    # 应用特定文件的增强
    filename = os.path.basename(filepath)
    if filename in enhancements:
        for pattern in enhancements[filename]["patterns"]:
            if re.search(pattern["old"], content):
                content = re.sub(pattern["old"], pattern["new"], content)
                modified = True

    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✓ 已增强图表显示")
        return True
    else:
        print(f"  - 无需处理")
        return False

def main():
    """主函数"""
    print("🎨 开始增强文章图表显示...")

    # 获取所有markdown文件
    md_files = glob.glob('content/posts/*.md')

    # 获取增强配置
    enhancements = enhance_specific_articles()

    enhanced_count = 0

    for filepath in md_files:
        if process_file(filepath, enhancements):
            enhanced_count += 1

    print(f"\n✅ 总计增强了 {enhanced_count} 个文件的图表显示")

if __name__ == "__main__":
    main()