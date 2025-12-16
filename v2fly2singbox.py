import os
import json

# 设置
base_dir = 'domain-list-community/data/' # 规则文件所在目录
version = 3 # Sing-box 规则版本

# 忽略列表：排除非规则文件和通常不需要走代理的中国大陆规则
ignore_files = [
    'README.md', 'README_CN.md', 'README_EN.md', '.DS_Store', 'all'
]
# 排除以特定后缀结尾的文件（如非规则文本文件）
exclude_suffixes = ['.txt', '.md'] 


# --- 辅助函数：清除内容中的注释和额外空格 ---
def clean_content(content):
    space_index = content.find(' ')
    if space_index != -1:
        return content[:space_index].strip()
    else:
        return content.strip()

# --- 规则文件处理核心逻辑：递归处理 include ---
def process_files(initial_files, base_path):
    files_to_process = list(initial_files)
    processed_files = set(initial_files)
    domain_suffix = [] 
    domain = [] 
    
    while files_to_process:
        current_file = files_to_process.pop(0)
        full_path = os.path.join(base_path, current_file)
        # 排除包含在忽略列表中的 include 依赖
        if current_file in ignore_files or any(current_file.endswith(s) for s in exclude_suffixes):
            print(f"[Ignore] Skipping ignored file: {current_file}")
            continue

        print(f"Processing {current_file} ......")
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                for line_number, line in enumerate(f, 1):
                    stripped_line = line.strip()
                    if not stripped_line: 
                        continue
                    if stripped_line.startswith('#'): 
                        continue
                    if stripped_line.startswith('regexp:'): 
                        continue
                    if stripped_line.startswith('include:'):
                        included_file = stripped_line[len('include:'):].strip()
                        if included_file: 
                            if included_file not in processed_files:
                                files_to_process.append(included_file)
                                processed_files.add(included_file)
                                print(f"[Include] New include: {included_file}, added to queue.")
                            else:
                                print(f"[Include] File {included_file} already exsists, skipped.")
                        continue 
                    if stripped_line.startswith('full:'):
                        content = stripped_line[len('full:'):].strip()
                        content = clean_content(content)
                        if content:
                            domain.append(content)
                        continue
                    else:
                        content = clean_content(stripped_line)
                        domain_suffix.append(content)
        except FileNotFoundError:
            print(f"!!! ERROR: NOT FOUND {full_path}")
        except Exception as e:
            print(f"!!! ERROR: READ FILE {current_file} OCCURS {e}")
        print(f"Processing {current_file} done. Now we have {domain_suffix.__len__()} domain_suffixies, {domain.__len__()} domains.")
            
    return domain_suffix, domain

# --- 写入 Sing-box JSON 格式 ---
def write_to_json(domain_suffix, domain, output_filename):
    rule={
        "domain": domain,
        "domain_suffix": domain_suffix
	} 
    data={
        "version": version,
        "rules": [rule]
    }
    
    try:
        with open(output_filename, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, indent=4, ensure_ascii=False)
        print(f"Write to file: {output_filename}")
    except Exception as e:
        print(f"!!! ERROR WRITE FILE {output_filename} OCCURS {e}")


# --- 主执行逻辑：动态获取所有规则并独立输出 ---

if __name__ == "__main__":
    generated_files = []
    
    # 1. 动态获取所有规则文件（排除忽略列表中的文件）
    try:
        # 获取 data/ 目录下所有文件
        all_initial_files = [
            f for f in os.listdir(base_dir) 
            if os.path.isfile(os.path.join(base_dir, f)) 
            and f not in ignore_files
            and not any(f.endswith(s) for s in exclude_suffixes)
        ]
    except FileNotFoundError:
        print(f"!!! ERROR: Data directory {base_dir} not found. Ensure git cloning was successful.")
        exit(1)

    print(f"Found {len(all_initial_files)} primary rule files to process.")
    
    # 2. 循环处理每一个文件，并独立输出
    for filename in all_initial_files:
        # 为每个文件创建一个独立的 .json 配置
        output_file_name = f"{filename}.json"
        
        # process_files 只传入当前文件，但它会递归处理该文件中的 include
        domain_suffix, domain = process_files(initial_files=[filename], base_path=base_dir)
        
        # 3. 将结果写入独立的 JSON 文件
        write_to_json(domain_suffix, domain, output_file_name)
        
        generated_files.append(output_file_name)
        
        print(f"\n--- {output_file_name} generation complete ---\n")
    
    print(f"All done. Total files generated: {len(generated_files)}.")
    print(f"Generated file names: {', '.join(generated_files)}")
