import streamlit as st
import pandas as pd

# 設定網頁標題與風格
st.set_page_config(page_title="臨床重症與團膳供膳全功能配對神器", page_icon="🧬", layout="wide")

# 網頁視覺大標
st.title("🧬 臨床重症與團膳供膳全功能配對神器")
st.write("已全面升級支援 ICU 重症營養、ERAS 術後加速康復、低渣/無渣飲食限制、三餐份量全自動分配，並導入 ONS 商業營養品預算扣除演算法！")

st.markdown("---")

# ==================== 疾病與臨床重症資料庫 ====================
DISEASE_DB = {
    "一般健康成人 (General Adult)": {"kcal_min": 25, "kcal_max": 30, "pro_min": 0.8, "pro_max": 1.0, "type": "📈 一般型", "notes": "維持一般均衡飲食，定錨基本微量元素平衡。"},
    "ICU 重症加護-急性期 (Critical Care-Acute)": {"kcal_min": 20, "kcal_max": 25, "pro_min": 1.2, "pro_max": 1.5, "type": "🚨 ICU 急性代謝型", "notes": "高發炎高消耗！給予高蛋白對抗肌肉分解。但初期熱量切記不可給太高（20-25 kcal/kg），嚴防致命的『再餵食症候群 (Refeeding Syndrome)』！"},
    "ICU 重症加護-恢復期 (Critical Care-Recovery)": {"kcal_min": 25, "kcal_max": 35, "pro_min": 1.5, "pro_max": 2.0, "type": "🍗 恢復期高蛋白型", "notes": "代謝風暴趨緩，進入組織重建期。熱量與蛋白質全面拉高，全力修復組織與瘦體組織。"},
    "ERAS 術後加速康復程 (ERAS Protocol)": {"kcal_min": 25, "kcal_max": 30, "pro_min": 1.2, "pro_max": 1.5, "type": "✂️ 外科手術術後型", "notes": "強調術後早期進食、減少生理應激。若為腸胃道手術，初期必須嚴格配合低渣或無渣飲食，減少腸道工作量。"},
    "第二型糖尿病 (Diabetes Mellitus)": {"kcal_min": 25, "kcal_max": 30, "pro_min": 1.0, "pro_max": 1.2, "type": "📊 控醣平衡型", "notes": "像會計師每餐『平均分帳』！控制總醣量、均勻分配三餐、增加膳食纖維。控制水果份量與時機，禁止含糖飲料。"},
    "慢性腎臟病-未透析 (CKD)": {"kcal_min": 30, "kcal_max": 35, "pro_min": 0.6, "pro_max": 0.8, "type": "⚠️ 嚴格限蛋白型", "notes": "限制蛋白質、鈉、鉀、磷。採低氮澱粉（冬粉、西谷米）、蔬菜切後必須汆燙以逼出鉀離子，避免高脂肉與堅果。"},
    "慢性腎臟病-已透析 (Dialysis)": {"kcal_min": 30, "kcal_max": 35, "pro_min": 1.0, "pro_max": 1.2, "type": "🥩 高蛋白補償型", "notes": "透析流失大量胺基酸！每餐補充足量優質蛋白（蛋、豆腐、魚、瘦肉），持續嚴格控鉀、控磷、限水分。"},
    "高血壓 (Hypertension)": {"kcal_min": 25, "kcal_max": 30, "pro_min": 0.8, "pro_max": 1.0, "type": "🧂 嚴格控鈉型", "notes": "每日鈉限制在 2000-2400mg 以下，少加工食品。低鈉不是完全無鹽，無禁忌時多增加鉀、鈣、鎂。"},
    "高血脂症 (Hyperlipidemia)": {"kcal_min": 25, "kcal_max": 30, "pro_min": 0.8, "pro_max": 1.2, "type": "🧈 脂質調配型", "notes": "降低飽和脂肪與反式脂肪，多選單元不飽和脂肪（橄欖油）與 omega-3 魚類，增加可溶性纖維。"},
    "痛風 (Gout)": {"kcal_min": 25, "kcal_max": 30, "pro_min": 0.8, "pro_max": 1.0, "type": "🍺 限普林型", "notes": "全面剔除內臟、濃肉湯、小魚乾、蝦米與酒精。多喝水促進尿酸排泄。"},
    "肝硬化 (Liver Cirrhosis)": {"kcal_min": 30, "kcal_max": 35, "pro_min": 1.2, "pro_max": 1.5, "type": "🌙 高能少量多餐型", "notes": "必須少量多餐，並強迫安排『夜間點心 (Late-night snack)』選用 BCAA 點心，阻斷夜間肌肉自噬。"}
}

