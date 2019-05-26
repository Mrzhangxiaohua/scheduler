import pandas as pd
import random
import function

# 1.对machine_resources编排格式
# 读取正常机器资源，后期用于存储放置资源
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
print(machine_resources_list[0])
print(machine_resources_list_compair[0])

# 2.对最初始的4040个机器按照已放置的进行更新机器资源并记录
data_machine = pd.read_csv('../data/scheduling_preliminary_b_instance_deploy_20180726.csv', header=None,
                           names=['instance_id', 'app', 'machine_id'])
a = list(set(data_machine['machine_id'].dropna().to_numpy().tolist()))
# 将所有machine进行打乱顺序，得到a
random.shuffle(a)

# 3.对merge_data按照cpu_ave进行降序排列
merge_data = pd.read_csv('merge.csv',
                         usecols=['app_id', 'cpu_average', 'mem_average', 'disk', 'P', 'M', 'PM', 'instance_id',
                                  'instance_host', 'cpu', 'mem'])[:-1][
    ['app_id', 'cpu_average', 'mem_average', 'disk', 'P', 'M', 'PM', 'instance_id', 'instance_host', 'cpu',
     'mem']].fillna(0)
merge_data_list = merge_data.copy().sort_values('cpu_average', ascending=False).to_numpy().tolist()

