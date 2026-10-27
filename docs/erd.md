# Thiết kế cơ sở dữ liệu — ERD

## 1. Tổng quan

Hệ thống Service Desk & Issue Tracking sử dụng bốn bảng nghiệp vụ chính:

1. `users`: Lưu thông tin người dùng.
2. `tickets`: Lưu thông tin yêu cầu hỗ trợ.
3. `comments`: Lưu bình luận của người dùng.
4. `ticket_events`: Lưu lịch sử các sự kiện liên quan đến yêu cầu hỗ trợ.

Các khóa chính sử dụng kiểu UUID. Các cột thời gian sử dụng kiểu `TIMESTAMPTZ` (timestamp có thông tin múi giờ).

Database còn có bảng `alembic_version` để Alembic quản lý phiên bản migration. Bảng này không thuộc ERD nghiệp vụ chính.

## 2. Bảng `users` — Người dùng

Lưu thông tin nhân viên, nhân viên hỗ trợ và quản trị viên.

| Cột | Kiểu dữ liệu | Ràng buộc |
|---|---|---|
| `id` | UUID | Khóa chính, NOT NULL |
| `full_name` | VARCHAR(120) | NOT NULL |
| `email` | VARCHAR(255) | NOT NULL, UNIQUE |
| `password_hash` | VARCHAR | NOT NULL |
| `role` | VARCHAR(30) | NOT NULL, CHECK |
| `is_active` | BOOLEAN | NOT NULL, mặc định TRUE |
| `created_at` | TIMESTAMPTZ | NOT NULL, mặc định `now()` |
| `updated_at` | TIMESTAMPTZ | NOT NULL, mặc định `now()` |

Các vai trò hợp lệ:

- `EMPLOYEE`: Nhân viên.
- `SUPPORT_AGENT`: Nhân viên hỗ trợ.
- `ADMIN`: Quản trị viên.

Database có chỉ mục UNIQUE `ix_users_email` trên cột `email`, bảo đảm các email không trùng nhau.

Cột `password_hash` lưu mật khẩu đã được băm, không lưu mật khẩu dạng văn bản thuần.

## 3. Bảng `tickets` — Yêu cầu hỗ trợ

Lưu thông tin yêu cầu hỗ trợ, mức độ ưu tiên, trạng thái xử lý và người phụ trách.

| Cột | Kiểu dữ liệu | Ràng buộc |
|---|---|---|
| `id` | UUID | Khóa chính, NOT NULL |
| `ticket_number` | VARCHAR(20) | NOT NULL, UNIQUE |
| `title` | VARCHAR(200) | NOT NULL |
| `description` | TEXT | NOT NULL |
| `category` | VARCHAR(50) | NOT NULL |
| `priority` | VARCHAR(20) | NOT NULL, CHECK |
| `status` | VARCHAR(20) | NOT NULL, CHECK, mặc định `OPEN` |
| `requester_id` | UUID | NOT NULL, FK → `users.id` |
| `assignee_id` | UUID | Có thể NULL, FK → `users.id` |
| `created_at` | TIMESTAMPTZ | NOT NULL, mặc định `now()` |
| `updated_at` | TIMESTAMPTZ | NOT NULL, mặc định `now()` |
| `resolved_at` | TIMESTAMPTZ | Có thể NULL |
| `closed_at` | TIMESTAMPTZ | Có thể NULL |

Các mức độ ưu tiên hợp lệ:

- `LOW`: Thấp.
- `MEDIUM`: Trung bình.
- `HIGH`: Cao.
- `URGENT`: Khẩn cấp.

Các trạng thái hợp lệ:

- `OPEN`: Mới tạo.
- `IN_PROGRESS`: Đang xử lý.
- `RESOLVED`: Đã giải quyết.
- `CLOSED`: Đã đóng.

Database có CHECK constraint giới hạn các giá trị hợp lệ của `priority` và `status`.

Ý nghĩa các cột quan trọng:

- `ticket_number`: Mã yêu cầu hỗ trợ, có giá trị duy nhất.
- `requester_id`: Người tạo yêu cầu.
- `assignee_id`: Người được giao xử lý; có thể NULL nếu chưa được phân công.
- `resolved_at`: Thời điểm giải quyết yêu cầu.
- `closed_at`: Thời điểm đóng yêu cầu.

