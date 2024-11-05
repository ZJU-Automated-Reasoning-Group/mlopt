import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.multioutput import MultiOutputClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score
from sklearn.feature_selection import RFE
from sklearn.svm import SVR

# 读取CSV文件
df = pd.read_csv('feature_1.csv')

# 划分特征和目标变量
X = df[['func_cnt', 'block_cnt', 'avg_blocks_per_function', 'instr_in_func_cnt',
        'avg_instr_per_block', 'global_cnt', 'constant_cnt', 'load_cnt',
        'store_cnt', 'alloca_cnt']]
y = df[['mem2reg', 'instcombine', 'sccp', 'simplifycfg', 'globaldce', 'strip']]

# 计算模型的准确率
accuracies_dt = {}
accuracies_knn = {}
accuracies_rf = {}
accuracies_mlp = {}

# 特征重要性字典
feature_importances_rf = {target: np.zeros(X.shape[1]) for target in y.columns}

# 创建不同的基分类器
dt_classifier = DecisionTreeClassifier(random_state=42)  # 决策树模型
knn_classifier = KNeighborsClassifier()  # KNN模型
rf_classifier = RandomForestClassifier(random_state=42)  # 随机森林模型
mlp_classifier = MLPClassifier(random_state=42)  # 多层感知机模型

# 创建多输出分类器，并分别包装不同的基分类器
multi_output_dt = MultiOutputClassifier(dt_classifier)
multi_output_knn = MultiOutputClassifier(knn_classifier)
multi_output_rf = MultiOutputClassifier(rf_classifier)
multi_output_mlp = MultiOutputClassifier(mlp_classifier)

for j in range(50):
    # 分割数据集为训练集和测试集
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.4, random_state=j)

    # 在训练集上训练模型
    multi_output_dt.fit(X_train, y_train)
    multi_output_knn.fit(X_train, y_train)
    multi_output_rf.fit(X_train, y_train)
    multi_output_mlp.fit(X_train, y_train)

    # 在测试集上做出预测
    y_pred_dt = multi_output_dt.predict(X_test)
    y_pred_knn = multi_output_knn.predict(X_test)
    y_pred_rf = multi_output_rf.predict(X_test)
    y_pred_mlp = multi_output_mlp.predict(X_test)

    for i, target in enumerate(y.columns):
        accuracy_dt = accuracy_score(y_test[target], y_pred_dt[:, i])
        accuracy_knn = accuracy_score(y_test[target], y_pred_knn[:, i])
        accuracy_rf = accuracy_score(y_test[target], y_pred_rf[:, i])
        accuracy_mlp = accuracy_score(y_test[target], y_pred_mlp[:, i])

        if j == 0:
            accuracies_dt[target] = accuracy_dt
            accuracies_knn[target] = accuracy_knn
            accuracies_rf[target] = accuracy_rf
            accuracies_mlp[target] = accuracy_mlp
        else:
            accuracies_dt[target] += accuracy_dt
            accuracies_knn[target] += accuracy_knn
            accuracies_rf[target] += accuracy_rf
            accuracies_mlp[target] += accuracy_mlp

        # 从多输出分类器中获取单个随机森林模型的特征重要性并累加
        feature_importances_rf[target] += multi_output_knn.estimators_[i].feature_importances_

    print(j)

# 输出每个分类器的预测准确率
print("决策树模型预测准确率:")
for target, accuracy in accuracies_dt.items():
    print(f"{target}: {accuracy / 50}")

print("\nKNN模型预测准确率:")
for target, accuracy in accuracies_knn.items():
    print(f"{target}: {accuracy / 50}")

print("\n随机森林模型预测准确率:")
for target, accuracy in accuracies_rf.items():
    print(f"{target}: {accuracy / 50}")

print("\n多层感知机模型预测准确率:")
for target, accuracy in accuracies_mlp.items():
    print(f"{target}: {accuracy / 50}")

# 计算平均特征重要性
average_feature_importances_rf = {target: importance / 50 for target, importance in feature_importances_rf.items()}

# 将特征重要性写入CSV文件
importance_df_rf = pd.DataFrame(average_feature_importances_rf, index=X.columns)
importance_df_rf.to_csv('feature_importances_rf.csv')

print("\n随机森林模型特征重要性已写入 'feature_importances_rf.csv'")

# 对特征重要性进行分析
for target in y.columns:
    print(f"\n特征重要性 - {target}:")
    for feature, importance in zip(X.columns, average_feature_importances_rf[target]):
        print(f"{feature}: {importance}")
