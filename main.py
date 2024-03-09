import config
import os
import datetime
import utils
from ConvertToOpCodesAndGraph import convertToOpCodesAndGraph

if __name__ == '__main__':
    start_time = datetime.datetime.now()
    for wait_detect_project in os.listdir(config.BYTECODE_DIR_PATH):
        convertToOpCodesAndGraph(wait_detect_project)  # 将目标文件夹中的字节码转换为对应的操作码，并保存到json文件中。
    end_time = datetime.datetime.now()
    utils.tip("程序一共执行了:" + str(end_time - start_time) + "秒")
