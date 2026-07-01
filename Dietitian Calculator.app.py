import streamlit as st
import pandas as pd

# 設定網頁標題與風格
st.set_page_config(page_title="臨床與團膳整合型精準營養配對神器", page_icon="🧬", layout="wide")

# 網頁視覺大標
st.title("🧬 臨床與團膳整合型精準營養配對神器")
st.write("已完美整合臨床營養照護流程 (NCP)、新版食物代換表常數與團膳供應管理 (HACCP) 核心關鍵管制點 (CCP)！")

st.markdown("---")

# ==================== 資料庫定義 ====================
DISEASE_DB = {
    "一般健康成人 (General Adult)": {"kcal_min": 25, "kcal_max": 30, "pro_min": 0.8, "pro_max": 1.0, "type": "📈 高代謝與一般", "notes": "維持一般均衡飲食，定錨基本微量元素與三大營養素平衡。"},
    "第二型糖尿病 (Diabetes Mellitus)": {"kcal_min": 25, "kcal_max": 30, "pro_min": 1.0, "pro_max": 1.2, "type": "📊 控醣平衡型", "notes": "像會計師每餐『平均分帳』！控制總醣量、均勻分配三餐、增加膳食纖維。絕非禁止水果，而是嚴格控管份量與進食時機，徹底禁止含糖飲料。"},
    "慢性腎臟病-未透析 (CKD)": {"kcal_min": 30, "kcal_max": 35, "pro_min": 0.6, "pro_max": 0.8, "type": "⚠️ 嚴格限蛋白型", "notes": "像『家裡排水管堵塞』！代謝廢物、鉀、磷、鈉易累積。必須嚴格執行低蛋白飲食以保護殘餘腎功能，但熱量必須給足！採低氮澱粉（冬粉、西谷米）、蔬菜切後必須汆燙以逼出鉀離子，避免高脂肉與堅果。"},
    "慢性腎臟病-已透析 (Dialysis)": {"kcal_min": 30, "kcal_max": 35, "pro_min": 1.0, "pro_max": 1.2, "type": "🥩 高蛋白補償型", "notes": "像『天天在搬家』！透析過程流失大量胺基酸，蛋白質需求大反轉！每餐補充足量優質蛋白（蛋、豆腐、魚、瘦肉），持續嚴格控鉀、控磷、限水分與高鉀水果。"},
    "高血壓 (Hypertension)": {"kcal_min": 25, "kcal_max": 30, "pro_min": 0.8, "pro_max": 1.0, "type": "🧂 嚴格控鈉型", "notes": "水管壓力太高，先拆除『鹽分』加壓器！每日鈉限制在 2000-2400mg 以下，少加工食品。低鈉不是完全無鹽（避免病人因口感極差而拒食破產），無禁忌時多增加鉀、鈣、鎂。"},
    "高血脂症 (Hyperlipidemia)": {"kcal_min": 25, "kcal_max": 30, "pro_min": 0.8, "pro_max": 1.2, "type": "🧈 脂質調配型", "notes": "降低飽和脂肪與反式脂肪，增加燕麥、豆類等可溶性纖維促進膽酸排泄。總脂肪不是越低越好，核心在於『脂肪的種類』，多選單元不飽和脂肪（橄欖油）與 omega-3 魚類。"},
    "痛風 (Gout)": {"kcal_min": 25, "kcal_max": 30, "pro_min": 0.8, "pro_max": 1.0, "type": "🍺 限普林型", "notes": "嚴格限制高普林！菜單全面剔除內臟、濃肉湯、小魚乾、蝦米與酒精。多喝水促進尿酸排泄。植物性豆製品（豆腐、豆漿）經研究證實可適量食用，不必完全禁止。"},
    "肝硬化 (Liver Cirrhosis)": {"kcal_min": 30, "kcal_max": 35, "pro_min": 1.2, "pro_max": 1.5, "type": "🌙 高能少量多餐型", "notes": "糖原儲存能力差，身體像在鬧饑荒！必須少量多餐，並強迫安排『夜間點心 (Late-night snack)』選用 BCAA 或高能量點心，阻斷夜間肌肉自噬溶解。非一律低蛋白，僅昏迷時調整。"},
    "慢性阻塞性肺疾病 (COPD)": {"kcal_min": 30, "kcal_max": 35, "pro_min": 1.2, "pro_max": 1.5, "type": "🖲️ 低 RQ 脂質依賴型", "notes": "呼吸肌日夜超負荷工作，身體像在燒燃料！嚴重患者為減少二氧化碳 (CO2) 蓄積負擔，應適度調降醣類比例、拉高脂肪比例（因脂肪的呼吸商 RQ 最低，產生的 CO2 最少），小量多餐防止吃太飽壓迫呼吸。"},
    "癌症 (Cancer)": {"kcal_min": 30, "kcal_max": 35, "pro_min": 1.2, "pro_max": 2.0, "type": "🔥 超高消耗對抗型", "notes": "惡病質高消耗狀態，身體在狂燒燃料！高蛋白、高熱量為主，依吞嚥能力調整質地，可大量介入液態口服營養補充品 (ONS)。千萬不要盲目過度限糖而導致個案總熱量嚴重赤字。"},
    "肥胖症 (Obesity)": {"kcal_min": 20, "kcal_max": 25, "pro_min": 1.0, "pro_max": 1.5, "type": "⚖️ 熱量赤字型", "notes": "每日設定總熱量赤字約 500-750 kcal/day。採取高纖、高蛋白、低能量密度策略。減重絕對不是只吃水果或不吃澱粉，需保留瘦體組織。"}
}

