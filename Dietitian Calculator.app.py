import streamlit as st
import pandas as pd

# 設定網頁標題與風格
st.set_page_config(page_title="臨床重症與團膳供膳全功能配對神器", page_icon="🧬", layout="wide")

# 網頁視覺大標
st.title("🧬 臨床重症與團膳供膳全功能配對神器")
st.write("已完美整合重症加護營養需求、ERAS 術後加速康復、低渣/無渣飲食限制、四大商業管灌配方決策矩陣與 50g 高血脂纖維干預指標！")

st.markdown("---")

# ==================== 資料庫定義 ====================
DISEASE_DB = {
    "一般健康成人 (General Adult)": {"kcal_min": 25, "kcal_max": 30, "pro_min": 0.8, "pro_max": 1.0, "type": "📈 一般型", "notes": "維持一般均衡飲食，定錨基本微量元素平衡。"},
    "ICU 重症加護-急性期 (Critical Care-Acute)": {"kcal_min": 20, "kcal_max": 25, "pro_min": 1.2, "pro_max": 1.5, "type": "🚨 ICU 急性代謝型", "notes": "高發炎高消耗！給予高蛋白對抗肌肉分解。但熱量切記不可給太高（20-25 kcal/kg），嚴防致命的『再餵食症候群 (Refeeding Syndrome)』！"},
    "ICU 重症加護-恢復期 (Critical Care-Recovery)": {"kcal_min": 25, "kcal_max": 35, "pro_min": 1.5, "pro_max": 2.0, "type": "🍗 恢復期高蛋白型", "notes": "代謝風暴趨緩，進入組織重建期。熱量與蛋白質全面拉高，全力修復組織。"},
    "ERAS 術後加速康復程 (ERAS Protocol)": {"kcal_min": 25, "kcal_max": 30, "pro_min": 1.2, "pro_max": 1.5, "type": "✂️ 外科手術術後型", "notes": "強調術後早期進食、減少生理應激。若為腸胃道手術，初期必須嚴格配合低渣或無渣飲食，減少腸道工作量。"},
    "第二型糖尿病 (Diabetes Mellitus)": {"kcal_min": 25, "kcal_max": 30, "pro_min": 1.0, "pro_max": 1.2, "type": "📊 控醣平衡型", "notes": "控制總醣量、均勻分配三餐、增加膳食纖維。控制水果份量與時機，禁止含糖飲料。"},
    "慢性腎臟病-未透析 (CKD)": {"kcal_min": 30, "kcal_max": 35, "pro_min": 0.6, "pro_max": 0.8, "type": "⚠️ 嚴格限蛋白型", "notes": "限制蛋白質、鈉、鉀、磷。採低氮澱粉（冬粉、西谷米）、蔬菜切後必須汆燙以避出鉀離子。"},
    "慢性腎臟病-已透析 (Dialysis)": {"kcal_min": 30, "kcal_max": 35, "pro_min": 1.0, "pro_max": 1.2, "type": "🥩 高蛋白補償型", "notes": "透析流失大量胺基酸！每餐補充足量優質蛋白（蛋、豆腐、魚、瘦肉），持續嚴格控鉀、控磷、限水分。"},
    "高血脂症 (Hyperlipidemia)": {"kcal_min": 25, "kcal_max": 30, "pro_min": 0.8, "pro_max": 1.2, "type": "🧈 脂質調配型", "notes": "降低飽和脂肪與反式脂肪，多選單元不飽和脂肪（橄欖油）與 omega-3 魚類，膳食纖維干預目標建議拉高至 50g 以上以加速膽酸排泄。"}
}

# ==================== Sidebar: 使用者輸入與臨床定錨區 ====================
st.sidebar.header("📋 第一步：NCP 臨床情境定錨")
weight = st.sidebar.number_input("請輸入個案體重 (kg):", min_value=30.0, max_value=200.0, value=60.0, step=0.5)

selected_disease = st.sidebar.selectbox("請選擇臨床情境/目標疾病:", list(DISEASE_DB.keys()))
disease_info = DISEASE_DB[selected_disease]

