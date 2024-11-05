import os
import csv


def get_ll_files(directory):
    ll_files = [os.path.join(directory, filename) for filename in os.listdir(directory) if filename.endswith('.ll')]
    return ll_files


def get_ir_feature(file, csv_file):
    filename = file.split("/")[-1]
    func_cnt = 0  # 函数个数
    block_cnt = 0  # 基本块个数
    avg_blocks_per_function = 0
    instr_in_func_cnt = 0  # 函数内所有代码行数
    avg_instr_per_block = 0
    global_cnt = 0
    constant_cnt = 0
    load_cnt = 0
    store_cnt = 0
    alloca_cnt = 0
    with open(file, 'r') as file:
        flag = False
        for line in file:
            if not line.startswith(("source_filename", "target datalayout", "target triple", "attributes", "!", ";")):
                parts = line.split()
                filtered_parts = filter(lambda x: x != '', parts)
                processed_line = list(filtered_parts)
                if processed_line:
                    if processed_line[0] == "define":
                        func_cnt += 1
                        block_cnt += 1
                        flag = True
                    elif processed_line[0] == "}":
                        flag = False
                    elif processed_line[0].endswith(":"):
                        block_cnt += 1
                    elif processed_line[0] == "store":
                        store_cnt += 1
                        if flag:
                            instr_in_func_cnt += 1
                    else:
                        if flag:
                            instr_in_func_cnt += 1
                        for part in processed_line:
                            if part == "global":
                                global_cnt += 1
                                break
                            elif part == "constant":
                                constant_cnt += 1
                                break
                            elif part == "load":
                                load_cnt += 1
                                break
                            elif part == "alloca":
                                alloca_cnt += 1
                                break
    avg_blocks_per_function = block_cnt / func_cnt
    avg_instr_per_block = instr_in_func_cnt / block_cnt
    with open(csv_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(
            [filename, func_cnt, block_cnt, avg_blocks_per_function, instr_in_func_cnt, avg_instr_per_block, global_cnt,
             constant_cnt, load_cnt, store_cnt, alloca_cnt])
    print(filename)


if __name__ == "__main__":
    csv_file = "feature.csv"  # CSV 文件路径

    # 判断文件是否存在，如果存在则删除原文件
    if os.path.exists(csv_file):
        os.remove(csv_file)
    # 写入CSV文件头部
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['file_name', 'func_cnt', 'block_cnt', 'avg_blocks_per_function', 'instr_in_func_cnt',
                         'avg_instr_per_block', 'global_cnt', 'constant_cnt', 'load_cnt', 'store_cnt', 'alloca_cnt'])
    ll_files = get_ll_files("IR_code/")
    for ll_file in ll_files:
        get_ir_feature(ll_file, csv_file)
    # print(ll_files)