# 4.正常进行一次放置
# 进行最初始的放置,没有放置的留存
rest_instance_resources_list = []
for i in range(len(merge_data_list)):
    # 判断是否早已放置，放置了则更新资源
    if (merge_data_list[i][8] != 0):
        # 拿到要更新的 machine_index
        machine_index = int(merge_data_list[i][8].split('_')[1]) - 1
        # 更新machine资源，并记录instance,cpu有峰值，因此需要处理
        # 对峰值的进行处理
        cpu_list = list(map(eval, merge_data_list[i][9].split('|')))
        mem_list = list(map(eval, merge_data_list[i][10].split('|')))

        machine_resources_list[machine_index][1] = [machine_resources_list[machine_index][1][j] - cpu_list[j] for j in
                                                    range(98)]
        machine_resources_list[machine_index][2] = [machine_resources_list[machine_index][2][j] - cpu_list[j] for j in
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
print('接下来需要将%d个实例放入到%d个乱序机器里尝试放置' % (len(rest_instance_resources_list), len(a)))

# 5.对于约束APP进行处理
app_constrain = pd.read_csv('../data/scheduling_preliminary_b_app_interference_20180726.csv', header=None,
                            names=['appbefore', 'appafter', 'capacity'])
app_constrain_list = app_constrain.to_numpy().tolist()
app_constrain_dict = {}
for i in range(len(app_constrain_list)):
    app_constrain_list[i].append(i)
    key = app_constrain_list[i][0] + '-' + app_constrain_list[i][1]
    app_constrain_dict[key] = str(app_constrain_list[i][2]) + '-' + str(app_constrain_list[i][3])

# print(app_constrain_dict)


# 6.将rest_instance_resources_list中6970个实例尝试放入到乱序4040机器
another_rest_instance_resources_list = []
for i in range(len(rest_instance_resources_list)):
    print("这是对第%d个的判断" % i)
    flag_placeable = False
    # 对于每一个实例需要定位到机器资源，并进行更新
    for j in range(len(a)):
        machine_index = int(a[j].split('_')[1]) - 1
        # 对cpu峰值判别函数
        flage_cpu = function.is_cpu_satisfied(rest_instance_resources_list[i], machine_resources_list[machine_index],
                                              machine_resources_list_compair[machine_index])
        # 对mem峰值进行判别
        flag_mem = function.is_mem_satisfied(rest_instance_resources_list[i], machine_resources_list[machine_index])
        # 对disk，P, M, PM进行判别
        flag_disk, flag_P, flag_M, flag_PM = function.is_flag_disk_P_M_PM(rest_instance_resources_list[i],
                                                                          machine_resources_list[machine_index])
        # 对约束条件的判断
        flag_constrain, constrain_index_list = function.is_flag_constrain_satisfied(rest_instance_resources_list[i],
                                                                                    machine_resources_list[
                                                                                        machine_index],
                                                                                    app_constrain_list,
                                                                                    app_constrain_dict)
        # 如果cpu峰值满足条件
        if flage_cpu:
            if flag_mem:
                if flag_disk and flag_P and flag_M and flag_PM:
                    if flag_constrain:
                        # 如果可放置，记录
                        flag_placeable = True
                        break
                    else:
                        continue
                else:
                    continue
            else:
                continue
        else:
            continue
    # 根据是否可放置，更新机器资源
    if flag_placeable:
        # 更新各种资源
        # function.update_resource(rest_instance_resources_list[i], machine_resources_list[machine_index], app_constrain_list, constrain_index_list)
        # 更新cpu峰值和mem峰值
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
        machine_resources_list[machine_index][7].append(rest_instance_resources_list[i][7])
        machine_resources_list[machine_index][8].append(rest_instance_resources_list[i][0])
        # 更新约束条件
        if len(constrain_index_list) != 0:
            for z in range(len(constrain_index_list)):
                app_constrain_list[z][2] -= 1

    else:
        # 记录无法放置的实例对象
        another_rest_instance_resources_list.append(rest_instance_resources_list[i])

print(another_rest_instance_resources_list)
print(len(another_rest_instance_resources_list))
# 将剩余的未放置的实例存放,转成list
df = pd.DataFrame(another_rest_instance_resources_list).to_csv('Next_instacne.csv',header =['app_id', 'cpu_ave', 'mem_ave', 'disk', 'P', 'M', 'PM', 'instance_id', 'app_ids', 'cpu', 'mem'])
second_place_instance = pd.read_csv('Next_instacne.csv', header=0,
                                names=['app_id', 'cpu_ave', 'mem_ave', 'disk', 'P', 'M', 'PM', 'instance_id','app_ids','cpu', 'mem'])
second_place_instance_list = second_place_instance.to_numpy().tolist()
# 对未放置的机器进行提取
second_place_machine_list =[]
for i in range(len(machine_resources_list)):
    if len(machine_resources_list[i][7])==0:
        second_place_machine_list.append(machine_resources_list[i])

# 接着放置第二次
second_rest_instance_resources_list = []
for i in range(len(second_place_instance_list)):
    print("这是对第%d个的判断" % i)
    flag_placeable = False
    # 对于每一个实例需要定位到机器资源，并进行更新一共1960个
    for j in range(len(second_place_machine_list)):
        machine_index = int(second_place_machine_list[j][0].split('_')[1]) - 1
        # 对cpu峰值判别函数
        flage_cpu = function.is_cpu_satisfied(second_place_instance_list[i], second_place_machine_list[j],
                                              machine_resources_list_compair[machine_index])
        # 对mem峰值进行判别
        flag_mem = function.is_mem_satisfied(second_place_instance_list[i], second_place_machine_list[j])
        # 对disk，P, M, PM进行判别
        flag_disk, flag_P, flag_M, flag_PM = function.is_flag_disk_P_M_PM(second_place_instance_list[i],
                                                                          second_place_machine_list[j])
        # 对约束条件的判断
        flag_constrain, constrain_index_list = function.is_flag_constrain_satisfied(second_place_instance_list[i],
                                                                                    second_place_machine_list[j],
                                                                                    app_constrain_list,
                                                                                    app_constrain_dict)
        if flage_cpu:
            if flag_mem:
                if flag_disk and flag_P and flag_M and flag_PM:
                    if flag_constrain:
                        # 如果可放置，记录
                        flag_placeable = True
                        break
                    else:
                        continue
                else:
                    continue
            else:
                continue
        else:
            continue
    # 根据是否可放置，更新机器资源
    if flag_placeable:
        # 更新各种资源
        # 更新cpu峰值和mem峰值
        merge_data_list_cpu_temp = list(map(eval, second_place_instance_list[i][9].split('|')))
        merge_data_list_mem_temp = list(map(eval, second_place_instance_list[i][10].split('|')))
        second_place_machine_list[j][1] = [second_place_machine_list[j][1][k] - merge_data_list_cpu_temp[k] for k in range(98)]
        second_place_machine_list[j][2] = [second_place_machine_list[j][2][k] - merge_data_list_mem_temp[k] for k in range(98)]
        # 更新disk，P，M，PM
        second_place_machine_list[j][3] -= second_place_instance_list[i][3]
        second_place_machine_list[j][4] -= second_place_instance_list[i][4]
        second_place_machine_list[j][5] -= second_place_instance_list[i][5]
        second_place_machine_list[j][6] -= second_place_instance_list[i][6]
        second_place_machine_list[j][7].append(second_place_instance_list[i][7])
        second_place_machine_list[j][8].append(second_place_instance_list[i][0])
        # 更新约束条件
        if len(constrain_index_list) != 0:
            for z in range(len(constrain_index_list)):
                app_constrain_list[z][2] -= 1
    else:
        # 记录无法放置的实例对象
        second_rest_instance_resources_list.append(second_place_instance_list[i])

# 整合machine_resource和second_place_machine_list
# 暂存数据
first = machine_resources_list.copy()
second = second_place_machine_list.copy()
# 最终整合
for i in range(len(second)):
    indexs = int(second[i][0].split('_')[1]) - 1
    first[indexs] = second[i]
# 保存结果
result = pd.DataFrame(first).to_csv('final_results.csv', header=['machine_id', 'cpu', 'mem', 'disk', 'P', 'M', 'PM','instance_ids', 'app_ids'])
# 最终只有一个没放置进去，app_8416。最后空机器只有829个空机器