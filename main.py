import config
import os
import datetime
import utils
import json
from ConvertToOpCodesAndGraph import convertToOpCodesAndGraph
from create_node_feature import create_node_feature
from gensim.models.word2vec import Word2Vec
from get_word2vec import get_word2vec
from contract_classification_train import contract_classification_train
from contract_classification_dataset import contract_classification_dataset

if __name__ == '__main__':
    start_time = datetime.datetime.now()
    for wait_detect_project in sorted(os.listdir(config.BYTECODE_DIR_PATH)):
        convertToOpCodesAndGraph(wait_detect_project)  # 将目标文件夹中的字节码转换为对应的操作码，并保存到json文件中。

    # 至此，全部转换为了操作码，并构建了数据流图和控制流图，都保存到了json文件中。读取所有的指令组以及指令的类型，用于构建对应的语料库，最终用于训练。
    if (config.create_word2vec == "create" or not os.path.exists(config.CORPUS_FILE_PATH)) or \
            config.create_word2vec == "update":
        sentences = []
        for train_dir in sorted(os.listdir(config.TRAIN_DATA_DIR_PATH)):
            get_word2vec(f"{config.TRAIN_DATA_DIR_PATH}/{train_dir}", sentences)

    if config.create_word2vec == "create" or not os.path.exists(config.CORPUS_FILE_PATH):  # 创建词向量模型
        # 因为之前没有文件，所以先进行训练。
        w2v = Word2Vec(sentences=[sentences], size=config.encode_dim, workers=16, sg=1, min_count=1)
        # 保存训练以后的模型。
        w2v.save(config.CORPUS_FILE_PATH)
        utils.tip(f"{config.CORPUS_FILE_PATH}语料库模型创建成功")
    elif config.create_word2vec == 'update':  # 更新词向量模型
        # 加载之前已经保存好的文件。
        w2v = Word2Vec.load(config.CORPUS_FILE_PATH)
        # 为新的sentence创建内容。
        update_sentences = [sentences]
        # 将这个内容添加到词表中。
        w2v.build_vocab(update_sentences, update=True)
        # 开始训练内容。
        w2v.train(update_sentences, total_examples=w2v.corpus_count, epochs=10)
        # 保存训练以后的模型。
        w2v.save(config.CORPUS_FILE_PATH)

    # 加载预训练模型，开始获取目标的向量。加载标签文件。这样就只需要加载一次，而不需要重复加载。
    word2vec_model = Word2Vec.load(config.CORPUS_FILE_PATH).wv
    labels_file_path = config.LABELS_PATH
    label_file = open(labels_file_path, 'r')
    label_dict = json.load(label_file)
    label_file.close()
    # 根据模型，创建所有图文件向量化以后的信息。
    for train_dir in sorted(os.listdir(config.TRAIN_DATA_DIR_PATH)):
        for json_file in os.listdir(f'{config.TRAIN_DATA_DIR_PATH}/{train_dir}'):
            if json_file.endswith(".json"):  # 只有json文件才需要创建对应的向量化文件。
                create_node_feature(f'{config.TRAIN_DATA_DIR_PATH}/{train_dir}/{json_file}',
                                    f'{config.TRAIN_DATA_DIR_PATH}/{train_dir}/{json_file.replace(".json", ".graph")}',
                                    word2vec_model, label_dict)

    # 加载数据集
    total_dataset = contract_classification_dataset(config.CLASSIFICATION_DIR_PATH)
    if config.run_mode == 'train':
        contract_classification_train(total_dataset)
    end_time = datetime.datetime.now()
    utils.tip("程序一共执行了:" + str(end_time - start_time) + "秒")
