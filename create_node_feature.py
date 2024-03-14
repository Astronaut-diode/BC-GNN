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

    actual_id_list = set()  # 找出所有参与过程的节点。
    for edge in content['CFG']:
        actual_id_list.add(edge[0])
        actual_id_list.add(edge[1])
    for edge in content['DFG']:
        actual_id_list.add(edge[0])
        actual_id_list.add(edge[1])
    actual_id_list = list(actual_id_list)
    actual_id_list = sorted(actual_id_list)

    node_feature_list = []
    for actual_id in actual_id_list:
        node = Node(-1, content['opcodes'][actual_id], -1)  # 这是为了快速获取需要用于获取节点的节点内容以及节点类型。
        node_feature = [0.0] * config.encode_dim  # 因为节点类型的内容无法直接转换为向量了，所以需要一开始创建一个内容为0的数组。
        opcodes = content['opcodes'][actual_id].split(' ')
        # for op in opcodes:
        #     if str(op).__contains__("INVALID"):
        #         op = "INVALID"
        node_feature = node_feature + word2vec_model[opcodes[0]]
        node_feature = node_feature.tolist()
        node_feature_list.append(node_feature)
    # 准备找到当前图对应的标签是什么
    contract_name = os.path.basename(content['filepath']).split(".")[0]
    target_name = f'{contract_name}.bin'

    hash_map = {}
    for index, actual_id in enumerate(actual_id_list):  # 更改CFG和DFG中的边指向的序号，这样就可以去除掉一切不必要的节点。
        hash_map[actual_id] = index
    for edge in content['CFG']:
        edge[0] = hash_map[edge[0]]
        edge[1] = hash_map[edge[1]]
    for edge in content['DFG']:
        edge[0] = hash_map[edge[0]]
        edge[1] = hash_map[edge[1]]

    # 最终需要保存的图数据。
    graph_data = {
        'node_feature': node_feature_list,
        'cfg_edge': content['CFG'],
        'dfg_edge': content['DFG'],
        'label': label_dict[target_name],
    }
    utils.save_json(graph_data, graph_path)  # 将图数据保存到图路径上。
    json_file.close()
