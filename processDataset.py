# 用于处理AST-GNN中的Contract-Augmentation数据集，用于生成字节码的纯净数据集。
import os
import json
import shutil
import utils
import subprocess

dataset_path = "/root/BC-GNN/dataset"

for type in os.listdir(dataset_path):
    dataset_type_path = f"{dataset_path}/{type}/sol_source"
    dataset_type_label_json_path = f"{dataset_path}/{type}/contract_labels.json"

    read_json = open(dataset_type_label_json_path, 'r', encoding="utf-8")
    content = json.load(read_json)

    new_label = {}

    for count, file in enumerate(os.listdir(dataset_type_path)):
        basename = file.split(".")[0]
        for label in content:
            if str(label['contract_name']).startswith(basename + "-"):
                new_name = str(label['contract_name']).replace(basename, str(count + 1), 1).replace(".sol", ".bin")
                new_label[new_name] = label['targets']
        utils.create_folder_if_not_exists(f'{dataset_path}/{type}/new_dataset/{count + 1}')
        shutil.copy(f'{dataset_type_path}/{file}', f'{dataset_path}/{type}/new_dataset/{count + 1}/{count + 1}.sol')
    json_file = f"{dataset_path}/{type}/new_contract_labels.json"

    if not os.path.exists(json_file):
        utils.save_json(new_label, json_file)

    version_hash = {"0.4.0": 0, "0.4.1": 0, "0.4.2": 0, "0.4.3": 0, "0.4.4": 0, "0.4.5": 0, "0.4.6": 0, "0.4.7": 0,
                    "0.4.8": 0, "0.4.9": 0, "0.4.10": 0,
                    "0.4.11": 0, "0.4.12": 0, "0.4.13": 0, "0.4.14": 0, "0.4.15": 0, "0.4.16": 0, "0.4.17": 0,
                    "0.4.18": 0, "0.4.19": 0, "0.4.20": 0,
                    "0.4.21": 0, "0.4.22": 0, "0.4.23": 0, "0.4.24": 0, "0.4.25": 0, "0.4.26": 0, "0.5.0": 0,
                    "0.5.1": 0, "0.5.2": 0, "0.5.3": 0, "0.5.4": 0,
                    "0.5.5": 0, "0.5.6": 0, "0.5.7": 0, "0.5.8": 0, "0.5.9": 0, "0.5.10": 0, "0.5.11": 0, "0.5.12": 0,
                    "0.5.13": 0, "0.5.14": 0, "0.5.15": 0,
                    "0.5.16": 0, "0.5.17": 0, "0.6.0": 0, "0.6.1": 0, "0.6.2": 0, "0.6.3": 0, "0.6.4": 0, "0.6.5": 0,
                    "0.6.6": 0, "0.6.7": 0, "0.6.8": 0, "0.6.9": 0,
                    "0.6.10": 0, "0.6.11": 0, "0.6.12": 0, "0.7.0": 0, "0.7.1": 0, "0.7.2": 0, "0.7.3": 0, "0.7.4": 0,
                    "0.7.5": 0, "0.7.6": 0, "0.8.0": 0, "0.8.1": 0,
                    "0.8.2": 0, "0.8.3": 0, "0.8.4": 0, "0.8.5": 0, "0.8.6": 0, "0.8.7": 0, "0.8.8": 0, "0.8.9": 0,
                    "0.8.10": 0, "0.8.11": 0, "0.8.12": 0, "0.8.13": 0,
                    "0.8.14": 0, "0.8.15": 0}
    versions = list(version_hash.keys())[::-1]
    for version in versions:
        utils.tip("切换为" + version + "版本，进行编译")
        cmd = f"/root/anaconda3/envs/lunikhod/bin/solc-select use {version}"
        subprocess.run(cmd, shell=True)
        for i in range(1, os.listdir(dataset_type_path).__len__(), 1):
            if os.listdir(f"{dataset_path}/{type}/new_dataset/{i}").__len__() == 1:
                cmd = f"/root/anaconda3/envs/lunikhod/bin/solc --bin -o {dataset_path}/{type}/new_dataset/{i} {dataset_path}/{type}/new_dataset/{i}/{i}.sol"
                utils.tip(f"编译{i}文件夹")
                subprocess.run(cmd, shell=True)

    total_count = 0
    for i in range(1, os.listdir(dataset_type_path).__len__(), 1):
        l = os.listdir(f"{dataset_path}/{type}/new_dataset/{i}")
        total_count += l.__len__()
        for f in l:
            if not f.endswith(".sol"):
                new_filename = f"{i}-{f.split('.')[0]}.bin"
                os.rename(os.path.join(f"{dataset_path}/{type}/new_dataset/{i}", f), os.path.join(f"{dataset_path}/{type}/new_dataset/{i}", new_filename))
                assert new_label.__contains__(new_filename), new_filename + "标签出现缺失"
