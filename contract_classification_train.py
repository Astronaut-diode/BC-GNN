import config
import torch
import utils
import datetime
from torch_geometric.loader import DataLoader
from contract_classification_model import contract_classification_model


def contract_classification_train(total_dataset):
    split = int(len(total_dataset) * config.train_test_split_percent)  # 找到临界值并进行切割。
    train_dataset = total_dataset[0:split]
    test_dataset = total_dataset[split:]

    model = contract_classification_model().to(config.device)  # 加载模型
    train_loader = DataLoader(dataset=train_dataset, batch_size=config.batch_size)
    # 创建优化器和反向传播函数
    optimizer = torch.optim.SGD(model.parameters(), lr=config.learning_rate, weight_decay=config.weight_decay)
    criterion = torch.nn.BCELoss()
    scheduler = torch.optim.lr_scheduler.StepLR(optimizer, config.learning_change_epoch,
                                                gamma=config.learning_change_gamma, last_epoch=-1)
    utils.tip("数据集和模型等工具加载完毕，开始训练。")
    train_start_time = datetime.datetime.now()
    # 开始训练
    model.train()
    for epoch in range(config.epoch_size):
        # 当前这一轮epoch的总损失值
        total_loss_of_now_epoch = 0.0
        # 更新学习率
        scheduler.step()
        for index, train in enumerate(train_loader):
            train = train.to(config.device)
            optimizer.zero_grad()
            predict = model(train)
            loss = criterion(predict.reshape(-1), train.y)  # 切换为一维数组进行损失的计算。
            loss.backward()
            optimizer.step()
            total_loss_of_now_epoch += loss.item()
        utils.tip(f"{epoch + 1}.结束，总损失值为: {total_loss_of_now_epoch}")
    train_end_time = datetime.datetime.now()
    test_start_time = datetime.datetime.now()
    utils.tip("训练完毕，开始验证。")
    # 开始验证集部分。
    model.eval()
    test_loader = DataLoader(dataset=test_dataset, batch_size=config.batch_size)
    predict_labels = torch.tensor([]).to(config.device)  # 用于待会计算TP、FP等参数的数组，记录预测值以及真是标签。
    y_labels = torch.tensor([]).to(config.device)
    for index, test in enumerate(test_loader):
        test = test.to(config.device)
        predict = model(test)
        predict_labels = torch.cat((predict_labels, predict.reshape(-1)), dim=0)
        y_labels = torch.cat((y_labels, test.y), dim=0)
    utils.tip("验证阶段结束，开始计算最终评估指标。")
    test_end_time = datetime.datetime.now()

    utils.tip(f"本次训练一共耗时{train_end_time - train_start_time}秒, 本次测试一共耗时{test_end_time - test_start_time}秒")
    utils.tip(f"本次的训练合约数为{len(train_dataset)}个, 测试的合约数为{len(test_dataset)}个")
    node_count = 0
    edge_count = 0
    mali_count = 0
    for sample in train_dataset:
        node_count += sample.x.shape[0]
        edge_count += sample.edge_index.shape[1]
        mali_count += int(sample.y.item())
    utils.tip(f"本次训练集中，一共有{node_count}个节点，{edge_count}条边，良性合约为{len(train_dataset) - mali_count}, 恶性合约为{mali_count}")
    node_count = 0
    edge_count = 0
    mali_count = 0
    for sample in test_dataset:
        node_count += sample.x.shape[0]
        edge_count += sample.edge_index.shape[1]
        mali_count += int(sample.y.item())
    utils.tip(f"本次测试集中，一共有{node_count}个节点，{edge_count}条边，良性合约为{len(train_dataset) - mali_count}, 恶性合约为{mali_count}")
    cal_score(predict_labels, y_labels)


# 根据计算出的标签以及原始标签，求出对应的评估指标。
def cal_score(predict_labels, y_labels):
    predict_matrix = (predict_labels >= torch.as_tensor(data=[0.5]).to(config.device)).add(0)
    tp = torch.sum(torch.logical_and(y_labels, predict_matrix), dim=0).reshape(-1, 1)
    fp = torch.sum(torch.logical_and(torch.sub(1, y_labels), predict_matrix), dim=0).reshape(-1, 1)
    tn = torch.sum(torch.logical_and(torch.sub(1, y_labels), torch.sub(1, predict_matrix)), dim=0).reshape(-1, 1)
    fn = torch.sum(torch.logical_and(y_labels, torch.sub(1, predict_matrix)), dim=0).reshape(-1, 1)
    # 由四个基础标签求出对应的四种参数。
    accuracy = tp.add(tn).div(tp.add(fp).add(tn).add(fn)).item()
    precision = tp.div(tp.add(fp)).item()
    recall = tp.div(tp.add(fn)).item()
    f_score = tp.mul(1 + config.beta ** 2).div(
        tp.mul(1 + config.beta ** 2).add(fn.mul(config.beta ** 2).add(fp).add(config.epsilon))).item()
    utils.tip(f"tp:{tp.item()}, fp:{fp.item()}, tn:{tn.item()}, fn:{fn.item()}")
    utils.tip(f"accuracy:{accuracy}, precision:{precision}, recall:{recall}, f_score:{f_score}")
