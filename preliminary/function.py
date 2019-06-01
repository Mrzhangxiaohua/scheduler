import pandas as pd
import random


def is_cpu_satisfied(merge_data_list, machine_resources_list, machine_resources_list_compair):
    """
    进行cpu是否满足的判断
    :param merge_data_list: 当前要放置的实例对象['app_id', 'cpu_ave', 'mem_ave', 'disk', 'P', 'M', 'PM', 'instance_id', 'cpu', 'mem']
    :param machine_resources_list: 当前要放置的机器资源情况['machine_id', 'cpu', 'mem', 'disk', 'P', 'M', 'PM','instance_ids', 'app_ids']
    :param machine_resources_list_compair: 同machine，cpu分时是machine的一半
    :return: 满足条件返回True，否则False
    """
    flag_cpu = True
    left_resource_cpu = [machine_resources_list_compair[1][k] * 2 - machine_resources_list[1][k] for k in range(98)]
    final_left_cpu = [machine_resources_list_compair[1][k] - left_resource_cpu[k] for k in range(98)]
    merge_data_list_cpu = list(map(eval, merge_data_list[9].split('|')))
    for i in range(98):
        if merge_data_list_cpu[i] <= final_left_cpu[i]:
            continue
        else:
            flag_cpu = False
            break
    return flag_cpu


def is_mem_satisfied(merge_data_list, machine_resources_list):
    """
    进行mem是否满足的判断
    :param merge_data_list: 当前要放置的实例对象['app_id', 'cpu_ave', 'mem_ave', 'disk', 'P', 'M', 'PM', 'instance_id', 'cpu', 'mem']
    :param machine_resources_list: 当前要放置的机器资源情况['machine_id', 'cpu', 'mem', 'disk', 'P', 'M', 'PM','instance_ids', 'app_ids']
    :return: 满足条件返回True，否则False
    """
    flag_mem = True
    final_left_mem = machine_resources_list[2]
    merge_data_list_mem = list(map(eval, merge_data_list[10].split('|')))
    for i in range(98):
        if merge_data_list_mem[i] <= final_left_mem[i]:
            continue
        else:
            flag_mem = False
            break
    return flag_mem


def is_flag_disk_P_M_PM(merge_data_list, machine_resources_list):
    """
    进行disk, P, M, PM是否满足的判断
    :param merge_data_list: 当前要放置的实例对象['app_id', 'cpu_ave', 'mem_ave', 'disk', 'P', 'M', 'PM', 'instance_id', 'cpu', 'mem']
    :param machine_resources_list: 当前要放置的机器资源情况['machine_id', 'cpu', 'mem', 'disk', 'P', 'M', 'PM','instance_ids', 'app_ids']
    :return: 满足条件分别返回True，否则False
    """
    flag_disk = merge_data_list[3] <= machine_resources_list[3]
    flag_P = merge_data_list[4] <= machine_resources_list[4]
    flag_M = merge_data_list[5] <= machine_resources_list[5]
    flag_PM = merge_data_list[6] <= machine_resources_list[6]
    return flag_disk, flag_P, flag_M, flag_PM


