import os
import utils
import argparse
import sys

# 设置最大递归层数为5000
sys.setrecursionlimit(5000)

# 当前这个BC-GNN项目的路径。
BC_GNN_PROJECT_DIR_PATH = os.path.abspath(os.curdir)

############################## ERROR CODE ##############################
NEW_OPCODES = -102
############################## ERROR CODE ##############################

# 词库文件当中，保存的每个单词的维度向量
encode_dim = 300
# 训练集中，用多少为比例进行划分。
train_test_split_percent = 0.7
# 计算度量标准的时候使用的参数
beta = 1
epsilon = 1e-8
# 攻击的最佳阈值
threshold = 0

# 默认会先加载config配置文件夹，然后设定好程序运行的配置。
parser = argparse.ArgumentParser(description='参数表')
parser.add_argument('--run_mode', type=str, default='none',
                    help="区分是训练还是预测(默认是none):\n"
                         "1.train:训练。\n"
                         "2.predict:预测。")
parser.add_argument('--create_word2vec', type=str, default='none',
                    help="针对运行预训练模型的模式(默认none):\n"
                         "1.none:不创建预训练模型，也不更新\n"
                         "2.create:创建预训练模型的时候用的。\n")
parser.add_argument('--device', type=str, default='cuda:0',
                    help="区分使用的设备，是CPU还是GPU(默认为cuda:0):\n"
                         "1.输入cpu:那就直接使用cpu。\n"
                         "2.输入cuda:i:那就直接使用第i张显卡。")
parser.add_argument('--learning_rate', type=float, default=0.2,
                    help="使用的学习率(默认为0.2):\n"
                         "直接输入浮点数。\n")
parser.add_argument('--weight_decay', type=float, default=0.0001,
                    help="模型权重正则化的参数(默认为0.0001):\n"
                         "直接输入浮点数。\n")
parser.add_argument('--dropout_probability', type=float, default=0.1,
                    help="dropout的概率(默认为0.1):\n"
                         "直接输入浮点数。\n")
parser.add_argument('--learning_change_gamma', type=float, default=0.1,
                    help="学习率更新的倍率(默认为0.1):\n"
                         "直接输入浮点数。\n")
parser.add_argument('--learning_change_epoch', type=int, default=10,
                    help="学习率更新epoch(默认为30):\n"
                         "直接输入整数。\n")
parser.add_argument('--epoch_size', type=int, default=50,
                    help="分多少世代(默认为50):\n"
                         "直接输入整数。\n")
parser.add_argument('--batch_size', type=int, default=1,
                    help="一次同时处理多少数据(默认为1):\n"
                         "直接输入整数。\n")
parser.add_argument('--attack_type', type=str,
                    help="数据文件夹的名字:\n")
# 下面更新config配置
args = parser.parse_args()
create_word2vec = args.create_word2vec
run_mode = args.run_mode
# 本次使用的gpu_id
device = args.device
# 使用的学习率
learning_rate = args.learning_rate
# 模型权重正则化的参数
weight_decay = args.weight_decay
# 学习率更新epoch
learning_change_epoch = args.learning_change_epoch
# 学习率更新的倍率
learning_change_gamma = args.learning_change_gamma
# 批处理数量
epoch_size = args.epoch_size
attack_type = args.attack_type
dropout_probability = args.dropout_probability
batch_size = args.batch_size
utils.tip(f"device:{device}")
utils.tip(f"learning_rate:{learning_rate}")
utils.tip(f"weight_decay:{weight_decay}")
utils.tip(f"learning_change_epoch:{learning_change_epoch}")
utils.tip(f"learning_change_gamma:{learning_change_gamma}")
utils.tip(f"epoch_size:{epoch_size}")
utils.tip(f"dropout_probability:{dropout_probability}")
utils.tip(f"batch_size:{batch_size}")
utils.tip(f"attack_type:{attack_type}")

# 资源文件夹的路径。
RESOURCES_DIR_PATH = f'{BC_GNN_PROJECT_DIR_PATH}/{attack_type}/resources'
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
# 训练模型的文件夹,保存数据集.pt以及训练以后得到的模型。
CLASSIFICATION_DIR_PATH = f'{BC_GNN_PROJECT_DIR_PATH}/{attack_type}/classification'
utils.create_folder_if_not_exists(CLASSIFICATION_DIR_PATH)
