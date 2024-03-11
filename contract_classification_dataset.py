from typing import Tuple, Union, List
from torch_geometric.data import Data, Dataset
import numpy as np
import torch
import json
import os
import config
import utils
import random


# 用于合约分类的数据集。
class contract_classification_dataset(Dataset):
    def __init__(self, root_dir):
        super().__init__(root_dir)
        self.data = torch.load(self.processed_file_names[0])
        random.shuffle(self.data)

    # 1.先判断原始文件是否已经存在了，如果存在了那就没有关系，否则是需要提醒报错的。
    # 这里指的原始文件是那几个使用built_vector_dataset创建的json文件。
    @property
    def raw_file_names(self) -> Union[str, List[str], Tuple]:
        # 保存原始文件中所有工程文件夹名字的列表
        project_file_list = []
        # 循环raw目录下所有的工程文件夹，获取所有的工程文件夹名字,保存的是全路径。
        for project_name in os.listdir(config.TRAIN_DATA_DIR_PATH):
            project_dir = os.path.join(config.TRAIN_DATA_DIR_PATH, project_name)
            project_file_list.append(project_dir)
        return project_file_list

    # 2.如果原始文件不存在，说明无法生成数据集。
    def download(self):
        if len(self.raw_file_names) == 0:
            utils.error("原始文件不存在，无法生成数据集。")

    # 3.获取处理以后文件的名字
    @property
    def processed_file_names(self) -> Union[str, List[str], Tuple]:
        # 保存文件为指定的名字,这就是数据集文件。
        return [f"{self.root}/processed/dataset.pt"]

    # 4.对文件进行处理，然后保存到processed中返回的文件列表里面去。
    def process(self):
        # 保存到数据集文件中的容器。
        data_list = []
        for project_full_path in self.raw_file_names:
            for graph_file in os.listdir(project_full_path):
                if not graph_file.endswith(".graph"):  # 不是图数据的文件，那就是.json的文件，里面保存的是原始的字节码和操作码那些信息，并不需要。
                    continue
                with open(f'{project_full_path}/{graph_file}') as graph:
                    graph_content = json.load(graph)
                    x = torch.as_tensor(data=np.array(graph_content['node_feature'], dtype=np.float32))
                    cfg_edge_index = torch.as_tensor(data=np.array(graph_content['cfg_edge'], dtype=np.int64)).T
                    cfg_edge_attr = torch.zeros(cfg_edge_index.shape[1]) + 1  # 制作边的属性，方便进行区分边类型。控制流设置为1，数据流设置为2.
                    dfg_edge_index = torch.as_tensor(data=np.array(graph_content['dfg_edge'], dtype=np.int64)).T
                    dfg_edge_attr = torch.zeros(dfg_edge_index.shape[1]) + 2
                    edge_index = torch.cat((cfg_edge_index, dfg_edge_index), dim=1)
                    edge_attr = torch.cat((cfg_edge_attr, dfg_edge_attr))
                    label = torch.as_tensor(data=np.array(graph_content['label'], dtype=np.float32))
                    data = Data(x=x,
                                edge_index=edge_index,
                                edge_attr=edge_attr,
                                y=label)
                    data_list.append(data)
        # 数据构造完毕以后，直接保存到对应文件中即可。
        torch.save(data_list, self.processed_file_names[0])

    def len(self) -> int:
        return len(self.data)

    def __getitem__(self, item):
        return self.data[item]

    def get(self, idx: int) -> Data:
        return self.data[idx]