def is_flag_constrain_satisfied(merge_data_list, machine_resources_list, app_constrain_list, app_constrain_dict):
    """
    进行约束条件的判断
    :param merge_data_list: 当前要放置的实例对象['app_id', 'cpu_ave', 'mem_ave', 'disk', 'P', 'M', 'PM', 'instance_id', 'cpu', 'mem']
    :param machine_resources_list: 当前要放置的机器资源情况['machine_id', 'cpu', 'mem', 'disk', 'P', 'M', 'PM','instance_ids', 'app_ids']
    :param app_constrain_list: 约束条件列表
    :param app_constrain_dict: 键值对字典
    :return: 满足条件分别返回True，否则False
    """
    flag_constrain = True
    constrain_index_list = []
    constrain_index_num = []
    # 1.拿出当前machine中的app_id
    app_list = machine_resources_list[8]
    # 2. 记录对应的已有的app_id种类对应{'app_3559': 1, 'app_3595': 2, 'app_6269': 1}
    app_kind_dict = {}
    for i in app_list:
        if i in app_kind_dict:
            app_kind_dict[i] += 1
        else:
            app_kind_dict[i] = 1
    # 3.组合对应的key进行判断，若重复，则当作一次计算
    # 3.1 进行正向组合
    app_list_combine_key1 = []
    for v in app_kind_dict:
        app_list_combine_key1.append(v + '-' + merge_data_list[0])
    for i in range(len(app_list_combine_key1)):
        # 3.1.1 对第i个key进行查找
        is_key_in_dict1 = app_list_combine_key1[i] in app_constrain_dict
        if not is_key_in_dict1:
            continue
        if is_key_in_dict1:
            # 找到list中的对应index
            constrain_index = int(app_constrain_dict[app_list_combine_key1[i]].split('-')[1])
            # 判断当前的拥有的限制数,如果放入的与已有的相同，则需要拿出数据
            constrain_left_right = app_list_combine_key1[i].split('-')

            constrain_num = app_kind_dict[constrain_left_right[0]] + 1 if (
                    constrain_left_right[0] == constrain_left_right[1]) else 1
            # 判断正向组合是否满足,满足则记录索引
            if app_constrain_list[constrain_index][2] >= constrain_num:
                constrain_index_list.append(constrain_index)
                constrain_index_num.append(constrain_num)
                continue
            else:
                flag_constrain = False
                constrain_index_list.clear()
                constrain_index_num.clear()
                break
    # 3.2 进行反向组合
    app_list_combine_key2 = []
    for v in app_kind_dict:
        if merge_data_list[0] != v:
            app_list_combine_key2.append(merge_data_list[0] + '-' + v)
    if flag_constrain:
        for i in range(len(app_list_combine_key2)):
            # 3.1.1 对第i个key进行查找
            is_key_in_dict2 = app_list_combine_key2[i] in app_constrain_dict
            if not is_key_in_dict2:
                continue
            if is_key_in_dict2:
                constrain_index = int(app_constrain_dict[app_list_combine_key2[i]].split('-')[1])

                constrain_left_right = app_list_combine_key2[i].split('-')
                constrain_num = app_kind_dict[constrain_left_right[1]]
                # 判断反向组合是否满足,满足则记录索引
                if app_constrain_list[constrain_index][2] >= constrain_num:
                    constrain_index_list.append(constrain_index)
                    constrain_index_num.append(constrain_num)
                    continue
                else:
                    flag_constrain = False
                    constrain_index_list.clear()
                    constrain_index_num.clear()
                    break
    return flag_constrain, constrain_index_list, constrain_index_num


def machine_resource_process():
    """
    最初始的机器资源读取，再对其进行格式的处理，返回资源列表和资源对比表
    :return: 返回机器资源列表和对比列表
    """
    machine_resources = pd.read_csv('../data/scheduling_preliminary_b_machine_resources_20180726.csv', header=None,
                                    names=['instance_host_id', 'cpu', 'mem', 'disk', 'P', 'M', 'PM'])
    machine_resources_list = machine_resources.copy().to_numpy().tolist()
    machine_resources_list_compair = machine_resources.copy().to_numpy().tolist()
    for i in range(len(machine_resources_list)):
        machine_resources_list[i].append([])
        machine_resources_list[i].append([])
        machine_resources_list[i][1] = [machine_resources_list[i][1]] * 98
        machine_resources_list[i][2] = [machine_resources_list[i][2]] * 98
        machine_resources_list_compair[i][1] = [machine_resources_list_compair[i][1] / 2] * 98
        machine_resources_list_compair[i][2] = [machine_resources_list_compair[i][2]] * 98
    print("---机器资源格式化处理完成---")
    return machine_resources_list, machine_resources_list_compair


