import config
import json
import utils
import os
from gensim.models.word2vec import Word2Vec
from Node import Node


def create_node_feature(json_path, graph_path, word2vec_model, label_dict):
    if os.path.exists(graph_path):  # 如果目标文件已经生成过了，那就不再覆盖生成。
        return
    json_file = open(json_path, 'r')
    content = json.load(json_file)
    node_feature_list = []
    for opcode in content['opcodes']:
        node = Node(-1, opcode, -1)  # 这是为了快速获取需要用于获取节点的节点内容以及节点类型。
        node_feature = word2vec_model[node.node_type]
        opcodes = opcode.split(' ')
        for op in opcodes:
            node_feature = node_feature + word2vec_model[op]
        node_feature = node_feature.tolist()
        node_feature_list.append(node_feature)
    # 准备找到当前图对应的标签是什么
    contract_name = os.path.basename(content['filepath']).split(".")[0]
    target_name = f'{contract_name}.bin'
    # 最终需要保存的图数据。
    graph_data = {
        'node_feature': node_feature_list,
        'cfg_edge': content['CFG'],
        'dfg_edge': content['DFG'],
        'label': label_dict[target_name],
    }
    utils.save_json(graph_data, graph_path)  # 将图数据保存到图路径上。
    json_file.close()
