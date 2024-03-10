import json
import os


# 自定义的输出函数，带有颜色。
def error(msg):
    print(f"\033[1;;31m{msg}\033[;;m")


def success(msg):
    print(f"\033[1;;32m{msg}\033[;;m")


def tip(msg, end="\n"):
    print(f"\033[1;;33m{msg}\033[;;m", end=end)


# 将content保存到path上，以json的格式。
def save_json(content, path):
    json_file = open(path, 'w')
    json.dump(content, json_file, ensure_ascii=False)
    json_file.close()
    success(f"文件{path}保存成功！")


# 递归创建并不存在的文件夹
def create_folder_if_not_exists(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        tip(f"文件夹 '{folder_path}'创建成功。")