# ==================== Sidebar: 使用者輸入與臨床定錨區 ====================
st.sidebar.header("📋 第一步：NCP 營養評估與診斷")
weight = st.sidebar.number_input("請輸入個案體重 (kg):", min_value=30.0, max_value=200.0, value=60.0, step=0.5)

# 疾病別自動帶入出題者思維矩陣
selected_disease = st.sidebar.selectbox("請選擇臨床目標疾病 (國考高頻整合版):", list(DISEASE_DB.keys()))
disease_info = DISEASE_DB[selected_disease]

st.sidebar.markdown("---")
st.sidebar.header("⚖️ 第二步：營養需求計算 (Requirements)")

# 動態設定疾病對應的熱量與蛋白質推薦區間
kcal_kg = st.sidebar.slider("每日每公斤熱量需求 (kcal/kg):", 15, 45, int(disease_info["kcal_max"]), step=1)
pro_g_kg = st.sidebar.slider("每日每公斤蛋白質需求 (g/kg):", 0.5, 2.5, float(disease_info["pro_min"]), step=0.1)

# 計算核心基礎數據
tdee = weight * kcal_kg
target_pro_g = weight * pro_g_kg
pro_kcal = target_pro_g * 4

# 防呆機制：如果蛋白質熱量直接壓過總熱量
if pro_kcal >= tdee:
    st.sidebar.error("❌ 錯誤：蛋白質所需熱量已超出總熱量預算，請調高熱量需求或調低蛋白質！")
else:
    # 計算剩餘熱量百分比，並提供醣類 1% 微調拉桿
    rem_kcal = tdee - pro_kcal
    pro_ratio_total = (pro_kcal / tdee) * 100
    
    # 計算最大允許的醣類比例 (留至少 10% 給脂肪)
    max_cho_ratio = 100 - pro_ratio_total - 10
    min_cho_ratio = 15.0
    
    # 決定預設的醣類比例
    default_cho_ratio = 50.0 if min_cho_ratio <= 50.0 <= max_cho_ratio else min_cho_ratio
    
    cho_ratio = st.sidebar.slider(
        "請微調 醣類比例 (占總熱量 %):", 
        int(min_cho_ratio), int(max_cho_ratio), int(default_cho_ratio), step=1
    )
    
    fat_ratio = 100 - pro_ratio_total - cho_ratio

    target_cho_g = (tdee * (cho_ratio / 100)) / 4
    target_fat_g = (tdee * (fat_ratio / 100)) / 9