# 🎛️ 渣質飲食型態選擇
residue_type = st.sidebar.radio("請選擇腸道渣質限制 (Residue Restriction):", ["常規一般飲食", "低渣飲食 (低纖維/限制乳品)", "無渣飲食 (腸道術後/完全清空/嚴禁乳品)"])

# 🎛️ 核心新增：膳食纖維臨床干預目標選擇
st.sidebar.markdown("---")
st.sidebar.header("🌾 膳食纖維干預指標")
fiber_mode = st.sidebar.radio("請選擇膳食纖維每日目標:", ["常規成人基礎需求 (34g/日)", "有效改善高血脂高劑量干預 (50g+/日)"])
target_fiber = 34 if "34g" in fiber_mode else 50

st.sidebar.markdown("---")
st.sidebar.header("⚙️ 第二步：外援商業營養品 (ONS) 扣除")
use_ons = st.sidebar.checkbox("此個案是否搭配使用『口服補充/商業配方』？")

ons_kcal, ons_p, ons_f, ons_c = 0.0, 0.0, 0.0, 0.0
if use_ons:
    ons_cans = st.sidebar.slider("每日使用罐數 (1罐預設250kcal, P:10g, F:8.5g, C:33.5g):", 1, 6, 2, step=1)
    ons_kcal = ons_cans * 250.0
    ons_p = ons_cans * 10.0
    ons_f = ons_cans * 8.5
    ons_c = ons_cans * 33.5

st.sidebar.markdown("---")
st.sidebar.header("⚖️ 第三步：自體淨需求計算")
kcal_kg = st.sidebar.slider("每日每公斤熱量需求 (kcal/kg):", 15, 45, int(disease_info["kcal_max"]), step=1)
pro_g_kg = st.sidebar.slider("每日每公斤蛋白質需求 (g/kg):", 0.5, 2.5, float(disease_info["pro_min"]), step=0.1)

raw_tdee = weight * kcal_kg
raw_pro_g = weight * pro_g_kg

tdee = max(0.0, raw_tdee - ons_kcal)
target_pro_g = max(0.0, raw_pro_g - ons_p)
pro_kcal = target_pro_g * 4

if pro_kcal >= tdee and tdee > 0:
    st.sidebar.error("❌ 錯誤：蛋白質熱量超出剩餘總熱量預算！")
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

# 🎛️ 核心解鎖：無渣飲食強制關閉乳品
if residue_type == "無渣飲食 (腸道術後/完全清空/嚴禁乳品)":
    milk_type = st.sidebar.selectbox("乳品分型 (無渣已強制鎖定):", ["不喝乳品/無乳品 (P:0g, F:0g, C:0g)"])
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

# 🎛️ 核心解鎖：肉類分級新增「無肉品」選項
meat_type = st.sidebar.selectbox("肉類分級選擇:", ["中脂肉類 (P:7g, F:5g)", "低脂肉類 (P:7g, F:3g)", "高脂肉類 (P:7g, F:10g)", "不吃肉類/無肉品 (P:0g, F:0g)"])

if "中脂" in meat_type:
    meat_p, meat_f, is_meat_free = 7.0, 5.0, False
    meat_ref = "生重 35 克中脂肉類 (如豆腐 80 克、雞蛋 55 克)"
elif "低脂" in meat_type:
    meat_p, meat_f, is_meat_free = 7.0, 3.0, False
    meat_ref = "生重 35 克低脂肉類 (如一般魚類 35 克、無糖豆漿 190 毫升)"
elif "高脂" in meat_type:
    meat_p, meat_f, is_meat_free = 7.0, 10.0, False
    meat_ref = "生重 35 克高脂肉類 (如百頁豆腐 70 克)"
else:
    meat_p, meat_f, is_meat_free = 0.0, 0.0, True
    meat_ref = "當前已完全剔除肉類蛋白質與脂肪分配！"

st.sidebar.markdown("---")
st.sidebar.header("🍽️ 第五步：餐次分配比例設定")
meal_mode = st.sidebar.selectbox(
    "請選擇餐次分配模式:",
    ["常規三餐等分 (早33.3%, 午33.3%, 晚33.3%)", "常規四餐結構 (早30%, 午30%, 晚30%, 點心10%)", "重症少量多餐 (六餐均分各16.6%)"]
)

