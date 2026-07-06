import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(page_title="پنل پخش ارسلان", layout="wide")

# ----------------------------
# داده‌ها در حافظه موقت
# ----------------------------
if "products" not in st.session_state:
    st.session_state.products = [
        {"code": 101, "name": "نوشابه خانواده", "unit": "کارتن", "price": 150000, "stock": 50},
        {"code": 102, "name": "کیک نظری", "unit": "کارتن", "price": 120000, "stock": 100},
        {"code": 103, "name": "روغن مایع", "unit": "کارتن", "price": 450000, "stock": 30},
    ]

if "orders" not in st.session_state:
    st.session_state.orders = []

if "cart" not in st.session_state:
    st.session_state.cart = []

# ----------------------------
# عنوان و منو
# ----------------------------
st.title("پنل پخش مویرگی ارسلان")

menu = st.sidebar.radio("منو", ["ثبت سفارش ویزیتور", "مدیریت سفارشات"])

# ----------------------------
# ثبت سفارش
# ----------------------------
if menu == "ثبت سفارش ویزیتور":
    st.header("ثبت سفارش جدید")

    customer_name = st.text_input("نام مشتری / فروشگاه")
    payment_type = st.radio("نوع تسویه", ["نقدی", "چکی (اعتباری)"])
    credit_days = st.number_input("مدت اعتبار چک (روز)", min_value=0, step=1)

    product_names = [p["name"] for p in st.session_state.products]
    selected_name = st.selectbox("انتخاب کالا", product_names)

    qty = st.number_input("تعداد کارتن / شل", min_value=1, step=1)

    if st.button("افزودن به سبد"):
        if not customer_name.strip():
            st.error("نام مشتری را وارد کنید.")
        else:
            product = next(p for p in st.session_state.products if p["name"] == selected_name)

            item = {
                "تاریخ": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "مشتری": customer_name,
                "کالا": product["name"],
                "تعداد": int(qty),
                "واحد": product["unit"],
                "فی": product["price"],
                "جمع کل": int(qty) * int(product["price"]),
                "تسویه": payment_type,
                "اعتبار (روز)": int(credit_days) if payment_type.startswith("چکی") else 0,
                "وضعیت": "در انتظار تایید",
            }

            st.session_state.cart.append(item)
            st.success("کالا به سبد اضافه شد.")

    st.subheader("سبد فعلی")
    if st.session_state.cart:
        st.dataframe(pd.DataFrame(st.session_state.cart), use_container_width=True)

        if st.button("ثبت نهایی سفارش"):
            st.session_state.orders.extend(st.session_state.cart)
            st.session_state.cart = []
            st.success("سفارش نهایی ثبت شد.")
    else:
        st.info("سبد خالی است.")

# ----------------------------
# مدیریت سفارشات
# ----------------------------
elif menu == "مدیریت سفارشات":
    st.header("مدیریت سفارشات")

    if not st.session_state.orders:
        st.info("هنوز سفارشی ثبت نشده است.")
    else:
        df = pd.DataFrame(st.session_state.orders)
        st.dataframe(df, use_container_width=True)

        st.subheader("تغییر وضعیت سفارش")
        selected_index = st.number_input("شماره ردیف سفارش", min_value=0, step=1)

        new_status = st.selectbox("وضعیت جدید", ["در انتظار تایید", "تایید شد", "رد شد", "اصلاح شد"])

        if st.button("اعمال وضعیت"):
            if 0 <= int(selected_index) < len(st.session_state.orders):
                st.session_state.orders[int(selected_index)]["وضعیت"] = new_status
                st.success("وضعیت سفارش به‌روزرسانی شد.")
            else:
                st.error("شماره ردیف معتبر نیست.")

        df = pd.DataFrame(st.session_state.orders)
        excel_file = "mahak_output.xlsx"
        df.to_excel(excel_file, index=False)

        with open(excel_file, "rb") as f:
            st.download_button(
                "دانلود خروجی اکسل برای محک",
                f,
                file_name="orders_to_mahak.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
