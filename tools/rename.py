import os
import re
from icecream import ic

def check_rename(file_path, new_file_path):
    choice = input(f"是否需要重命名 {file_path} -> {new_file_path}？(y_enter/n): ").strip().lower()
    if choice in ['y', '']:
        os.rename(file_path, new_file_path)
    else:
        print("跳过此文件。")

def rename_files_in_directory(folder_path):
    # 检查文件夹是否存在
    if not os.path.exists(folder_path):
        print(f"文件夹路径不存在: {folder_path}")
        return
    
    # 特殊处理的文件后缀
    special_suffixes = ("-fanart.jpg", "-poster.jpg", "-thumb.jpg")
    
    # 遍历文件夹中的所有文件
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        
        # 检查是否为文件（排除子目录）
        if os.path.isfile(file_path):
            # 提取文件名和扩展名
            name, ext = os.path.splitext(filename)
            ic(name,ext)
            # 处理 .mp4 文件
            if ext == ".mp4":
                # 使用正则表达式检查是否已经包含 -cd<数字>.mp4
                if not re.search(r"-cd\d\.mp4$", filename):
                    # 重命名为 -cd1.mp4
                    new_filename = f"{name}-cd1.mp4"
                    new_file_path = os.path.join(folder_path, new_filename)
                    check_rename(file_path, new_file_path)

            # 处理特殊文件：-fanart.jpg / -poster.jpg / -thumb.jpg
            elif any(filename.endswith(suffix) for suffix in special_suffixes):
                # 已经包含 cd 编号就跳过
                if re.search(r"-cd\d-", filename) or filename.startswith("cd"):
                    continue

                # 提取基础名称（去掉 -fanart 等后缀）
                for suffix in special_suffixes:
                    if filename.endswith(suffix):
                        base_name = filename[:-len(suffix)]
                        break

                new_filename = f"{base_name}-cd1{suffix}"
                new_file_path = os.path.join(folder_path, new_filename)
                check_rename(file_path, new_file_path)
            
            # 处理其他文件类型（如 .nfo, .jpg, .thumb.jpg 等）
            else:
                # 使用正则表达式提取文件名的核心部分
                match = re.match(r"^(.*?)(-cd\d)?$", name)
                if match:
                    base_name = match.group(1)  # 提取核心部分
                    cd_part = match.group(2) or "-cd1"  # 默认添加 -cd1，如果已有则保留
                    
                    # 构造新的文件名
                    new_filename = f"{base_name}{cd_part}{ext}"
                    new_file_path = os.path.join(folder_path, new_filename)
                    
                    # 重命名文件
                    check_rename(file_path, new_file_path)


if __name__ == "__main__":
    # 输入文件夹路径
    folder_path = input("请输入文件夹路径: ")
    rename_files_in_directory(folder_path)