if "常規三餐" in meal_mode:
    meals = {"早餐": 0.333, "午餐": 0.333, "晚餐": 0.334}
elif "常規四餐" in meal_mode:
    meals = {"早餐": 0.30, "午餐": 0.30, "晚餐": 0.30, "點心": 0.10}
else:
    meals = {"第一餐": 0.166, "第二餐": 0.166, "第三餐": 0.166, "第四餐": 0.166, "第五餐": 0.166, "第六餐": 0.17}

# ==================== Core Algorithm ====================
veg_servings = 0.0 if residue_type == "無渣飲食 (腸道術後/完全清空/嚴禁乳品)" else 3.0
fruit_servings = 0.0 if residue_type == "無渣飲食 (腸道術後/完全清空/嚴禁乳品)" else 2.0

base_cho = (veg_servings * 5) + (fruit_servings * 15) + (milk_servings * milk_c)
base_pro = (veg_servings * 1) + (fruit_servings * 0) + (milk_servings * milk_p)
base_fat = (veg_servings * 0) + (fruit_servings * 0) + (milk_servings * milk_f)

rem_cho = target_cho_g - base_cho
rem_pro = target_pro_g - base_pro

grain_servings = max(0.0, rem_cho / 15)
rem_pro_after_grain = rem_pro - (grain_servings * 2)

if is_meat_free:
    meat_servings = 0.0
    if rem_pro_after_grain > 0 and tdee > 0:
        st.sidebar.warning("⚠️ 臨床提示：已設定無肉品，但扣除主食後仍有剩餘蛋白質需求，系統將自動將賸餘醣類分配給全穀雜糧類補足。")
else:
    meat_servings = max(0.0, rem_pro_after_grain / meat_p)

current_fat = base_fat + (meat_servings * meat_f)
rem_fat = target_fat_g - current_fat
fat_servings = max(0.0, rem_fat / 5)

# ==================== Dashboard: 三分頁系統呈現 ====================
tab1, tab2, tab3 = st.tabs(["📊 精準營養神算配對 (含餐次)", "🏥 供膳供應管理 (HACCP) 核檢", "🧪 商業管灌配方臨床決策系統"])

with tab1:
    st.subheader(f"🩺 當前疾病/重症情境：{selected_disease}")
    st.info(f"💡 **臨床核心介入指引**：{disease_info['notes']}\n\n⚠️ **當前渣質設定**：{residue_type}")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📊 總熱量需求 (含外援)", f"{raw_tdee:.0f} kcal")
    col2.metric("🍚 淨天然食物熱量需求", f"{tdee:.0f} kcal")
    col3.metric("🍗 淨蛋白質目標", f"{target_pro_g:.1f} g")
    col4.metric("🌾 膳食纖維干預目標", f"{target_fiber} g/日")

    st.markdown("### 🍽️ 淨天然食物：六大類食物每日精準總份數")
    
    grain_note = "禁止糙米雜糧，請全面改用白米飯、白吐司、冬粉或西谷米！" if "一般" not in residue_type else "一份等於生重20-30g，如1/4碗飯。"
    veg_note = "無渣飲食已將蔬菜降為0份。" if residue_type == "無渣飲食 (腸道術後/完全清空/嚴禁乳品)" else "一份等於生重100g。限鉀個案切記要先切再充分汆燙！"
    fruit_note = "無渣飲食已將水果降為0份。" if residue_type == "無渣飲食 (腸道術後/完全清空/嚴禁乳品)" else "一份約100g。控管高血脂、糖尿病與透析個案的份數。"
    milk_note = "已強制關閉乳品類，避免酪蛋白凝乳造成腸道殘渣！" if milk_servings == 0 else f"1份等於240ml。當前選用：{milk_type}"

    food_groups_data = {
        "六大類食物名稱": ["全穀雜糧類", "豆魚蛋肉類", "乳品類", "蔬菜類", "水果類", "油脂與堅果種子類"],
        "每日精準總份數": [f"{grain_servings:.1f} 份", f"{meat_servings:.1f} 份", f"{milk_servings:.1f} 份", f"{veg_servings:.1f} 份", f"{fruit_servings:.1f} 份", f"{fat_servings:.1f} 份"],
        "臨床生重與品項精確指引": [grain_note, f"搭配目前設定，1份相當於：{meat_ref}。低渣/無渣個案嚴禁油炸與帶筋老肉！", milk_note, veg_note, fruit_note, f"約 {fat_servings*5:.1f} 克烹調油。低渣/無渣飲食者嚴禁食用整粒堅果，避免顆粒摩擦腸壁！"]
    }
    st.dataframe(pd.DataFrame(food_groups_data), use_container_width=True)

    st.markdown("### ⏰ 每餐次六大類食物份數自動配對表")
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

