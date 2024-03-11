import utils
import os
import config
from create_control_flow_graph import create_control_flow_graph
from create_data_flow_graph import create_data_flow_graph
from Node import Node


# 读取bin文件中的内容，返回对应的二进制结果
def read_bin(bin_file):
    wait_detect_bin = []
    with open(bin_file, 'r') as bin:
        wait_detect_bin.append(bin.readline().replace('\n', '').upper())
        # for count, line in enumerate(bin.readlines()):
        #     if line.__contains__("======"):  # 这是标题行，可以忽略
        #         continue
        #     elif line.__contains__("Binary:"):  # 这是启动行，一样可以忽略:
        #         continue
        #     elif line == "\n":  # 这一行是空行，没有信息，可以不采集。
        #         continue
        #     else:  # 这是我们等待训练或者检测的内容。
        #         start_index = 0
        #         first_index = line.find('_') - 1
        #         while 0 < first_index < len(line):
        #             if line[first_index + 1] == '_':  # 从非_进入_状态
        #                 first_index = first_index + 1
        #                 wait_detect_bin.append(line[start_index:first_index].upper())
        #                 while line[first_index + 1] == '_':
        #                     first_index = first_index + 1
        #                     continue
        #                 while line[first_index + 1] != '_':
        #                     first_index = first_index + 1
        #                     continue
        #                 while line[first_index + 1] == '_':
        #                     first_index = first_index + 1
        #                     continue
        #                 start_index = first_index + 1
        #                 first_index = line.find('_', start_index) - 1
        #         wait_detect_bin.append(line[start_index:].replace('\n', '').upper())
    return wait_detect_bin


# 将wait_detect_project这个路径中的字节码(后缀为.bin)转换为操作码(后缀为.op)，并保存下来。
# wait_detect_project:这是个待检测项目的目录
def convertToOpCodesAndGraph(wait_detect_project):
    utils.create_folder_if_not_exists(f'{config.TRAIN_DATA_DIR_PATH}/{wait_detect_project}')  # 先检测对应的操作码工程文件夹是否已经存在
    file_list = os.listdir(f'{config.TRAIN_DATA_DIR_PATH}/{wait_detect_project}')  # 获取对应的已经生成的操作码文件列表
    for file in os.listdir(f'{config.BYTECODE_DIR_PATH}/{wait_detect_project}'):
        if file.endswith(".bin") and os.path.getsize(f'{config.BYTECODE_DIR_PATH}/{wait_detect_project}/{file}') > 0:  # 判断是否存在对应的操作码文件了
            bin_file = f'{config.BYTECODE_DIR_PATH}/{wait_detect_project}/{file}'
            basename = os.path.basename(bin_file).split('.')[0]
            opcodes_file_name = basename + ".json"
            if file_list.__contains__(opcodes_file_name):  # 如果已经存在了操作码文件，就跳过当前文件，进而处理下一个字节码文件。
                continue
            wait_detect_bin = read_bin(bin_file)  # 先读取所有需要检测的字节码内容。
            # 根据文件的名字以及字节码，创建对应的操作码文件。将所有的合约的操作码，全部捏到一起。
            res_json = create_opcodes(wait_detect_bin,
                                      f'{config.TRAIN_DATA_DIR_PATH}/{wait_detect_project}/{opcodes_file_name}')
            # 这是整张图。
            G = []
            for index, opcode in enumerate(res_json["opcodes"]):
                G.append(Node(index + 1, opcode, index))
            assert len(G) == len(res_json['opcodes'])
            create_control_flow_graph(res_json, G)  # 根据当前二进制的文件转换为操作码以后的内容，构造控制流图。
            create_data_flow_graph(res_json, G)  # 根据当前二进制的文件转换为操作码以后的内容，构造控制流图。
            utils.save_json(res_json, f'{config.TRAIN_DATA_DIR_PATH}/{wait_detect_project}/{opcodes_file_name}')


# 从start开始，读取length字节的内容
# 返回对应的内容以及下次的起始位置
def read_one_byte(bin, start, length):
    return bin[start * 2: start * 2 + length * 2], start + length