Cột `category` lưu trực tiếp danh mục dưới dạng `VARCHAR(50)`. Database hiện tại không có bảng `categories` riêng.

## 4. Bảng `comments` — Bình luận

Lưu nội dung trao đổi trong từng yêu cầu hỗ trợ.

| Cột | Kiểu dữ liệu | Ràng buộc |
|---|---|---|
| `id` | UUID | Khóa chính, NOT NULL |
| `ticket_id` | UUID | NOT NULL, FK → `tickets.id` |
| `author_id` | UUID | NOT NULL, FK → `users.id` |
| `body` | TEXT | NOT NULL |
| `created_at` | TIMESTAMPTZ | NOT NULL, mặc định `now()` |

Mỗi bình luận thuộc về một yêu cầu hỗ trợ và có một người viết.

Một yêu cầu có thể có nhiều bình luận. Một người dùng cũng có thể viết nhiều bình luận.

## 5. Bảng `ticket_events` — Lịch sử sự kiện

Lưu lại các sự kiện quan trọng để theo dõi quá trình xử lý yêu cầu hỗ trợ.

| Cột | Kiểu dữ liệu | Ràng buộc |
|---|---|---|
| `id` | UUID | Khóa chính, NOT NULL |
| `ticket_id` | UUID | NOT NULL, FK → `tickets.id` |
| `actor_id` | UUID | NOT NULL, FK → `users.id` |
| `event_type` | VARCHAR(40) | NOT NULL |
| `old_value` | JSONB | Có thể NULL |
| `new_value` | JSONB | Có thể NULL |
| `created_at` | TIMESTAMPTZ | NOT NULL, mặc định `now()` |

Ý nghĩa các cột:

- `ticket_id`: Yêu cầu phát sinh sự kiện.
- `actor_id`: Người thực hiện thao tác.
- `event_type`: Loại sự kiện.
- `old_value`: Giá trị trước khi thay đổi.
- `new_value`: Giá trị sau khi thay đổi.
- `created_at`: Thời điểm ghi nhận sự kiện.

Ví dụ về các loại sự kiện ở cấp ứng dụng:

- `TICKET_CREATED`: Tạo yêu cầu.
- `ASSIGNEE_CHANGED`: Thay đổi người phụ trách.
- `STATUS_CHANGED`: Thay đổi trạng thái.
- `PRIORITY_CHANGED`: Thay đổi mức độ ưu tiên.

Các giá trị trên là ví dụ nghiệp vụ; database hiện tại chưa được xác nhận có CHECK constraint giới hạn `event_type` vào một danh sách cố định.

Các sự kiện lịch sử nên được ghi thêm thay vì chỉnh sửa trong quá trình vận hành thông thường.

## 6. Quan hệ giữa các bảng

Database có sáu khóa ngoại đã được xác minh.

| Bảng nguồn | Cột khóa ngoại | Bảng đích | Ý nghĩa |
|---|---|---|---|
| `tickets` | `requester_id` | `users.id` | Người tạo yêu cầu |
| `tickets` | `assignee_id` | `users.id` | Người được giao xử lý |
| `comments` | `ticket_id` | `tickets.id` | Bình luận thuộc yêu cầu |
| `comments` | `author_id` | `users.id` | Người viết bình luận |
| `ticket_events` | `ticket_id` | `tickets.id` | Sự kiện thuộc yêu cầu |
| `ticket_events` | `actor_id` | `users.id` | Người thực hiện sự kiện |

Diễn giải:

- Một người dùng có thể tạo nhiều yêu cầu hỗ trợ.
- Một người dùng có thể được giao xử lý nhiều yêu cầu.
- Một yêu cầu có thể có nhiều bình luận.
- Một người dùng có thể viết nhiều bình luận.
- Một yêu cầu có thể có nhiều sự kiện lịch sử.
- Một người dùng có thể thực hiện nhiều thao tác được ghi nhận.

Hai quan hệ từ `tickets` đến `users` có ý nghĩa khác nhau: người yêu cầu và người được giao xử lý.

Do `assignee_id` cho phép NULL, một yêu cầu có thể chưa được phân công.

## 7. Ràng buộc dữ liệu

Các ràng buộc đã xác minh:

- Bốn bảng nghiệp vụ đều có khóa chính trên cột `id`.
- Có sáu khóa ngoại giữa các bảng.
- `users.email` có chỉ mục UNIQUE `ix_users_email`.
- `tickets.ticket_number` có ràng buộc UNIQUE.
- `users.role` có CHECK constraint giới hạn vai trò.
- `tickets.priority` có CHECK constraint giới hạn mức ưu tiên.
- `tickets.status` có CHECK constraint giới hạn trạng thái.
- Các cột bắt buộc có ràng buộc NOT NULL.
- `users.is_active` mặc định TRUE.
- `tickets.status` mặc định `OPEN`.
- Các cột thời gian được liệt kê trong thiết kế có giá trị mặc định `now()` theo kết quả kiểm tra database.

Lưu ý: `DEFAULT now()` chỉ cung cấp giá trị mặc định khi chèn bản ghi nếu không truyền giá trị khác. Nó không tự động cập nhật `updated_at` mỗi khi bản ghi được sửa.

## 8. Chỉ mục

Đã xác minh 12 chỉ mục trên bốn bảng nghiệp vụ.

| Bảng | Tên chỉ mục | Cột | Loại |
|---|---|---|---|
| `users` | `users_pkey` | `id` | UNIQUE, khóa chính |
| `users` | `ix_users_email` | `email` | UNIQUE |
| `tickets` | `tickets_pkey` | `id` | UNIQUE, khóa chính |
| `tickets` | `tickets_ticket_number_key` | `ticket_number` | UNIQUE |
| `tickets` | `ix_tickets_assignee_id` | `assignee_id` | Chỉ mục thường |
| `tickets` | `ix_tickets_created_at` | `created_at` | Chỉ mục thường |
| `tickets` | `ix_tickets_requester_id` | `requester_id` | Chỉ mục thường |
| `tickets` | `ix_tickets_status` | `status` | Chỉ mục thường |
| `comments` | `comments_pkey` | `id` | UNIQUE, khóa chính |
| `comments` | `ix_comments_ticket_id` | `ticket_id` | Chỉ mục thường |
| `ticket_events` | `ticket_events_pkey` | `id` | UNIQUE, khóa chính |
| `ticket_events` | `ix_ticket_events_ticket_id` | `ticket_id` | Chỉ mục thường |

Các chỉ mục trên hỗ trợ những truy vấn phổ biến như:

- Tìm tài khoản theo email.
- Tìm yêu cầu theo mã yêu cầu.
- Lọc yêu cầu theo người tạo, người phụ trách hoặc trạng thái.
- Sắp xếp yêu cầu theo thời điểm tạo.
- Lấy bình luận và lịch sử sự kiện theo yêu cầu.

PostgreSQL tự tạo chỉ mục cho khóa chính và ràng buộc UNIQUE. Các khóa ngoại không tự động tạo chỉ mục trên cột tham chiếu ở bảng nguồn; các chỉ mục tương ứng đã được xác nhận trong kết quả truy vấn ở trên.

## 9. Quy tắc giao dịch và ghi lịch sử

Các thao tác cập nhật dữ liệu nghiệp vụ và ghi lịch sử liên quan nên nằm trong cùng một transaction.

Ví dụ:

- Tạo yêu cầu và ghi sự kiện `TICKET_CREATED`.
- Thay đổi người phụ trách và ghi sự kiện tương ứng.
- Thay đổi trạng thái và ghi sự kiện thay đổi trạng thái.

Nếu một thao tác thất bại, các thay đổi liên quan cần được rollback để tránh dữ liệu nghiệp vụ và lịch sử không nhất quán.

Đây là yêu cầu xử lý ở cấp ứng dụng; chỉ cấu trúc bảng không tự bảo đảm toàn bộ quy tắc này.

## 10. Phân quyền và toàn vẹn dữ liệu

- Kiểm tra quyền theo vai trò và quyền truy cập từng yêu cầu ở service layer.
- Xác định người thực hiện thao tác từ danh tính đã xác thực, không tin tưởng `actor_id` do client gửi lên.
- Kiểm tra các bước chuyển trạng thái bằng logic nghiệp vụ.
- Không trả `password_hash` trong API response.
- Sử dụng khóa ngoại để ngăn tham chiếu đến người dùng hoặc yêu cầu không tồn tại.
- Ghi lịch sử nhất quán với thao tác nghiệp vụ tương ứng.