def machine_4040_shuffle():
    """
    得到对机器id的随机序列
    :return: 返回随机机器序列
    """
    data_machine = pd.read_csv('../data/scheduling_preliminary_b_instance_deploy_20180726.csv', header=None,
                               names=['instance_id', 'app', 'machine_id'])
    machine_id = list(set(data_machine['machine_id'].dropna().to_numpy().tolist()))
    random.shuffle(machine_id)
    print("---前4040个机器乱序处理完成---")
    return machine_id


def merge_data_cpu_ave_desecend():
    """
    将合并数据以cpu降序顺序排列进行放置
    :return: 返回降序的实例列表
    """
    merge_data = pd.read_csv('merge.csv',
                             usecols=['app_id', 'cpu_average', 'mem_average', 'disk', 'P', 'M', 'PM', 'instance_id',
                                      'instance_host', 'cpu', 'mem'])[:-1][
        ['app_id', 'cpu_average', 'mem_average', 'disk', 'P', 'M', 'PM', 'instance_id', 'instance_host', 'cpu',
         'mem']].fillna(0)
    merge_data_list = merge_data.copy().sort_values('cpu_average', ascending=False).to_numpy().tolist()
    print("---合并数据按照cpu_average降序排列完成---")
    return merge_data_list


def app_constrain_dict_and_key():
    """
    对约束条件进行处理，得到字典索引格式和list格式
    :return: 返回约束list和dict
    """
    app_constrain = pd.read_csv('../data/scheduling_preliminary_b_app_interference_20180726.csv', header=None,
                                names=['appbefore', 'appafter', 'capacity'])
    app_constrain_list = app_constrain.to_numpy().tolist()
    app_constrain_dict = {}
    for i in range(len(app_constrain_list)):
        app_constrain_list[i].append(i)
        key_1 = app_constrain_list[i][0] + '-' + app_constrain_list[i][1]
        app_constrain_dict[key_1] = str(app_constrain_list[i][2]) + '-' + str(app_constrain_list[i][3])
    print("---app约束数据封装处理完成---")
    return app_constrain_list, app_constrain_dict


def first_assign(merge_data_list, machine_resources_list):
    """
    进行最初始的放置,没有放置的进行二次检测放置
    :param merge_data_list: 需要检测的放置实例
    :param machine_resources_list: 所有的机器资源实例
    :return: 返回更新后的机器资源和为
    """
    rest_instance_resources_list = []
    for i in range(len(merge_data_list)):
        # 判断是否早已放置，放置了则更新资源
        if merge_data_list[i][8] != 0:
            machine_index = int(merge_data_list[i][8].split('_')[1]) - 1
            # 更新machine资源，并记录instance,cpu有峰值，因此需要处理
            # 对峰值的进行处理
            cpu_list = list(map(eval, merge_data_list[i][9].split('|')))
            mem_list = list(map(eval, merge_data_list[i][10].split('|')))
            machine_resources_list[machine_index][1] = [machine_resources_list[machine_index][1][j] - cpu_list[j] for j
                                                        in
                                                        range(98)]
            machine_resources_list[machine_index][2] = [machine_resources_list[machine_index][2][j] - mem_list[j] for j
                                                        in
                                                        range(98)]
            machine_resources_list[machine_index][3] -= merge_data_list[i][3]
            machine_resources_list[machine_index][4] -= merge_data_list[i][4]
            machine_resources_list[machine_index][5] -= merge_data_list[i][5]
            machine_resources_list[machine_index][6] -= merge_data_list[i][6]
            # index为7放置instance顺寻，index为8放置app顺序
            machine_resources_list[machine_index][7].append(merge_data_list[i][7])
            machine_resources_list[machine_index][8].append(merge_data_list[i][0])
        else:
            rest_instance_resources_list.append(merge_data_list[i])
    print("已有的固定资源已放置完成")
    print('接下来需要将%d个实例放入到4040个乱序机器里尝试放置' % (len(rest_instance_resources_list)))
    return machine_resources_list, rest_instance_resources_list


