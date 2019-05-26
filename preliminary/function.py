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
    constrain_index_list=[]
    # 1.拿出当前machine中的app_id
    app_list = machine_resources_list[8]
    # 2.与将要放置的app_id组合成键值对
    app_list_combine_key = [app_list[v] + '-' + merge_data_list[0] for v in range(len(app_list))]
    # 3.对组合的每个key在已有的dict中查找
    flag_constrain = True
    for i in range(len(app_list_combine_key)):
        # 3.1 对第i个key进行查找
        is_key_in_dict = app_list_combine_key[i] in app_constrain_dict
        # 3.2 如果没有找到约束条件，则继续遍历
        if not is_key_in_dict:
            continue
        # 3.3 如果找到了约束条件，查看约束条件是否满足可放置要求
        if is_key_in_dict:
            # 3.3.1 如果约束数目大于1，则continue
            constrain_index = int(app_constrain_dict[app_list_combine_key[i]].split('-')[1])
            if app_constrain_list[constrain_index][2] >= 1:
                # 记录可以更新的index
                constrain_index_list.append(constrain_index)
                continue
            # 3.3.2 如果约束数目大于1，则continue
            else:
                flag_constrain = False
                constrain_index_list.clear()
                break
    return flag_constrain, constrain_index_list


def update_resource(merge_data_list, machine_resources_list, app_constrain_list, constrain_index_list):
    """
    更新机器资源和约束资源
    :param merge_data_list: 当前要放置的实例对象['app_id', 'cpu_ave', 'mem_ave', 'disk', 'P', 'M', 'PM', 'instance_id', 'cpu', 'mem']
    :param machine_resources_list: 当前要放置的机器资源情况['machine_id', 'cpu', 'mem', 'disk', 'P', 'M', 'PM','instance_ids', 'app_ids']
    :return:
    """
    # 更新cpu峰值和mem峰值
    merge_data_list_cpu_temp = list(map(eval, merge_data_list[9].split('|')))
    merge_data_list_mem_temp = list(map(eval, merge_data_list[10].split('|')))
    machine_resources_list[1] = [machine_resources_list[1][i] - merge_data_list_cpu_temp[i] for i in range(98)]
    machine_resources_list[2] = [machine_resources_list[2][i] - merge_data_list_mem_temp[i] for i in range(98)]
    # 更新disk，P，M，PM
    machine_resources_list[3] -= merge_data_list[3]
    machine_resources_list[4] -= merge_data_list[4]
    machine_resources_list[5] -= merge_data_list[5]
    machine_resources_list[6] -= merge_data_list[6]
    # 更新约束条件
    if len(constrain_index_list)!=0:
        for i in range(len(constrain_index_list)):
            app_constrain_list[i][2] -= 1