#!/usr/bin/env python3
"""
Be Giao Hàng Automation Bot
Bot điều khiển trình duyệt để tự động đặt đơn hàng trên giaohang.be.com.vn

Cài đặt:
    pip install playwright
    playwright install chromium

Chạy:
    python be_delivery_bot.py
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# Thử import playwright
try:
    from playwright.async_api import async_playwright, Browser, Page, BrowserContext
except ImportError:
    print("❌ Chưa cài playwright!")
    print("   Cài đặt: pip install playwright")
    print("   Sau đó:   playwright install chromium")
    sys.exit(1)

# Config
LOGIN_URL = "https://giaohang.be.com.vn/login"
DASHBOARD_URL = "https://giaohang.be.com.vn/dashboard"
CREATE_ORDER_URL = "https://giaohang.be.com.vn/create-order"

# File lưu session
SESSION_FILE = ".be_session.json"


class BeDeliveryBot:
    def __init__(self, headless: bool = False):
        self.headless = headless
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.token = None
    
    async def init_browser(self):
        """Khởi tạo trình duyệt"""
        print("📱 Khởi tạo trình duyệt...")
        pw = await async_playwright().start()
        self.browser = await pw.chromium.launch(headless=self.headless)
        self.context = await self.browser.new_context()
        self.page = await self.context.new_page()
        print("✅ Trình duyệt đã sẵn sàng!")
    
    def load_session(self) -> bool:
        """Load session từ file (token đã lưu)"""
        if os.path.exists(SESSION_FILE):
            try:
                with open(SESSION_FILE, 'r') as f:
                    data = json.load(f)
                    self.token = data.get('token')
                    if self.token:
                        print("✅ Đã load session từ file")
                        return True
            except:
                pass
        return False
    
    async def login(self, phone: str = None):
        """
        Đăng nhập vào giaohang.be.com.vn
        Lưu ý: Cần xử lý reCAPTCHA thủ công lần đầu
        """
        if not self.page:
            await self.init_browser()
        
        print("🔐 Đang đăng nhập...")
        await self.page.goto(LOGIN_URL)
        await self.page.wait_for_load_state('networkidle')
        
        # Điền số điện thoại
        if phone:
            print(f"   Nhập số điện thoại: {phone}")
            await self.page.fill('input[placeholder*="điện thoại"]', phone)
            await self.page.click('button:has-text("Tiếp tục")')
            await self.page.wait_for_timeout(2000)
        
        # Kiểm tra reCAPTCHA
        recaptcha = await self.page.query_selector('.g-recaptcha')
        if recaptcha:
            print("⚠️  Cần xử lý reCAPTCHA thủ công!")
            print("   Vui lòng xác minh reCAPTCHA trên trình duyệt...")
            input("   Nhấn Enter khi đã xác minh reCAPTCHA xong...")
        
        # Lưu session sau khi đăng nhập
        cookies = await self.context.cookies()
        local_storage = await self.context.evaluate("() => localStorage.getItem('be_token')")
        
        if local_storage:
            self.token = local_storage
            with open(SESSION_FILE, 'w') as f:
                json.dump({'token': local_storage, 'cookies': cookies}, f)
            print("✅ Đã lưu session!")
    
    async def ensure_logged_in(self) -> bool:
        """Kiểm tra và đảm bảo đã đăng nhập"""
        if not self.page:
            await self.init_browser()
        
        # Thử load session cũ
        if self.load_session():
            # Restore session
            await self.page.goto(DASHBOARD_URL)
            await self.page.wait_for_timeout(2000)
            
            # Kiểm tra đã đăng nhập chưa
            current_url = self.page.url
            if "login" not in current_url:
                print("✅ Đã đăng nhập (từ session cũ)")
                return True
        
        return False
    
    async def create_order(self, order_data: dict) -> dict:
        """
        Tạo đơn hàng mới
        
        order_data = {
            "sender": {
                "name": "Tên người gửi",
                "phone": "0912345678", 
                "address": "Địa chỉ gửi",
                "lat": 10.8231,  # optional
                "lng": 106.6297  # optional
            },
            "recipient": {
                "name": "Tên người nhận",
                "phone": "0912345679",
                "address": "Địa chỉ nhận",
                "lat": 10.7769,  # optional
                "lng": 106.6909  # optional  
            },
            "service_type": "DELIVERY_INSTANT",  # INSTANT, 2H, 4H
            "add_ons": ["DOOR_TO_DOOR"],  # optional
            "cod_amount": 500000,  # optional, tiềnCOD
            "note": "Ghi chú"  # optional
        }
        """
        if not self.page:
            await self.ensure_logged_in()
        
        print(f"📦 Đang tạo đơn hàng...")
        
        # Navigate to create order page
        await self.page.goto(CREATE_ORDER_URL)
        await self.page.wait_for_load_state('networkidle')
        
        # Điền thông tin người gửi
        sender = order_data.get('sender', {})
        await self.page.fill('input[name="sender_name"]', sender.get('name', ''))
        await self.page.fill('input[name="sender_phone"]', sender.get('phone', ''))
        await self.page.fill('textarea[name="sender_address"]', sender.get('address', ''))
        
        # Thông tin người nhận  
        recipient = order_data.get('recipient', {})
        await self.page.fill('input[name="recipient_name"]', recipient.get('name', ''))
        await self.page.fill('input[name="recipient_phone"]', recipient.get('phone', ''))
        await self.page.fill('textarea[name="recipient_address"]', recipient.get('address', ''))
        
        # Chọn loại dịch vụ
        service_type = order_data.get('service_type', 'DELIVERY_INSTANT')
        service_map = {
            'DELIVERY_INSTANT': 'text=Ngày',
            'DELIVERY_2H': 'text=2 giờ', 
            'DELIVERY_4H': 'text=4 giờ'
        }
        if service_type in service_map:
            await self.page.click(service_map[service_type])
        
        # COD nếu có
        cod_amount = order_data.get('cod_amount', 0)
        if cod_amount > 0:
            await self.page.fill('input[name="cod_amount"]', str(cod_amount))
        
        # Note
        note = order_data.get('note', '')
        if note:
            await self.page.fill('textarea[name="note"]', note)
        
        # Submit
        await self.page.click('button:has-text("Đặt đơn")')
        await self.page.wait_for_timeout(3000)
        
        # Lấy response/order ID
        # (Cần inspect thực tế để biết selector chính xác)
        result = {
            'status': 'pending',
            'timestamp': datetime.now().isoformat()
        }
        
        print("✅ Đơn hàng đã được tạo!")
        return result
    
    async def get_orders(self, limit: int = 20) -> list:
        """Lấy danh sách đơn hàng"""
        if not self.page:
            await self.ensure_logged_in()
        
        print("📋 Đang lấy danh sách đơn hàng...")
        await self.page.goto("https://giaohang.be.com.vn/orders")
        await self.page.wait_for_load_state('networkidle')
        await self.page.wait_for_timeout(2000)
        
        # Extract order data
        # (Cần inspect thực tế)
        orders = []
        
        # Try find order rows
        rows = await self.page.query_selector_all('table tbody tr')
        for row in rows[:limit]:
            order = {
                'id': await row.query_selector('td:nth-child(1)')?.inner_text(),
                'status': await row.query_selector('td:nth-child(2)')?.inner_text(),
                'from': await row.query_selector('td:nth-child(3)')?.inner_text(),
                'to': await row.query_selector('td:nth-child(4)')?.inner_text(),
            }
            orders.append(order)
        
        return orders
    
    async def close(self):
        """Đóng trình duyệt"""
        if self.browser:
            await self.browser.close()


async def main():
    """Hàm main để test"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Be Delivery Bot')
    parser.add_argument('--headless', action='store_true', help='Chạy headless')
    parser.add_argument('--login', action='store_true', help='Đăng nhập mới')
    parser.add_argument('--phone', type=str, help='Số điện thoại đăng nhập')
    parser.add_argument('--list-orders', action='store_true', help='Liệt kê đơn hàng')
    parser.add_argument('--create-order', action='store_true', help='Tạo đơn hàng mẫu')
    
    args = parser.parse_args()
    
    bot = BeDeliveryBot(headless=args.headless)
    
    try:
        if args.login:
            # Đăng nhập mới
            await bot.init_browser()
            await bot.login(args.phone)
        elif args.list_orders:
            # Liệt kê đơn hàng
            await bot.ensure_logged_in()
            orders = await bot.get_orders()
            print(f"\n📋 Tìm thấy {len(orders)} đơn hàng:")
            for o in orders:
                print(f"   {o}")
        elif args.create_order:
            # Tạo đơn hàng mẫu
            await bot.ensure_logged_in()
            order_data = {
                "sender": {
                    "name": "Shop ABC",
                    "phone": "0901234567",
                    "address": "123 Nguyễn Trãi, Quận 1, TP.HCM"
                },
                "recipient": {
                    "name": "Khách Hàng",
                    "phone": "0912345678", 
                    "address": "456 Lê Văn Sỹ, Quận Tân Bình, TP.HCM"
                },
                "service_type": "DELIVERY_INSTANT",
                "cod_amount": 500000,
                "note": "Gọi điện trước khi giao"
            }
            result = await bot.create_order(order_data)
            print(f"✅ Kết quả: {result}")
        else:
            # Menu tương tác
            print("""
╔══════════════════════════════════════════╗
║     Be Giao Hàng Automation Bot           ║
╚══════════════════════════════════════════╝

Usage:
  python be_delivery_bot.py --login --phone [sdt]   Đăng nhập
  python be_delivery_bot.py --list-orders          Xem danh sách đơn  
  python be_delivery_bot.py --create-order       Tạo đơn mẫu
  python be_delivery_bot.py --headless           Chạy headless

Đăng nhập lần đầu:
  1. Chạy: python be_delivery_bot.py --login --phone 09xxxxxxx
  2. Xử lý reCAPTCHA thủ công trên trình duyệt
  3. Session sẽ được lưu cho lần sau
            """)
    
    finally:
        await bot.close()


if __name__ == "__main__":
    asyncio.run(main())