with tab2:
    st.subheader("🏥 大量製備與供膳管理全流程核檢 (HACCP CCP 對齊)")
    haccp_flow = {
        "NCP / 團膳管理步驟": [
            "1. 評估與採購", "2. 診斷與驗收 🚨CCP", "3. 需求計算與儲存", "4. 食物代換與備料", 
            "5. 菜單設計與烹調 🚨CCP", "6. 可行性核檢與配膳", "7. 菜單定案與供餐", "8. 留樣備查 🚨核心管制", "9. 監測與評值"
        ],
        "重症、ERAS 與高纖供膳控制重點說明": [
            "採購必須確保特殊低渣代用品、ONS 商業配方之穩定供應鏈。高纖飲食應採購新鮮富含水溶性纖維之天然食材。",
            "驗收開啟強迫症『數量、品質、重量、溫度、有效期限』五大核檢。冷藏應≤7°C，冷凍應≤-18°C。",
            "儲存遵循 FIFO 與 FEFO，生熟食徹底分區存放，嚴防血水滴落引發交叉污染。",
            "依據『低渣/無渣/高纖限制』備料。低渣/無渣個案之肉品需徹底去皮、去骨、去筋，粗纖維蔬菜一律剔除；高纖個案保留全穀麩皮。",
            "烹調使用中心溫度計量測，確保中心溫度達標。低渣個案食材需完全煮軟，高纖個案避免過度高溫油炸破壞必需脂肪酸。",
            "生鮮食材成本控制在 45%-55% 之間。特殊重症餐（如無渣餐、無肉餐）配膳時絕對不可與一般餐混淆，防止嚴重醫療事故。",
            "熱食保溫必須≥60°C，冷食保溫必須<7°C，以最快速度穿過 7°C-60°C 危险溫度帶。",
            "醫院集體供膳每餐、每道菜皆必須強迫留樣！精確秤取 100-150 克食物檢體，密封後置於冷藏環境（≤7°C）下，儲存至少 48 小時。",
            "定期監測患者之 HbA1c、BUN、Cr、Albumin、血脂 TC/LDL-C 數據，若高血脂個案纖維調配至 50g 仍未改善，即刻啟動 PDCA 修正！"
        ]
    }
    st.table(pd.DataFrame(haccp_flow))

