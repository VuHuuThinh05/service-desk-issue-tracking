# Service Desk & Issue Tracking

Hệ thống quản lý yêu cầu hỗ trợ nội bộ (ticket), được xây dựng bằng FastAPI, SQLAlchemy và PostgreSQL. Dự án minh họa quy trình tiếp nhận ticket, phân quyền người dùng, phân công nhân viên hỗ trợ, cập nhật trạng thái, trao đổi bình luận và lưu lịch sử xử lý.

## 1. Chức năng hiện có

- **Xác thực:** đăng nhập bằng email/mật khẩu, cấp JWT access token và lấy thông tin tài khoản hiện tại.
- **Quản lý người dùng:** Admin xem danh sách, tạo tài khoản và bật/tắt trạng thái hoạt động.
- **Quản lý ticket:** tạo ticket, xem danh sách và chi tiết theo quyền truy cập.
- **Lọc và phân trang:** danh sách ticket hỗ trợ lọc theo trạng thái (status), cùng tham số limit và offset.
- **Phân công:** Admin giao ticket cho Support Agent đang hoạt động.
- **Quy trình trạng thái:** Support Agent được giao ticket có thể chuyển trạng thái theo các quy tắc được triển khai.
- **Bình luận và lịch sử:** xem/thêm bình luận, xem các sự kiện của ticket; không cho thêm bình luận khi ticket đã đóng.
- **Dashboard:** thống kê ticket theo trạng thái và một số mức ưu tiên, với phạm vi dữ liệu phụ thuộc vai trò.
- **Giao diện demo:** frontend HTML, CSS và JavaScript được phục vụ bởi ứng dụng FastAPI.

> Lưu ý về phạm vi: API danh sách ticket hiện hỗ trợ lọc theo trạng thái, không có bộ lọc query riêng theo priority hoặc assignee. Tài liệu này mô tả hành vi đang có, không xem các chức năng dự kiến là chức năng đã hoàn thành.

## 2. Vai trò người dùng

| Vai trò | Quyền chính theo triển khai hiện tại |
|---|---|
| EMPLOYEE | Tạo ticket và truy cập ticket do mình tạo. |
| SUPPORT_AGENT | Truy cập ticket được giao cho mình, chuyển trạng thái và trao đổi trong ticket có quyền truy cập. |
| ADMIN | Quản lý người dùng, xem toàn bộ ticket và phân công ticket cho Support Agent. |

Các kiểm tra quyền được thực hiện ở backend. Việc giao ticket cho Support Agent đang hoạt động được giới hạn cho Admin.

## 3. Công nghệ sử dụng

| Công nghệ | Vai trò |
|---|---|
| Python 3.11 | Ngôn ngữ backend |
| FastAPI | REST API và OpenAPI documentation |
| Pydantic / pydantic-settings | Kiểm tra dữ liệu và đọc cấu hình |
| SQLAlchemy | ORM và truy vấn dữ liệu |
| PostgreSQL 16 | Cơ sở dữ liệu |
| Alembic | Quản lý migration |
| JWT (PyJWT) | Access token |
| Argon2 (pwdlib) | Băm và xác minh mật khẩu |
| pytest, HTTPX, TestClient | Kiểm thử |
| Docker, Docker Compose | Đóng gói và chạy dịch vụ |
| HTML, CSS, JavaScript | Giao diện demo |

## 4. Kiến trúc và cấu trúc thư mục

Dự án sử dụng kiểu **modular monolith**: backend chạy trong một ứng dụng FastAPI, được tổ chức theo các module chức năng.

![System Architecture](docs/images/system-architecture.png)