# ==================== Sidebar: 使用者輸入與臨床定錨區 ====================
st.sidebar.header("📋 第一步：NCP 臨床情境定錨")
weight = st.sidebar.number_input("請輸入個案體重 (kg):", min_value=30.0, max_value=200.0, value=60.0, step=0.5)

selected_disease = st.sidebar.selectbox("請選擇臨床情境/目標疾病:", list(DISEASE_DB.keys()))
disease_info = DISEASE_DB[selected_disease]

# 🎛️ 核心新增：渣質飲食型態選擇 (直接連動主食衛教與乳品限制)
residue_type = st.sidebar.radio("請選擇腸道渣質限制 (Residue Restriction):", ["常規一般飲食", "低渣飲食 (低纖維/限制乳品)", "無渣飲食 (腸道術後/完全清空/嚴禁乳品)"])

st.sidebar.markdown("---")
st.sidebar.header("⚙️ 第二步：外援商業營養品 (ONS) 扣除")
use_ons = st.sidebar.checkbox("此個案是否搭配使用『商業營養品/罐裝配方』？")

ons_kcal, ons_p, ons_f, ons_c = 0.0, 0.0, 0.0, 0.0
if use_ons:
    ons_cans = st.sidebar.slider("每日使用罐數 (1罐預設250kcal, P:10g, F:8.5g, C:33.5g):", 1, 6, 2, step=1)
    ons_kcal = ons_cans * 250.0
    ons_p = ons_cans * 10.0
    ons_f = ons_cans * 8.5
    ons_c = ons_cans * 33.5
    st.sidebar.success(f"已鎖定 ONS 外援：\n- 熱量：-{ons_kcal:.0f} kcal\n- PRO：-{ons_p:.1f} g\n- FAT：-{ons_f:.1f} g\n- CHO：-{ons_c:.1f} g")

st.sidebar.markdown("---")
st.sidebar.header("⚖️ 第三步：自體淨需求計算")
kcal_kg = st.sidebar.slider("每日每公斤熱量需求 (kcal/kg):", 15, 45, int(disease_info["kcal_max"]), step=1)
pro_g_kg = st.sidebar.slider("每日每公斤蛋白質需求 (g/kg):", 0.5, 2.5, float(disease_info["pro_min"]), step=0.1)

# 計算原始需求與扣除外援後的「淨天然食物需求」
raw_tdee = weight * kcal_kg
raw_pro_g = weight * pro_g_kg

tdee = max(0.0, raw_tdee - ons_kcal)
target_pro_g = max(0.0, raw_pro_g - ons_p)
pro_kcal = target_pro_g * 4

if pro_kcal >= tdee and tdee > 0:
    st.sidebar.error("❌ 錯誤：扣除營養品後，剩餘蛋白質熱量超出總熱量預算！請調高熱量或調低蛋白質。")
else:
    pro_ratio_total = (pro_kcal / tdee) * 100 if tdee > 0 else 0
    max_cho_ratio = max(15.0, 100 - pro_ratio_total - 10)
    min_cho_ratio = 15.0
    default_cho_ratio = 50.0 if min_cho_ratio <= 50.0 <= max_cho_ratio else min_cho_ratio
    
    cho_ratio = st.sidebar.slider("請微調 醣類比例 (占剩餘總熱量 %):", int(min_cho_ratio), int(max_cho_ratio), int(default_cho_ratio), step=1)
    fat_ratio = 100 - pro_ratio_total - cho_ratio

    target_cho_g = ((tdee * (cho_ratio / 100)) / 4) if tdee > 0 else 0
    target_fat_g = ((tdee * (fat_ratio / 100)) / 9) if tdee > 0 else 0

st.sidebar.markdown("---")
st.sidebar.header("🧬 第四步：代換表資料庫微調")

# 🎛️ 核心升級：當選擇無渣飲食時，乳品強制鎖定為「無乳品」，消滅酪蛋白凝乳殘渣
if residue_type == "無渣飲食 (腸道術後/完全清空/嚴禁乳品)":
    milk_type = st.sidebar.selectbox("乳品分型 (無渣飲食已強制鎖定):", ["不喝乳品/無乳品 (P:0g, F:0g, C:0g)"])
else:
    milk_type = st.sidebar.selectbox("乳品分型:", ["低脂乳品 (P:8g, F:4g, C:12g)", "全脂乳品 (P:8g, F:8g, C:12g)", "脫脂乳品 (P:8g, F:0g, C:12g)", "不喝乳品/無乳品 (P:0g, F:0g, C:0g)"])