def second_assign(rest_instance_resources_list, a, machine_resources_list, machine_resources_list_compair,
                  app_constrain_list, app_constrain_dict):
    """
    进行第二次放置，将需要放置的实例放入到4040个机器中进行检测
    :param rest_instance_resources_list: 剩余要放置的实例
    :param a: 乱序的机器
    :param machine_resources_list: 机器资源列表
    :param machine_resources_list_compair: 用于原始资源对比的机器资源列表
    :param app_constrain_list: 约束列表
    :param app_constrain_dict: 约束字典
    :return: 放置后的机器资源列表，机器资源限制列表，剩余无法放置的机器列表
    """
    # 存放不合适的实例
    not_suit_machine_4040 = []
    for i in range(len(rest_instance_resources_list)):
        print("这是对第%d个的判断" % i)
        flag_placeable = False
        for j in range(len(a)):
            machine_index = int(a[j].split('_')[1]) - 1
            # 对cpu峰值判别函数
            flage_cpu = is_cpu_satisfied(rest_instance_resources_list[i], machine_resources_list[machine_index],
                                         machine_resources_list_compair[machine_index])
            # 对mem峰值进行判别
            flag_mem = is_mem_satisfied(rest_instance_resources_list[i], machine_resources_list[machine_index])
            # 对disk，P, M, PM进行判别
            flag_disk, flag_P, flag_M, flag_PM = is_flag_disk_P_M_PM(rest_instance_resources_list[i],
                                                                     machine_resources_list[machine_index])
            # 对约束条件的判断
            flag_constrain, constrain_index_list, constrain_index_num = is_flag_constrain_satisfied(
                rest_instance_resources_list[i], machine_resources_list[machine_index],
                app_constrain_list, app_constrain_dict)
            if flage_cpu and flag_mem and flag_disk and flag_P and flag_M and flag_PM and flag_constrain:

                merge_data_list_cpu_temp = list(map(eval, rest_instance_resources_list[i][9].split('|')))
                merge_data_list_mem_temp = list(map(eval, rest_instance_resources_list[i][10].split('|')))
                machine_resources_list[machine_index][1] = [
                    machine_resources_list[machine_index][1][i] - merge_data_list_cpu_temp[i] for i in range(98)]
                machine_resources_list[machine_index][2] = [
                    machine_resources_list[machine_index][2][i] - merge_data_list_mem_temp[i] for i in range(98)]
                # 更新disk，P，M，PM
                machine_resources_list[machine_index][3] -= rest_instance_resources_list[i][3]
                machine_resources_list[machine_index][4] -= rest_instance_resources_list[i][4]
                machine_resources_list[machine_index][5] -= rest_instance_resources_list[i][5]
                machine_resources_list[machine_index][6] -= rest_instance_resources_list[i][6]
                # 记录对应的instance_id和app_id
                machine_resources_list[machine_index][7].append(rest_instance_resources_list[i][7])
                machine_resources_list[machine_index][8].append(rest_instance_resources_list[i][0])
                # 更新约束条件
                if len(constrain_index_list) != 0:
                    for z in range(len(constrain_index_list)):
                        app_constrain_list[constrain_index_list[z]][2] -= constrain_index_num[z]
                flag_placeable = True
                break
            else:
                continue
        if not flag_placeable:
            not_suit_machine_4040.append(rest_instance_resources_list[i])
    print('重新扫描后，原来6523 个实例未放置，如今还剩 %d 个实例未放置' % len(not_suit_machine_4040))
    return machine_resources_list, app_constrain_list, not_suit_machine_4040


