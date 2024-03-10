from Node import Node


# 直接传入操作码的json文件内容，用于构造控制流图。
def create_control_flow_graph(opcodes_json):
    # 这是整张图。
    G = []
    for index, opcode in enumerate(opcodes_json["opcodes"]):
        G.append(Node(index + 1, opcode, index))
    print()