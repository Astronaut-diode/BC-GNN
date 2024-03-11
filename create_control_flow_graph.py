from Node import Node
import utils


# 直接传入操作码的json文件内容，用于构造控制流图。
def create_control_flow_graph(opcodes_json, G):
    #################先假设控制流图创建好了#######################
    for node in G:
        node.append_control_flow(G[node.belong_byte])
    #################先假设控制流图创建好了#######################
    for node in G:
        source_id = node.node_id
        for cfg_target_node in node.cfg_edge:
            dest_id = cfg_target_node.node_id
            opcodes_json['CFG'].append([source_id - 1, dest_id - 1])  # 注意，后期pytorch需要的id是索引要从0开始的。
