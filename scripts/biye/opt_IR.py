import subprocess
import re
import os
import csv

min_time = 100000.0
min_num = -1


def optimize_ir(input_file, output_file, optimization_flags, csv_file):
    # 构建要执行的命令
    global min_time, min_num
    opt_command = [
        "opt",
        "-S",  # 保留为文本形式
        "-time-passes",  # 记录优化时间
    ]
    if optimization_flags < 64:
        # 添加各个优化选项
        if optimization_flags & 0b000001:
            opt_command.append("-mem2reg")
        if optimization_flags & 0b000010:
            opt_command.append("-instcombine")
        if optimization_flags & 0b000100:
            opt_command.append("-sccp")
        if optimization_flags & 0b001000:
            opt_command.append("-simplifycfg")
        if optimization_flags & 0b010000:
            opt_command.append("-globaldce")
        if optimization_flags & 0b100000:
            opt_command.append("-strip")
    elif optimization_flags == 64:
        opt_command.append("-O2")
    else:
        opt_command.append("-O3")

    opt_command.extend([input_file, "-o", output_file])

    # 执行命令
    try:
        result = subprocess.run(opt_command, capture_output=True, text=True, check=True)
        opt_execution_time = re.search(r'Total Execution Time: (\d+\.\d+) seconds', result.stderr)
        if opt_execution_time:
            opt_time = float(opt_execution_time.group(1))
            print("优化选项：", optimization_flags, "总优化时间：", opt_time)
            wpa_command = ["wpa", "-ander", "-stat", output_file]
            wpa_result = subprocess.run(wpa_command, capture_output=True, text=True, check=True)
            ptr_analysis_time_match = re.search(r'TotalTime\s+(\d+\.\d+)', wpa_result.stdout)
            if ptr_analysis_time_match:
                ptr_analysis_time = float(ptr_analysis_time_match.group(1))
                print("ptr analysis time:", ptr_analysis_time, "seconds")
            else:
                print("ptr analysis time not found")
            # 将数据写入CSV文件
            total_time = opt_time + ptr_analysis_time
            if total_time < min_time:
                min_time = total_time
                min_num = optimization_flags
            with open(csv_file, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([optimization_flags, opt_time, ptr_analysis_time, total_time])

        rm_command = ["rm", output_file]
        subprocess.run(rm_command, capture_output=True, text=True, check=True)

    except subprocess.CalledProcessError as e:
        print("优化选项：", optimization_flags, "优化失败")
        print(e.stderr)


if __name__ == "__main__":
    input_file = "IR_code/leveldb_tests.ll"  # 输入的 LLVM IR 文件
    csv_file = "IR_code/leveldb_tests/optimization_times.csv"  # CSV 文件路径
    if not os.path.exists("IR_code/leveldb_tests"):
        os.makedirs("IR_code/leveldb_tests")

    # 判断文件是否存在，如果存在则删除原文件
    if os.path.exists(csv_file):
        os.remove(csv_file)
    # 写入CSV文件头部
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(
            ['Optimization Flags', 'Opt Time (seconds)', 'Ptr Analysis Time (seconds)', 'Total Time (seconds)'])

    # wpa_command = ["wpa", "-ander", "-stat", input_file]
    # wpa_result = subprocess.run(wpa_command, capture_output=True, text=True, check=True)
    # ptr_analysis_time_match = re.search(r'TotalTime\s+(\d+\.\d+)', wpa_result.stdout)
    # if ptr_analysis_time_match:
    #     ptr_analysis_time = float(ptr_analysis_time_match.group(1))
    #     print("ptr analysis time:", ptr_analysis_time, "seconds")
    #     min_time = ptr_analysis_time
    #     min_num = 0
    #     with open(csv_file, mode='a', newline='') as file:
    #         writer = csv.writer(file)
    #         writer.writerow([0, 0, ptr_analysis_time, ptr_analysis_time])
    # else:
    #     print("ptr analysis time not found")

    # for i in range(1, 66):
    #     optimize_ir(input_file, "IR_code/leveldb_tests/" + str(i) + ".ll", i, csv_file)
    optimize_ir(input_file, "IR_code/leveldb_tests/" + str(65) + ".ll", 65, csv_file)

    print(min_num, min_time)
