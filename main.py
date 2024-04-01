import numpy as np
import torch
from torch_geometric.data import Data

import config
import os
import datetime
import utils
import json
from ConvertToOpCodesAndGraph import convertToOpCodesAndGraph
from contract_classification_model import contract_classification_model
from create_node_feature import create_node_feature
from gensim.models.word2vec import Word2Vec
from get_word2vec import get_word2vec
from contract_classification_train import contract_classification_train
from contract_classification_dataset import contract_classification_dataset

if __name__ == '__main__':
    os.chdir("/root/BC-GNN")
    start_time = datetime.datetime.now()

    if config.run_mode == "predict":
        convertToOpCodesAndGraph(f"{config.target_dir}")  # 将目标文件夹中的字节码转换为对应的操作码，并保存到json文件中。
        detect_res = f"{config.RESOURCES_DIR_PATH}/res.json"
        res_json = []
        if os.path.exists(detect_res):  # 如果文件存在，读取一下
            with open(detect_res, 'r') as res:
                res_json = json.load(res)
        attack_type = ['access_control', 'arithmetic', 'dos', 'front_running', 'reentrancy', 'time_manipulation',
                       'unchecked']
        for attack in attack_type:
            model_dir = config.model_data_dir.replace("predict", attack)
            max_mode_file = os.listdir(model_dir)[0]
            max_score = 0
            for model_file in os.listdir(model_dir):
                score = float(model_file.replace(".pth", ""))
                if score > max_score:
                    max_score = score
                    max_mode_file = model_file
            model = contract_classification_model()
            # 加载原始保存的参数
            model_params_dict = torch.load(os.path.join(model_dir, max_mode_file))
            best_threshold = model_params_dict["best_threshold"]
            # 将加载的参数添加到模型当中去
            model.load_state_dict(model_params_dict["model_params"])
            # 加载预训练模型，开始获取目标的向量。加载标签文件。这样就只需要加载一次，而不需要重复加载。
            word2vec_model = Word2Vec.load(config.CORPUS_FILE_PATH.replace("predict", attack)).wv
            # 根据模型，创建所有图文件向量化以后的信息。
            json_file = f'{config.TRAIN_DATA_DIR_PATH}/{config.target_dir}/{config.target_file}.json'
            graph_file = f'{config.TRAIN_DATA_DIR_PATH}/{config.target_dir}/{config.target_file}.graph'
            if not json_file.endswith(".json"):  # 只有json文件才需要创建对应的向量化文件。
                continue
            create_node_feature(json_file,
                                graph_file,
                                word2vec_model, None)
            with open(graph_file) as graph:
                graph_content = json.load(graph)
                x = torch.as_tensor(data=np.array(graph_content['node_feature'], dtype=np.float32))
                cfg_edge_index = torch.as_tensor(data=np.array(graph_content['cfg_edge'], dtype=np.int64)).T
                cfg_edge_attr = torch.zeros(cfg_edge_index.shape[1]) + 1  # 制作边的属性，方便进行区分边类型。控制流设置为1，数据流设置为2.
                dfg_edge_index = torch.as_tensor(data=np.array(graph_content['dfg_edge'], dtype=np.int64)).T
                dfg_edge_attr = torch.zeros(dfg_edge_index.shape[1]) + 2
                edge_index = torch.cat((cfg_edge_index, dfg_edge_index), dim=1)
                edge_attr = torch.cat((cfg_edge_attr, dfg_edge_attr))
                data = Data(x=x,
                            edge_index=edge_index,
                            edge_attr=edge_attr)
                predict = model(data)
                if predict.item() >= best_threshold:
                    print("存在", attack, "类型的漏洞")
                    res_json.append(
                        {
                            "name": f"{config.target_file}.bin",
                            "label": 1,
                            "attack_type": attack
                        }
                    )
                else:
                    print("不存在", attack, "类型的漏洞")
                    res_json.append(
                        {
                            "name": f"{config.target_file}.bin",
                            "label": 0,
                            "attack_type": attack
                        }
                    )
        utils.save_json(res_json, detect_res)
        exit(1)

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

    if config.run_mode == 'train':
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
        contract_classification_train(total_dataset)
    end_time = datetime.datetime.now()
    utils.tip("程序一共执行了:" + str(end_time - start_time) + "秒")
