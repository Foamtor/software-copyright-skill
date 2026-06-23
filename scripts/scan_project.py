#!/usr/bin/env python3
"""
扫描项目结构，提取项目信息
输出JSON格式的项目信息
"""

import os
import json
import argparse
from pathlib import Path
from collections import defaultdict

# 忽略的目录和文件
IGNORE_DIRS = {
    'node_modules', '.git', '__pycache__', '.vscode', '.idea',
    'dist', 'build', 'target', 'bin', 'obj', '.next', '.nuxt',
    'vendor', 'venv', 'env', '.env', 'coverage', '.cache'
}

IGNORE_FILES = {
    '.gitignore', '.dockerignore', 'Dockerfile', 'docker-compose.yml',
    'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml',
    '.DS_Store', 'Thumbs.db'
}

# 代码文件扩展名
CODE_EXTENSIONS = {
    '.java', '.py', '.js', '.ts', '.jsx', '.tsx', '.vue', '.go',
    '.rs', '.cpp', '.c', '.h', '.hpp', '.cs', '.php', '.rb',
    '.swift', '.kt', '.scala', '.lua', '.r', '.m', '.sql'
}

CONFIG_EXTENSIONS = {
    '.xml', '.json', '.yaml', '.yml', '.toml', '.ini', '.cfg',
    '.properties', '.env', '.conf'
}

def scan_directory(path, max_depth=5, current_depth=0):
    """递归扫描目录结构"""
    result = {
        'name': os.path.basename(path),
        'type': 'directory',
        'children': []
    }
    
    if current_depth >= max_depth:
        return result
    
    try:
        entries = sorted(os.scandir(path), key=lambda e: (not e.is_dir(), e.name))
    except PermissionError:
        return result
    
    for entry in entries:
        if entry.name.startswith('.') and entry.name not in {'.env'}:
            continue
        if entry.name in IGNORE_DIRS:
            continue
        if entry.name in IGNORE_FILES:
            continue
            
        if entry.is_dir():
            child = scan_directory(entry.path, max_depth, current_depth + 1)
            if child['children']:  # 只包含非空目录
                result['children'].append(child)
        else:
            result['children'].append({
                'name': entry.name,
                'type': 'file',
                'size': entry.stat().st_size
            })
    
    return result

def count_code_lines(path):
    """统计代码行数"""
    total_lines = 0
    file_stats = defaultdict(lambda: {'count': 0, 'lines': 0})
    
    for root, dirs, files in os.walk(path):
        # 过滤忽略的目录
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in CODE_EXTENSIONS:
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = sum(1 for _ in f)
                        total_lines += lines
                        file_stats[ext]['count'] += 1
                        file_stats[ext]['lines'] += lines
                except Exception:
                    pass
    
    return total_lines, dict(file_stats)

