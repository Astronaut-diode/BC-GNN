# BC-GNN
基于字节码的图融合的智能合约漏洞检测

## Introduce

因为AST-GNN(MVD-HG)仅能够作用于源代码，所以需要进一步的创建一个可以作用于字节码的研究工作。这里首先从字节码中提取操作码，之后在操作码的基础上提取控制流图和数据流图以形成异构图，最终使用异构图以及图神经网络实现漏洞检测任务。

## Usage

在dataset.zip和rt_dataset.zip中分别保存了全体字节码和runtime部分的字节码的压缩包，解压缩以后按照python main.py --help的指示一个个填入参数即可。如下所示：
``` bash
(lunikhod) root@0efc54cd086a:~/BC-GNN# python main.py --help
usage: main.py [-h] [--run_mode RUN_MODE] [--create_word2vec CREATE_WORD2VEC] [--device DEVICE] [--learning_rate LEARNING_RATE] [--weight_decay WEIGHT_DECAY]
               [--dropout_probability DROPOUT_PROBABILITY] [--learning_change_gamma LEARNING_CHANGE_GAMMA] [--learning_change_epoch LEARNING_CHANGE_EPOCH] [--epoch_size EPOCH_SIZE]
               [--batch_size BATCH_SIZE] [--attack_type ATTACK_TYPE] [--target_dir TARGET_DIR] [--target_file TARGET_FILE]

参数表

optional arguments:
  -h, --help            show this help message and exit
  --run_mode RUN_MODE   区分是训练还是预测(默认是none): 1.train:训练。 2.predict:预测。
  --create_word2vec CREATE_WORD2VEC
                        针对运行预训练模型的模式(默认none): 1.none:不创建预训练模型，也不更新 2.create:创建预训练模型的时候用的。
  --device DEVICE       区分使用的设备，是CPU还是GPU(默认为cuda:0): 1.输入cpu:那就直接使用cpu。 2.输入cuda:i:那就直接使用第i张显卡。
  --learning_rate LEARNING_RATE
                        使用的学习率(默认为0.2): 直接输入浮点数。
  --weight_decay WEIGHT_DECAY
                        模型权重正则化的参数(默认为0.0001): 直接输入浮点数。
  --dropout_probability DROPOUT_PROBABILITY
                        dropout的概率(默认为0.1): 直接输入浮点数。
  --learning_change_gamma LEARNING_CHANGE_GAMMA
                        学习率更新的倍率(默认为0.1): 直接输入浮点数。
  --learning_change_epoch LEARNING_CHANGE_EPOCH
                        学习率更新epoch(默认为30): 直接输入整数。
  --epoch_size EPOCH_SIZE
                        分多少世代(默认为50): 直接输入整数。
  --batch_size BATCH_SIZE
                        一次同时处理多少数据(默认为1): 直接输入整数。
  --attack_type ATTACK_TYPE
                        数据文件夹的名字:
  --target_dir TARGET_DIR
                        预测文件夹的名字:
  --target_file TARGET_FILE
                        预测文件的名字:
```

## Expermental Results

数据集组成

![图4-4 Bytecode_dataset](https://github.com/Astronaut-diode/BC-GNN/assets/57606131/a34baebc-3bde-4029-96dc-90ace8be9f54)

对比实验一，多个方法在Bytecode-Origin上进行实验，记录了七种漏洞类型上的F1 Score。

![图4-5 对比实验4-1](https://github.com/Astronaut-diode/BC-GNN/assets/57606131/b1505275-da32-455d-93a9-2039351d8e6e)

对比实验二，多个方法在Bytecode-Augmentation上进行实验，记录了七种漏洞类型上的F1 Score。

![图4-6 对比实验4-2](https://github.com/Astronaut-diode/BC-GNN/assets/57606131/29486cfa-ef01-4926-8099-acb86dec1f43)

以下两图是对比实验二中所对应的ROC曲线

![4-7ROC-1](https://github.com/Astronaut-diode/BC-GNN/assets/57606131/d1eaad3f-868f-46f9-b357-f32193b77266)
![4-8ROC-2](https://github.com/Astronaut-diode/BC-GNN/assets/57606131/a1d99fd7-44f3-4275-854a-3238e2c050b7)

消融实验结果图（分为部分结果图以及详细结果图版本，包含的评估指标是不同的）

![图4-9 消融实验部分结果](https://github.com/Astronaut-diode/BC-GNN/assets/57606131/52ee26f0-2d4b-49b3-9925-9bf7fd72bd2c)

![图4-10 消融实验详细](https://github.com/Astronaut-diode/BC-GNN/assets/57606131/cbfab56a-dc3f-4b3c-aa7d-2e89d59bb17b)


## 项目结构
```shell
(lunikhod) root@0efc54cd086a:~/BC-GNN# tree
.
|-- contract_classification_dataset.py  # 为模型创建数据集。
|-- contract_classification_model.py  # 模型。
|-- contract_classification_train.py  # 训练的过程。
|-- ConvertToOpcodesAndGraph.py  # 将存放在原始的字节码文件夹中的字节码文件进行文件处理，并转换为图结构。
|-- create_control_flow_graph.py  # 创建控制流图。
|-- create_data_flow_graph.py  # 创建数据流图。
|-- create_node_feature.py  # 向量化并保存到graph文件中。
|-- get_word2vec.py  # 获取所有的相关词向量
|-- README.md
|-- config.py  # 配置文件
|-- main.py  # 主入口
|-- resources  # 资源文件夹
|   |-- bytecode  # 存放待检测的工程项目。
|   |   |-- 1  # 工程项目的名字
|   |       |-- A.bin # 待检测的字节码文件
|   |-- train  # 保存数据处理以后的操作码的位置。
|   |   |-- 1  # 工程项目的名字
|   |       |-- A.json # 字节码文件生成的操作码，并以json格式保存
|-- utils.py  # 一些工具函数。
|-- Node.py  # 节点类。
|-- processDataset.py 处理数据集，因为原始的数据集是Contract-Augmentation,所以需要处理为字节码形式的。
|-- dataset  # 存储数据集的地方，这里一开始存的是Contract-Augmentation。已经保存为了压缩包，自己解开就行。
|   |-- xxx  # 七种攻击的文件夹，其中保存的是解压缩以后处理的内容。
|       |-- sol_source  # 里面保存的是原始的智能合约文件。
|       |-- contract_labels.json  # 对应的原始的标签文件。
|       |-- bytecode  # 里面就保存处理以后的字节码文件。
|       |-- labels.json  # 存储的是字节码文件对应的标签文件。 
|-- dataset.zip  # 字节码数据集的压缩包。
|-- rt_dataset.zip  # 仅包含runtime部分字节码的压缩包。
```

## Maintainers

徐敬杰

[@Astronaut-diode](https://github.com/Astronaut-diode) 

浙江工业大学 软件工程专业硕士在读

邮箱地址:925791559@qq.com
