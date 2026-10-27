# Service Desk Issue Tracking

## 1. Giới thiệu dự án

### 1.1. Tổng quan

**Service Desk Issue Tracking** là hệ thống quản lý yêu cầu hỗ trợ kỹ thuật, được xây dựng nhằm hỗ trợ doanh nghiệp tiếp nhận, theo dõi và xử lý các sự cố hoặc yêu cầu từ nhân viên.

Trong môi trường doanh nghiệp, các yêu cầu hỗ trợ như lỗi phần mềm, sự cố thiết bị hoặc vấn đề về tài khoản cần được ghi nhận và quản lý tập trung. Nếu xử lý thông qua các kênh trao đổi riêng lẻ, việc theo dõi tiến độ, phân công trách nhiệm và tra cứu lịch sử có thể gặp nhiều khó khăn.

Dự án giải quyết vấn đề này bằng cách xây dựng một hệ thống quản lý ticket, cho phép người dùng tạo yêu cầu, nhân viên hỗ trợ tiếp nhận và xử lý, đồng thời lưu lại lịch sử thay đổi để phục vụ việc theo dõi và kiểm tra.

### 1.2. Mục tiêu

- Xây dựng API phục vụ việc tạo, truy vấn và quản lý ticket.
- Quản lý người dùng và phân quyền theo vai trò.
- Hỗ trợ phân công nhân viên phụ trách và cập nhật trạng thái xử lý.
- Lưu trữ bình luận và lịch sử thay đổi của ticket.
- Áp dụng PostgreSQL để quản lý dữ liệu có cấu trúc.
- Sử dụng Docker Compose để triển khai môi trường chạy ứng dụng.
- Xây dựng bộ kiểm thử nhằm kiểm tra tính đúng đắn của các chức năng và quy tắc nghiệp vụ.

### 1.3. Các chức năng chính

| Nhóm chức năng | Mô tả |
|---|---|
| Xác thực | Đăng nhập và xác định người dùng hiện tại bằng JWT |
| Quản lý người dùng | Quản lý thông tin và vai trò người dùng |
| Quản lý ticket | Tạo, xem, lọc và theo dõi yêu cầu hỗ trợ |
| Phân công | Gán ticket cho nhân viên hỗ trợ |
| Quản lý trạng thái | Theo dõi quá trình xử lý ticket |
| Bình luận | Trao đổi thông tin trong từng ticket |
| Lịch sử hoạt động | Ghi nhận các thay đổi quan trọng để phục vụ kiểm tra |
| Thống kê | Tổng hợp thông tin phục vụ theo dõi tình hình xử lý yêu cầu |

### 1.4. Đối tượng sử dụng

Hệ thống được thiết kế với ba vai trò chính:

- **EMPLOYEE:** tạo yêu cầu hỗ trợ và theo dõi các ticket của mình.
- **SUPPORT_AGENT:** tiếp nhận, xử lý và cập nhật các ticket được phân công.
- **ADMIN:** quản lý hệ thống và thực hiện các thao tác quản trị theo quyền được cấp.

Các quyền truy cập cụ thể được kiểm soát ở phía backend nhằm hạn chế việc người dùng thực hiện những thao tác không được phép.

## 2. Kiến trúc hệ thống và công nghệ sử dụng

### 2.1. Kiến trúc hệ thống

Dự án sử dụng kiến trúc **Modular Monolith**. Các module backend được tổ chức theo trách nhiệm riêng nhưng cùng chạy trong một ứng dụng FastAPI.

Kiến trúc này phù hợp với quy mô dự án vì dễ phát triển, kiểm thử, bảo trì và triển khai trên môi trường cục bộ.

![System Architecture](docs/images/system-architecture.png)


Trong đó:

- **API Layer:** tiếp nhận HTTP request, kiểm tra dữ liệu đầu vào và trả về HTTP response.
- **Authentication & Authorization:** xác thực người dùng và kiểm tra quyền thực hiện thao tác.
- **Service Layer:** xử lý quy tắc nghiệp vụ như phân công ticket, chuyển trạng thái và ghi nhận lịch sử.
- **Repository / Data Access Layer:** thực hiện truy vấn và thao tác dữ liệu thông qua SQLAlchemy.
- **Database Layer:** lưu trữ thông tin người dùng, ticket, bình luận và lịch sử hoạt động.

