from Node import Node
import utils


# 直接传入操作码的json文件内容，用于构造控制流图。
def create_data_flow_graph(opcodes_json, G):
    #################先假设控制流图创建好了#######################
    create(opcodes_json, G, 0)
    #################先假设控制流图创建好了#######################
    for node in G:
        source_id = node.node_id
        for dfg_target_node in node.dfg_edge:
            dest_id = dfg_target_node.node_id
            opcodes_json['DFG'].append([source_id - 1, dest_id - 1])


# 创建数据流图
def create(opcodes_json, G, now):
    for node in G:
        # 这些都是从Stack中读取内容，然后操作完再返回给stack的。
        if node.node_content in ['ADD', 'MUL', 'SUB', 'DIV', 'SDIV', 'MOD', 'SMOD', 'ADDMOD', 'MULMOD', 'EXP',
                                 'SIGNEXTEND', 'LT', 'GT', 'SLT', 'SGT', 'EQ', 'ISZERO', 'AND', 'OR', 'XOR',
                                 'NOT', 'BYTE', 'SHL', 'SHR', 'SAR', 'SHA3', 'BALANCE', 'CALLDATALOAD', 'EXTCODESIZE',
                                 'EXTCODEHASH', 'BLOCKHASH', 'CREATE', 'CALL', 'CALLCODE', 'DELEGATECALL', 'CREATE2',
                                 'STATICCALL'] or \
                str(node.node_content).startswith('DUP') or str(node.node_content).startswith('SWAP'):
            G[-4].append_data_flow(node)
            node.append_data_flow(G[-4])
        # 直接将内容保存到Stack中,并不读取内容
        elif node.node_content in ['ADDRESS', 'ORIGIN', 'CALLER', 'CALLVALUE', 'CALLDATASIZE', 'GASPRICE',
                                   'RETURNDATASIZE', 'COINBASE', 'TIMESTAMP', 'NUMBER', 'PREVRANDAO', 'GASLIMIT',
                                   'CHAINID', 'SELFBALANCE', 'BASEFEE', 'PC', 'MSIZE', 'GAS'] or \
                str(node.node_content).startswith('PUSH'):
            node.append_data_flow(G[-4])
        # 从stack中弹出内容，并不存入内容
        elif node.node_content in ['POP', 'JUMP', 'JUMPI', 'LOG0', 'LOG1', 'LOG2', 'LOG3', 'LOG4', 'RETURN', 'REVERT',
                                   'SELFDESTRUCT']:
            G[-4].append_data_flow(node)
        # 读取stack的内容，保存到memory中。
        elif node.node_content in ['CALLDATACOPY', 'EXTCODECOPY', 'RETURNDATACOPY', 'MSTORE', 'MSTORE8']:
            G[-4].append_data_flow(node)
            node.append_data_flow(G[-3])
        # 栈和memory都被读取，但是往栈中写内容。
        elif node.node_content in ['MLOAD']:
            G[-4].append_data_flow(node)
            G[-3].append_data_flow(node)
            node.append_data_flow(G[-4])
        # 读取stack的内容，保存到Storage中。
        elif node.node_content in ['SSTORE']:
            G[-4].append_data_flow(node)
            node.append_data_flow(G[-3])
        # 栈和Storarge都被读取，但是往栈中写内容。
        elif node.node_content in ['SLOAD']:
            G[-4].append_data_flow(node)
            G[-2].append_data_flow(node)
            node.append_data_flow(G[-4])