def rest_1960_machine(machine_resources_list, not_suit_machine_4040):
    """
    将剩余的1960个机器提取出来，将未放置的实例进行放置
    :param machine_resources_list: 机器资源列表
    :param not_suit_machine_4040: 机器实例列表
    :return: 无法放置的机器实例列表，剩余的机器资源列表
    """
    second_place_instance_list = not_suit_machine_4040.copy()
    second_place_machine_list = []
    for i in range(len(machine_resources_list)):
        if len(machine_resources_list[i][7]) == 0:
            second_place_machine_list.append(machine_resources_list[i])
    return second_place_instance_list, second_place_machine_list


def third_assign(second_place_instance_list, second_place_machine_list, machine_resources_list_compair,
                 app_constrain_list, app_constrain_dict):
    """
    第三次进行放置，将剩余的机器实例放置到剩下的1960个机器中
    :param second_place_instance_list: 需要放置第实例
    :param second_place_machine_list: 需要放置的机器
    :param machine_resources_list_compair: 对比资源列表
    :param app_constrain_list: 约束条件列表
    :param app_constrain_dict: 约束条件字典
    :return: 返回最后的机器列表，最后无法放置的实例，app约束列表
    """
    second_rest_instance_resources_list = []
    for i in range(len(second_place_instance_list)):
        print("这是对第%d个的判断" % i)
        flag_placeable = False
        # 对于每一个实例需要定位到机器资源，并进行更新一共1960个
        for j in range(len(second_place_machine_list)):
            second_machine_index = int(second_place_machine_list[j][0].split('_')[1]) - 1
            # 对cpu峰值判别函数
            flage_cpu = is_cpu_satisfied(second_place_instance_list[i], second_place_machine_list[j],
                                         machine_resources_list_compair[second_machine_index])
            # 对mem峰值进行判别
            flag_mem = is_mem_satisfied(second_place_instance_list[i], second_place_machine_list[j])
            # 对disk，P, M, PM进行判别
            flag_disk, flag_P, flag_M, flag_PM = is_flag_disk_P_M_PM(second_place_instance_list[i],
                                                                     second_place_machine_list[j])
            # 对约束条件的判断
            flag_constrain, constrain_index_list, constrain_index_num = is_flag_constrain_satisfied(
                second_place_instance_list[i], second_place_machine_list[j], app_constrain_list, app_constrain_dict)
            if flage_cpu and flag_mem and flag_disk and flag_P and flag_M and flag_PM and flag_constrain:
                # 更新各种资源
                # 更新cpu峰值和mem峰值
                merge_data_list_cpu_temp = list(map(eval, second_place_instance_list[i][9].split('|')))
                merge_data_list_mem_temp = list(map(eval, second_place_instance_list[i][10].split('|')))
                second_place_machine_list[j][1] = [second_place_machine_list[j][1][k] - merge_data_list_cpu_temp[k] for
                                                   k in range(98)]
                second_place_machine_list[j][2] = [second_place_machine_list[j][2][k] - merge_data_list_mem_temp[k] for
                                                   k in range(98)]
                # 更新disk，P，M，PM
                second_place_machine_list[j][3] -= second_place_instance_list[i][3]
                second_place_machine_list[j][4] -= second_place_instance_list[i][4]
                second_place_machine_list[j][5] -= second_place_instance_list[i][5]
                second_place_machine_list[j][6] -= second_place_instance_list[i][6]
                # 记录对应的instance_id和app_id
                second_place_machine_list[j][7].append(second_place_instance_list[i][7])
                second_place_machine_list[j][8].append(second_place_instance_list[i][0])
                # 更新约束条件
                if len(constrain_index_list) != 0:
                    for z in range(len(constrain_index_list)):
                        app_constrain_list[constrain_index_list[z]][2] -= constrain_index_num[z]
                flag_placeable = True
                break
            else:
                continue
        if not flag_placeable:
            second_rest_instance_resources_list.append(second_place_instance_list[i])
    print("最终有%d个放置不进去" % len(second_rest_instance_resources_list))
    return second_place_machine_list, second_rest_instance_resources_list, app_constrain_list

