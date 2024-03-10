# BC-GNN
基于字节码的图融合的智能合约漏洞检测

## 项目结构
```shell
(lunikhod) root@0efc54cd086a:~/BC-GNN# tree
.
|-- ConvertToOpcodesAndGraph.py  # 将存放在原始的字节码文件夹中的字节码文件进行文件处理，并转换为图结构。
|-- create_control_flow_graph.py  # 创建控制流图。
|-- README.md
|-- config.py  # 配置文件
|-- main.py  # 主入口
|-- resources  # 资源文件夹
|   |-- bytecode  # 存放待检测的工程项目。
|   |   `-- 1  # 工程项目的名字
|   |       |-- A.bin # 待检测的字节码文件
|   `-- train  # 保存数据处理以后的操作码的位置。
|   |   `-- 1  # 工程项目的名字
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
```