if "低脂" in milk_type:
    milk_p, milk_f, milk_c, milk_servings = 8.0, 4.0, 12.0, 1.0
elif "全脂" in milk_type:
    milk_p, milk_f, milk_c, milk_servings = 8.0, 8.0, 12.0, 1.0
elif "脫脂" in milk_type:
    milk_p, milk_f, milk_c, milk_servings = 8.0, 0.0, 12.0, 1.0
else:
    milk_p, milk_f, milk_c, milk_servings = 0.0, 0.0, 0.0, 0.0

meat_type = st.sidebar.selectbox("肉類分級:", ["中脂肉類 (P:7g, F:5g)", "低脂肉類 (P:7g, F:3g)", "高脂肉類 (P:7g, F:10g)"])
meat_p, meat_f = (7.0, 5.0) if "中脂" in meat_type else ((7.0, 3.0) if "低脂" in meat_type else (7.0, 10.0))

st.sidebar.markdown("---")
st.sidebar.header("🍽️ 第五步：餐次分配比例設定")
meal_mode = st.sidebar.selectbox(
    "請選擇餐次分配模式 (Meal Distribution):",
    ["常規三餐等分 (早33.3%, 午33.3%, 晚33.3%)", 
     "常規四餐結構 (早30%, 午30%, 晚30%, 點心10%)", 
     "重症/肝硬化少量多餐 (六餐均分各16.6%)"]
)

if "常規三餐" in meal_mode:
    meals = {"早餐": 0.333, "午餐": 0.333, "晚餐": 0.334}
elif "常規四餐" in meal_mode:
    meals = {"早餐": 0.30, "午餐": 0.30, "晚餐": 0.30, "點心": 0.10}
else:
    meals = {"第一餐": 0.166, "第二餐": 0.166, "第三餐": 0.166, "第四餐": 0.166, "第五餐": 0.166, "第六餐": 0.17}

# ==================== Core Algorithm: 臨床食物交換表演算法 ====================
veg_servings = 0.0 if residue_type == "無渣飲食 (腸道術後/完全清空/嚴禁乳品)" else 3.0
fruit_servings = 0.0 if residue_type == "無渣飲食 (腸道術後/完全清空/嚴禁乳品)" else 2.0

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
tab1, tab2 = st.tabs(["📊 臨床精準營養神算配對 (含餐次分配)", "🏥 供膳供應管理 (HACCP) 與 NCP 流程核檢"])

