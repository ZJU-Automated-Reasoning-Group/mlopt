import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.multioutput import MultiOutputClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# 读取CSV文件
df = pd.read_csv('feature_1.csv')

# 划分特征和目标变量
X = df[['func_cnt', 'block_cnt', 'avg_blocks_per_function', 'instr_in_func_cnt',
        'avg_instr_per_block', 'global_cnt', 'constant_cnt', 'load_cnt',
        'store_cnt', 'alloca_cnt']]
y = df[['mem2reg', 'instcombine', 'sccp', 'simplifycfg', 'globaldce', 'strip']]

# 创建随机森林模型
rf_classifier = RandomForestClassifier(random_state=42)
multi_output_rf = MultiOutputClassifier(rf_classifier)

# 分割数据集为训练集和测试集
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.4, random_state=42)

# 在训练集上训练模型
multi_output_rf.fit(X_train, y_train)

# 在整个数据集上做出预测
y_pred_rf = multi_output_rf.predict(X)

# 保存预测结果到CSV文件
y_pred_df = pd.DataFrame(y_pred_rf, columns=y.columns)
y_pred_df.to_csv('predicted_results.csv', index=False)

print("预测结果已保存到 'predicted_results.csv' 文件。")

# 计算并输出每个目标变量的预测准确率
accuracies_rf = {}
for i, target in enumerate(y.columns):
    accuracy_rf = accuracy_score(y[target], y_pred_rf[:, i])
    accuracies_rf[target] = accuracy_rf

print("\n随机森林模型预测准确率:")
for target, accuracy in accuracies_rf.items():
    print(f"{target}: {accuracy}")
