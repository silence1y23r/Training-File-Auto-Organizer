import os
import re
import shutil

# ============================================================
# 【第一部分：配置区域】 —— 直接在此处粘贴你的名单
# ============================================================
# 以后你只需要改这里引号里面的内容就行了
raw_info = """
cindy(肖三) 10组
"""

# ============================================================
# 【第二部分：核心逻辑】 —— 已经全部修好，请放心使用
# ============================================================

def main():
    print("="*50)
    print("      全能自动归类系统 (最终修复版)")
    print("="*50)
    
    # 1. 建立基础变量
    folder_names = []
    group_mapping = {} 
    
    # 解析名单
    for line in raw_info.strip().split('\n'):
        parts = line.split()
        if len(parts) >= 2:
            full_name = parts[0]
            group_id = parts[1]
            folder_names.append(full_name)
            c_match = re.search(r'\((.*?)\)', full_name)
            if c_match:
                c_name = c_match.group(1)
                if group_id not in group_mapping:
                    group_mapping[group_id] = []
                group_mapping[group_id].append(c_name)

    # 确定当前干活的文件夹
    current_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(current_dir)
    script_name = os.path.basename(__file__)

    # 2. 询问并创建同学文件夹
    missing_folders = [f for f in folder_names if not os.path.exists(os.path.join(current_dir, f))]
    if missing_folders:
        print(f"\n[提示] 发现有 {len(missing_folders)} 个同学文件夹还没建立。")
        choice = input("是否现在自动创建这些文件夹？(y/n): ").strip().lower()
        if choice == 'y':
            for f_name in missing_folders:
                os.makedirs(os.path.join(current_dir, f_name))
            print("✓ 文件夹已全部创建。")

    # 3. 建立搜索索引
    name_to_path = {}
    eng_name_to_path = {}
    for f_name in folder_names:
        f_path = os.path.join(current_dir, f_name)
        c_match = re.search(r'\((.*?)\)', f_name)
        if c_match: name_to_path[c_match.group(1)] = f_path
        e_match = re.match(r'^([a-zA-Z_]+)\(', f_name)
        if e_match: eng_name_to_path[e_match.group(1).lower()] = f_path

    # 4. 选择模式
    print("\n模式选择：")
    print(" [1] 小组全员分发 (匹配小组名时，组内成员各得一份复制)")
    print(" [2] 仅按名字分发 (忽略小组)")
    mode = input("请输入数字 (1 或 2): ").strip()

    # --- 关键修复点：提前定义“未匹配文档”路径 ---
    unmatched_dir = os.path.join(current_dir, "未匹配文档")
    if not os.path.exists(unmatched_dir): 
        os.makedirs(unmatched_dir)

    # 5. 扫描当前目录下除了脚本和同学文件夹以外的东西
    exclude_list = set(folder_names)
    exclude_list.add("未匹配文档")
    exclude_list.add(script_name)

    all_items = []
    for item in os.listdir(current_dir):
        # 自动跳过临时文件和排除列表里的东西
        if item.startswith("~$") or item in exclude_list:
            continue
        all_items.append(item)

    # 6. 执行归类搬运
    print(f"\n[系统] 发现待分类项目: {len(all_items)} 个，开始执行...")
    
    for item in all_items:
        source_path = os.path.join(current_dir, item)
        target_paths = [] 
        
        # A. 优先尝试小组匹配
        if mode == '1':
            for g_id, members in group_mapping.items():
                if g_id in item:
                    for m in members:
                        if m in name_to_path:
                            target_paths.append(name_to_path[m])
                    break 
        
        # B. 没匹配到组，再找个人名字
        if not target_paths:
            # 中文匹配
            for c_name, path in name_to_path.items():
                if c_name in item:
                    target_paths.append(path)
                    break
            # 英文匹配
            if not target_paths:
                clean_eng = re.sub(r'[^a-z]', '', item.lower())
                for e_name, path in eng_name_to_path.items():
                    if e_name in clean_eng:
                        target_paths.append(path)
                        break

        # C. 物理分发
        if target_paths:
            target_paths = list(set(target_paths)) 
            for i, target_dir in enumerate(target_paths):
                destination = os.path.join(target_dir, item)
                is_last = (i == len(target_paths) - 1)
                
                try:
                    if os.path.isdir(source_path): # 处理文件夹
                        if is_last: shutil.move(source_path, destination)
                        else:
                            if os.path.exists(destination): shutil.rmtree(destination)
                            shutil.copytree(source_path, destination)
                    else: # 处理文件
                        if is_last: shutil.move(source_path, destination)
                        else: shutil.copy2(source_path, destination)
                    print(f"  ✓ {item} --> 已放入 {os.path.basename(target_dir)}")
                except Exception as e:
                    print(f"  ✗ 处理 {item} 失败: {e}")
        else:
            # 这里就是刚才报错的地方，现在绝对没问题了
            try:
                shutil.move(source_path, os.path.join(unmatched_dir, item))
                print(f"  ? {item} --> 放入 未匹配文档")
            except Exception as e:
                print(f"  ✗ 移动至未匹配文件夹失败: {e}")

    input("\n[完成] 任务已结束，按回车键关闭窗口...")

if __name__ == "__main__":

    main()
