
from args import inputParameters, isIceEnable
from icecream import ic
import logging
from rich.logging import RichHandler

FORMAT = "%(message)s"
logging.basicConfig(
    level="NOTSET", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)

log = logging.getLogger("rich")
# INFO\WARNING、ERROR 或 CRITICAL
log.setLevel(logging.INFO)

import os
import glob
import re
import shutil

def GetVideoList(path):
    video_files = []
    for ext in ('*.mp4', '*.mkv'):
        video_files.extend(glob.glob(os.path.join(path, ext)))
    return ic(video_files)

def alpha2num(s):
    if s.isalpha():
        return sum(ord(c) - ord('A') + 1 for c in s.upper())
    else:
        return int(s)

def ExstractJAV(video_filename):
    ic(video_filename)
    # 定义正则表达式模式
    pattern = r"""
        ^(?P<series>[a-zA-Z]+)          # 系列名称，由大写或小写字母组成
        (?:[0-]+|-)?(?P<id>\d+)          # ID，由0或-分割的第一个数字编号ID
        (?:[_-](?P<cd_id>\d*[a-zA-Z]*))? # CD-ID，由_或-分割的数字或字母
        (?:[_-](?P<resolution>[8|4][K|k]))?     # 清晰度，可选的8k或4k
        (?:@*)?
        $
    """
    # 使用正则表达式进行匹配
    match = re.match(pattern, video_filename, re.VERBOSE)
    if match:
        # 提取匹配的组
        series = match.group('series').upper()
        id = match.group('id').zfill(3)
        cd_id = str(alpha2num(match.group('cd_id'))) if match.group('cd_id') else None
        resolution = match.group('resolution').upper() if match.group('resolution') else None
        # 返回结果字典
        return {
            'series': series,
            'id': id,
            'cd_id': cd_id,
            'resolution': resolution
        }
    else:
        # 如果没有匹配到，返回None或适当的错误信息
        log.warning(f"Failed to parse video filename: {video_filename}")
        return None

def extract_resolution_from_path(path):
    # 分割路径
    parts = path.split(os.sep)    
    # 遍历路径的每个部分
    for part in parts:
        # 检查是否包含分辨率
        if '8k' in part.lower():
            return '8K'
        if '4k' in part.lower():
            return '4K'
    return '4K'


def SearchTargetJav(path, JAV_ID):
    # 构建正则表达式模式
    pattern = re.compile(rf"^{re.escape(JAV_ID['series'])}-{re.escape(JAV_ID['id'])}.*$")
    
    # 存储匹配的文件夹列表
    matching_folders = []
    target_resolution = []
    
    # 递归遍历目录
    def search_recursive(current_path, depth):
        if depth > 2:
            return
        for entry in os.listdir(current_path):
            full_path = os.path.join(current_path, entry)
            # 检查是否是文件夹
            if os.path.isdir(full_path):
                # 检查文件夹名称是否匹配模式
                if pattern.match(entry):
                    matching_folders.append(full_path)
                    target_resolution.append(extract_resolution_from_path(full_path))
                # 递归遍历子文件夹
                search_recursive(full_path, depth + 1)
    
    # 从指定路径开始递归搜索
    search_recursive(path, 1)
    
    return matching_folders, target_resolution
# 检查是否可以替换目标文件：1.目标文件是否存在，不存在则直接替换 2.目标文件大小是否小于源文件，小于则直接替换 3.目标文件是否是文件夹
def CheckIfPlace(target_file, source_file):
    if not os.path.exists(target_file):
        return True
    elif os.path.getsize(target_file) < os.path.getsize(source_file):
        log.warning("target size: {}, source size: {}".
                 format(os.path.getsize(target_file), os.path.getsize(source_file)))
        return True
    elif os.path.isdir(target_file):
        return False
    else:
        log.warning("target size: {}, source size: {}".
                 format(os.path.getsize(target_file), os.path.getsize(source_file)))
        return False

def MoveVideos(target_file, source_file):
    try:
        shutil.move(source_file, target_file)
        log.info(f"File moved successfully: {source_file} to {target_file}")
    except Exception as e:
        log.error(f"Failed to move file: {source_file} to {target_file}. Error: {e}")
    
if __name__ == '__main__':
    args_list = inputParameters()
    isIceEnable(args_list.debug)
    fvideo_list = GetVideoList(f"{args_list.path}/failed")
    for failed_video in fvideo_list:
        # 过滤掉文件大小小于100MB 的文件， 或者名称里包含中文的
        if os.path.getsize(failed_video) < 100 * 1024 * 1024 or re.search(r'[\u4e00-\u9fa5]', failed_video): 
            log.info("Skip no target file: {}".format(failed_video))
            continue
        # 提取出文件名import os


        video_filename = os.path.splitext(os.path.basename(failed_video))[0]
        video_type = os.path.splitext(os.path.basename(failed_video))[1]
        # 识别出 AV 的标识
        JAV_ID = ExstractJAV(video_filename)
        ic(JAV_ID)
        target_folder, target_resolution = SearchTargetJav(f"{args_list.path}/JAV_output", JAV_ID)
        ic(target_folder)
        if len(target_folder) == 0:
            log.info("Skip no target folder: {}".format(failed_video))
            continue
        target_file_name = f"{JAV_ID['series']}-{JAV_ID['id']}-{target_resolution[0]}-cd{JAV_ID['cd_id'] if JAV_ID['cd_id'] else ''}{video_type}"
        target_file_path = f"{target_folder[0]}/{target_file_name}"
        ic(target_file_path)
        if CheckIfPlace(target_file_path, failed_video):
            if JAV_ID['resolution'] and target_resolution[0] != JAV_ID['resolution']:
                log.warning("target resolution: {}, source resolution: {}".
                         format(target_resolution[0], JAV_ID['resolution']))
            print("Move {} file to {} ".format(failed_video,target_file_path ))
            
            user_input = input("Do you want to proceed with the move? [y/Enter to skip]: ").strip().lower()
            
            if user_input in ['y', '']:
                MoveVideos(target_file_path, failed_video)
            else:
                log.info("Move operation skipped by user.")