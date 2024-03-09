import os
import utils

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

############################## ERROR CODE ##############################
NEW_OPCODES = -102
############################## ERROR CODE ##############################
