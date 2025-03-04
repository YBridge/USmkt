import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from yahooquery import Ticker
import pytz
import httpx
import json
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# Perplexity API配置
PERPLEXITY_API_KEY = os.getenv('PERPLEXITY_API_KEY', 'your-api-key-here')

# 设置页面配置
st.set_page_config(
    page_title="美股市场分析",
    page_icon="",
    layout="wide"
)

# 页面标题
st.title("美股市场分析工具 ")

# 侧边栏
st.sidebar.header("")

# 添加股票代码示例和说明
st.sidebar.markdown("""
### 股票代码示例:
- : AAPL
- : GOOGL
- : TSLA
- : MSFT
- : NVDA
""")

# 股票代码输入
stock_symbol = st.sidebar.text_input("", "AAPL").upper().strip()

# 时间范围选择
time_ranges = {
    "1": "1wk",
    "1": "1mo",
    "3": "3mo",
    "6": "6mo",
    "1": "1y",
    "2": "2y"
}
selected_range = st.sidebar.selectbox("", list(time_ranges.keys()))

def get_stock_data(symbol, interval):
    """获取股票数据"""
    try:
        # 创建Ticker对象
        ticker = Ticker(symbol)
        
        # 获取历史数据
        hist = ticker.history(period=interval)
        if isinstance(hist, pd.DataFrame):
            hist.reset_index(inplace=True)
            hist.set_index('date', inplace=True)
        else:
            return None, ""
        
        # 获取报价数据
        quote = ticker.price[symbol]
        
        return {
            'history': hist,
            'quote': quote
        }, None
        
    except Exception as e:
        return None, str(e)

def get_stock_analysis(symbol):
    """使用Perplexity API分析股票"""
    try:
        url = "https://api.perplexity.ai/chat/completions"
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {PERPLEXITY_API_KEY}"
        }
        
        system_message = """你是一位专业的股票分析师，擅长从基本面和技术面分析股票。
请保持分析的客观性和专业性，使用准确的金融术语，并确保建议中包含风险提示。
回答要简洁、有条理，使用markdown格式。"""
        
        prompt = f"""请分析{symbol}股票，包括：
1. 公司基本面：财务状况、营收增长、利润率
2. 技术面分析：价格趋势、支撑/阻力位、成交量
3. 行业地位：市场份额、竞争优势、行业发展
4. 未来前景：增长机会、潜在风险、发展战略
5. 投资建议：短期和长期投资建议，风险提示

使用markdown格式回答，要专业、客观、全面。"""
        
        data = {
            "model": "sonar",  # 使用 sonar 模型
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ]
        }
        
        with httpx.Client(timeout=30.0) as client:
            response = client.post(url, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                return result['choices'][0]['message']['content']
            else:
                st.error(f"API响应格式错误: {result}")
                return None
            
    except Exception as e:
        st.error(f"获取分析失败: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            st.error(f"API响应: {e.response.text}")
        return None

# 
try:
    if not stock_symbol:
        st.warning("")
    else:
        with st.spinner(f" {stock_symbol} ..."):
            data, error = get_stock_data(stock_symbol, time_ranges[selected_range])
            
            if error:
                st.error(f" {error}")
            elif data is not None:
                hist = data['history']
                quote = data['quote']
                
                # 
                col1, col2, col3 = st.columns(3)
                with col1:
                    current_price = quote.get('regularMarketPrice', 'N/A')
                    previous_close = quote.get('regularMarketPreviousClose', 'N/A')
                    if current_price != 'N/A' and previous_close != 'N/A':
                        price_change = current_price - previous_close
                        price_change_pct = (price_change / previous_close) * 100
                        st.metric("", 
                                f"${current_price:.2f}", 
                                f"{price_change:+.2f} ({price_change_pct:+.2f}%)")
                    else:
                        st.metric("", "N/A")
                
                with col2:
                    market_cap = quote.get('marketCap', 'N/A')
                    if market_cap != 'N/A':
                        st.metric("", f"${market_cap:,.0f}")
                    else:
                        st.metric("", "N/A")
                
                with col3:
                    day_high = quote.get('regularMarketDayHigh', 'N/A')
                    day_low = quote.get('regularMarketDayLow', 'N/A')
                    if day_high != 'N/A' and day_low != 'N/A':
                        st.metric("", f"${day_low:.2f} - ${day_high:.2f}")
                    else:
                        st.metric("", "N/A")

                # K
                fig = go.Figure(data=[go.Candlestick(
                    x=hist.index,
                    open=hist['open'],
                    high=hist['high'],
                    low=hist['low'],
                    close=hist['close']
                )])
                
                fig.update_layout(
                    title=f"{stock_symbol} ",
                    yaxis_title=" (USD)",
                    xaxis_title="",
                    template="plotly_dark"
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # 
                volume_fig = go.Figure(data=[go.Bar(
                    x=hist.index,
                    y=hist['volume'],
                    name=""
                )])
                
                volume_fig.update_layout(
                    title=f"{stock_symbol} ",
                    yaxis_title="",
                    xaxis_title="",
                    template="plotly_dark"
                )
                
                st.plotly_chart(volume_fig, use_container_width=True)
                
                # 
                st.subheader("")
                st.dataframe(hist)
                
                # AI
                st.subheader("AI")
                with st.spinner(" ..."):
                    analysis = get_stock_analysis(stock_symbol)
                    st.markdown(analysis)
            else:
                st.error("")
except Exception as e:
    st.error(f": {str(e)}")
    st.info("")