with tab1:
    st.subheader(f"🩺 當前疾病/重症情境：{selected_disease} ({disease_info['type']})")
    st.info(f"💡 **臨床核心介入指引**：{disease_info['notes']}\n\n⚠️ **當前渣質設定**：{residue_type}")
    
    # 總量卡片展示
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📊 總熱量需求 (含外援)", f"{raw_tdee:.0f} kcal")
    col2.metric("🍚 淨天然食物熱量需求", f"{tdee:.0f} kcal")
    col3.metric("🍗 淨蛋白質目標", f"{target_pro_g:.1f} g")
    col4.metric("🥛 商業營養品 (ONS)", f"{ons_kcal:.0f} kcal ({ons_cans if use_ons else 0} 罐)")

    st.markdown("### 🍽️ 淨天然食物：六大類食物每日精準總份數")
    
    # 動態調整衛教文字
    grain_note = "依生重20-30g換算，約1/4碗飯。若為低渣/無渣，禁止糙米雜糧，請全面改用白米飯、白吐司、冬粉或西谷米！" if "一般" not in residue_type else "依生重20-30g換算，約1/4碗飯。若是CKD限蛋白個案，請善用冬粉等低氮澱粉！"
    veg_note = "無渣飲食已將蔬菜降為0份。低渣個案必須去皮去籽且充分煮軟，限鉀個案切記要汆燙！" if "一般" not in residue_type else "一份等於可食生重100g。限鉀個案切記：必須先切、後充分汆燙再撈起拌油！"
    fruit_note = "無渣飲食已將水果降為0份。低渣個案僅限過濾去渣果汁，嚴防纖維殘留！" if "一般" not in residue_type else "一份約100g。嚴格控管糖尿病與透析個案的份數，避開高鉀水果。"
    milk_note = "已強制關閉乳品類，避免酪蛋白凝乳造成腸道下段高額殘渣包袱！" if milk_servings == 0 else f"1份等於240ml。當前選用：{milk_type}"

    food_groups_data = {
        "六大類食物名稱 (Food Groups)": ["全穀雜糧類", "豆魚蛋肉類", "乳品類", "蔬菜類", "水果類", "油脂與堅果種子類"],
        "每日精準總份數 (Total Servings)": [f"{grain_servings:.1f} 份", f"{meat_servings:.1f} 份", f"{milk_servings:.1f} 份", f"{veg_servings:.1f} 份", f"{fruit_servings:.1f} 份", f"{fat_servings:.1f} 份"],
        "臨床生重與品項精確指引 (Clinical Reference)": [grain_note, f"約 {meat_servings*35:.1f} 克生肉。低渣/無渣個案嚴禁油炸、嚴禁帶筋帶皮老肉，改用嫩豆腐、去皮清蒸魚肉、蛋白！", milk_note, veg_note, fruit_note, f"約 {fat_servings*5:.1f} 克烹調油。注意：低渣/無渣飲食者嚴禁食用整粒堅果與花生仁，避免顆粒摩擦與高纖殘渣！"]
    }
    st.dataframe(pd.DataFrame(food_groups_data), use_container_width=True)

    st.markdown("### ⏰ 臨床高機動性：每餐次六大類食物份數自動配對表")
    st.write(f"當前分配模式：**{meal_mode}**（表格內數字為各餐建議分配『份數』）")
    
    # 矩陣式計算每餐份數
    meal_rows = []
    for m_name, m_pct in meals.items():
        meal_rows.append({
            "餐次 (Meal Time)": f"{m_name} ({m_pct*100:.1f}%)",
            "全穀雜糧類": f"{grain_servings * m_pct:.1f} 份",
            "豆魚蛋肉類": f"{meat_servings * m_pct:.1f} 份",
            "乳品類": f"{milk_servings * m_pct:.1f} 份" if milk_servings > 0 else "0.0 份",
            "蔬菜類": f"{veg_servings * m_pct:.1f} 份" if veg_servings > 0 else "0.0 份",
            "水果類": f"{fruit_servings * m_pct:.1f} 份" if fruit_servings > 0 else "0.0 份",
            "油脂堅果類": f"{fat_servings * m_pct:.1f} 份"
        })
    st.dataframe(pd.DataFrame(meal_rows), use_container_width=True)
    st.success("🎉 運算成功！這套選單已完美適配臨床餐次與重症渣質限制，讓你在幾分鐘內掏出手機就能完成最高規格的諮詢！")

with tab2:
    st.subheader("🏥 大量製備與供膳管理全流程核檢 (HACCP 🚨CCP 對齊)")
    
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
        "重症與 ERAS 供膳特異性控制重點說明": [
            "精確收集重症生化指標 (Hb, Albumin, Cr)。採購必須確保特殊腸道配方、ONS、低氮澱粉之穩定供應鏈。",
            "確立 PES 診斷陳述式。開啟強迫症『驗收五大項』核檢：數量、品質、重量、溫度、有效期限。冷藏應≤7°C，冷凍應≤-18°C。",
            "精算疾病/重症 TDEE 與蛋白質常數，決定 ONS 扣除量。儲存遵循 FIFO 與 FEFO，嚴防生熟食血水交叉污染。",
            "依據『低渣/無渣限制』換算份數。備料解凍限用冷藏、流水或微波，嚴禁室溫暴露！低渣/無渣個案之食材肉品需徹底去皮、去骨、去筋、去籽，粗纖維蔬菜一律剔除。",
            "依據少量多餐模式編排結構化餐次（如六餐均分），避免廚房設備產能撞車。烹調使用中心溫度計量測，確保中心溫度達標，且質地必須完全符合吞嚥與腸道耐受度。",
            "生鮮食材成本控制在 45%-55% 之間。配膳採用標準餐具與精確秤重，特殊重症餐（如無渣餐）絕對不可與一般餐混淆，防止嚴重醫療事故。",
            "將菜單標準化並配送至病榻。運送冷鏈溫度把關：熱食保溫必須≥60°C，冷食保溫必須<7°C，以最快速度穿過 7°C-60°C 危险溫度帶。",
            "醫院集體供膳每餐、每道菜皆必須強迫留樣！精確秤取 100-150 克食物檢體，密封後置於冷藏環境（≤7°C）下，嚴格保存至少 48 小時，作為毒素追溯之法醫學證據。",
            "定期監測患者之 HbA1c、BUN、Cr、Albumin、剩食率與病患滿意度。若糖化血色素等指標依然異常，即刻啟動 PDCA 閉環修正菜單！"
        ]
    }
    st.table(pd.DataFrame(haccp_flow))