def detect_tech_stack(path):
    """检测技术栈"""
    tech_stack = {
        'frontend': [],
        'backend': [],
        'database': [],
        'tools': []
    }
    
    # 检查 package.json
    package_json_path = os.path.join(path, 'package.json')
    if os.path.exists(package_json_path):
        try:
            with open(package_json_path, 'r', encoding='utf-8') as f:
                pkg = json.load(f)
                deps = {**pkg.get('dependencies', {}), **pkg.get('devDependencies', {})}
                
                # 前端框架
                if 'vue' in deps or '@vue/cli-service' in deps:
                    tech_stack['frontend'].append('Vue.js')
                if 'react' in deps or 'react-dom' in deps:
                    tech_stack['frontend'].append('React')
                if '@angular/core' in deps:
                    tech_stack['frontend'].append('Angular')
                if 'next' in deps:
                    tech_stack['frontend'].append('Next.js')
                if 'nuxt' in deps:
                    tech_stack['frontend'].append('Nuxt.js')
                
                # UI框架
                if 'element-ui' in deps or 'element-plus' in deps:
                    tech_stack['frontend'].append('Element UI')
                if 'antd' in deps or '@ant-design/vue' in deps:
                    tech_stack['frontend'].append('Ant Design')
                
                # 构建工具
                if 'vite' in deps:
                    tech_stack['tools'].append('Vite')
                if 'webpack' in deps:
                    tech_stack['tools'].append('Webpack')
        except Exception:
            pass
    
    # 检查 pom.xml
    pom_xml_path = os.path.join(path, 'pom.xml')
    if os.path.exists(pom_xml_path):
        tech_stack['backend'].append('Java')
        try:
            with open(pom_xml_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'spring-boot' in content:
                    tech_stack['backend'].append('Spring Boot')
                if 'mybatis' in content:
                    tech_stack['database'].append('MyBatis')
        except Exception:
            pass
    
    # 检查 requirements.txt / pyproject.toml
    req_path = os.path.join(path, 'requirements.txt')
    pyproject_path = os.path.join(path, 'pyproject.toml')
    if os.path.exists(req_path) or os.path.exists(pyproject_path):
        tech_stack['backend'].append('Python')
        try:
            content = ''
            if os.path.exists(req_path):
                with open(req_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            elif os.path.exists(pyproject_path):
                with open(pyproject_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            
            if 'django' in content.lower():
                tech_stack['backend'].append('Django')
            if 'flask' in content.lower():
                tech_stack['backend'].append('Flask')
            if 'fastapi' in content.lower():
                tech_stack['backend'].append('FastAPI')
        except Exception:
            pass
    
    # 检查 go.mod
    go_mod_path = os.path.join(path, 'go.mod')
    if os.path.exists(go_mod_path):
        tech_stack['backend'].append('Go')
    
    # 检查 Cargo.toml
    cargo_path = os.path.join(path, 'Cargo.toml')
    if os.path.exists(cargo_path):
        tech_stack['backend'].append('Rust')
    
    # 检查 docker-compose.yml
    docker_path = os.path.join(path, 'docker-compose.yml')
    if os.path.exists(docker_path):
        tech_stack['tools'].append('Docker')
    
    return tech_stack

def extract_project_name(path):
    """提取项目名称"""
    # 尝试从 package.json
    package_json_path = os.path.join(path, 'package.json')
    if os.path.exists(package_json_path):
        try:
            with open(package_json_path, 'r', encoding='utf-8') as f:
                pkg = json.load(f)
                if 'name' in pkg:
                    return pkg['name']
        except Exception:
            pass
    
    # 尝试从 pom.xml
    pom_xml_path = os.path.join(path, 'pom.xml')
    if os.path.exists(pom_xml_path):
        try:
            import re
            with open(pom_xml_path, 'r', encoding='utf-8') as f:
                content = f.read()
                match = re.search(r'<artifactId>(.*?)</artifactId>', content)
                if match:
                    return match.group(1)
        except Exception:
            pass
    
    # 使用目录名
    return os.path.basename(os.path.abspath(path))

def extract_version(path):
    """提取版本号"""
    # 尝试从 package.json
    package_json_path = os.path.join(path, 'package.json')
    if os.path.exists(package_json_path):
        try:
            with open(package_json_path, 'r', encoding='utf-8') as f:
                pkg = json.load(f)
                if 'version' in pkg:
                    return f"V{pkg['version']}"
        except Exception:
            pass
    
    return "V1.0"

def get_code_files(path, max_files=100):
    """获取代码文件列表"""
    code_files = []
    
    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in CODE_EXTENSIONS:
                filepath = os.path.join(root, file)
                rel_path = os.path.relpath(filepath, path)
                size = os.path.getsize(filepath)
                code_files.append({
                    'path': rel_path,
                    'size': size,
                    'extension': ext
                })
    
    # 按大小排序，取前N个
    code_files.sort(key=lambda x: x['size'], reverse=True)
    return code_files[:max_files]

def main():
    parser = argparse.ArgumentParser(description='扫描项目结构')
    parser.add_argument('--path', required=True, help='项目路径')
    parser.add_argument('--output', required=True, help='输出JSON文件路径')
    parser.add_argument('--max-depth', type=int, default=4, help='最大扫描深度')
    args = parser.parse_args()
    
    project_path = os.path.abspath(args.path)
    
    if not os.path.exists(project_path):
        print(f"错误：路径不存在 {project_path}")
        return
    
    print(f"扫描项目：{project_path}")
    
    # 扫描目录结构
    print("  扫描目录结构...")
    dir_structure = scan_directory(project_path, max_depth=args.max_depth)
    
    # 统计代码行数
    print("  统计代码行数...")
    total_lines, line_stats = count_code_lines(project_path)
    
    # 检测技术栈
    print("  检测技术栈...")
    tech_stack = detect_tech_stack(project_path)
    
    # 提取项目名称和版本
    project_name = extract_project_name(project_path)
    version = extract_version(project_path)
    
    # 获取代码文件列表
    print("  获取代码文件列表...")
    code_files = get_code_files(project_path)
    
    # 组装结果
    result = {
        'project_name': project_name,
        'version': version,
        'project_path': project_path,
        'directory_structure': dir_structure,
        'code_stats': {
            'total_lines': total_lines,
            'by_extension': line_stats
        },
        'tech_stack': tech_stack,
        'code_files': code_files
    }
    
    # 写入输出文件
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"扫描完成，结果已保存到：{args.output}")
    print(f"  项目名称：{project_name}")
    print(f"  版本号：{version}")
    print(f"  代码总行数：{total_lines}")
    print(f"  技术栈：前端={tech_stack['frontend']}, 后端={tech_stack['backend']}")

if __name__ == '__main__':
    main()
