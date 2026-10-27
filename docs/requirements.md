# Service Desk & Issue Tracking System

## 1. Giới thiệu

Service Desk & Issue Tracking System là hệ thống hỗ trợ nhân viên gửi yêu cầu hỗ trợ IT, theo dõi tình trạng xử lý và trao đổi với nhân viên hỗ trợ.

Mục tiêu là xây dựng một Backend API có xác thực, phân quyền, quản lý vòng đời ticket và lưu lại lịch sử xử lý.

## 2. Đối tượng sử dụng

- **Employee:** Tạo ticket, xem ticket của mình và trao đổi trong ticket.
- **Support Agent:** Xem ticket được giao, cập nhật trạng thái và phản hồi.
- **Admin:** Quản lý người dùng, xem toàn bộ ticket và phân công ticket cho Support Agent.

## 3. Chức năng chính

### 3.1. Tài khoản và xác thực

- Đăng nhập bằng email và mật khẩu.
- Trả về access token khi đăng nhập thành công.
- Xác định người dùng hiện tại từ token.
- Phân quyền theo vai trò Employee, Support Agent và Admin.
- Mật khẩu phải được băm trước khi lưu vào cơ sở dữ liệu.

### 3.2. Quản lý ticket

- Employee hoặc Admin tạo ticket gồm tiêu đề, mô tả, danh mục và mức độ ưu tiên; Support Agent không được tạo ticket trong phiên bản hiện tại.
- Người tạo được xác định từ tài khoản đăng nhập.
- Người dùng xem danh sách ticket theo quyền của mình.
- API danh sách ticket hỗ trợ lọc theo trạng thái (`status`) và phân trang bằng `limit`, `offset`. Chưa có tham số API lọc riêng theo mức ưu tiên hoặc người phụ trách.
- Admin phân công ticket cho Support Agent.
- Support Agent cập nhật trạng thái ticket được giao.

### 3.3. Trạng thái ticket

Ticket có bốn trạng thái:

- `OPEN`: Mới được tạo.
- `IN_PROGRESS`: Đang xử lý.
- `RESOLVED`: Đã xử lý xong.
- `CLOSED`: Đã đóng.

Luồng trạng thái hợp lệ:

`OPEN → IN_PROGRESS → RESOLVED → CLOSED`

Nếu cần xử lý lại, ticket `RESOLVED` có thể quay về `IN_PROGRESS`. Các chuyển đổi không hợp lệ phải bị từ chối.

### 3.4. Bình luận và lịch sử

- Người dùng có quyền truy cập ticket được phép trao đổi theo quy tắc phân quyền.
- Không cho phép thêm bình luận vào ticket đã `CLOSED`.
- Hệ thống ghi sự kiện tạo ticket (`TICKET_CREATED`), phân công (`TICKET_ASSIGNED`), thay đổi trạng thái (`STATUS_CHANGED`) và thêm bình luận (`COMMENT_ADDED`).
- Mỗi sự kiện phải có người thực hiện và thời điểm xảy ra.

### 3.5. Thống kê

Cung cấp API thống kê số ticket theo trạng thái và mức độ ưu tiên để phục vụ dashboard.

## 4. Quy tắc nghiệp vụ

1. Người dùng chưa đăng nhập không được truy cập các API yêu cầu xác thực.
2. Employee chỉ được xem ticket do mình tạo.
3. Chỉ Admin được phân công ticket.
4. Support Agent chỉ được cập nhật ticket đã được giao cho mình.
5. Backend tự xác định người tạo và người thực hiện từ tài khoản đăng nhập, không tin các ID do client tự gửi lên.
6. Chỉ cho phép các chuyển đổi trạng thái hợp lệ.
7. Thay đổi dữ liệu quan trọng phải được ghi vào lịch sử.
8. Dữ liệu ticket và lịch sử liên quan phải nhất quán khi xảy ra lỗi.
9. Tài khoản bị vô hiệu hóa không được tiếp tục sử dụng hệ thống.
10. API phải kiểm tra dữ liệu đầu vào và trả về mã lỗi phù hợp.

## 5. Phạm vi phiên bản đầu tiên

Bao gồm:

- Xác thực và phân quyền.
- Tạo và xem ticket; lọc theo trạng thái, phân trang; cập nhật thông qua thao tác phân công và chuyển trạng thái (chưa có API sửa tự do các trường ticket).
- Phân công ticket.
- Chuyển trạng thái.
- Bình luận và lịch sử xử lý.
- API thống kê cơ bản.
- Kiểm thử tự động.
- Giao diện demo tối giản.
- Docker Compose và tài liệu hướng dẫn chạy dự án.

Không bao gồm:

- Gửi email hoặc SMS.
- Tích hợp hệ thống doanh nghiệp bên ngoài.
- AI tự động phân loại ticket.
- Triển khai cloud trong phiên bản đầu tiên.

## 6. Tiêu chí nghiệm thu

- Khởi chạy được ứng dụng và PostgreSQL bằng Docker Compose.
- Có hướng dẫn tạo và cập nhật cấu trúc cơ sở dữ liệu.
- Đăng nhập và phân quyền hoạt động đúng.
- Các thao tác ticket tuân thủ quy tắc nghiệp vụ.
- Người dùng không thể truy cập dữ liệu ngoài quyền hạn.
- Lịch sử xử lý được lưu chính xác.
- Các trường hợp thành công và thất bại quan trọng đều có kiểm thử.
- API có tài liệu tương tác tại `/docs`.
- README có hướng dẫn cài đặt, chạy, kiểm thử và minh họa dự án.
