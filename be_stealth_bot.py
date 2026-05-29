#!/usr/bin/env python3
"""
Be Giao Hàng - Stealth Bot for Server/VPS
Chống bị phát hiện là bot automation
"""

import asyncio
import json
import sys
import random

try:
    from playwright.async_api import async_playwright
except ImportError:
    print("❌ Cài: pip install playwright")
    sys.exit(1)

# ============ CONFIG =============
TOKEN = "eyJhbGciOiJIUzUxMiIsImtpZCI6IlQwVm9NazF0Y0c5YVYzUnJWMGN3ZVZNeU5YQldibFpUWlZWR2RWVkZVakJWU0ZwSFkwWk9iRlpWTlZCWk0wVjRVMFJXUW1GdGVFZGpSMHAzVW10M01tSnVjR3RUTUhoRVV6Rm9WMDVxU25GamF6bFZVbXRKTVZwR1drUlJhemx2VjFaS1dGbHJhekpaYmtreFlWZEdORkV5UmtWa1NGSkRXak5PYlZwRmNHOWhWM2haWTFWU1ZsWXhXVE5TYmswelUwaHdjMU5YWjNoT01IUk5aRWRHUzFsWGNGZFNNMDAxVVZad05GbHJWakZqYmxwRlltNW5OR0ZYWkRKaGJtczBVMGhaZVdGdGFHeGhNbEpaWWxSS1RHSnRiRmRrVmtvMSIsInR5cCI6IkpXVCJ9.eyJhdWQiOiIxIiwiZXhwIjoxNzgyNjE5MDUyLCJ1c2VyX2lkIjoxMTgyNTU1Mywic2Vzc2lvbl9pZCI6ImY0MzMxNGY1ZDM0ZjRiOTk1MDRhNjkwZDgwZDAwZDUwIiwidmVuZG9yIjoiV2ViIERlbGl2ZXJ5In0.dMEWRu0QVKfXMT-r1btsniXqeXfyZ_t431854VVJ7iQWOsvzT3CnwjkuEJvGLNHIA9z2duyKzwVnu4bElqOvlw"
PHONE = "+84904080804"
BASE = "https://giaohang.be.com.vn"

# Fake browser args 
STEALTH_ARGS = [
    '--disable-blink-features=AutomationControlled',
    '--disable-dev-shm-usage', 
    '--no-sandbox',
    '--disable-setuid-sandbox',
    '--disable-gpu',
    '--disable-web-security',
    '--disable-features=IsolateOrigins,site-per-process',
    '--window-size=1920,1080',
]

class BeStealthBot:
    def __init__(self):
        self.browser = None
        self.ctx = None
        self.page = None
    
    async def start(self, headless=False):
        """Khởi động stealth browser"""
        pw = await async_playwright().start()
        
        self.browser = await pw.chromium.launch(
            headless=headless,
            args=STEALTH_ARGS
        )
        
        self.ctx = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='vi-VN',
            timezone_id='Asia/Ho_Chi_Minh',
        )
        
        self.page = await self.ctx.new_page()
        
        # Inject stealth scripts
        await self.page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            Object.defineProperty(navigator, 'plugins', { get: () => [1,2,3,4,5] });
            Object.defineProperty(navigator, 'languages', { get: () => ['vi-VN','vi','en-US','en'] });
            window.chrome = { runtime: {} };
            navigator.permissions.query = ({name}) => Promise.resolve({state: 'granted'});
        """)
        print("✅ Browser started (stealth mode)")
        return self
    
    async def login(self):
        """Login với token"""
        await self.page.goto(BASE)
        await self.page.wait_for_load_state('domcontentloaded')
        
        # Inject token vào localStorage
        js_token = f"localStorage.setItem('access_token', '{TOKEN}'); localStorage.setItem('phone', '{PHONE}');"
        await self.page.evaluate(js_token)
        
        # Reload để apply
        await self.page.reload()
        await self.page.wait_for_timeout(3000)
        
        if "login" not in self.page.url:
            print("✅ Logged in!")
            return True
        print("⚠️ Still at login page")
        return False
    
    async def get_orders(self):
        """Lấy danh sách đơn"""
        await self.page.goto(f"{BASE}/orders")
        await self.page.wait_for_timeout(5000)
        
        content = await self.page.content()
        
        # Tìm order IDs
        import re
        orders = re.findall(r'18\d{6}', content)
        return list(set(orders))[:20]
    
    async def track(self, order_id):
        """Theo dõi đơn"""
        await self.page.goto(f"{BASE}/order-tracking/{order_id}")
        await self.page.wait_for_timeout(5000)
        
        return await self.page.inner_text('body')
    
    async def close(self):
        if self.browser:
            await self.browser.close()


async def main():
    # Demo run
    bot = BeStealthBot()
    await bot.start(headless=False)  # Show browser
    
    await bot.login()
    orders = await bot.get_orders()
    print(f"📦 Orders: {orders}")
    
    # Track first order
    if orders:
        status = await bot.track(orders[0])
        print(f"Tracking: {status[:200]}")
    
    await bot.close()


if __name__ == "__main__":
    print("""
╔═══════════════════════════════════════╗
║   BE STEALTH BOT (Server/VPS Edition)   ║
╚═══════════════════════════════════════╝

Usage:
  python be_stealth_bot.py           # Show browser (recommended for VPS)
  python be_stealth_bot.py --headless # Run hidden
  python be_stealth_bot.py --track 123456789  # Track order
      
On VPS/Server:
  1. Connect via VNC or RDP to see GUI
  2. Or use xvfb-run:
     xvfb-run python be_stealth_bot.py --headless
""")
    asyncio.run(main())