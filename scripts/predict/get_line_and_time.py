import os
import csv

def get_ll_files(directory):
    ll_files = [os.path.join(directory, filename) for filename in os.listdir(directory) if filename.endswith('.ll')]
    return ll_files

def get_ir_feature(file_path, csv_file):
    file_name = file_path.split('/')[-1]
    line_count = 0
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
            line_count = len(lines)
            with open(csv_file, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([file_name, line_count])
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
    except IOError:
        print(f"Error: Failed to open or read the file '{file_path}'.")
    pass


if __name__ == "__main__":
    csv_file = "compare.csv"  # CSV 文件路径

    # 判断文件是否存在，如果存在则删除原文件
    if os.path.exists(csv_file):
        os.remove(csv_file)
    # 写入CSV文件头部
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['file_name', 'code_line', 'no_opt_time', 'O2_time', 'O3_time'])
    ll_files = get_ll_files("IR_code/")
    for ll_file in ll_files:
        get_ir_feature(ll_file, csv_file)
    # print(ll_files)
