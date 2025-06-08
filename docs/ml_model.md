# ML 模型说明

模型采用监督学习方式训练，输入交易特征输出风险评分。训练脚本位于
`fraud_detection/model/train.py`。

当前默认模型为 IsolationForest，同时也支持 Local Outlier Factor (LOF)。
训练完成后将模型文件保存为 `fraud_model.pkl` 并在配置中指定路径。

模型阈值可在 `config.yaml` 的 `model.threshold` 字段调整，以控制误报率。
