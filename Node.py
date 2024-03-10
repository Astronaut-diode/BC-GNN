class Node:
    node_id = -1  # 代表节点的id，第几个创建的节点。
    node_content = "暂未定义"  # 这组操作码的详细内容。
    node_type = "暂未定义"  # 操作码，如果是PUSH指令，并不带上结尾的操作数据。
    cfg_edge = []  # 控制流流向了哪里。
    belong_byte = -1  # 属于第几个字节，索引从0开始计算，即字节码的第一个字节的指令，这个值应该是0，这个是用于方便跳转的。

    def __init__(self, node_id, node_content, belong_byte):
        self.node_id = node_id
        self.node_content = node_content
        node_type = str(node_content).split(" ")[0]  # PUSH指令不取操作数
        if node_type.__contains__("INVALID") or node_type.__contains__("NULL"):  # 无效指令就直接记录为数值类型。
            node_type = "HEX"
        self.node_type = node_type
        self.belong_byte = belong_byte

    def __str__(self):
        return self.node_type
