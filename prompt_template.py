PROMPT_TEMPLATE = """
你是專業的醫學文獻分析專家。請閱讀以下醫學文獻內容，並提取下列 18 個關鍵欄位。
請以 JSON 格式輸出，不要包含 Markdown 標記 (如 ```json ... ```)，直接輸出 JSON 物件即可。
若文中未提及某欄位，請填入 "N/A" 或根據上下文合理推斷，若無法推斷則留空。

**輸出欄位定義:**

1.  **Title**: 研究標題 (String)
2.  **Year**: 發表年份 (String, e.g., "2023")
3.  **Journal**: 期刊名稱 (String)
4.  **Study Type**: 研究類型 (String, 請從以下選項擇一: "Others", "Guidelines", "SR-Meta", "SR", "Review", "RCT", "Obs-Cohort", "Case report", "Animal", "in vitro")
5.  **Population**: 受試族群 (String, 請使用繁體中文簡述受試者特徵)
6.  **Sample Size**: 樣本數 (String, e.g., "N=123")
7.  **Duration**: 介入時間 (String, e.g., "12 weeks")
8.  **Comparator**: 對照組 (String, 請使用繁體中文說明對照組內容，若無則填 "無")
9.  **Outcome Type**: 研究評估的結果類別 (String, 請使用繁體中文, e.g., "症狀", "生化指標", "生活品質" 等)
10. **Bias Concern**: 偏差風險 (String, 選項: "Low", "Moderate", "High")
11. **Evidence Strength**: 證據強度 (String, 選項: "High", "Moderate", "Low")
12. **Primary Outcome**: 主要結果 (String, 請使用繁體中文一句話總結)
13. **Effect Direction**: 效果方向 (String, 選項: "Positive", "Neutral", "Negative")
14. **Effect Size Note**: 效果大小註記 (String, 選項: "Significant", "Small", "Unclear", "N/A" 或自訂描述)
15. **Consistency**: 一致性 (String, 針對 SR/Meta-analysis, 若不適用則填 "N/A")
16. **Key Limitations**: 最大限制 (String, 請使用繁體中文簡述研究最大問題)
17. **Non-generalizable**: 不可外推性 (String, 請使用繁體中文說明結果不能應用於哪些族群)
18. **Red Flags**: 紅色警示 (String, 請使用繁體中文說明副作用/交互作用/其他風險)

**文獻內容:**
{text}
"""
