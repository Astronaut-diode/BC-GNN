from Node import Node
import utils


# 直接传入操作码的json文件内容，用于构造控制流图。
def create_data_flow_graph(opcodes_json, G):
    #################先假设控制流图创建好了#######################
    G[0].append_data_flow(G[0])
    #################先假设控制流图创建好了#######################
    for node in G:
        source_id = node.node_id
        for dfg_target_node in node.dfg_edge:
            dest_id = dfg_target_node.node_id
            opcodes_json['DFG'].append([source_id - 1, dest_id - 1])