# 根据bin创建对应的字节码文件
def create_opcodes(bin_code, opcodes_file_path):
    assert len(bin_code) == 1, "这里的单个bin文件中包含了不止一组字节码"
    bin = bin_code[0]
    start = 0  # 当前已经读取到了第几个字节。
    line = 0  # 当前已经是第几行的指令。
    runtime_bytecode_len = 0  # 这两个数值分别用于记录下面遍历的时候，一直不断的读出的PUSH指令中记录的数值，runtime_bytecode的总长度就是这个长度。
    runtime_bytecode_offset = 0  # 这是runtime_bytecode保存的位置。此外这两个值相加的结果应该是bin的总字节数，如果匹配到了，那么就代表可以分割出来了。
    deployed_code = []
    runtime_code = []
    auxdata = []
    state = 1  # 状态一共有三种，1代表当前记录deployed，2代表runtime_bytecode、3代表auxdata
    count = 0  # 记录当前的状态已经记录了多少字节的操作码，如果状态到了，那就可以开始切换状态了。
    opcodes = []
    while True:
        line = line + 1
        value, start = read_one_byte(bin, start, 1)
        if opcodes_dict.__contains__(value):  # 代表确实是操作码，并且是有效的操作码。
            opcode = opcodes_dict[value][0]  # 操作码的类型。
            oplen = opcodes_dict[value][1]  # 操作码操作的长度。
            content = opcode
            count += 1
            for i in range(len(oplen)):  # 一共读取len(oplen)次，每次按照对应的数组元素的大小进行读取
                num, start = read_one_byte(bin, start, oplen[i])
                content = content + " 0x" + num
                count += oplen[i]
                # 代表找到了runtime_bytecode的长度以及偏移量，找到了以后就不再发生改变。
                if (runtime_bytecode_len + runtime_bytecode_offset) * 2 != len(bin):
                    runtime_bytecode_len = runtime_bytecode_offset
                    runtime_bytecode_offset = int("0x" + num, 16)
            opcodes.append(content)  # 加入到opcodes，这是总的，有时候如果需要使用总的就不需要分割。
            if len(oplen) > 0:
                for i in range(oplen[0]):
                    if i + start - oplen[0] < len(bin) / 2:  # 字节读取数是从0开始计算的，所以500字节只能读取[0,499]
                        opcodes.append("NULL")  # 这只是顶替行用的，方便快速进行跳转。
            if state == 3:
                auxdata.append(content)
            if state == 2:
                runtime_code.append(content)
                # 代表第二阶段的内容已经全部读完了。减去86，是因为末尾的43字节为aux代码。
                if count == runtime_bytecode_len - 43 and start == len(bin) / 2 - 43:
                    state = 3
                    count = 0
            if state == 1:
                deployed_code.append(content)
                if count == runtime_bytecode_offset:  # 代表一阶段的内容已经全部读完了。
                    state = 2
                    count = 0
        elif value == '':
            break
        else:
            utils.error("汇报，有新的操作码，0x" + str(value) + "还未加入操作列表!")
            exit(config.NEW_OPCODES)
    opcodes.append("CONTRACT")  # 外部合约，执行CALL指令以及CALLCODE的代码时就可以进行调用。这永远设定为倒数第一个节点。
    res_json = {
        'filepath': opcodes_file_path,
        'bytecode': bin,
        'opcodes': opcodes,
        'total_bytes': runtime_bytecode_len + runtime_bytecode_offset,
        'deployed_opcodes_range': [0, runtime_bytecode_offset],
        'runtime_opcodes_range': [runtime_bytecode_offset, runtime_bytecode_len + runtime_bytecode_offset - 43],
        'auxdata_opcodes_range': [runtime_bytecode_len + runtime_bytecode_offset - 43,
                                  runtime_bytecode_len + runtime_bytecode_offset],
        'deployed_opcodes': deployed_code,
        'runtime_opcodes': runtime_code,
        'auxdata_opcodes': auxdata,
        'CFG': [],
        'DFG': [],
        'readme': 'filepath中存储的是对应的操作码文件的保存路径' +
                  "bytecode中存储的是全部的二进制代码；" +
                  "opcodes中存储的是全部的操作码，其中包含了NULL进行占位，存储的格式是数组，这样方便取，所以索引从0开始" +
                  "total_bytes中保存的是字节码一共有多少字节" +
                  "deployed_opcodes_range保存的是部署的字节码在bytecode中的范围，左闭右开，保存的格式是数组" +
                  "runtime_opcodes_range保存的是部署的字节码在bytecode中的范围，左闭右开，保存的格式是数组" +
                  "auxdata_opcodes_range保存的是部署的字节码在bytecode中的范围，左闭右开，保存的格式是数组" +
                  "deployed_opcodes中部署的是部署代码的操作码，保存的格式是数组，并且没有使用NULL进行占位" +
                  "runtime_opcodes中部署的是部署代码的操作码，保存的格式是数组，并且没有使用NULL进行占位" +
                  "auxdata_opcodes中部署的是部署代码的操作码，保存的格式是数组，并且没有使用NULL进行占位" +
                  "CFG中保存的是哪个节点指向了哪个节点，使用的是索引，DFG同理。",
    }
    return res_json


