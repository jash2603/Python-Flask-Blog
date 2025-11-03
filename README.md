# 📝 BlogSphere

🌐 **Live Demo:** BlogSphere  

BlogSphere is a secure, role-based Flask blogging platform built with modern authentication, role management (Admin, Author, Reader), and SQLite as the database backend. Users can register, log in, create posts, and interact within a dynamic blog environment — all from a clean web interface.

---

## 🚀 Features

### 🔑 User Authentication & Roles
- Register with username, password, and role (Admin / Author / Reader)
- Secure password hashing with **Flask-Bcrypt**
- Role-based dashboard redirection and access control
- Session-based authentication using Flask sessions

---

### 🧑‍💻 Role Management

| Role | Permissions |
|------|--------------|
| **Admin** | Full access — manage all posts and users |
| **Author** | Can create, edit, and delete their own posts |
| **Reader** | Can read and browse posts only |

---

### 📰 Blog Management
- Add, edit, and delete posts (authors & admins)
- Posts linked to individual users
- Upload post images to a configurable upload folder
- Pagination for better post navigation

---

### 📧 Contact Form Integration
- Send messages via the contact page directly to admin email
- Configurable using Flask-Mail (Gmail SMTP)
- Email notifications for contact form submissions

---

### 💾 Database
- Backend powered by **MySQL** for simplicity and portability  
- Models managed with **SQLAlchemy ORM**

---

### ⚙️ Tech Stack

| Component | Technology |
|------------|-------------|
| **Backend** | Flask (Python) |
| **Frontend** | HTML, CSS, Bootstrap |
| **Database** | MySQL |
| **Authentication** | Flask-Bcrypt + Flask Sessions |
| **Email** | Flask-Mail (SMTP) |

---

### 🧩 Folder Structure
