import argparse
import os
import shutil
import subprocess
import json

# 改变当前工作目录到 /var
os.chdir("/root/BC-GNN")
# 默认会先加载config配置文件夹，然后设定好程序运行的配置。
parser = argparse.ArgumentParser(description='参数表')
parser.add_argument('--source_dir', type=str,
                    help="原始目录:\n")
parser.add_argument('--dest_dir', type=str,
                    help="目标目录:\n")
parser.add_argument('--filename', type=str,
                    help="文件名字:\n")
# 下面更新config配置
args = parser.parse_args()
source_dir = args.source_dir
dest_dir = args.dest_dir
filename = args.filename

source_file = source_dir + "/" + filename
# 确保目标文件夹存在，如果不存在则创建
os.makedirs(dest_dir + "/bytecode/" + str(source_dir).split("/")[-1], exist_ok=True)
# 拷贝文件到目标文件夹
shutil.copy(source_file, dest_dir + "/bytecode/" + str(source_dir).split("/")[-1])

cmd = f"/root/anaconda3/envs/lunikhod/bin/python3 /root/BC-GNN/main.py --run_mode predict --attack_type predict --target_dir {str(source_dir).split('/')[-1]} --target_file {filename.split('.')[0]}"
print(cmd)
# 创建一个子进程并立即返回
process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
# 获取命令的标准输出和标准错误输出
stdout, stderr = process.communicate()
# 输出命令执行结果
print("Command Output:", stdout.decode())
print("Command Output:", stderr.decode())
# 输出命令执行结果
file = open(dest_dir + "/res.json", 'r')
content = json.load(file)
file.close()

log_json = {}
if os.path.exists(source_file.replace(".bin", ".log")):
    file = open(source_file.replace(".bin", ".log"), 'r')
    log_json = json.load(file)
    file.close()
for c in content:
    if c['name'] == os.path.basename(source_file):
        log_json[c['attack_type']] = c['label']


# 将content保存到path上，以json的格式。
def save_json(content, path):
    json_file = open(path, 'w')
    json.dump(content, json_file)
    json_file.close()


save_json(log_json, source_file.replace(".bin", ".log"))
print(source_file.replace(".bin", ".log"))

with open(source_file, 'r') as tmp:
    # 接下来准备将raw文件夹中的对应的json文件移动到java项目中去。
    train_user_dir = dest_dir + "/train/" + str(source_dir).split("/")[-1]
    shutil.copy(train_user_dir + '/' + filename.replace(".bin", ".json"), source_dir)