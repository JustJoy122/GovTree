import os
import json
import yaml # 需要PyYAML库

DATA_DIR = 'data'
OUTPUT_FILE = 'dist/tree.json'
ROOT_NAME = '浙江省教育系统' # 最终生成的树的总根节点名

def load_info(path):
    """安全地加载一个info.yaml文件，失败时返回空字典。"""
    info_path = os.path.join(path, 'info.yaml')
    try:
        with open(info_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        return {}
    except Exception as e:
        print(f"警告：解析 {info_path} 出错: {e}")
        return {}

def build_tree(path):
    """
    递归扫描目录，构建树结构。
    返回一个字典，代表当前节点及其子树。
    """
    node_name = os.path.basename(path)
    node = {'name': node_name}
    
    # 1. 加载当前目录的info信息
    info = load_info(path)
    if info:
        node['info'] = info
    
    # 2. 递归扫描子节点
    children = []
    try:
        dir_contents = sorted(os.listdir(path))
    except PermissionError:
        print(f"警告：无权限读取目录 {path}")
        dir_contents = []

    for item in dir_contents:
        item_path = os.path.join(path, item)
        # 只处理目录，且忽略以下划线开头的目录（如 _category）
        if os.path.isdir(item_path) and not item.startswith('_'):
            child_node = build_tree(item_path)
            children.append(child_node)
    
    # 3. 如果有子节点，则添加到当前节点下
    if children:
        node['children'] = children
        
    return node

def generate():
    """
    主函数：扫描数据目录，构建完整树并输出到JSON文件。
    """
    print("开始生成组织结构树...")
    
    # 1. 创建输出目录
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    # 2. 构建树结构
    tree_data = []
    for entry in os.scandir(DATA_DIR):
        if entry.is_dir():
            # 为每一个顶层目录生成一棵树
            root_node = build_tree(entry.path)
            tree_data.append(root_node)
    
    # 3. 如果希望所有顶层节点在一个根下面，可以包装一层
    final_data = {
        'name': ROOT_NAME,
        'children': tree_data
    }
    
    # 4. 写入JSON文件
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=2)
    
    print(f"生成完成！树结构已保存到: {OUTPUT_FILE}")

if __name__ == '__main__':
    # 检查依赖
    try:
        import yaml
    except ImportError:
        print("请先安装依赖：pip install pyyaml")
        exit(1)
    generate()
