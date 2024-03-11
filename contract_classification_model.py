# coding=UTF-8
from torch_geometric.nn import MessagePassing, GATConv, global_mean_pool, Linear, RGCNConv
from typing import Optional
from torch import Tensor
from torch.nn import ReLU, Sigmoid, Dropout
from torch_sparse import SparseTensor
import config
import torch


class contract_classification_model(MessagePassing):
    def __init__(self):
        super(contract_classification_model, self).__init__()
        self.RGCNconv1 = RGCNConv(in_channels=3, out_channels=1, num_relations=2)
        self.final_Linear = Linear(in_channels=1, out_channels=1)
        self.dropout = Dropout(p=config.dropout_probability)
        self.relu = ReLU()
        self.sigmoid = Sigmoid()

    def forward(self, data):
        x = self.RGCNconv1(data.x, data.edge_index, data.edge_attr)
        x = self.dropout(x)
        x = self.relu(x)
        x = global_mean_pool(x, data.batch)  # 全局均值池化
        real_res = self.final_Linear(x)
        real_res = self.sigmoid(real_res)
        return real_res

    def message(self, x_j: Tensor) -> Tensor:
        pass

    def aggregate(self, inputs: Tensor, index: Tensor,
                  ptr: Optional[Tensor] = None,
                  dim_size: Optional[int] = None) -> Tensor:
        pass

    def update(self, inputs: Tensor) -> Tensor:
        pass

    def message_and_aggregate(self, adj_t: SparseTensor) -> Tensor:
        pass

    def edge_update(self) -> Tensor:
        pass
