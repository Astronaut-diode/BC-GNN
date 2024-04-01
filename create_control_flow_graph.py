from Node import Node
import utils


# 直接传入操作码的json文件内容，用于构造控制流图。
def create_control_flow_graph(opcodes_json, G):
    #################建造控制流图#######################
    dfs(opcodes_json, G, opcodes_json['deployed_opcodes_range'][0])  # 真正用于建造控制流图的地方, 使用递归的算法，其中从0开始走
    dfs(opcodes_json, G, opcodes_json['runtime_opcodes_range'][0])  # 真正用于建造控制流图的地方, 使用递归的算法，其中从0开始走
    dfs(opcodes_json, G, opcodes_json['auxdata_opcodes_range'][0])  # 真正用于建造控制流图的地方, 使用递归的算法，其中从0开始走
    for node in G:
        if node.node_type == "JUMPDEST":
            dfs(opcodes_json, G, node.belong_byte)  # 真正用于建造控制流图的地方, 使用递归的算法
    #################建造控制流图#######################
    for node in G:
        if str(node.node_content).__contains__("INVALID"):  # 将父节点连接到自己的子节点上。
            parents = node.cfg_parent
            childs = node.cfg_edge
            for p in parents:
                p.cfg_edge.remove(node)
            for c in childs:
                c.cfg_parent.remove(node)
            node.cfg_edge = []
            node.cfg_parent = []
            for p in parents:
                for c in childs:
                    p.append_control_flow(c)
    for node in G:
        source_id = node.node_id
        for cfg_target_node in node.cfg_edge:
            dest_id = cfg_target_node.node_id
            opcodes_json['CFG'].append([source_id - 1, dest_id - 1])  # 注意，后期pytorch需要的id是索引要从0开始的。


def dfs(opcodes_json, G, now):
    if not now < len(G):
        print("不能继续搜索了，否则越界了。")
        return
    if G[now].node_type == 'HEX' and G[now].node_content == 'NULL':  # 这种节点是并不需要连接控制流的，作为孤立节点即可。
        pass
    elif G[now].node_type == "REVERT" and G[now].node_content == "REVERT":  # 回滚操作，不再继续深度递归
        pass
    elif G[now].node_type == "STOP" and G[now].node_content == "STOP":  # 终止操作，不再继续深度递归
        pass
    elif G[now].node_type == "RETURN" and G[now].node_content == "RETURN":  # 返回操作，不再继续深度递归
        pass
    elif G[now].node_type == "SELFDESTRUCT" and G[now].node_content == "SELFDESTRUCT":  # 自毁操作，不再继续深度递归
        pass
    elif G[now].node_type == "JUMPI" and G[now].node_content == "JUMPI":  # 有条件的跳转
        if len(G[now].cfg_parent) == 1 and G[now].cfg_parent[0].node_type.startswith("PUSH"):
            next_index = 0
            if G[now].cfg_parent[0].node_content == 'PUSH0':
                next_index = 0
            else:
                next_index = int(G[now].cfg_parent[0].node_content.split(' ')[1], 16)  # 找出父节点的操作指令指向的是哪里。
            if len(G) > next_index and G[next_index].node_type == "JUMPDEST":  # 必须是跳跃点才能进行跳跃
                G[now].append_control_flow(G[next_index])
                dfs(opcodes_json, G, next_index)  # 可以跳转到目标节点执行，也可能直接跳转到下一条指令执行。
                dfs(opcodes_json, G, now + 1)
    elif G[now].node_type == "JUMP" and G[now].node_content == "JUMP":  # 无条件的跳转
        if len(G[now].cfg_parent) == 1 and G[now].cfg_parent[0].node_type.startswith("PUSH"):
            next_index = 0
            if G[now].cfg_parent[0].node_content == 'PUSH0':
                next_index = 0
            else:
                next_index = int(G[now].cfg_parent[0].node_content.split(' ')[1], 16)  # 找出父节点的操作指令指向的是哪里。
            if len(G) > next_index and G[next_index].node_type == "JUMPDEST":  # 必须是跳跃点才能进行跳跃。
                if not G[next_index].cfg_parent:  # 只有数组不为空的时候，才能往里面添加控制流，因为这是一条绝路，只能走一次。
                    G[now].append_control_flow(G[next_index])
                    dfs(opcodes_json, G, next_index)  # 必须跳转到目标节点执行。
    elif G[now].node_type.startswith("PUSH") and G[now].node_content.startswith("PUSH"):  # PUSH类型的指令，需要跳过后续的i个指令。
        length = int(G[now].node_type.replace("PUSH", ""))  # 操作长度
        if len(G) > now + length + 1 and not G[now + length + 1].cfg_parent:  # 只有数组不为空的时候，才能往里面添加控制流，因为这是一条绝路，只能走一次。
            G[now].append_control_flow(G[now + length + 1])
            dfs(opcodes_json, G, now + length + 1)  # 直接跳转到i+1条指令以后执行。
    elif G[now].node_type == "CALL" and G[now].node_content == "CALL":  # CALL类型的指令。
        if len(G) > now and not G[now].cfg_edge:  # 只有数组不为空的时候，才能往里面添加控制流，因为这是一条绝路，只能走一次。
            G[now].append_control_flow(G[-1])  # 先调用外部，但是实际上，调用完外部合约以后，一定要回来，并继续调用下一行代码，所以这里直接就写掉了。
            G[-1].append_control_flow(G[now + 1])
            dfs(opcodes_json, G, now + 1)
    elif G[now].node_type == "CALLCODE" and G[now].node_content == "CALLCODE":  # CALLCODE类型的指令。
        if len(G) > now and not G[now].cfg_edge:  # 只有数组不为空的时候，才能往里面添加控制流，因为这是一条绝路，只能走一次。
            G[now].append_control_flow(G[-1])  # 先调用外部，但是实际上，调用完外部合约以后，一定要回来，并继续调用下一行代码，所以这里直接就写掉了。
            G[-1].append_control_flow(G[now + 1])
            dfs(opcodes_json, G, now + 1)
    elif G[now].node_type == "DELEGATECALL" and G[now].node_content == "DELEGATECALL":  # DELEGATECALL类型的指令。
        if len(G) > now and not G[now].cfg_edge:  # 只有数组不为空的时候，才能往里面添加控制流，因为这是一条绝路，只能走一次。
            G[now].append_control_flow(G[-1])  # 先调用外部，但是实际上，调用完外部合约以后，一定要回来，并继续调用下一行代码，所以这里直接就写掉了。
            G[-1].append_control_flow(G[now + 1])
            dfs(opcodes_json, G, now + 1)
    elif G[now].node_type == "STATICCALL" and G[now].node_content == "STATICCALL":  # STATICCALL类型的指令。
        if len(G) > now and not G[now].cfg_edge:  # 只有数组不为空的时候，才能往里面添加控制流，因为这是一条绝路，只能走一次。
            G[now].append_control_flow(G[-1])  # 先调用外部，但是实际上，调用完外部合约以后，一定要回来，并继续调用下一行代码，所以这里直接就写掉了。
            G[-1].append_control_flow(G[now + 1])
            dfs(opcodes_json, G, now + 1)
    else:  # 所有普通类型的指令，都是顺序执行的，所以一并操作。
        if len(G) > now + 1 and not G[now + 1].cfg_parent:  # 只有数组不为空的时候，才能往里面添加控制流，因为这是一条绝路，只能走一次。
            G[now].append_control_flow(G[now + 1])
            dfs(opcodes_json, G, now + 1)  # 正常执行下一条指令。
