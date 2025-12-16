import os
import json

# 设置
initial_files_list = ['google'] #要处理的规则列表
base_dir = 'domain-list-community/data/' #规则文件所在目录
output_file = 'google.json' #输出文件名
version =3



def clean_content(content):
    space_index = content.find(' ')
    if space_index != -1:
        return content[:space_index].strip()
    else:
        return content.strip()

def process_files(initial_files, base_path):
    files_to_process = list(initial_files)
    processed_files = set(initial_files)
    domain_suffix = [] 
    domain = [] 
    
    while files_to_process:
        current_file = files_to_process.pop(0)
        full_path = os.path.join(base_path, current_file)
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

def write_to_json(domain_suffix, domain, output_filename="output.json"):
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



if __name__ == "__main__":
    domain_suffix, domain = process_files(initial_files_list, base_path=base_dir)
    write_to_json(domain_suffix, domain, output_file)
    print(f"All done.")
    print(f"Domain_suffix: {domain_suffix.__len__()}.")
    print(f"Domain:        {domain.__len__()}.")
