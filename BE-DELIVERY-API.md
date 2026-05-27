# Be Giao Hàng API Documentation

Hướng dẫn tích hợp API của Be Delivery (giaohang.be.com.vn) để tự động đặt đơn hàng và theo dõi đơn hàng.

## 📋 Mục lục

1. [Giới thiệu](#giới-thiệu)
2. [Authentication](#authentication)
3. [Base URL](#base-url)
4. [API Endpoints](#api-endpoints)
5. [Ví dụ sử dụng](#ví-dụ-sử-dụng)
6. [Webhook](#webhook)
7. [Mã lỗi](#mã-lỗi)

---

## Giới thiệu

Be Delivery API cho phép các đối tác đã xác minh sử dụng dịch vụ giao hàng Be theo thỏa thuận trong hợp đồng dịch vụ.

**Các chức năng chính của API:**
- Lấy thông tin các dịch vụ khả dụng (Giao hàng ngay, Giao hàng 2h, Giao hàng 4h)
- Tính phí giao hàng cho từng dịch vụ và tính năng bổ sung
- Tạo đơn hàng giao hàng
- Lấy thông tin chi tiết đơn hàng, trạng thái hiện tại & theo dõi lộ trình
- Hủy đơn hàng
- Webhook cho cập nhật trạng thái đơn hàng

---

## Authentication

### Cách lấy thông tin đăng nhập

Be cung cấp cho đối tác thông tin tài khoản qua email, bao gồm:
- `client_id`
- `client_secret`

Để được cấp thông tin này, bạn cần:
1. Liên hệ Be qua email: hotro@be.com.vn
2. Hoặc gọi hotline: 1900232345
3. Ký hợp đồng đối tác với Be

### Sử dụng Token

```python
import requests
from requests.auth import HTTPBasicAuth

# OAuth 2.0 Client Credentials
def get_access_token(client_id, client_secret):
    url = "https://gw.be.com.vn/api/v1/be-booking-gateway/partner/v1/oauth/token"
    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret
    }
    response = requests.post(url, data=data)
    return response.json().get("access_token")

# Sử dụng token trong header
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}
```

---

## Base URL

| Môi trường | URL |
|-----------|-----|
| **Staging** | `https://gw.veep.me/api/v1/be-booking-gateway/partner/v1` |
| **Production** | `https://gw.be.com.vn/api/v1/be-booking-gateway/partner/v1` |

**IPs cho phép:**
| Môi trường | IPs |
|-----------|-----|
| Staging | 34.87.118.100, 34.87.5.56 |
| Production | 35.240.135.8, 34.126.91.149 |

---

## API Endpoints

### 1. Lấy danh sách dịch vụ khả dụng

```http
GET /services
```

**Response:**
```json
{
  "services": [
    {
      "service_type": "DELIVERY_INSTANT",
      "description": "On-demand delivery. One order - one driver",
      "constraints": {
        "max_weight": "15kg",
        "max_distance": "15km"
      }
    },
    {
      "service_type": "DELIVERY_2H",
      "description": "Commit delivery in 2h with lower price",
      "constraints": {
        "max_weight": "30kg",
        "max_distance": "25km"
      }
    },
    {
      "service_type": "DELIVERY_4H",
      "description": "Commit delivery in 4h with lowest price",
      "constraints": {
        "max_weight": "30kg",
        "max_distance": "30km"
      }
    }
  ]
}
```

### 2. Tính phí giao hàng

```http
POST /fare/calculate
```

**Request Body:**
```json
{
  "service_type": "DELIVERY_INSTANT",
  "sender": {
    "lat": 10.8231,
    "lng": 106.6297,
    "address": "123 Nguyễn Trãi, Quận 1, TP.HCM"
  },
  "recipient": {
    "lat": 10.7769,
    "lng": 106.6909,
    "address": "456 Lê Văn Sỹ, Quận Tân Bình, TP.HCM"
  },
  "add_ons": ["DOOR_TO_DOOR"],
  "cod_amount": 0,
  "item_value": 0
}
```

**Response:**
```json
{
  "fare": {
    "base_fee": 25000,
    "distance_fee": 15000,
    "add_on_fee": 5000,
    "total": 45000,
    "currency": "VND"
  }
}
```

### 3. Tạo đơn hàng mới

```http
POST /orders
```

**Request Body:**
```json
{
  "service_type": "DELIVERY_INSTANT",
  "external_order_id": "ORDER_12345",
  "sender": {
    "name": "Nguyễn Văn A",
    "phone": "0901234567",
    "address": "123 Nguyễn Trãi, Quận 1, TP.HCM",
    "lat": 10.8231,
    "lng": 106.6297
  },
  "recipient": {
    "name": "Trần Thị B",
    "phone": "0912345678",
    "address": "456 Lê Văn Sỹ, Quận Tân Bình, TP.HCM",
    "lat": 10.7769,
    "lng": 106.6909
  },
  "add_ons": ["DOOR_TO_DOOR", "SMS"],
  "cod_amount": 500000,
  "item_description": "Điện thoại iPhone 15",
  "note": "Gọi điện trước khi giao"
}
```

**Response:**
```json
{
  "order_id": "BE2024010112345",
  "external_order_id": "ORDER_12345",
  "status": "PENDING",
  "estimated_pickup_time": "2024-01-01T10:00:00Z",
  "estimated_delivery_time": "2024-01-01T11:00:00Z",
  "fare": {
    "total": 55000,
    "currency": "VND"
  }
}
```

### 4. Lấy thông tin đơn hàng

```http
GET /orders/{orderId}
```

**Response:**
```json
{
  "order_id": "BE2024010112345",
  "external_order_id": "ORDER_12345",
  "status": "PICKING_UP",
  "status_details": {
    "status": "PICKING_UP",
    "status_message": "Tài xế đang lấy hàng",
    "updated_at": "2024-01-01T10:15:00Z"
  },
  "driver": {
    "id": "DRIVER_001",
    "name": "Lê Văn Tài",
    "phone": "0389012345",
    "vehicle_type": "bike",
    "rating": 4.8
  },
  "route": {
    "current_location": {
      "lat": 10.8250,
      "lng": 106.6350
    },
    "tracking_url": "https://track.be.com.vn/abc123"
  },
  "fare": {
    "total": 55000,
    "currency": "VND"
  }
}
```

### 5. Lấy danh sách đơn hàng

```http
GET /orders?page=1&limit=20&status=PENDING
```

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| page | int | Số trang |
| limit | int | Số lượng kết quả tối đa |
| status | string | Lọc theo trạng thái |
| from_date | string | Từ ngày (ISO 8601) |
| to_date | string | Đến ngày (ISO 8601) |

### 6. Hủy đơn hàng

```http
DELETE /orders/{orderId}
```

**Request Body:**
```json
{
  "cancellation_reason": "Khách hàng yêu cầu hủy"
}
```

**Response:**
```json
{
  "order_id": "BE2024010112345",
  "status": "CANCELLED",
  "refund": {
    "amount": 55000,
    "currency": "VND",
    "estimated_days": 3
  }
}
```

---

## Các loại dịch vụ

| Service Type | Mô tả | Phù hợp |
|-------------|-------|---------|
| `DELIVERY_INSTANT` | Giao hàng ngay lập tức, 1 đơn - 1 tài xế | Giao gấp, hàng có giá trị cao |
| `DELIVERY_2H` | Giao hàng trong 2 giờ, có thể ghép đơn | Giao nhanh, tiết kiệm |
| `DELIVERY_4H` | Giao hàng trong 4 giờ, giá thấp nhất | Tiết kiệm nhất |

---

## Các dịch vụ bổ sung (Add-ons)

| Add-on | Mô tả | Áp dụng |
|-------|-------|---------|
| `COD_PAY_IN_ADVANCE` | COD tạm ứng - Tài xế trả tiền hộ trước | Tất cả dịch vụ |
| `COD_COLLECT_CASH` | COD thu hộ - Thu tiền từ người nhận | Chỉ DELIVERY_4H |
| `BULKY_ITEMS` | Giao hàng cồng kềnh | Chỉ DELIVERY_INSTANT |
| `DOOR_TO_DOOR` | Giao hàng tận cửa | Chỉ DELIVERY_INSTANT |
| `SMS` | Gửi SMS thông báo cho người nhận | Tất cả dịch vụ |

---

## Trạng thái đơn hàng

| Status | Mô tả tiếng Việt |
|--------|-----------------|
| `PENDING` | Đơn hàng đang chờ xử lý |
| `CONFIRMED` | Đơn hàng đã được xác nhận |
| `ASSIGNING` | Đang tìm tài xế |
| `PICKING_UP` | Tài xế đang đến lấy hàng |
| `PICKED_UP` | Đã lấy hàng |
| `DELIVERING` | Đang giao hàng |
| `DELIVERED` | Đã giao hàng |
| `COMPLETED` | Hoàn thành |
| `CANCELLED` | Đã hủy |
| `RETURNING` | Đang trả hàng |
| `RETURNED` | Đã trả hàng |

---

## Webhook

### Đăng ký Webhook

```http
POST /webhook/register
```

**Request Body:**
```json
{
  "webhook_url": "https://your-domain.com/webhook/be",
  "events": ["ORDER_STATUS_CHANGED", "ORDER_DELIVERED"]
}
```

**Response:**
```json
{
  "webhook_id": "WH_12345",
  "webhook_url": "https://your-domain.com/webhook/be",
  "status": "ACTIVE"
}
```

### Event Payload

```json
{
  "event": "ORDER_STATUS_CHANGED",
  "order_id": "BE2024010112345",
  "external_order_id": "ORDER_12345",
  "status": "DELIVERED",
  "timestamp": "2024-01-01T10:45:00Z",
  "driver": {
    "name": "Lê Văn Tài",
    "phone": "0389012345"
  }
}
```

---

## Mã lỗi

| Mã lỗi | Mô tả |
|--------|-------|
| 400 | Bad Request - Tham số không hợp lệ |
| 401 | Unauthorized - Token không hợp lệ |
| 403 | Forbidden - Không có quyền truy cập |
| 404 | Not Found - Không tìm thấy |
| 422 | Unprocessable Entity - Dữ liệu không hợp lệ |
| 429 | Too Many Requests - Quá nhiều request |
| 500 | Internal Server Error - Lỗi server |
| 503 | Service Unavailable - Dịch vụ không khả dụng |

---

## Ví dụ sử dụng

### Ví dụ 1: Tạo đơn hàng một cách đầy đủ

```python
import requests
import json
from datetime import datetime

class BeDeliveryAPI:
    def __init__(self, client_id, client_secret, base_url="https://gw.be.com.vn/api/v1/be-booking-gateway/partner/v1"):
        self.base_url = base_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
    
    def authenticate(self):
        """Đăng nhập và lấy token"""
        url = f"{self.base_url}/oauth/token"
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        response = requests.post(url, data=data)
        if response.status_code == 200:
            self.access_token = response.json().get("access_token")
            return True
        return False
    
    def get_headers(self):
        """Lấy headers cho request"""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
    
    def calculate_fare(self, sender, recipient, service_type="DELIVERY_INSTANT", add_ons=None):
        """Tính phí giao hàng"""
        url = f"{self.base_url}/fare/calculate"
        data = {
            "service_type": service_type,
            "sender": sender,
            "recipient": recipient,
            "add_ons": add_ons or []
        }
        response = requests.post(url, json=data, headers=self.get_headers())
        return response.json()
    
    def create_order(self, external_order_id, sender, recipient, service_type="DELIVERY_INSTANT",
                   add_ons=None, cod_amount=0, item_description="", note=""):
        """Tạo đơn hàng mới"""
        url = f"{self.base_url}/orders"
        data = {
            "service_type": service_type,
            "external_order_id": external_order_id,
            "sender": sender,
            "recipient": recipient,
            "add_ons": add_ons or [],
            "cod_amount": cod_amount,
            "item_description": item_description,
            "note": note
        }
        response = requests.post(url, json=data, headers=self.get_headers())
        return response.json()
    
    def get_order(self, order_id):
        """Lấy thông tin đơn hàng"""
        url = f"{self.base_url}/orders/{order_id}"
        response = requests.get(url, headers=self.get_headers())
        return response.json()
    
    def cancel_order(self, order_id, reason):
        """Hủy đơn hàng"""
        url = f"{self.base_url}/orders/{order_id}"
        data = {"cancellation_reason": reason}
        response = requests.delete(url, json=data, headers=self.get_headers())
        return response.json()

# Sử dụng
api = BeDeliveryAPI(
    client_id="your_client_id",
    client_secret="your_client_secret"
)

# Đăng nhập
api.authenticate()

# Định nghĩa thông tin
sender = {
    "name": "Nguyễn Văn A",
    "phone": "0901234567",
    "address": "123 Nguyễn Trãi, Quận 1, TP.HCM",
    "lat": 10.8231,
    "lng": 106.6297
}

recipient = {
    "name": "Trần Thị B",
    "phone": "0912345678", 
    "address": "456 Lê Văn Sỹ, Quận Tân Bình, TP.HCM",
    "lat": 10.7769,
    "lng": 106.6909
}

# Tính phí
fare = api.calculate_fare(sender, recipient, "DELIVERY_INSTANT", ["DOOR_TO_DOOR"])
print(f"Phí giao hàng: {fare['fare']['total']} VND")

# Tạo đơn
order = api.create_order(
    external_order_id="ORD_001",
    sender=sender,
    recipient=recipient,
    service_type="DELIVERY_INSTANT",
    add_ons=["DOOR_TO_DOOR", "SMS"],
    cod_amount=500000,
    item_description="Điện thoại iPhone 15",
    note="Gọi điện trước khi giao"
)
print(f"Order ID: {order['order_id']}")
```

### Ví dụ 2: Bot theo dõi đơn hàng tự động

```python
import time
import requests
from threading import Thread

class OrderMonitor:
    def __init__(self, api, webhook_url=None):
        self.api = api
        self.webhook_url = webhook_url
        self.running = False
        self.callbacks = {}
    
    def register_callback(self, status, callback):
        """Đăng ký callback cho trạng thái"""
        self.callbacks[status] = callback
    
    def check_order_status(self, order_id):
        """Kiểm tra trạng thái đơn hàng"""
        order = self.api.get_order(order_id)
        return order.get("status")
    
    def monitor_order(self, order_id, interval=30, timeout=3600):
        """Theo dõi đơn hàng"""
        start_time = time.time()
        
        while self.running and (time.time() - start_time) < timeout:
            status = self.check_order_status(order_id)
            
            # Kiểm tra callback
            if status in self.callbacks:
                self.callbacks[status](order_id, status)
            
            # Dừng nếu hoàn thành
            if status in ["COMPLETED", "DELIVERED", "CANCELLED"]:
                break
            
            time.sleep(interval)
    
    def start_monitoring(self, order_id, interval=30, timeout=3600):
        """Bắt đầu theo dõi"""
        self.running = True
        thread = Thread(target=self.monitor_order, 
                      args=(order_id, interval, timeout))
        thread.start()
        return thread
    
    def stop_monitoring(self):
        """Dừng theo dõi"""
        self.running = False

# Sử dụng
monitor = OrderMonitor(api)

# Đăng ký callbacks
def on_delivered(order_id, status):
    print(f"🔔 Đơn hàng {order_id} đã được giao!")

def on_cancelled(order_id, status):
    print(f"⚠️ Đơn hàng {order_id} đã bị hủy!")

monitor.register_callback("DELIVERED", on_delivered)
monitor.register_callback("CANCELLED", on_cancelled)

# Bắt đầu theo dõi
monitor.start_monitoring("BE2024010112345")

# Sau khi hoàn thành
monitor.stop_monitoring()
```

### Ví dụ 3: Sử dụng với cURL

```bash
# 1. Lấy access token
curl -X POST "https://gw.be.com.vn/api/v1/be-booking-gateway/partner/v1/oauth/token" \
  -d "grant_type=client_credentials" \
  -d "client_id=your_client_id" \
  -d "client_secret=your_client_secret"

# 2. Lấy danh sách dịch vụ
curl -X GET "https://gw.be.com.vn/api/v1/be-booking-gateway/partner/v1/services" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# 3. Tính phí giao hàng
curl -X POST "https://gw.be.com.vn/api/v1/be-booking-gateway/partner/v1/fare/calculate" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "service_type": "DELIVERY_INSTANT",
    "sender": {"lat": 10.8231, "lng": 106.6297, "address": "123 Nguyễn Trãi, Q1, TP.HCM"},
    "recipient": {"lat": 10.7769, "lng": 106.6909, "address": "456 Lê Văn Sỹ, TB, TP.HCM"}
  }'

# 4. Tạo đơn hàng
curl -X POST "https://gw.be.com.vn/api/v1/be-booking-gateway/partner/v1/orders" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "service_type": "DELIVERY_INSTANT",
    "external_order_id": "ORD_12345",
    "sender": {"name": "Nguyễn Văn A", "phone": "0901234567", "address": "123 Nguyễn Trãi, Q1, TP.HCM", "lat": 10.8231, "lng": 106.6297},
    "recipient": {"name": "Trần Thị B", "phone": "0912345678", "address": "456 Lê Văn Sỹ, TB, TP.HCM", "lat": 10.7769, "lng": 106.6909},
    "add_ons": ["DOOR_TO_DOOR"],
    "item_description": "Hàng hóa"
  }'

# 5. Lấy thông tin đơn hàng
curl -X GET "https://gw.be.com.vn/api/v1/be-booking-gateway/partner/v1/orders/BE2024010112345" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# 6. Hủy đơn hàng
curl -X DELETE "https://gw.be.com.vn/api/v1/be-booking-gateway/partner/v1/orders/BE2024010112345" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"cancellation_reason": "Khách hàng yêu cầu hủy"}'
```

---

## Liên hệ hỗ trợ

- **Hotline:** 1900232345
- **Email:** hotro@be.com.vn
- **Website:** https://be.com.vn
- **Developers Portal:** https://developers.be.com.vn

---

## License

MIT License - © 2024