import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import classification_report, confusion_matrix, ConfusionMatrixDisplay
import matplotlib.pyplot as plt

# 加载 Excel 数据
data_path = r"xxx"  # 替换为你的文件路径
data = pd.read_excel(data_path)  # 跳过第一行无数据行

# 提取特征和标签
width_height_ratio = data.iloc[:, 1].values.reshape(-1, 1)  # 第二列为宽高比
plant_type = data.iloc[:, 2].values  # 第三列为真实株型

# 划分训练集和测试集
X_train, X_test, y_train, y_test = train_test_split(
    width_height_ratio, plant_type, test_size=0.2, random_state=42
)

# 创建决策树分类器并训练
dt_model = DecisionTreeClassifier(random_state=42)
dt_model.fit(X_train, y_train)

# 进行预测
y_pred = dt_model.predict(X_test)

# 评估分类器
print("分类报告：")
print(classification_report(y_test, y_pred, zero_division=0))

# 混淆矩阵可视化
conf_matrix = confusion_matrix(y_test, y_pred)
disp = ConfusionMatrixDisplay(conf_matrix, display_labels=dt_model.classes_)
disp.plot(cmap=plt.cm.Blues)
plt.title("Confusion Matrix (Decision Tree)")
plt.show()

# 保存分类结果
data['Predicted'] = dt_model.predict(width_height_ratio)  # 全部数据的预测值
output_path = r"xxx"
data.to_excel(output_path, index=False)
print(f"分类结果已保存至：{output_path}")