```text
.
├── app/
│   ├── api/
│   │   ├── deps.py
│   │   └── v1/
│   │       ├── auth.py
│   │       ├── dashboard.py
│   │       ├── tickets.py
│   │       └── users.py
│   ├── core/                 # Cấu hình và bảo mật
│   ├── db/                   # Database base và session
│   ├── models/               # SQLAlchemy models
│   ├── schemas/              # Pydantic request/response schemas
│   ├── services/
│   │   └── ticket_service.py # Quy tắc nghiệp vụ ticket
│   └── main.py
├── docs/
│   ├── images/
│   ├── architecture.md
│   ├── erd.md
│   └── requirements.md
├── frontend/
├── migrations/
│   └── versions/
├── scripts/
├── tests/
├── .env.example
├── alembic.ini
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

Tầng nghiệp vụ ticket hiện được tập trung chủ yếu trong app/services/ticket_service.py; truy vấn dữ liệu khác được thực hiện từ các router bằng SQLAlchemy. Dự án **không có package Repository riêng**.

Tài liệu chi tiết:
- [Kiến trúc hệ thống](docs/architecture.md)
- [Thiết kế cơ sở dữ liệu (ERD)](docs/erd.md)
- [Yêu cầu nghiệp vụ](docs/requirements.md)

## 5. Mô hình dữ liệu

Cơ sở dữ liệu nghiệp vụ gồm bốn bảng chính:

- **users:** tài khoản, vai trò và trạng thái hoạt động.
- **tickets:** yêu cầu hỗ trợ, người tạo, người phụ trách, trạng thái và mức ưu tiên.
- **comments:** nội dung trao đổi trên ticket.
- **ticket_events:** lịch sử sự kiện và giá trị trước/sau thay đổi.

![Entity Relationship Diagram](docs/images/erd.png)

Các trạng thái ticket được sử dụng là OPEN, IN_PROGRESS, RESOLVED và CLOSED. Mức ưu tiên gồm LOW, MEDIUM, HIGH và URGENT. Chi tiết cột, khóa ngoại và ràng buộc được trình bày trong [docs/erd.md](docs/erd.md).

## 6. Chạy dự án bằng Docker Compose

### Yêu cầu

- Git
- Docker Desktop có Docker Compose

### Bước 1: Tải mã nguồn

```powershell
git clone https://github.com/VuHuuThinh05/service-desk-issue-tracking.git
cd service-desk-issue-tracking
```

### Bước 2: Tạo file cấu hình

```powershell
Copy-Item .env.example .env
```

Mở .env và thay các giá trị mẫu, đặc biệt là POSTGRES_PASSWORD và JWT_SECRET_KEY. Không commit file .env hoặc secret thực tế lên GitHub.

### Bước 3: Khởi động dịch vụ

```powershell
docker compose up --build -d
docker compose ps
```

Docker Compose định nghĩa hai dịch vụ:
- **db:** PostgreSQL 16, dữ liệu lưu trong Docker volume.
- **api:** FastAPI, công bố cổng 8000.

Cấu hình Compose truyền thông tin kết nối database cho API qua hostname nội bộ db và cổng 5432. Cổng PostgreSQL trên máy host được đặt bằng POSTGRES_HOST_PORT trong file .env.

Xem log khi cần:

```powershell
docker compose logs --tail 100
```

### Bước 4: Khởi tạo schema

Migration được quản lý bằng Alembic. Khi chạy lệnh migration từ máy host, cần có môi trường Python đã cài dependencies và file .env được cấu hình để kết nối đúng database:

```powershell
python -m pip install -r requirements.txt
alembic upgrade head
```

Không chạy migration từ môi trường host nếu cấu hình kết nối chưa trỏ đúng tới database đang sử dụng. Hãy kiểm tra log và trạng thái schema trước khi chạy migration để tránh thao tác nhầm database.

## 7. Địa chỉ truy cập

Với cấu hình cổng mặc định trong dự án:

| Thành phần | Địa chỉ |
|---|---|
| Giao diện demo | http://localhost:8000/ |
| Swagger UI | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |
| Health check | http://localhost:8000/health |

![Swagger UI](docs/images/api-docs.png)

![Ticket Management Interface](docs/images/ticket-interface.png)

Health check trả về trạng thái ứng dụng. Điều này không thay thế việc kiểm tra riêng kết nối database và các thao tác nghiệp vụ.

## 8. API chính

Các endpoint được đăng ký dưới tiền tố /api/v1.

| Nhóm | Endpoint | Mục đích |
|---|---|---|
| Auth | POST /api/v1/auth/login | Đăng nhập, nhận access token |
| Auth | GET /api/v1/auth/me | Lấy thông tin người dùng hiện tại |
| Users | GET /api/v1/users | Liệt kê người dùng (Admin) |
| Users | POST /api/v1/users | Tạo người dùng (Admin) |
| Users | PATCH /api/v1/users/{user_id}/status | Bật/tắt tài khoản (Admin) |
| Tickets | POST /api/v1/tickets | Tạo ticket |
| Tickets | GET /api/v1/tickets | Liệt kê ticket theo quyền; hỗ trợ status, limit, offset |
| Tickets | GET /api/v1/tickets/{ticket_id} | Xem chi tiết ticket |
| Tickets | POST /api/v1/tickets/{ticket_id}/assign | Phân công ticket |
| Tickets | POST /api/v1/tickets/{ticket_id}/transitions | Chuyển trạng thái |
| Comments | GET /api/v1/tickets/{ticket_id}/comments | Xem bình luận |
| Comments | POST /api/v1/tickets/{ticket_id}/comments | Thêm bình luận |
| Events | GET /api/v1/tickets/{ticket_id}/events | Xem lịch sử sự kiện |
| Dashboard | GET /api/v1/dashboard/summary | Lấy thống kê tổng hợp |

Swagger UI tại /docs là nguồn tham khảo trực tiếp để xem schema request/response hiện hành.

## 9. Kiểm thử

Chạy bộ kiểm thử từ thư mục gốc khi đã cài dependencies:

```powershell
python -m pytest -v
```

Bộ test hiện có tập trung vào xác thực, người dùng và ticket. Cần đọc fixture trong tests/conftest.py để xác định loại database được sử dụng khi test; kết quả test dùng SQLite không đồng nghĩa với việc đã kiểm thử tích hợp trên PostgreSQL.

![Test Results](docs/images/test-results.png)

Kết quả và số lượng test trong ảnh cần được cập nhật từ lần chạy thực tế gần nhất, không nên dùng ảnh cũ nếu kết quả đã thay đổi.

## 10. Hình ảnh minh chứng khác

### Luồng xử lý request

![Request Processing Flow](docs/images/request-processing-flow.png)

### Dịch vụ Docker

![Docker Services](docs/images/docker-services.png)

## 11. Giới hạn hiện tại và hướng phát triển

Các hướng mở rộng có thể cân nhắc trong tương lai:

- Bổ sung bộ lọc ticket theo mức ưu tiên và người phụ trách nếu cần.
- Bổ sung SLA, thời hạn xử lý và cảnh báo ticket quá hạn.
- Mở rộng dashboard và các chỉ số thời gian xử lý.
- Bổ sung kiểm thử tích hợp trực tiếp với PostgreSQL.
- Thiết lập CI để tự động chạy test khi có thay đổi.
- Hoàn thiện cấu hình production, logging và quản lý secret.

Đây là các hướng phát triển đề xuất, không phải cam kết rằng những chức năng đó đã có trong phiên bản hiện tại.
