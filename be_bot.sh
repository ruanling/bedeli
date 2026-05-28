#!/bin/bash
# Be Giao Hàng Bot Launcher
# 
# Cách dùng:
#   1. Chạy bot: python be_bot.py --login
#   2. Đăng nhập lần đầu + xử lý reCAPTCHA thủ công
#   3. Session sẽ được lưu
#   4. Lần sau chạy: python be_bot.py --list-orders

echo "╔════════════════════════════════════════════════╗"
echo "║     Be Giao Hàng Automation Bot                  ║"
echo "╚════════════════════════════════════════════════╝"

# Kiểm tra arguments
if [ "$1" = "--login" ]; then
    echo "🚀 Đang khởi động bot để đăng nhập..."
    cd "$(dirname "$0")"
    python3 be_delivery_bot.py --login "${@:2}"
elif [ "$1" = "--list" ]; then
    echo "📋 Đang lấy danh sách đơn hàng..."
    cd "$(dirname "$0")"  
    python3 be_delivery_bot.py --list-orders
elif [ "$1" = "--create" ]; then
    echo "📦 Đang tạo đơn hàng..."
    cd "$(dirname "$0")"
    python3 be_delivery_bot.py --create-order
else
    echo "
Cách dùng:
  ./be_bot.sh --login         Đăng nhập (lần đầu cần xử lý reCAPTCHA)
  ./be_bot.sh --list        Xem danh sách đơn hàng  
  ./be_bot.sh --create      Tạo đơn hàng mẫu

Ví dụ:
  ./be_bot.sh --login --phone 0901234567
  
Lưu ý: 
  - Lần đầu chạy cần xử lý reCAPTCHA thủ công
  - Session sẽ được lưu cho lần sau
"
fi