import streamlit as st
from huggingface_hub import InferenceClient
import firebase  # Import thư viện firebase-rest-api [9]

# ==========================================
# 1. CẤU HÌNH FIREBASE
# ==========================================
# THAY THẾ BẰNG CẤU HÌNH THẬT CỦA BẠN LẤY TỪ FIREBASE CONSOLE [9]
config = {
    "apiKey": "AIzaSyB1TZlKeLFntLZCUUV7xBgUZPJF9-dF09o",
    "authDomain": "fir-816eb.firebaseapp.com",
    "databaseURL": "https://fir-816eb-default-rtdb.asia-southeast1.firebasedatabase.app",
    "projectId": "fir-816eb",
    "storageBucket": "fir-816eb.firebasestorage.app",
    "messagingSenderId": "307344273645",
    "appId": "1:307344273645:web:e3571b905b5ff4d96cdce4"
}

# Khởi tạo kết nối với Firebase [10]
firebase_app = firebase.initialize_app(config)
db = firebase_app.database() # Gọi dịch vụ Database [3]

# ==========================================
# 2. CẤU HÌNH HUGGING FACE AI
# ==========================================
import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

# Tải các biến môi trường từ file .env lên
load_dotenv()

# Lấy token một cách an toàn
client = InferenceClient(token=os.getenv("HF_TOKEN"))


def analyze_preferences(user_text):
    labels = ["Vegetarian", "Romantic Dating", "Cheap Budget", "Car Parking", "Fast Food"]
    try:
        results = client.zero_shot_classification(
            user_text, candidate_labels=labels, model="facebook/bart-large-mnli"
        )
        return results
    except Exception as e:
        return {"error": str(e)}

# ==========================================
# 3. GIAO DIỆN & XỬ LÝ LƯU DỮ LIỆU
# ==========================================
st.set_page_config(page_title="FoOdyssey Demo", page_icon="🍔")
st.title("🍔 FoOdyssey: AI & Firebase Demo")

user_input = st.text_input("Bạn muốn tìm quán như thế nào?")

if st.button("Phân tích và Lưu vào Database"):
    if user_input:
        with st.spinner("AI đang xử lý..."):
            result = analyze_preferences(user_input)
            
            if isinstance(result, dict) and "error" in result:
                st.error("🚨 Lỗi từ Hugging Face:")
                st.code(result["error"])
            else:
                top_1 = result[0]
                top_2 = result[1]
                
                st.success("Phân tích thành công!")
                st.write(f"👉 **Tiêu chí 1:** {top_1['label']} (Độ tự tin: {top_1['score']:.2f})")
                st.write(f"👉 **Tiêu chí 2:** {top_2['label']} (Độ tự tin: {top_2['score']:.2f})")
                
                # --- PHẦN MỚI: LƯU VÀO FIREBASE ---
                # Gom dữ liệu thành dạng Dictionary (JSON) [3]
                data_to_save = {
                    "user_request": user_input,
                    "ai_detected_label_1": top_1['label'],
                    "ai_detected_score_1": float(top_1['score']),
                    "timestamp": "Now" # Trong thực tế bạn có thể dùng thư viện datetime
                }
                
                try:
                    # Đẩy dữ liệu lên Firebase vào nhánh "search_history" [3]
                    db.child("search_history").push(data_to_save)
                    st.success("✅ Đã lưu lịch sử tìm kiếm của bạn lên Firebase thành công!")
                except Exception as e:
                    st.error(f"Lỗi không thể lưu vào Firebase: {e}")
                    st.info("💡 Mẹo: Bạn đã nhớ bật Firebase Database sang chế độ 'Test Mode' chưa?")
    else:
        st.warning("Vui lòng nhập gì đó trước khi phân tích!")