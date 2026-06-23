#!/usr/bin/env python3
"""
配图生成脚本（matplotlib版本）
使用matplotlib生成专业架构图、流程图等
适用于Word文档插入（A4纸打印优化）
"""

import os
import json
import argparse
import matplotlib
matplotlib.use('Agg')  # 非交互式后端
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import numpy as np

# 设置中文字体（WSL环境下WenQuanYi Zen Hei更可靠）
plt.rcParams['font.sans-serif'] = ['WenQuanYi Zen Hei', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 专业配色方案
COLORS = {
    'primary': '#2E86AB',      # 主色调-蓝色
    'secondary': '#A23B72',    # 辅助色-紫色
    'accent': '#F18F01',       # 强调色-橙色
    'success': '#2D6A4F',      # 成功色-绿色
    'light': '#F8F9FA',        # 浅色背景
    'dark': '#212529',         # 深色文字
    'white': '#FFFFFF',        # 白色
    'gray': '#6C757D',         # 灰色
}

def create_architecture_diagram(project_info=None):
    """创建系统架构图"""
    fig, ax = plt.subplots(1, 1, figsize=(10, 7.5))
    
    ax.set_title('系统架构图', fontsize=16, fontweight='bold', pad=20)
    
    # 定义层级
    layers = [
        ('表示层', ['用户界面', 'Vue3 + TypeScript', 'Ant Design Vue'], COLORS['primary']),
        ('业务逻辑层', ['状态管理', '路由管理', '功能模块'], COLORS['secondary']),
        ('数据处理层', ['Python数据处理', 'Pandas/NumPy', 'SQLite数据库'], COLORS['success']),
        ('桌面应用层', ['Electron框架', 'Node.js运行时', 'IPC通信'], COLORS['accent']),
    ]
    
    y_positions = np.linspace(0.85, 0.15, len(layers))
    layer_height = 0.15
    layer_width = 0.8
    
    for i, (layer_name, components, color) in enumerate(layers):
        y = y_positions[i]
        
        # 绘制层级背景
        rect = FancyBboxPatch((0.1, y - layer_height/2), layer_width, layer_height,
                             boxstyle="round,pad=0.02", 
                             facecolor=color, alpha=0.3, 
                             edgecolor=color, linewidth=2)
        ax.add_patch(rect)
        
        # 添加层级名称
        ax.text(0.15, y, layer_name, fontsize=12, fontweight='bold',
                verticalalignment='center', color=COLORS['dark'])
        
        # 添加组件
        component_text = ' | '.join(components)
        ax.text(0.5, y, component_text, fontsize=10,
                verticalalignment='center', horizontalalignment='center',
                color=COLORS['dark'])
        
        # 绘制连接箭头
        if i < len(layers) - 1:
            next_y = y_positions[i + 1]
            ax.annotate('', xy=(0.5, next_y + layer_height/2 + 0.02),
                       xytext=(0.5, y - layer_height/2 - 0.02),
                       arrowprops=dict(arrowstyle='->', color=COLORS['gray'], lw=2))
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    
    # 添加图例
    legend_elements = [mpatches.Patch(facecolor=color, alpha=0.3, label=name)
                      for name, _, color in layers]
    ax.legend(handles=legend_elements, loc='lower right', 
             bbox_to_anchor=(0.98, 0.02), fontsize=9)
    
    plt.tight_layout()
    return fig

def create_data_flow_diagram(project_info=None):
    """创建数据流向图"""
    fig, ax = plt.subplots(1, 1, figsize=(10, 5))
    
    ax.set_title('数据流向图', fontsize=16, fontweight='bold', pad=20)
    
    nodes = [
        ('数据输入', ['CSV', 'Excel', 'JSON'], 0.1),
        ('数据处理', ['解析', '映射', '验证', '清洗'], 0.35),
        ('数据存储', ['SQLite', '数据集'], 0.6),
        ('数据应用', ['分析', '可视化', '导出'], 0.85),
    ]
    
    node_height = 0.6
    y_center = 0.5
    
    for i, (node_name, components, x_center) in enumerate(nodes):
        rect = FancyBboxPatch((x_center - 0.08, y_center - node_height/2), 
                             0.16, node_height,
                             boxstyle="round,pad=0.02",
                             facecolor=COLORS['primary'], alpha=0.2,
                             edgecolor=COLORS['primary'], linewidth=2)
        ax.add_patch(rect)
        
        ax.text(x_center, y_center + 0.25, node_name, 
                fontsize=11, fontweight='bold',
                horizontalalignment='center', verticalalignment='center',
                color=COLORS['dark'])
        
        component_text = '\n'.join(components)
        ax.text(x_center, y_center - 0.1, component_text,
                fontsize=9, horizontalalignment='center',
                verticalalignment='center', color=COLORS['dark'])
        
        if i < len(nodes) - 1:
            next_x = nodes[i + 1][2]
            ax.annotate('', xy=(next_x - 0.08, y_center),
                       xytext=(x_center + 0.08, y_center),
                       arrowprops=dict(arrowstyle='->', 
                                     color=COLORS['accent'], lw=2))
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    
    plt.tight_layout()
    return fig

def create_module_diagram(project_info=None):
    """创建功能模块图"""
    fig, ax = plt.subplots(1, 1, figsize=(10, 7.5))
    
    ax.set_title('功能模块图', fontsize=16, fontweight='bold', pad=20)
    
    modules = [
        ('项目管理', ['创建项目', '项目列表', '项目详情'], 0.2, 0.8),
        ('数据导入', ['文件上传', '数据预览', '字段映射'], 0.5, 0.8),
        ('数据治理', ['数据清洗', '数据校验', '脚本执行'], 0.8, 0.8),
        ('数据资源', ['数据集浏览', '数据集详情', '数据集操作'], 0.2, 0.4),
        ('统计分析', ['数据查询', '图表分析'], 0.5, 0.4),
        ('数据导出', ['格式选择', '条件设置', '导出执行'], 0.8, 0.4),
    ]
    
    module_width = 0.25
    module_height = 0.3
    
    for module_name, functions, x_center, y_center in modules:
        rect = FancyBboxPatch((x_center - module_width/2, y_center - module_height/2),
                             module_width, module_height,
                             boxstyle="round,pad=0.02",
                             facecolor=COLORS['secondary'], alpha=0.2,
                             edgecolor=COLORS['secondary'], linewidth=2)
        ax.add_patch(rect)
        
        ax.text(x_center, y_center + 0.1, module_name,
                fontsize=11, fontweight='bold',
                horizontalalignment='center', verticalalignment='center',
                color=COLORS['dark'])
        
        function_text = '\n'.join(functions[:3])
        ax.text(x_center, y_center - 0.05, function_text,
                fontsize=8, horizontalalignment='center',
                verticalalignment='center', color=COLORS['gray'])
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    
    plt.tight_layout()
    return fig

def create_tech_stack_diagram(project_info=None):
    """创建技术栈图"""
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))
    
    ax.set_title('技术栈图', fontsize=16, fontweight='bold', pad=20)
    
    tech_stacks = [
        ('前端技术', ['Vue3', 'TypeScript', 'Ant Design', 'Tailwind CSS', 'Pinia'], 
         COLORS['primary'], 0.25),
        ('后端技术', ['Python', 'FastAPI', 'Pandas', 'NumPy', 'SQLite'], 
         COLORS['success'], 0.5),
        ('桌面应用', ['Electron', 'Node.js', 'IPC通信'], 
         COLORS['accent'], 0.75),
    ]
    
    stack_width = 0.25
    stack_height = 0.7
    
    for stack_name, technologies, color, x_center in tech_stacks:
        rect = FancyBboxPatch((x_center - stack_width/2, 0.15), 
                             stack_width, stack_height,
                             boxstyle="round,pad=0.02",
                             facecolor=color, alpha=0.2,
                             edgecolor=color, linewidth=2)
        ax.add_patch(rect)
        
        ax.text(x_center, 0.8, stack_name,
                fontsize=12, fontweight='bold',
                horizontalalignment='center', verticalalignment='center',
                color=COLORS['dark'])
        
        tech_text = '\n'.join(technologies)
        ax.text(x_center, 0.45, tech_text,
                fontsize=9, horizontalalignment='center',
                verticalalignment='center', color=COLORS['dark'])
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    
    plt.tight_layout()
    return fig

