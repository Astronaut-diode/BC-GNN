import os
import json
from Node import Node


# 从train_dir中，读取所有的json文件，并将对应的文本内容加入到sentences中。
def get_word2vec(train_dir, sentences):
    for filename in os.listdir(train_dir):
        if filename.endswith(".json"):
            json_file_path = f"{train_dir}/{filename}"
            json_file = open(json_file_path, 'r')
            json_content = json.load(json_file)
            for op in json_content['opcodes']:
                node = Node(-1, op, -1)  # 这是为了快速获取需要用于获取节点的节点内容以及节点类型。
                sentences.append(node.node_type)
                sentences.extend(node.node_content.split(' '))
            json_file.close()
