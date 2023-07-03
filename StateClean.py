# 导入json模块
import json
# 导入os模块
import os
# 导入tqdm模块
from tqdm import tqdm
# 导入csv模块
import csv
from collections import defaultdict

# 定义提取变量关系的函数
def extract_variable_relationship(json_data):
    # 创建一个字典来存储函数与变量之间的关系
    function_variable_map = {}

    # 定义一个函数来递归遍历JSON结构
    def traverse(node):
        # 如果节点是字典类型
        if isinstance(node, dict):
            # 检查节点类型是否为函数定义
            if node.get('type') == 'FunctionDefinition':
                # 获取函数名称
                function_name = node.get('name')

                # 提取函数的参数列表中的变量
                parameters = node.get('parameters', {}).get('parameters', [])
                function_variables = [param.get('name') for param in parameters]

                # 提取函数体中引用的变量
                function_body = node.get('body', {})
                variable_references = extract_variable_references(function_body)

                # 将函数与变量之间的关系存储到字典中
                function_variable_map[function_name] = {
                    'variables': function_variables,
                    'references': variable_references
                }

            # 递归遍历子节点
            for key, value in node.items():
                traverse(value)
        # 如果节点是列表类型
        elif isinstance(node, list):
            # 递归遍历列表中的元素
            for item in node:
                traverse(item)

    # 定义一个函数来提取函数体中引用的变量
    def extract_variable_references(node):
        references = []

        # 如果节点是字典类型
        if isinstance(node, dict):
            # 检查节点类型是否为变量引用
            if node.get('type') == 'Identifier':
                reference_name = node.get('name')
                references.append(reference_name)

            # 递归遍历子节点
            for key, value in node.items():
                references.extend(extract_variable_references(value))
        # 如果节点是列表类型
        elif isinstance(node, list):
            # 递归遍历列表中的元素
            for item in node:
                references.extend(extract_variable_references(item))

        return references

    # 开始遍历JSON结构
    traverse(json_data)

    return function_variable_map

# 定义提取状态变量的函数
def extract_state_variables(json_data):
    state_vars = []

    # 定义一个函数来处理节点
    def process_node(node):
        # 如果节点是字典类型
        if isinstance(node, dict):
            # 如果节点是状态变量
            if "isStateVar" in node and node["isStateVar"]:
                state_vars.append(node)
            # 遍历节点的所有子节点
            for key, value in node.items():
                process_node(value)
        # 如果节点是列表类型
        elif isinstance(node, list):
            # 遍历列表中的所有元素
            for item in node:
                process_node(item)

    # 开始处理节点
    process_node(json_data)
    return state_vars

# 获取"AST"文件夹中的所有目录列表
ast_dirs = [dir for dir in os.listdir("AST") if os.path.isdir(os.path.join("AST", dir))]

# 遍历每个目录
for ast_dir in tqdm(ast_dirs):
    # 创建一个字典来存储状态变量及其对应的文件
    state_vars_dict = {}

    # 获取当前目录中的所有JSON文件列表
    json_files = [file for file in os.listdir(os.path.join("AST", ast_dir)) if file.endswith(".json")]

    # 遍历每个JSON文件
    for json_file in json_files:
        # 构造JSON文件的路径
        json_path = os.path.join("AST", ast_dir, json_file)

        # 读取JSON文件
        try:
            with open(json_path, "r") as file:
                json_str = file.read()
        except FileNotFoundError:
            continue

        # 将JSON字符串解析为Python对象（字典）
        try:
            json_data = json.loads(json_str)
        except json.JSONDecodeError:
            continue

        # 提取函数和变量之间的关系
        try:
            relationship_map = extract_variable_relationship(json_data)
        except KeyError:
            continue

        # 提取状态变量
        try:
            state_variables = extract_state_variables(json_data)
        except KeyError:
            continue

        # 将状态变量及其对应的文件添加到字典中
        state_vars_set = frozenset((var['name'], str(var['typeName'])) for var in state_variables)
        if state_vars_set not in state_vars_dict:
            state_vars_dict[state_vars_set] = (ast_dir, json_file, relationship_map)

    # 遍历每个唯一的状态变量集合
    for state_vars_set, (ast_dir, json_file, relationship_map) in state_vars_dict.items():
        # 如果"State"文件夹中对应的目录不存在，则创建它
        os.makedirs(os.path.join("StateClean", ast_dir), exist_ok=True)

        # 构造"State"文件夹中CSV文件的路径
        csv_file = os.path.join("StateClean", ast_dir, json_file.replace(".json", ".csv"))

        # 将结果保存到CSV文件中
        try:
            with open(csv_file, mode='w') as file:
                writer = csv.writer(file)
                writer.writerow(['函数名称', '参数列表', '引用的变量'])
                for function_name, relationship in relationship_map.items():
                    writer.writerow([function_name, relationship['variables'], relationship['references']])

                writer.writerow(['变量名', '变量类型'])
                for state_var in state_vars_set:
                    writer.writerow([state_var[0], state_var[1]])
        except PermissionError:
            continue