st.sidebar.markdown("---")
st.sidebar.header("🧬 第三步：代換表資料庫微調")
milk_type = st.sidebar.selectbox("乳品分型:", ["低脂乳品 (P:8g, F:4g, C:12g)", "全脂乳品 (P:8g, F:8g, C:12g)", "脫脂乳品 (P:8g, F:0g, C:12g)"])
milk_p, milk_f, milk_c = (8.0, 4.0, 12.0) if "低脂" in milk_type else ((8.0, 8.0, 12.0) if "全脂" in milk_type else (8.0, 0.0, 12.0))

meat_type = st.sidebar.selectbox("肉類分級:", ["中脂肉類 (P:7g, F:5g)", "低脂肉類 (P:7g, F:3g)", "高脂肉類 (P:7g, F:10g)"])
meat_p, meat_f = (7.0, 5.0) if "中脂" in meat_type else ((7.0, 3.0) if "低脂" in meat_type else (7.0, 10.0))

# ==================== Core Algorithm: 臨床食物交換表演算法 ====================
veg_servings, fruit_servings, milk_servings = 3.0, 2.0, 1.0

base_cho = (veg_servings * 5) + (fruit_servings * 15) + (milk_servings * milk_c)
base_pro = (veg_servings * 1) + (fruit_servings * 0) + (milk_servings * milk_p)
base_fat = (veg_servings * 0) + (fruit_servings * 0) + (milk_servings * milk_f)

rem_cho = target_cho_g - base_cho
rem_pro = target_pro_g - base_pro

grain_servings = max(0.0, rem_cho / 15)
rem_pro_after_grain = rem_pro - (grain_servings * 2)
meat_servings = max(0.0, rem_pro_after_grain / meat_p)

current_fat = base_fat + (meat_servings * meat_f)
rem_fat = target_fat_g - current_fat
fat_servings = max(0.0, rem_fat / 5)

# ==================== Dashboard: 雙分頁系統呈現 ====================
tab1, tab2 = st.tabs(["📊 臨床精準營養神算配對", "🏥 供膳供應管理 (HACCP) 與 NCP 流程核檢"])

with tab1:
    st.subheader(f"🩺 當前疾病診斷偏好：{selected_disease} ({disease_info['type']})")
    st.info(f"💡 **臨床介入核心指引**：{disease_info['notes']}")
    
    # 統計指標圖卡
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📊 總熱量需求 (TDEE)", f"{tdee:.0f} kcal")
    col2.metric("🍚 醣類目標", f"{target_cho_g:.1f} g ({cho_ratio:.0f}%)")
    col3.metric("🍗 蛋白質目標", f"{target_pro_g:.1f} g ({pro_ratio_total:.0f}%)")
    col4.metric("🧈 脂肪目標", f"{target_fat_g:.1f} g ({fat_ratio:.0f}%)")

    # 檢查預算是否破產
    if rem_cho < 0 or rem_pro_after_grain < 0:
        st.warning("⚠️ 臨床警訊：當前設定之總熱量或醣類比例過低，已不足以分配給臨床指南必備之基本蔬果乳品分量，請適度調高左側預算！")

    st.markdown("### 🍽️ 換算六大類食物精準份數與克數 (對接官方最新手冊常數)")
    
    food_groups_data = {
        "六大類食物名稱 (Food Groups)": [
            "全穀雜糧類 (Whole Grains)",
            "豆魚蛋肉類 (Beans, Fish, Eggs, Meat)",
            "指定乳品類 (Selected Dairy)",
            "蔬菜類 (Vegetables)",
            "水果類 (Fruits)",
            "油脂與堅果種子類 (Fats & Oils)"
        ],
        "計算出之精準份數 (Servings)": [
            f"{grain_servings:.1f} 份",
            f"{meat_servings:.1f} 份",
            f"{milk_servings:.1f} 份",
            f"{veg_servings:.1f} 份",
            f"{fruit_servings:.1f} 份",
            f"{fat_servings:.1f} 份"
        ],
        "新版生重與品項精確換算參考 (Grams/Reference)": [
            f"約 {grain_servings*25:.1f} 克未熟乾穀 (1份等於生重20-30g，如1/4碗飯。若是CKD限蛋白個案，請善用冬粉、西谷米等低氮澱粉！)",
            f"約 {meat_servings*35:.1f} 克生肉 (1份等於生重30-35g。當前設定下，高脂肉如百頁豆腐70g、中脂肉如雞蛋55g、低脂肉如一般魚類35g)",
            f"約 {milk_servings*240:.1f} 毫升液態奶 (1份等於240ml。全脂提供8g脂肪、低脂4g脂肪、脫脂0g脂肪)",
            f"約 {veg_servings*100:.1f} 克生菜 (1份等於可食生重100g。限鉀個案切記：必須先切、後充分汆燙再撈起拌油！)",
            f"約 {fruit_servings*100:.1f} 克切塊水果 (1份約等於碗裝8分滿/100g。嚴格控管糖尿病與透析個案的份數，避開高鉀水果)",
            f"約 {fat_servings*5:.1f} 克烹調油 (1份等於精製油5g或各式花生仁10粒。注意：堅果類每份含5g脂肪，但常伴隨1-4g蛋白質，限蛋白個案慎用！)"
        ]
    }
    st.dataframe(pd.DataFrame(food_groups_data), use_container_width=True)
    st.success("🎉 運算成功！這套選單就像完美的情人，精準滿足個案身體與疾病的每一分預算！")

