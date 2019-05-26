import pandas as pd
import numpy as np

app_resources = pd.read_csv('../data/scheduling_preliminary_b_app_resources_20180726.csv', header=None,
                            names=['app_id', 'cpu', 'mem', 'disk', 'P', 'M', 'PM'])
# 以|分隔数据列
cpu = app_resources['cpu'].str.split('|', expand=False)
mem = app_resources['mem'].str.split('|', expand=False)

# 统计cpu的各项特征
app_resources['cpu_max'] = [np.array(x, dtype=np.float).max() for x in cpu[:]]
app_resources['cpu_min'] = [np.array(x, dtype=np.float).min() for x in cpu[:]]
app_resources['cpu_average'] = [np.array(x, dtype=np.float).mean() for x in cpu[:]]
app_resources['cpu_var'] = [np.array(x, dtype=np.float).std() for x in cpu[:]]
# 统计mem的各项特征
app_resources['mem_max'] = [np.array(x, dtype=np.float).max() for x in mem[:]]
app_resources['mem_min'] = [np.array(x, dtype=np.float).min() for x in mem[:]]
app_resources['mem_average'] = [np.array(x, dtype=np.float).mean() for x in mem[:]]
app_resources['mem_var'] = [np.array(x, dtype=np.float).std() for x in mem[:]]
# 生成cpu、mem各项指标
app_resources.to_csv('test.csv', index=False)

instance_deploy = pd.read_csv('../data/scheduling_preliminary_b_instance_deploy_20180726.csv', header=None,
                              names=['instance_id', 'app_id', 'instance_host'])
app_resources_and_instance_deploy = pd.merge(app_resources, instance_deploy, how='left', on='app_id')

# 将统计特征最后汇总
final_disk = app_resources_and_instance_deploy['disk'].sum()
final_cpu_max = app_resources_and_instance_deploy['cpu_max'].sum()
final_cpu_min = app_resources_and_instance_deploy['cpu_min'].sum()
final_cpu_average = app_resources_and_instance_deploy['cpu_average'].sum()
final_cpu_var = app_resources_and_instance_deploy['cpu_var'].sum()

final_mem_max = app_resources_and_instance_deploy['mem_max'].sum()
final_mem_min = app_resources_and_instance_deploy['mem_min'].sum()
final_mem_average = app_resources_and_instance_deploy['mem_average'].sum()
final_mem_var = app_resources_and_instance_deploy['mem_var'].sum()

All_value_counts = app_resources_and_instance_deploy['disk'].value_counts()
print(All_value_counts)

df = pd.DataFrame([None, None, None, final_disk, None, None, None,
                   final_cpu_max, final_cpu_min, final_cpu_average, final_cpu_var,
                   final_mem_max, final_mem_min, final_mem_average, final_mem_var,
                   None, None]).T

# 列对应
df.columns = app_resources_and_instance_deploy.columns
# 组合最后的统计信息
app_resources_and_instance_deploy = pd.concat([app_resources_and_instance_deploy, df, ], ignore_index=True)

app_resources_and_instance_deploy.to_csv('merge.csv')

