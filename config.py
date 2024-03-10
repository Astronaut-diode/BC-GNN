import os
import utils
import argparse

# 当前这个BC-GNN项目的路径。
BC_GNN_PROJECT_DIR_PATH = os.path.abspath(os.curdir)

# 资源文件夹的路径。
RESOURCES_DIR_PATH = f'{BC_GNN_PROJECT_DIR_PATH}/resources'
utils.create_folder_if_not_exists(RESOURCES_DIR_PATH)
# 所有的待训练字节码都会以文件夹的形式保存在这个目录中，这都是原始样本数据。
BYTECODE_DIR_PATH = f'{RESOURCES_DIR_PATH}/bytecode'
utils.create_folder_if_not_exists(BYTECODE_DIR_PATH)
# 所有的待训练操作码都会以文件夹的形式保存在这个目录中，这都是经过数据处理以后的结果。
TRAIN_DATA_DIR_PATH = f'{RESOURCES_DIR_PATH}/train'
utils.create_folder_if_not_exists(TRAIN_DATA_DIR_PATH)
# 词库预训练模型的保存位置。
CORPUS_FILE_PATH = f'{RESOURCES_DIR_PATH}/corpus_model.pkl'
# 标签文件的标准位置。
LABELS_PATH = f'{RESOURCES_DIR_PATH}/labels.json'

############################## ERROR CODE ##############################
NEW_OPCODES = -102
############################## ERROR CODE ##############################

# 词库文件当中，保存的每个单词的维度向量
encode_dim = 3

# 默认会先加载config配置文件夹，然后设定好程序运行的配置。
parser = argparse.ArgumentParser(description='参数表')
parser.add_argument('--create_word2vec', type=str,
                    help="针对运行预训练模型的模式:\n"
                         "1.create:创建预训练模型的时候用的。\n")
# 下面更新config配置
args = parser.parse_args()
create_word2vec = args.create_word2vec