with tab2:
    st.subheader("🏠 大量製備與供膳管理全流程核檢 (PDCA 循環)")
    st.write("依據臨床營養照護流程 (NCP) 與團體膳食安全管理，在每個步驟落實食品安全與品質控制：")
    
    haccp_flow = {
        "NCP / 團膳管理步驟": [
            "1. 評估與採購 (Assessment & Purchasing)",
            "2. 診斷與驗收 (Diagnosis & Receiving) 🚨CCP",
            "3. 需求計算與儲存 (Requirements & Storage)",
            "4. 食物代換與備料 (Exchange & Preparation)",
            "5. 菜單設計與烹調 (Menu & Cooking) 🚨CCP",
            "6. 可行性核檢與配膳 (Feasibility & Portioning)",
            "7. 菜單定案與供餐 (Implementation & Distribution)",
            "8. 留樣備查 (Food Sampling) 🚨核心管制",
            "9. 監測與評值 (Monitoring & Evaluation)"
        ],
        "核心風險與工作內容說明": [
            "收集個案基本資料與生化指標，確認合格供應商規格，採購符合疾病規格且價格合理之食材，嚴禁盲目追求低價。",
            "確立 PES 診斷陳述式。開啟強迫症『驗收五大項』核檢：數量、品質、重量、溫度、有效期限。冷藏應≤7°C，冷凍應≤-18°C。",
            "精算疾病特異性 TDEE 與蛋白質常數。儲存嚴格遵循 FIFO (先進先出) 與 FEFO (先到期先出)。生熟食徹底分區存放，嚴防血水滴落引發交叉污染。",
            "換算六大類食物份數。備料解凍限用冷藏解凍、流水解凍或微波立即烹調，嚴禁室溫暴露一天！刀具砧板實施分色管理。",
            "編排結構化餐次，避免同餐烹調設備撞車。烹調必須使用中心溫度計量測，確保中心溫度確實達標、充分加熱殺滅病原菌，嚴防半熟出餐。",
            "生鮮食材成本嚴格控制在 45%-55% 之間。配膳採用標準餐具與精確秤重，嚴密核對特殊飲食與患者身份，防止送錯引發醫療事故。",
            "將菜單標準化並配送至病榻。運送冷鏈溫度把關：熱食保溫必須≥60°C，冷食保溫必須<7°C，以最快速度穿過 7°C-60°C 危险溫度帶。",
            "醫院集體供膳每餐、每道菜皆必須強迫留樣！精確秤取 100-150 克食物檢體，密封後置於冷藏環境（≤7°C）下，嚴格保存至少 48 小時，作為毒素追溯之法醫學證據。",
            "定期監測患者之 HbA1c、BUN、Cr、Albumin、剩食率與病患滿意度。若糖化血色素等指標依然異常，即刻啟動 PDCA 閉環修正菜單！"
        ]
    }
    st.table(pd.DataFrame(haccp_flow))