Việc tách các tầng giúp hạn chế đặt toàn bộ logic nghiệp vụ trực tiếp trong các API endpoint, đồng thời thuận tiện hơn khi kiểm thử từng thành phần.



### 2.2. Công nghệ sử dụng

| Công nghệ | Vai trò |
|---|---|
| Python 3.11 | Ngôn ngữ lập trình backend |
| FastAPI | Xây dựng REST API |
| Pydantic | Kiểm tra và chuẩn hóa dữ liệu request/response |
| SQLAlchemy | ORM và thao tác với cơ sở dữ liệu |
| PostgreSQL 16 | Hệ quản trị cơ sở dữ liệu quan hệ |
| Alembic | Quản lý phiên bản và migration cơ sở dữ liệu |
| JWT | Xác thực thông qua access token |
| Argon2 | Băm mật khẩu trước khi lưu trữ |
| pytest | Xây dựng và chạy kiểm thử tự động |
| HTTPX / FastAPI TestClient | Kiểm thử API |
| Docker | Đóng gói các thành phần chạy ứng dụng |
| Docker Compose | Khởi động và quản lý các dịch vụ |
| HTML, CSS, JavaScript | Xây dựng giao diện demo |
| OpenAPI / Swagger UI | Mô tả và tương tác với API |

### 2.3. Các nguyên tắc thiết kế

Dự án áp dụng một số nguyên tắc cơ bản:

- Phân chia module theo chức năng và trách nhiệm.
- Tách database model khỏi schema dùng cho API.
- Kiểm tra quyền truy cập tại backend thay vì chỉ dựa vào giao diện.
- Không lưu mật khẩu dạng văn bản thuần.
- Sử dụng biến môi trường cho cấu hình nhạy cảm.
- Dùng transaction khi một thao tác nghiệp vụ cần cập nhật nhiều bản ghi liên quan.
- Sử dụng migration để quản lý thay đổi cấu trúc cơ sở dữ liệu.

## 3. Cấu trúc thư mục dự án

Cấu trúc thư mục được tổ chức để tách biệt mã nguồn, cấu hình, tài liệu và kiểm thử.

```text
Service-Desk-Issue-Tracking/
├── app/                                    # Thư mục nguồn chính của ứng dụng Backend (FastAPI)
│   ├── api/                                # Các điểm truy cập API
│   │   ├── deps.py                         # Phụ thuộc chung (Dependencies: xác thực token, kết nối DB)
│   │   └── v1/                             # Chứa các tệp Router định nghĩa API phiên bản 1
│   ├── core/                               # Cấu hình lõi (biến môi trường, cài đặt bảo mật JWT, hash mật khẩu)
│   ├── db/                                 # Cấu hình kết nối và cơ sở dữ liệu SQLAlchemy
│   ├── models/                             # Định nghĩa các bản mẫu ORM Models (bảng CSDL)
│   ├── schemas/                            # Pydantic Schemas (Validate dữ liệu vào/ra cho API)
│   │   ├── auth.py                         # Schema cho thông tin xác thực/token
│   │   ├── dashboard.py                    # Schema cho dữ liệu bảng điều khiển
│   │   ├── ticket.py                       # Schema cho yêu cầu/sự cố (ticket)
│   │   └── user.py                         # Schema cho thông tin người dùng
│   ├── services/                           # Tầng xử lý logic nghiệp vụ (Business Logic)
│   │   └── ticket_service.py               # Logic nghiệp vụ xử lý các thao tác trên ticket
│   └── main.py                             # Tệp chính khởi chạy ứng dụng FastAPI
├── docs/                                   # Tài liệu dự án và hình ảnh
│   ├── images/                             # Lưu trữ hình ảnh minh họa hệ thống, ERD, giao diện
│   ├── architecture.md                     # Tài liệu thiết kế kiến trúc hệ thống
│   ├── erd.md                              # Tài liệu mô hình sơ đồ quan hệ CSDL
│   └── requirements.md                     # Tài liệu phân tích yêu cầu bài toán
├── frontend/                               # Giao diện web phía client (Single Page Application)
├── migrations/                             # Thư mục quản lý các phiên bản dịch chuyển CSDL (Alembic)
│   ├── versions/                           # Các tệp script cập nhật cấu trúc bảng CSDL
│   ├── env.py                              # Môi trường chạy migration
│   ├── README                              # Tài liệu hướng dẫn sử dụng migration
│   └── script.py.mako                      # Template tạo script migration mới
├── scripts/                                # Các kịch bản phụ trợ
├── tests/                                  # Bộ kiểm thử tự động (Automated Tests với Pytest)
│   ├── conftest.py                         # Thiết lập các fixture mẫu cho việc kiểm thử
│   ├── test_auth.py                        # Kiểm thử chức năng xác thực
│   ├── test_tickets.py                     # Kiểm thử quy trình quản lý ticket
│   └── test_users.py                       # Kiểm thử chức năng quản lý người dùng
├── docker-compose.yml                      # Tệp cấu hình khởi chạy các dịch vụ bằng Docker Compose
├── Dockerfile                              # Tệp chỉ dẫn đóng gói ứng dụng Backend thành Docker Container
└── README.md                               # Trang tài liệu tổng quan giới thiệu dự án trên GitHub
```