def save_diagram(fig, output_path, dpi=300):
    """保存图表为PNG"""
    fig.savefig(output_path, dpi=dpi, bbox_inches='tight', 
               facecolor=COLORS['white'], edgecolor='none')
    plt.close(fig)
    print(f"  保存到: {output_path}")

def generate_all_diagrams(project_info, output_dir):
    """生成所有配图"""
    os.makedirs(output_dir, exist_ok=True)
    
    diagrams = [
        ("architecture", create_architecture_diagram, "架构图"),
        ("data_flow", create_data_flow_diagram, "数据流向图"),
        ("module", create_module_diagram, "功能模块图"),
        ("tech_stack", create_tech_stack_diagram, "技术栈图"),
    ]
    
    results = {}
    for name, create_func, desc in diagrams:
        print(f"生成 {desc}...")
        fig = create_func(project_info)
        filepath = os.path.join(output_dir, f"{name}.png")
        save_diagram(fig, filepath)
        results[name] = {"success": True, "path": filepath}
    
    return results

def main():
    parser = argparse.ArgumentParser(description='生成配图（matplotlib版本）')
    parser.add_argument('--project-info', help='项目信息JSON文件路径（可选）')
    parser.add_argument('--output-dir', required=True, help='输出目录')
    parser.add_argument('--diagram-type', 
                       choices=['all', 'architecture', 'data_flow', 'tech_stack', 'module'], 
                       default='all', help='配图类型')
    parser.add_argument('--dpi', type=int, default=300, help='输出分辨率')
    args = parser.parse_args()
    
    # 读取项目信息（可选）
    project_info = None
    if args.project_info and os.path.exists(args.project_info):
        with open(args.project_info, 'r', encoding='utf-8') as f:
            project_info = json.load(f)
    
    # 创建输出目录
    os.makedirs(args.output_dir, exist_ok=True)
    
    # 生成配图
    if args.diagram_type == 'all':
        results = generate_all_diagrams(project_info, args.output_dir)
        print(f"\n配图生成结果:")
        for name, result in results.items():
            status = "成功" if result["success"] else "失败"
            print(f"  {name}: {status}")
    else:
        func_map = {
            'architecture': create_architecture_diagram,
            'data_flow': create_data_flow_diagram,
            'tech_stack': create_tech_stack_diagram,
            'module': create_module_diagram,
        }
        fig = func_map[args.diagram_type](project_info)
        filepath = os.path.join(args.output_dir, f"{args.diagram_type}.png")
        save_diagram(fig, filepath, args.dpi)
        print(f"配图生成成功: {filepath}")

if __name__ == '__main__':
    main()
