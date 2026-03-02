from database_manager import DatabaseManager
import bcrypt

def create_dev():
    db = DatabaseManager()
    
    name = "المطور"
    email = "dev@admin.com"
    password = "123" # يرجى تغييرها لاحقاً
    role_id = 99
    store_id = None
    
    # Hash password
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    
    try:
        # Check if exists
        db.cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        if db.cursor.fetchone():
            print("❌ حساب المطور موجود بالفعل")
            return

        db.cursor.execute("""
            INSERT INTO users (name, email, password, phone, role_id, store_id, created_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (name, email, hashed, "0000", role_id, store_id, 1))
        db.conn.commit()
        print(f"✅ تم إنشاء حساب المطور بنجاح")
        print(f"البريد: {email}")
        print(f"كلمة المرور: {password}")
    except Exception as e:
        print(f"❌ خطأ: {str(e)}")

if __name__ == "__main__":
    create_dev()