# 操作码的列表，记录的是value和操作码的对应关系,这是一个全局的变量。并且还记录了这个操作码需要操作后续多长字节的内容。
# '60': ['PUSH1', [1]]代表序号60的时候，对应的是操作码是PUSH1，后续的操作的数字一共有len([1])个，长度分别为[1]
opcodes_dict = {
    '00': ['STOP', []],
    '01': ['ADD', []],
    '02': ['MUL', []],
    '03': ['SUB', []],
    '04': ['DIV', []],
    '05': ['SDIV', []],
    '06': ['MOD', []],
    '07': ['SMOD', []],
    '08': ['ADDMOD', []],
    '09': ['MULMOD', []],
    '0A': ['EXP', []],
    '0B': ['SIGNEXTEND', []],
    '0C': ['0X0C(INVALID)', []],  # 这是个特殊值
    '0D': ['0X0D(INVALID)', []],  # 这是个特殊值
    '0E': ['0X0E(INVALID)', []],  # 这是个特殊值
    '0F': ['0X0F(INVALID)', []],  # 这是个特殊值
    '10': ['LT', []],
    '11': ['GT', []],
    '12': ['SLT', []],
    '13': ['SGT', []],
    '14': ['EQ', []],
    '15': ['ISZERO', []],
    '16': ['AND', []],
    '17': ['OR', []],
    '18': ['XOR', []],
    '19': ['NOT', []],
    '1A': ['BYTE', []],
    '1B': ['SHL', []],
    '1C': ['SHR', []],
    '1D': ['SAR', []],
    '1E': ['0X1E(INVALID)', []],  # 这是个特殊值
    '1F': ['0X1F(INVALID)', []],  # 这是个特殊值
    '20': ['SHA3', []],
    '21': ['0X21(INVALID)', []],  # 这是个特殊值
    '22': ['0X22(INVALID)', []],  # 这是个特殊值
    '23': ['0X23(INVALID)', []],  # 这是个特殊值
    '24': ['0X24(INVALID)', []],  # 这是个特殊值
    '25': ['0X25(INVALID)', []],  # 这是个特殊值
    '26': ['0X26(INVALID)', []],  # 这是个特殊值
    '27': ['0X27(INVALID)', []],  # 这是个特殊值
    '28': ['0X28(INVALID)', []],  # 这是个特殊值
    '29': ['0X29(INVALID)', []],  # 这是个特殊值
    '2A': ['0X2A(INVALID)', []],  # 这是个特殊值
    '2B': ['0X2B(INVALID)', []],  # 这是个特殊值
    '2C': ['0X2C(INVALID)', []],  # 这是个特殊值
    '2D': ['0X2D(INVALID)', []],  # 这是个特殊值
    '2E': ['0X2E(INVALID)', []],  # 这是个特殊值
    '2F': ['0X2F(INVALID)', []],  # 这是个特殊值
    '30': ['ADDRESS', []],
    '31': ['BALANCE', []],
    '32': ['ORIGIN', []],
    '33': ['CALLER', []],
    '34': ['CALLVALUE', []],
    '35': ['CALLDATALOAD', []],
    '36': ['CALLDATASIZE', []],
    '37': ['CALLDATACOPY', []],
    '38': ['CODESIZE', []],
    '39': ['CODECOPY', []],
    '3A': ['GASPRICE', []],
    '3B': ['EXTCODESIZE', []],
    '3C': ['EXTCODECOPY', []],
    '3D': ['RETURNDATASIZE', []],
    '3E': ['RETURNDATACOPY', []],
    '3F': ['EXTCODEHASH', []],
    '40': ['BLOCKHASH', []],
    '41': ['COINBASE', []],
    '42': ['TIMESTAMP', []],
    '43': ['NUMBER', []],
    '44': ['PREVRANDAO', []],
    '45': ['GASLIMIT', []],
    '46': ['CHAINID', []],
    '47': ['SELFBALANCE', []],
    '48': ['BASEFEE', []],
    '49': ['0X49(INVALID)', []],  # 这是个特殊值
    '4A': ['0X4A(INVALID)', []],  # 这是个特殊值
    '4B': ['0X4B(INVALID)', []],  # 这是个特殊值
    '4C': ['0X4C(INVALID)', []],  # 这是个特殊值
    '4D': ['0X4D(INVALID)', []],  # 这是个特殊值
    '4E': ['0X4E(INVALID)', []],  # 这是个特殊值
    '4F': ['0X4F(INVALID)', []],  # 这是个特殊值
    '50': ['POP', []],
    '51': ['MLOAD', []],
    '52': ['MSTORE', []],
    '53': ['MSTORE8', []],
    '54': ['SLOAD', []],
    '55': ['SSTORE', []],
    '56': ['JUMP', []],
    '57': ['JUMPI', []],
    '58': ['PC', []],
    '59': ['MSIZE', []],
    '5A': ['GAS', []],
    '5B': ['JUMPDEST', []],
    '5C': ['0X5D(INVALID)', []],  # 这是个特殊值
    '5D': ['0X5D(INVALID)', []],  # 这是个特殊值
    '5E': ['0X5E(INVALID)', []],  # 这是个特殊值
    '5F': ['PUSH0', []],
    '60': ['PUSH1', [1]],
    '61': ['PUSH2', [2]],
    '62': ['PUSH3', [3]],
    '63': ['PUSH4', [4]],
    '64': ['PUSH5', [5]],
    '65': ['PUSH6', [6]],
    '66': ['PUSH7', [7]],
    '67': ['PUSH8', [8]],
    '68': ['PUSH9', [9]],
    '69': ['PUSH10', [10]],
    '6A': ['PUSH11', [11]],
    '6B': ['PUSH12', [12]],
    '6C': ['PUSH13', [13]],
    '6D': ['PUSH14', [14]],
    '6E': ['PUSH15', [15]],
    '6F': ['PUSH16', [16]],
    '70': ['PUSH17', [17]],
    '71': ['PUSH18', [18]],
    '72': ['PUSH19', [19]],
    '73': ['PUSH20', [20]],
    '74': ['PUSH21', [21]],
    '75': ['PUSH22', [22]],
    '76': ['PUSH23', [23]],
    '77': ['PUSH24', [24]],
    '78': ['PUSH25', [25]],
    '79': ['PUSH26', [26]],
    '7A': ['PUSH27', [27]],
    '7B': ['PUSH28', [28]],
    '7C': ['PUSH29', [29]],
    '7D': ['PUSH30', [30]],
    '7E': ['PUSH31', [31]],
    '7F': ['PUSH32', [32]],
    '80': ['DUP1', []],
    '81': ['DUP2', []],
    '82': ['DUP3', []],
    '83': ['DUP4', []],
    '84': ['DUP5', []],
    '85': ['DUP6', []],
    '86': ['DUP7', []],
    '87': ['DUP8', []],
    '88': ['DUP9', []],
    '89': ['DUP10', []],
    '8A': ['DUP11', []],
    '8B': ['DUP12', []],
    '8C': ['DUP13', []],
    '8D': ['DUP14', []],
    '8E': ['DUP15', []],
    '8F': ['DUP16', []],
    '90': ['SWAP1', []],
    '91': ['SWAP2', []],
    '92': ['SWAP3', []],
    '93': ['SWAP4', []],
    '94': ['SWAP5', []],
    '95': ['SWAP6', []],
    '96': ['SWAP7', []],
    '97': ['SWAP8', []],
    '98': ['SWAP9', []],
    '99': ['SWAP10', []],
    '9A': ['SWAP11', []],
    '9B': ['SWAP12', []],
    '9C': ['SWAP13', []],
    '9D': ['SWAP14', []],
    '9E': ['SWAP15', []],
    '9F': ['SWAP16', []],
    'A0': ['LOG0', []],
    'A1': ['LOG1', []],
    'A2': ['LOG2', []],
    'A3': ['LOG3', []],
    'A4': ['LOG4', []],
    'A5': ['0XA5(INVALID)', []],  # 这是个特殊值
    'A6': ['0XA6(INVALID)', []],  # 这是个特殊值
    'A7': ['0XA7(INVALID)', []],  # 这是个特殊值
    'A8': ['0XA8(INVALID)', []],  # 这是个特殊值
    'A9': ['0XA9(INVALID)', []],  # 这是个特殊值
    'AA': ['0XAA(INVALID)', []],  # 这是个特殊值
    'AB': ['0XAB(INVALID)', []],  # 这是个特殊值
    'AC': ['0XAC(INVALID)', []],  # 这是个特殊值
    'AD': ['0XAD(INVALID)', []],  # 这是个特殊值
    'AE': ['0XAE(INVALID)', []],  # 这是个特殊值
    'AF': ['0XAF(INVALID)', []],  # 这是个特殊值
    'B0': ['0XB0(INVALID)', []],  # 这是个特殊值
    'B1': ['0XB1(INVALID)', []],  # 这是个特殊值
    'B2': ['0XB2(INVALID)', []],  # 这是个特殊值
    'B3': ['0XB3(INVALID)', []],  # 这是个特殊值
    'B4': ['0XB4(INVALID)', []],  # 这是个特殊值
    'B5': ['0XB5(INVALID)', []],  # 这是个特殊值
    'B6': ['0XB6(INVALID)', []],  # 这是个特殊值
    'B7': ['0XB7(INVALID)', []],  # 这是个特殊值
    'B8': ['0XB8(INVALID)', []],  # 这是个特殊值
    'B9': ['0XB9(INVALID)', []],  # 这是个特殊值
    'BA': ['0XBA(INVALID)', []],  # 这是个特殊值
    'BB': ['0XBB(INVALID)', []],  # 这是个特殊值
    'BC': ['0XBC(INVALID)', []],  # 这是个特殊值
    'BD': ['0XBD(INVALID)', []],  # 这是个特殊值
    'BE': ['0XBE(INVALID)', []],  # 这是个特殊值
    'BF': ['0XBF(INVALID)', []],  # 这是个特殊值
    'C0': ['0XC0(INVALID)', []],  # 这是个特殊值
    'C1': ['0XC1(INVALID)', []],  # 这是个特殊值
    'C2': ['0XC2(INVALID)', []],  # 这是个特殊值
    'C3': ['0XC3(INVALID)', []],  # 这是个特殊值
    'C4': ['0XC4(INVALID)', []],  # 这是个特殊值
    'C5': ['0XC5(INVALID)', []],  # 这是个特殊值
    'C6': ['0XC6(INVALID)', []],  # 这是个特殊值
    'C7': ['0XC7(INVALID)', []],  # 这是个特殊值
    'C8': ['0XC8(INVALID)', []],  # 这是个特殊值
    'C9': ['0XC9(INVALID)', []],  # 这是个特殊值
    'CA': ['0XCA(INVALID)', []],  # 这是个特殊值
    'CB': ['0XCB(INVALID)', []],  # 这是个特殊值
    'CC': ['0XCC(INVALID)', []],  # 这是个特殊值
    'CD': ['0XCD(INVALID)', []],  # 这是个特殊值
    'CE': ['0XCE(INVALID)', []],  # 这是个特殊值
    'CF': ['0XCF(INVALID)', []],  # 这是个特殊值
    'D0': ['0XD0(INVALID)', []],  # 这是个特殊值
    'D1': ['0XD1(INVALID)', []],  # 这是个特殊值
    'D2': ['0XD2(INVALID)', []],  # 这是个特殊值
    'D3': ['0XD3(INVALID)', []],  # 这是个特殊值
    'D4': ['0XD4(INVALID)', []],  # 这是个特殊值
    'D5': ['0XD5(INVALID)', []],  # 这是个特殊值
    'D6': ['0XD6(INVALID)', []],  # 这是个特殊值
    'D7': ['0XD7(INVALID)', []],  # 这是个特殊值
    'D8': ['0XD8(INVALID)', []],  # 这是个特殊值
    'D9': ['0XD9(INVALID)', []],  # 这是个特殊值
    'DA': ['0XDA(INVALID)', []],  # 这是个特殊值
    'DB': ['0XDB(INVALID)', []],  # 这是个特殊值
    'DC': ['0XDC(INVALID)', []],  # 这是个特殊值
    'DD': ['0XDD(INVALID)', []],  # 这是个特殊值
    'DE': ['0XDE(INVALID)', []],  # 这是个特殊值
    'DF': ['0XDF(INVALID)', []],  # 这是个特殊值
    'E0': ['0XE0(INVALID)', []],  # 这是个特殊值
    'E1': ['0XE1(INVALID)', []],  # 这是个特殊值
    'E2': ['0XE2(INVALID)', []],  # 这是个特殊值
    'E3': ['0XE3(INVALID)', []],  # 这是个特殊值
    'E4': ['0XE4(INVALID)', []],  # 这是个特殊值
    'E5': ['0XE5(INVALID)', []],  # 这是个特殊值
    'E6': ['0XE6(INVALID)', []],  # 这是个特殊值
    'E7': ['0XE7(INVALID)', []],  # 这是个特殊值
    'E8': ['0XE8(INVALID)', []],  # 这是个特殊值
    'E9': ['0XE9(INVALID)', []],  # 这是个特殊值
    'EA': ['0XEA(INVALID)', []],  # 这是个特殊值
    'EB': ['0XEB(INVALID)', []],  # 这是个特殊值
    'EC': ['0XEC(INVALID)', []],  # 这是个特殊值
    'ED': ['0XED(INVALID)', []],  # 这是个特殊值
    'EE': ['0XEE(INVALID)', []],  # 这是个特殊值
    'EF': ['0XEF(INVALID)', []],  # 这是个特殊值
    'F0': ['CREATE', []],
    'F1': ['CALL', []],
    'F2': ['CALLCODE', []],
    'F3': ['RETURN', []],
    'F4': ['DELEGATECALL', []],
    'F5': ['CREATE2', []],
    'F6': ['0XF6(INVALID)', []],  # 这是个特殊值
    'F7': ['0XF7(INVALID)', []],  # 这是个特殊值
    'F8': ['0XF8(INVALID)', []],  # 这是个特殊值
    'F9': ['0XF9(INVALID)', []],  # 这是个特殊值
    'FA': ['STATICCALL', []],
    'FB': ['CREATE2', []],
    'FC': ['0XFC(INVALID)', []],  # 这是个特殊值
    'FD': ['REVERT', []],
    'FE': ['INVALID', []],
    'FF': ['SELFDESTRUCT', []],
}