## 4. Thiết kế cơ sở dữ liệu

### 4.1. Tổng quan

Cơ sở dữ liệu sử dụng PostgreSQL và gồm bốn bảng nghiệp vụ cốt lõi:

- `users`: lưu thông tin người dùng.
- `tickets`: lưu các yêu cầu hỗ trợ.
- `comments`: lưu nội dung trao đổi trong ticket.
- `ticket_events`: lưu lịch sử các sự kiện và thay đổi quan trọng.

Các khóa chính sử dụng UUID. Những trường thời gian sử dụng kiểu dữ liệu có thông tin múi giờ để hỗ trợ lưu trữ thời điểm tạo và cập nhật dữ liệu.

### 4.2. Các bảng chính

**Bảng `users`**

Lưu thông tin người dùng, bao gồm mã định danh, họ tên, email, mật khẩu đã băm, vai trò, trạng thái hoạt động và thời gian tạo/cập nhật.

Email phải là duy nhất. Mật khẩu được lưu dưới dạng hash, không lưu trực tiếp mật khẩu gốc.

**Bảng `tickets`**

Lưu thông tin yêu cầu hỗ trợ, bao gồm mã ticket, tiêu đề, mô tả, danh mục, mức độ ưu tiên, trạng thái, người tạo, người được phân công và các mốc thời gian xử lý.

Các trạng thái được sử dụng gồm:

- `OPEN`
- `IN_PROGRESS`
- `RESOLVED`
- `CLOSED`

Các mức độ ưu tiên gồm `LOW`, `MEDIUM`, `HIGH` và `URGENT`.

`requester_id` xác định người tạo yêu cầu; `assignee_id` xác định nhân viên được phân công xử lý. Hai trường này cùng tham chiếu đến bảng `users`.

**Bảng `comments`**

Lưu các bình luận thuộc một ticket, bao gồm mã ticket, người viết, nội dung và thời gian tạo.

**Bảng `ticket_events`**

Lưu lại các sự kiện quan trọng, chẳng hạn như tạo ticket, thay đổi người phụ trách, thay đổi trạng thái hoặc mức độ ưu tiên. Các trường `old_value` và `new_value` cho phép ghi lại thông tin trước và sau thay đổi dưới dạng JSONB.

### 4.3. Quan hệ giữa các bảng

- Một người dùng có thể tạo nhiều ticket.
- Một nhân viên hỗ trợ có thể được phân công nhiều ticket.
- Một ticket có thể có nhiều bình luận.
- Một người dùng có thể viết nhiều bình luận.
- Một ticket có thể có nhiều sự kiện lịch sử.
- Một người dùng có thể thực hiện nhiều sự kiện được ghi nhận.

Các khóa ngoại giúp đảm bảo tính toàn vẹn tham chiếu giữa các bảng. Quyền xem và chỉnh sửa dữ liệu vẫn cần được kiểm tra tại tầng nghiệp vụ.

### 4.4. Ràng buộc và tính toàn vẹn dữ liệu

Thiết kế cơ sở dữ liệu chú trọng các điểm sau:

- Email người dùng và mã ticket phải duy nhất.
- Các khóa ngoại phải tham chiếu đến bản ghi hợp lệ.
- Vai trò, trạng thái và mức độ ưu tiên phải thuộc tập giá trị được cho phép.
- Các trường thường dùng để lọc ticket cần được cân nhắc đánh chỉ mục.
- Tạo ticket và ghi sự kiện khởi tạo phải thuộc cùng một transaction.
- Thay đổi trạng thái hoặc người phụ trách và ghi lịch sử tương ứng phải được thực hiện nhất quán.


![Entity Relationship Diagram](docs/images/erd.png)

## 5. Hướng dẫn khởi động dự án

### 5.1. Yêu cầu môi trường

Trước khi chạy dự án, cần chuẩn bị:

- Python 3.11.
- Docker Desktop và Docker Compose.
- Git nếu cần tải mã nguồn từ repository.

Các lệnh bên dưới được thực hiện tại thư mục gốc của dự án bằng PowerShell.

### 5.2. Lấy mã nguồn

Nếu dự án đã có trên GitHub, chạy:

```powershell
git clone <REPOSITORY_URL>
cd Service-Desk-Issue-Tracking
```

Thay `<REPOSITORY_URL>` bằng địa chỉ repository thực tế.

Nếu mã nguồn đã có trên máy, chỉ cần mở thư mục dự án trong VS Code và mở terminal tại thư mục gốc.

### 5.3. Cấu hình biến môi trường

Kiểm tra các biến môi trường mà ứng dụng yêu cầu, đặc biệt là:

- Chuỗi kết nối PostgreSQL.
- Khóa bí mật dùng để ký JWT.
- Các thông số xác thực cần thiết khác.

Nếu repository có tệp `.env.example`, sao chép thành `.env`:

```powershell
Copy-Item .env.example .env
```

Sau đó chỉnh các giá trị trong `.env` theo cấu hình cục bộ.

Không đưa `.env`, mật khẩu hoặc khóa bí mật thực tế lên GitHub.

### 5.4. Khởi động bằng Docker Compose

Tại thư mục chứa tệp Compose thực tế, chạy:

```powershell
docker compose up --build -d
```

Lệnh trên yêu cầu Docker Compose đọc cấu hình dịch vụ, build image nếu cần và khởi động các container ở chế độ nền.

Kiểm tra trạng thái dịch vụ:

```powershell
docker compose ps
```

Xem log khi cần kiểm tra lỗi:

```powershell
docker compose logs --tail 100
```

Nếu tệp Compose có tên khác hoặc nằm trong thư mục con, cần chỉ định đúng đường dẫn bằng tùy chọn `-f`.

### 5.5. Khởi tạo cơ sở dữ liệu

Sau khi dịch vụ database đã sẵn sàng, chạy migration bằng Alembic từ môi trường Python đã được cấu hình:

```powershell
alembic upgrade head
```

Lệnh này áp dụng các migration đang có để đưa cấu trúc cơ sở dữ liệu về phiên bản mới nhất của dự án.

Chỉ chạy lệnh sau khi đã cài các thư viện cần thiết và cấu hình kết nối database đúng với môi trường hiện tại.

### 5.6. Cài thư viện và chạy backend thủ công

Nếu muốn chạy backend ngoài Docker, có thể tạo môi trường ảo:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Sau khi hoàn tất cấu hình môi trường, khởi chạy ứng dụng bằng Uvicorn với module entry point thực tế của repository. Ví dụ, nếu ứng dụng được khai báo tại `app.main:app`:

```powershell
uvicorn app.main:app --reload
```

Không cần chạy backend thủ công nếu Docker Compose đã quản lý dịch vụ API.

### 5.7. Kiểm tra trạng thái hoạt động

Sau khi khởi động, kiểm tra:

- Container của API và PostgreSQL đã chạy.
- Kết nối cơ sở dữ liệu hoạt động.
- Migration đã được áp dụng thành công.
- API có thể truy cập từ trình duyệt hoặc công cụ gửi HTTP request.

Nếu gặp lỗi, kiểm tra log của dịch vụ liên quan trước khi thay đổi cấu hình.

## 6. Truy cập ứng dụng

