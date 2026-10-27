# TÀI LIỆU KIẾN TRÚC HỆ THỐNG

## 1. Kiểu kiến trúc

Hệ thống sử dụng kiến trúc nguyên khối có phân chia mô-đun (*Modular Monolith*). Toàn bộ chức năng Backend chạy trong một ứng dụng FastAPI duy nhất, nhưng được chia thành các mô-đun riêng biệt theo trách nhiệm nghiệp vụ.

Cách thiết kế này phù hợp với dự án portfolio vì dễ phát triển, kiểm thử, tìm lỗi và triển khai hơn kiến trúc vi dịch vụ (*Microservices*). Khi hệ thống lớn hơn, kiến trúc có thể được điều chỉnh dựa trên nhu cầu thực tế.

## 2. Công nghệ sử dụng

- **Ngôn ngữ lập trình:** Python 3.11.
- **Framework Backend:** FastAPI, dùng để xây dựng REST API.
- **Kiểm tra dữ liệu đầu vào:** Pydantic.
- **ORM:** SQLAlchemy, hỗ trợ thao tác với cơ sở dữ liệu thông qua các đối tượng Python.
- **Hệ quản trị cơ sở dữ liệu:** PostgreSQL.
- **Quản lý thay đổi cấu trúc cơ sở dữ liệu:** Alembic.
- **Xác thực:** JWT Access Token.
- **Băm mật khẩu:** Argon2.
- **Kiểm thử tự động:** pytest, HTTPX và FastAPI TestClient.
- **Đóng gói và khởi chạy dịch vụ:** Docker và Docker Compose.
- **Giao diện demo:** HTML, CSS và JavaScript.
- **Tài liệu API:** OpenAPI được FastAPI tạo tự động.

## 3. Các thành phần của hệ thống

### 3.1. Lớp API

Tiếp nhận yêu cầu HTTP từ người dùng hoặc giao diện. Lớp này kiểm tra dữ liệu đầu vào, phối hợp với cơ chế xác thực và phân quyền, gọi các chức năng nghiệp vụ và trả kết quả qua HTTP Response.

### 3.2. Lớp nghiệp vụ

Chứa các quy tắc xử lý chính của hệ thống, bao gồm:

- Tạo và cập nhật ticket.
- Phân công ticket cho nhân viên hỗ trợ.
- Kiểm tra tính hợp lệ của việc chuyển trạng thái.
- Kiểm tra quyền thao tác trên từng ticket.
- Ghi nhận lịch sử xử lý.
- Bảo đảm các thao tác liên quan được thực hiện nhất quán.

Các quy tắc nghiệp vụ được tập trung tại lớp này thay vì viết rải rác trong các API endpoint.

### 3.3. Lớp truy cập dữ liệu

Chịu trách nhiệm thực hiện các truy vấn và thao tác lưu dữ liệu thông qua SQLAlchemy. Lớp này giúp tách biệt việc truy cập cơ sở dữ liệu khỏi các quy tắc nghiệp vụ.

### 3.4. Lớp mô hình dữ liệu

Định nghĩa các thực thể tương ứng với những bảng trong PostgreSQL, bao gồm người dùng, ticket, bình luận và sự kiện lịch sử. Lớp này cũng xác định các mối quan hệ giữa các bảng.

### 3.5. Lớp lược đồ dữ liệu

Sử dụng Pydantic để định nghĩa cấu trúc dữ liệu đầu vào và đầu ra của API.

Các lược đồ giúp kiểm tra dữ liệu, giới hạn những trường được phép cập nhật và tránh trả về thông tin nhạy cảm như mật khẩu đã băm.

### 3.6. Lớp cơ sở dữ liệu

PostgreSQL lưu trữ dữ liệu người dùng, ticket, bình luận và lịch sử xử lý. Alembic quản lý các phiên bản thay đổi cấu trúc bảng trong quá trình phát triển.

## 4. Luồng xử lý yêu cầu

Luồng xử lý cơ bản của hệ thống:

Người dùng hoặc giao diện  
→ API Router của FastAPI  
→ Xác thực và phân quyền  
→ Lớp nghiệp vụ  
→ Lớp truy cập dữ liệu  
→ PostgreSQL  
→ Trả kết quả HTTP cho người dùng.

Các quy tắc nghiệp vụ quan trọng phải được kiểm tra ở phía Backend. Không được chỉ dựa vào việc ẩn hoặc hiện nút trên giao diện để bảo vệ dữ liệu.

## 5. Các mô-đun chính

- **auth:** Đăng nhập và xác định người dùng hiện tại.
- **users:** Quản lý tài khoản và trạng thái hoạt động của người dùng.
- **tickets:** Tạo, xem, lọc, cập nhật và phân công ticket.
- **workflow:** Kiểm tra và xử lý việc chuyển trạng thái ticket.
- **comments:** Quản lý nội dung trao đổi trong ticket.
- **events:** Ghi nhận lịch sử thay đổi và người thực hiện.
- **dashboard:** Tổng hợp số liệu phục vụ thống kê.

## 6. Bảo mật

- Chỉ lưu mật khẩu dưới dạng giá trị đã được băm; không lưu mật khẩu nguyên văn.
- Lưu thông tin bí mật trong biến môi trường, không ghi trực tiếp vào mã nguồn.
- Sử dụng JWT Access Token cho các yêu cầu cần xác thực.
- Kiểm tra quyền theo vai trò và quyền truy cập từng tài nguyên ở Backend.
- Kiểm tra dữ liệu đầu vào trước khi xử lý.
- Không tin tưởng ID người tạo, người thực hiện hoặc người phụ trách do client tự gửi mà không kiểm tra quyền và tính hợp lệ.
- Không trả về thông tin nhạy cảm hoặc chi tiết lỗi nội bộ không cần thiết.
- Sử dụng giao dịch cơ sở dữ liệu cho những thao tác liên quan cần thành công hoặc thất bại đồng thời.

## 7. Triển khai hệ thống

Docker Compose quản lý các dịch vụ của dự án, trước mắt gồm:

- Backend API chạy bằng FastAPI.
- PostgreSQL lưu trữ dữ liệu.

PostgreSQL sử dụng Docker volume để dữ liệu không bị mất khi container được tạo lại trong những trường hợp thông thường. Backend kết nối đến PostgreSQL thông qua tên dịch vụ trên mạng nội bộ của Docker Compose.

Alembic được sử dụng để quản lý các thay đổi cấu trúc cơ sở dữ liệu.

## 8. Chiến lược kiểm thử

### 8.1. Kiểm thử đơn vị

Kiểm tra các quy tắc chuyển trạng thái, điều kiện phân quyền và các hàm nghiệp vụ độc lập.

### 8.2. Kiểm thử API

Kiểm tra đăng nhập, tạo và xem ticket, phân công, chuyển trạng thái, bình luận và lọc dữ liệu.

### 8.3. Kiểm thử tích hợp

Kiểm tra sự phối hợp giữa API, lớp nghiệp vụ và PostgreSQL, bao gồm việc lưu dữ liệu và xử lý giao dịch.

### 8.4. Kiểm thử trường hợp lỗi

Bao gồm dữ liệu đầu vào không hợp lệ, chuyển trạng thái không được phép, truy cập không có quyền, token không hợp lệ và lỗi trong quá trình ghi dữ liệu.

## 9. Nguyên tắc phát triển

- Ưu tiên mã nguồn đơn giản, rõ ràng và dễ bảo trì.
- Mỗi mô-đun đảm nhiệm một nhóm chức năng cụ thể.
- Tách mô hình cơ sở dữ liệu khỏi lược đồ API.
- Sử dụng migration thay vì phụ thuộc hoàn toàn vào việc tự động tạo bảng khi khởi động ứng dụng.
- Tách dữ liệu kiểm thử và dữ liệu demo khỏi logic nghiệp vụ.
- Kiểm thử các quy tắc quan trọng trước khi bổ sung chức năng mới.
- Chỉ bổ sung công nghệ khi có lý do rõ ràng từ yêu cầu dự án.
