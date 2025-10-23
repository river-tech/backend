import os
import psycopg2
import uuid
from datetime import datetime

def seed_user_notifications_and_wishlist():
    # Lấy chuỗi kết nối DB
    db_url = os.getenv("DATABASE_URL", "postgresql://usitech_user:1234@localhost:6969/usitech")
    if not db_url:
        print("❌ DATABASE_URL env not found!")
        return

    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()

        # 1️⃣ Lấy user_id theo email
        email = "nguyenha17022k5@gmail.com"
        cur.execute("SELECT id FROM users WHERE email = %s", (email,))
        user_row = cur.fetchone()
        if not user_row:
            print(f"❌ User {email} not found!")
            return
        user_id = user_row[0]
        print(f"✅ Found user ID: {user_id}")

        # 2️⃣ Tạo danh sách notification
        notifications = [
            (str(uuid.uuid4()), user_id, "🎉 Chào mừng bạn!", "Cảm ơn bạn đã đăng ký tài khoản USITech.", "SUCCESS", True, datetime.now()),
            (str(uuid.uuid4()), user_id, "🧩 Có workflow mới!", "Khám phá ngay workflow tự động hóa vừa ra mắt.", "INFO", True, datetime.now()),
            (str(uuid.uuid4()), user_id, "💡 Gợi ý hôm nay", "Thử workflow 'Email Automation' để tiết kiệm 2h mỗi ngày.", "INFO", True, datetime.now()),
            (str(uuid.uuid4()), user_id, "🔥 Ưu đãi hot", "Giảm 20% cho tất cả workflow trong 24h tới!", "WARNING", True, datetime.now()),
        ]

        cur.executemany("""
            INSERT INTO notifications (id, user_id, title, message, type, is_unread, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, notifications)
        print(f"✅ Added {len(notifications)} notifications for {email}")

        # 3️⃣ Lấy 2 workflow để add wishlist (nếu có)
        cur.execute("SELECT id FROM workflows LIMIT 2")
        workflows = cur.fetchall()
        if workflows:
            favorites = [
                (str(uuid.uuid4()), user_id, wf_id, datetime.now())
                for (wf_id,) in workflows
            ]
            cur.executemany("""
                INSERT INTO favorites (id, user_id, workflow_id, created_at)
                VALUES (%s, %s, %s, %s)
            """, favorites)
            print(f"✅ Added {len(favorites)} workflows to wishlist")
        else:
            print("⚠️ No workflows found to add to wishlist")

        conn.commit()
        print("🎯 Data seeded successfully!")

    except Exception as e:
        print("❌ Error:", e)

    finally:
        if conn:
            cur.close()
            conn.close()

if __name__ == "__main__":
    seed_user_notifications_and_wishlist()