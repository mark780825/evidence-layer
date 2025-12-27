import streamlit as st
import google.generativeai as genai
import json
import os
import pandas as pd
from pypdf import PdfReader
from prompt_template import PROMPT_TEMPLATE
from dotenv import load_dotenv

# Determine the absolute path to the .env file
base_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(base_dir, ".env")

# Try loading .env with specific encodings
if os.path.exists(env_path):
    # Try UTF-8 first
    if not load_dotenv(dotenv_path=env_path, encoding="utf-8"):
        # If no keys loaded (or update fails), try UTF-16
        load_dotenv(dotenv_path=env_path, encoding="utf-16")


st.set_page_config(page_title="醫療文獻分析 (表格版)", layout="wide")

st.title("🏥 醫療文獻自動分析")
st.markdown("無需串接 Notion，直接生成表格供您複製使用。")

# Sidebar - Configuration
st.sidebar.header("⚙️ 設定 (Configuration)")

# Check for API Key in environment
gemini_api_key = os.getenv("GEMINI_API_KEY")

# Fallback: Manual parsing if load_dotenv failed silently
if not gemini_api_key and os.path.exists(env_path):
    try:
        with open(env_path, "r", encoding="utf-8-sig") as f:
            for line in f:
                if line.strip().startswith("GEMINI_API_KEY="):
                    # Extract value, remove quotes and whitespace
                    key_val = line.split("=", 1)[1].strip().strip('"').strip("'")
                    if key_val:
                        gemini_api_key = key_val
                        os.environ["GEMINI_API_KEY"] = key_val
                        break
    except Exception as e:
        print(f"Manual load error: {e}")

if gemini_api_key:
    st.sidebar.success("✅ 已讀取 .env 金鑰")
else:
    st.sidebar.error("❌ 未偵測到 .env 金鑰")
    st.sidebar.info(f"請確認 .env 檔案存在且包含 GEMINI_API_KEY\n偵測路徑: {env_path}")

# Model selection
model_mapping = {
    "超省 (Economy) - Gemini 2.0 Flash Lite": "gemini-2.0-flash-lite",
    "標準 (Medium) - Gemini 2.5 Flash": "gemini-2.5-flash"
}

selected_label = st.sidebar.selectbox(
    "選擇模型等級 (Model Level)", 
    list(model_mapping.keys()),
    index=0 # Default to Economy
)
model_name = model_mapping[selected_label]


st.sidebar.markdown("---")
st.sidebar.markdown("### 使用說明")
st.sidebar.markdown("1. 輸入 Gemini API Key。")
st.sidebar.markdown("2. 上傳醫療文獻 PDF 檔。")
st.sidebar.markdown("3. AI 分析完成後，會顯示表格。")
st.sidebar.markdown("4. 您可以複製表格內容，或下載 CSV。")

# Function to extract text from PDF
def extract_text_from_pdf(uploaded_file):
    try:
        reader = PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return None

# Function to call Gemini API
def analyze_with_gemini(text, api_key, model_name='gemini-1.5-flash'):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        model_name,
        generation_config=genai.GenerationConfig(max_output_tokens=2000)
    )
    try:
        response = model.generate_content(PROMPT_TEMPLATE.format(text=text))
        content = response.text
        if "```json" in content:
            content = content.replace("```json", "").replace("```", "")
        elif "```" in content:
            content = content.replace("```", "")
        
        # Capture usage metadata if available
        usage = None
        if hasattr(response, 'usage_metadata'):
            usage = response.usage_metadata
            
        return json.loads(content), usage
    except Exception as e:
        st.error(f"Gemini Analysis Failed: {e}")
        return None, None



# Main App Logic
uploaded_file = st.file_uploader("上傳 PDF 檔案", type=["pdf"])

if uploaded_file and gemini_api_key:
    if st.button("🚀 開始分析 (Start Analysis)"):
        with st.spinner(f"正在使用 {model_name} 進行分析..."):
            text = extract_text_from_pdf(uploaded_file)
            if text:
                result, usage = analyze_with_gemini(text, gemini_api_key, model_name)
                if result:
                    st.session_state['analysis_result'] = result
                    st.session_state['usage_data'] = usage
                    st.success("分析完成！")
                else:
                    st.error("分析失敗，未能取得結構化資料。")

if 'analysis_result' in st.session_state:
    st.subheader("📊 分析結果 - 準備匯出")
    
    data = st.session_state['analysis_result']
    
    # Map to User's Specific Notion Column Names based on their screenshot
    # Check if keys exist before mapping to avoid KeyError
    def get_val(k): return data.get(k, "")
    
    mapped_data = {
        "【A】 Titel": [get_val("Title")],  # Note: User's screenshot says 'Titel'
        "【A】 Year": [get_val("Year")],
        "【A】 Journal": [get_val("Journal")],
        "【A】 Study Type": [get_val("Study Type")],
        "【A】 Population": [get_val("Population")],
        "【B】 Sample Size": [get_val("Sample Size")],
        "【B】 Duration": [get_val("Duration")],
        "【B】 Comparator": [get_val("Comparator")],
        "【B】 Outcome Type": [get_val("Outcome Type")],
        "【B】 Bias Concern": [get_val("Bias Concern")],
        "【B】 Evidence Strength": [get_val("Evidence Strength")],
        "【C】 Primary Outcome": [get_val("Primary Outcome")],
        "【C】 Effect Direction": [get_val("Effect Direction")],
        "【C】 Effect Size Note": [get_val("Effect Size Note")],
        "【C】 Consistency": [get_val("Consistency")],
        "【D】 Key Limitations": [get_val("Key Limitations")],
        "【D】 Non-generalizable": [get_val("Non-generalizable")],
        "【D】 Red Flags": [get_val("Red Flags")]
    }
    
    # Create DataFrame
    df = pd.DataFrame(mapped_data)
    
    # Display Options
    st.markdown("##### 1. 表格預覽 (可直接複製)")
    st.dataframe(df)

    # Transposed view for easier reading
    st.markdown("##### 2. 垂直檢視 (方便核對)")
    st.table(df.T.rename(columns={0: "Analyzed Value"}))
    
    # CSV Download
    csv = df.to_csv(index=False).encode('utf-8-sig') # utf-8-sig for Excel compatibility in Asia
    
    st.download_button(
        label="📥 下載為 CSV (Download CSV)",
        data=csv,
        file_name='evidence_analysis.csv',
        mime='text/csv',
    )
    
else:
    if not uploaded_file:
        st.info("👋 請先上傳 PDF 檔案。")
    elif not gemini_api_key:
        st.warning("👉 請在左側輸入 Gemini API Key。")
