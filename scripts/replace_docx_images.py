#!/usr/bin/env python3
"""
替换docx文件中的图片
用于更新已生成docx中的配图，无需重新生成整个文档
"""

import os
import shutil
import zipfile
import argparse


def replace_images_in_docx(docx_path, output_path, image_mapping, clean_backups=True):
    """
    替换docx文件中的图片
    
    参数:
        docx_path: 原始docx文件路径
        output_path: 输出docx文件路径
        image_mapping: 图片映射字典 {原文件名: 新图片路径}
            例如: {'image1.png': '/path/to/new_architecture.png'}
        clean_backups: 是否清理备份文件（推荐True，否则会增加文件大小）
    """
    # 创建临时目录
    temp_dir = "/tmp/docx_replace_temp"
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)
    
    # 解压docx文件
    with zipfile.ZipFile(docx_path, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)
    
    # 替换图片
    replaced = []
    for original_name, new_image_path in image_mapping.items():
        original_path = os.path.join(temp_dir, 'word', 'media', original_name)
        if os.path.exists(original_path):
            shutil.copy2(new_image_path, original_path)
            replaced.append(original_name)
            print(f"  替换: {original_name} -> {os.path.basename(new_image_path)}")
        else:
            print(f"  警告: 未找到 {original_name}")
    
    # 清理备份文件（重要！否则会增加文件大小）
    if clean_backups:
        media_dir = os.path.join(temp_dir, 'word', 'media')
        for filename in os.listdir(media_dir):
            if filename.endswith('.backup'):
                os.remove(os.path.join(media_dir, filename))
                print(f"  清理备份: {filename}")
    
    # 重新打包docx文件
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, temp_dir)
                zipf.write(file_path, arcname)
    
    # 清理临时目录
    shutil.rmtree(temp_dir)
    
    return replaced


def list_docx_images(docx_path):
    """列出docx中的所有图片"""
    with zipfile.ZipFile(docx_path, 'r') as docx_zip:
        media_files = [f for f in docx_zip.namelist() if f.startswith('word/media/')]
        print(f"docx中的图片 ({len(media_files)} 个):")
        for f in media_files:
            with docx_zip.open(f) as img_file:
                img_size = len(img_file.read())
                print(f"  {f}: {img_size/1024:.1f}KB")


def main():
    parser = argparse.ArgumentParser(description='替换docx中的图片')
    parser.add_argument('docx_path', help='原始docx文件路径')
    parser.add_argument('output_path', help='输出docx文件路径')
    parser.add_argument('--images', nargs='+', help='图片映射 (原文件名=新图片路径)')
    parser.add_argument('--list', action='store_true', help='列出docx中的图片')
    parser.add_argument('--no-clean', action='store_true', help='不清理备份文件')
    
    args = parser.parse_args()
    
    if args.list:
        list_docx_images(args.docx_path)
        return
    
    if not args.images:
        print("错误: 需要指定 --images 参数")
        return
    
    # 解析图片映射
    image_mapping = {}
    for img_arg in args.images:
        if '=' not in img_arg:
            print(f"错误: 图片映射格式应为 '原文件名=新图片路径', 收到: {img_arg}")
            return
        original, new = img_arg.split('=', 1)
        image_mapping[original] = new
    
    print(f"开始替换图片...")
    print(f"源文件: {args.docx_path}")
    print(f"输出文件: {args.output_path}")
    
    replaced = replace_images_in_docx(
        args.docx_path, 
        args.output_path, 
        image_mapping, 
        clean_backups=not args.no_clean
    )
    
    print(f"\n完成! 替换了 {len(replaced)} 张图片")
    print(f"输出文件: {args.output_path}")


if __name__ == '__main__':
    main()