with tab3:
    st.subheader("🧪 商業管灌配方臨床輔助決策系統")
    st.write("根據個案之腸胃道功能（GI Function）與特定疾病狀態，臨床管灌配方嚴格分類為『四大型男』，不允許隨便亂配！")
    
    formula_choice = st.selectbox(
        "請選擇欲評估的商業配方類別 (Commercial Formula Selector):",
        ["聚合配方 (Polymeric Formula)", "單體配方 / 元素配方 (Monomeric Formula)", "特殊疾病配方 (Disease-Specific Formula)", "單素配方 (Modular Formula)"]
    )
    
    if "聚合" in formula_choice:
        st.success("👨‍⚕️ **聚合配方 (Polymeric Formula) ——『完整付出的常規正餐』**")
        st.markdown("""
        * **核心特徵**：含有完整未水解的三大營養素。大部分產品不含乳糖，可取代正餐。
        * **理化常數**：熱量密度約 1~1.2 kcal/mL，滲透壓最接近人體生理體液，約 **300~500 mOsm/kg**。配方濃度愈高，滲透壓隨之增高。
        * **臨床應用**：可用於**消化吸收功能完全正常**的病患。大部分病人均可耐受此一般配方。
        * **國考辨識/對應口訣**：*完整聚合，最貼人和！* 誤以為其滲透壓極高會導致腹瀉是常見陷阱。
        """)
    elif "單體" in formula_choice:
        st.error("🧪 **單體配方 / 元素配方 (Monomeric Formula) ——『直接給現金的乾爹』**")
        st.markdown("""
        * **核心特徵**：又稱元素配方 (Elemental Formula)。蛋白質預先切碎為**水解酪蛋白、水解乳清蛋白、胜肽 (Peptide) 或游離胺基酸** (約占 12~20%)；醣類為修飾澱粉或麥芽糊精 (約占 60~70%)；脂肪改用**中鏈脂肪酸 (MCT)** 及少量長鏈脂肪酸 (LCT) 提供必需脂肪酸 (總脂約占 12~20%)。一般不含乳糖，價格昂貴。
        * **理化常數**：相同重量下分子被切碎導致溶質粒子數暴增，**滲透壓極高，高達 500~600 mOsm/kg**。
        * **臨床應用**：專門用於**胃腸道功能嚴重受損**、需要水解營養素以利吸收的病患（如短腸症、急性胰臟炎、嚴重吸收不良）。
        * **國考辨訊/對應口訣**：*單體切碎，高壓狂瀉！* 臨床灌食必須放慢速度，否則高滲透壓會強行將細胞水分抽入腸腔，引發嚴重的滲透性腹瀉。
        """)
    elif "特殊" in formula_choice:
        st.info("🧬 **特殊疾病配方 (Disease-Specific Formula) ——『量身打造的專屬情人』**")
        st.markdown("""
        * **核心特徵**：針對特定器官衰竭或代謝障礙病患的病理機轉進行特殊比例調整。價格昂貴，部分配方滲透壓極高。
        * **各大器官特異性對照矩陣**：
            1. **肝臟疾病**：富含支鏈胺基酸 (BCAA)，用於調節氨代謝，防治肝性腦病變。
            2. **腎臟疾病**：依據透析前後嚴密調整蛋白質含量 (洗腎前限制蛋白，洗腎後補償高蛋白)。
            3. **肺部疾病 / 葡萄糖不耐症**：嚴格採取**低醣高脂**設計。
            4. **免疫功能缺陷**：富含麩胺酸 (Glutamine)、精胺酸 (Arginine)、ω-3 脂肪酸、魚油、核糖核酸 (RNA)。
        * **國考辨識/對應口訣**：*肺病低醣，呼吸順暢！* 肺病配方因脂肪的呼吸商 (RQ) 最低，代謝產生的二氧化碳最少，可有效減輕肺部呼吸負擔，切忌誤選高醣。
        """)
    else:
        st.warning("🛠️ **單素配方 (Modular Formula) ——『單一功能的工具人』**")
        st.markdown("""
        * **核心特徵**：**只提供醣類、蛋白質或脂肪的單一營養素**（如純粉飴、純乳清蛋白粉）的商業配方。完全缺乏維生素、礦物質與必需脂肪酸。
        * **臨床應用**：可以與其他配方組合，用來製作特殊配方以增加營養缺口。
        * **國考頂級陷阱/對應口訣**：*單素工具，拒絕獨處！* 題目只要問「不可單獨使用」、「僅提供單一營養」，毫无懸念直接選單素配方！若單獨使用將引發嚴重的巨量與微量營養素缺乏症。在患者使用高劑量皮質類固醇引發高血糖時，若盲目單獨添加純醣類單素配方，將導致血糖徹底失控誘發高滲透壓非酮酸性昏迷 (HHNK)。
        """)
        
    st.markdown("---")
    st.caption("🚨 **出題者思維例外防呆提示**：因科學文獻數據不足、無法確立除了聚合、單體、特殊疾病、單素這四大分類之外，還有哪些具有臨床共識的獨立商業配方分類結果。若超出此生化邏輯框架，則屬於非腸道可吸收之物質。")
