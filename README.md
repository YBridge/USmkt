# US Market Analysis Tool

一个用于分析美股市场的 Streamlit 应用程序，提供实时股票数据和 AI 分析。

## 功能

- 实时股票数据显示
- K线图和成交量图表
- 技术指标分析
- AI 智能分析（需要 Perplexity API key）
- 历史数据查看

## 安装

1. 克隆仓库：
```bash
git clone https://github.com/YBridge/USmkt.git
cd USmkt
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 配置环境变量：
   - 创建 `.env` 文件
   - 添加你的 Perplexity API key：
```
PERPLEXITY_API_KEY=your-api-key-here
```

## 运行

```bash
streamlit run app.py
```

## 使用说明

1. 在侧边栏输入股票代码（例如：AAPL、GOOGL、MSFT）
2. 选择时间范围
3. 查看实时数据、图表和 AI 分析

## 注意事项

- 请确保在运行应用前设置好 Perplexity API key
- 所有数据来自 Yahoo Finance，为实时市场数据
- AI 分析功能需要联网使用
