import pandas as pd
import numpy as np

"""
得到不同满足条件的机器需要的最少数目
"""
# machine_resources机器资源,先对disk进行判断需要多少个machine
machine_resources = pd.read_csv('../data/scheduling_preliminary_b_machine_resources_20180726.csv', header=None,
                                names=['instance_host_id', 'cpu', 'mem', 'disk', 'P', 'M', 'PM'])
# 浅复制作为更改的预留
machine_resources_copy = machine_resources.copy()


def count_min_disk_num():
    """
    统计只考虑disk放置，需要的最少机器数目
    经过计算，至少需要机器数目为3103台
    """
    # 定义disk统计的变量
    variables = {60: 53542, 40: 5287, 100: 4832, 80: 2448, 200: 1168, 150: 338,
                 300: 275, 120: 117, 167: 67, 500: 60, 600: 27, 250: 24, 180: 21, 1024: 11, 650: 5, 1000: 2}
    # 对disk进行降序排序
    variables = sorted(variables.items(), key=lambda item: item[0], reverse=True)
    print(variables)

    # 遍历降序排列的disk和数目
    for i in range(len(variables)):
        # 查看variables中的统计信息，1024disk的有4个app
        flag = variables[i][1]
        # 有1024的部署4次
        for k in range(flag):
            print('第 %d 个元组 |  需要操作 %d 个实例，本次是第 %d 个' % (i, flag, k))
            # 每一次部署操作，遍历dataFrame每一行数据
            for j in range(0, len(machine_resources_copy)):
                # 当前的disk需求若小于所给的disk大小，则进行改变变量
                if variables[i][0] <= machine_resources_copy.iloc[j]['disk']:
                    machine_resources_copy['disk'].iloc[j] -= variables[i][0]  # 更新disk值
                    # print(machine_resources.iloc[j]['disk'])
                    break  # 每次部署一个跳出，重新检索下一个
    # 满足所有实例所需的disk最少数量是3103台
    print('对于disk分析所需要的内存为： ' + str(np.sum(machine_resources['disk'] != machine_resources_copy['disk'])))


def count_min_cpu_num():
    """
    统计只考虑disk放置，需要的最少机器数目
    经过计算，至少需要机器数目为4885台
    """
    merge_data = pd.read_csv('merge.csv', usecols=['cpu_average'])[:-1]
    machine_resources = pd.read_csv('../data/scheduling_preliminary_b_machine_resources_20180726.csv', header=None,
                                    names=['instance_host_id', 'cpu', 'mem', 'disk', 'P', 'M', 'PM']).iloc[
                        ::-1].reset_index()
    machine_resources = machine_resources[['cpu']]
    machine_resources_copy1 = machine_resources.copy()
    length = len(merge_data)
    for i in range(len(merge_data)):
        print('一共 %d 个任务，这是第 %d 个调度' % (length, i))
        for j in range(len(machine_resources)):
            if merge_data.iloc[i]['cpu_average'] <= machine_resources_copy1.iloc[j]['cpu']:
                machine_resources_copy1['cpu'].iloc[j] -= merge_data.iloc[i]['cpu_average']
                break
    print('对于cpu分析所需要的machine个数为为： ' + str(np.sum(machine_resources['cpu'] != machine_resources_copy1['cpu'])))


def count_min_mem_num():
    """
    统计只考虑mem放置，需要的最少机器数目
    经过计算，至少需要机器数目为2252台
    """
    merge_data = pd.read_csv('merge.csv', usecols=['mem_max'])[:-1]
    machine_resources = pd.read_csv('../data/scheduling_preliminary_b_machine_resources_20180726.csv', header=None,
                                    names=['instance_host_id', 'cpu', 'mem', 'disk', 'P', 'M', 'PM']).iloc[
                        ::-1].reset_index()
    machine_resources = machine_resources[['mem']]
    machine_resources_copy1 = machine_resources.copy()
    length = len(merge_data)
    for i in range(len(merge_data)):
        print('一共 %d 个任务，这是第 %d 个调度' % (length, i))
        for j in range(len(machine_resources)):
            if merge_data.iloc[i]['mem_max'] <= machine_resources_copy1.iloc[j]['mem']:
                machine_resources_copy1['mem'].iloc[j] -= merge_data.iloc[i]['mem_max']
                break
    print('对于mem分析所需要的machine个数为为： ' + str(np.sum(machine_resources['mem'] != machine_resources_copy1['mem'])))


count_min_disk_num()
# count_min_cpu_num()
# count_min_mem_num()
