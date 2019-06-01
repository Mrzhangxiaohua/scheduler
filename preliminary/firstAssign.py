from function import *

# 1.对machine_resources编排格式
machine_resources_list, machine_resources_list_compair = machine_resource_process()

# 2.对最初始的4040个机器按照已放置的进行更新机器资源并记录
a = machine_4040_shuffle()

# 3.对merge_data按照cpu_ave进行降序排列
merge_data_list = merge_data_cpu_ave_desecend()

# 4.对于约束APP进行处理
app_constrain_list, app_constrain_dict = app_constrain_dict_and_key()

# 4.正常进行一次放置资源的更新
machine_resources_list, rest_instance_resources_list = first_assign(merge_data_list, machine_resources_list)

# 5.将rest_instance_resources_list中6970个实例尝试放入到乱序4040机器
machine_resources_list, app_constrain_list, not_suit_machine_4040 = second_assign(rest_instance_resources_list, a,
                                                                                  machine_resources_list,
                                                                                  machine_resources_list_compair,
                                                                                  app_constrain_list,
                                                                                  app_constrain_dict)
# 6.整理剩余需要放置的1960个机器和剩余的实例
second_place_instance_list, second_place_machine_list = rest_1960_machine(machine_resources_list, not_suit_machine_4040)

# 7.接着放置第二次放置，将剩余实例放置到1960个实例中去
second_place_machine_list, second_rest_instance_resources_list, app_constrain_list = third_assign(
    second_place_instance_list, second_place_machine_list, machine_resources_list_compair, app_constrain_list,
    app_constrain_dict)

# 8.生成提交文件
sub = []
for i in range(6000):
    if machine_resources_list[i][7] != 0:
        for j in range(len(machine_resources_list[i][7])):
            sub.append([machine_resources_list[i][7][j], machine_resources_list[i][0]])

submission = pd.DataFrame(sub).to_csv("re_check_submit.csv", index=False, header=0)