Sau khi hệ thống khởi động thành công, các địa chỉ truy cập phụ thuộc vào cổng được cấu hình trong Docker Compose hoặc cấu hình chạy backend.

### 6.1. Giao diện API

![Swagger UI](docs/images/api-docs.png)

Swagger UI cho phép xem danh sách endpoint, cấu trúc request/response và gửi thử các request trực tiếp từ trình duyệt.

**ReDoc**

[Chèn link ReDoc tại đây]

ReDoc cung cấp cách trình bày tài liệu API theo cấu trúc, thuận tiện để tra cứu các endpoint và schema.

### 6.2. Giao diện demo

![Ticket Management Interface](docs/images/ticket-interface.png)

Giao diện demo giúp người dùng quan sát cách hệ thống hiển thị và thao tác với các ticket. Địa chỉ cụ thể cần căn cứ vào cổng được công bố trong cấu hình triển khai.

## 7. Hình ảnh minh họa

Phần này cung cấp hình ảnh minh chứng cho kiến trúc, thiết kế dữ liệu, giao diện và kết quả kiểm thử của dự án. Các hình ảnh được đặt trong thư mục `docs/images/` để thuận tiện quản lý và hiển thị trong README.


### 7.1. Luồng xử lý yêu cầu

Hình ảnh mô tả quá trình một request đi từ client qua các tầng xử lý, truy cập cơ sở dữ liệu và trả về response.

![Luồng xử lý yêu cầu](docs/images/request-processing-flow.png)


### 7.2 . Trạng thái các dịch vụ Docker

Hình ảnh minh chứng trạng thái hoạt động của các container trong môi trường triển khai cục bộ.

![Trạng thái các dịch vụ Docker](docs/images/docker-services.png)

### 7.3. Kết quả kiểm thử tự động

Dự án sử dụng `pytest` để kiểm tra các chức năng và quy tắc nghiệp vụ. Các bài kiểm thử có thể bao gồm xác thực, thao tác với ticket, phân quyền, kiểm tra trạng thái và xử lý các trường hợp dữ liệu không hợp lệ.

Kết quả kiểm thử được sử dụng để phát hiện lỗi và xác nhận hành vi của hệ thống trước khi hoàn thiện dự án.

![Kết quả kiểm thử tự động](docs/images/test-results.png)


## 8. Hướng phát triển

Trong các phiên bản tiếp theo, dự án có thể được mở rộng theo các hướng sau:

- **Hoàn thiện phân quyền:** bổ sung và kiểm tra đầy đủ quyền truy cập theo vai trò, người tạo ticket và nhân viên được phân công.
- **Mở rộng nghiệp vụ:** bổ sung SLA, thời hạn xử lý và cơ chế cảnh báo ticket quá hạn.
- **Cải thiện thống kê:** xây dựng dashboard theo trạng thái, mức độ ưu tiên, danh mục và thời gian xử lý.
- **Nâng cao kiểm thử:** bổ sung kiểm thử tích hợp với PostgreSQL thực tế, kiểm thử lỗi và kiểm thử các trường hợp đồng thời.
- **Tăng cường bảo mật:** bổ sung giới hạn tần suất request, chính sách quản lý token và các biện pháp bảo vệ API phù hợp.
- **Tự động hóa triển khai:** xây dựng CI để tự động chạy kiểm thử và kiểm tra chất lượng mã nguồn khi có thay đổi.
- **Cải thiện giao diện:** hoàn thiện trải nghiệm người dùng, thông báo lỗi và khả năng theo dõi tiến độ xử lý ticket.
- **Triển khai môi trường thực tế:** xây dựng cấu hình production riêng, quản lý secrets và thiết lập logging, monitoring phù hợp.

## Kết luận

Service Desk Issue Tracking là dự án thực hành xây dựng backend có cấu trúc rõ ràng, kết hợp API, cơ sở dữ liệu quan hệ, xác thực, phân quyền, kiểm thử tự động và container hóa.

Thông qua dự án, các kiến thức về thiết kế hệ thống, quản lý dữ liệu, xử lý nghiệp vụ và triển khai ứng dụng được kết hợp trong một bài toán gần với nhu cầu hỗ trợ kỹ thuật tại doanh nghiệp.
