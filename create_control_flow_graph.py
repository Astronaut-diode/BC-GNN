import utils


# 直接传入操作码的json文件内容，用于构造控制流图。
def create_control_flow_graph(opcodes_json):
    utils.tip(f"准备进行{opcodes_json['filepath']}转换为控制流图的过程。")