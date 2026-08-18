# আমাদের গল্প — Online Version ❤️

এই version-এ local SQLite/uploads বাদ দিয়ে Supabase ব্যবহার করা হয়েছে:
- Supabase Postgres → Story, Photos metadata, Oviman, Promise, Meetup
- Supabase Storage → আসল ছবি
- Render → Flask website hosting

## 1) Local setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Supabase environment variables সেট করে:

```bash
export SUPABASE_URL="YOUR_SUPABASE_URL"
export SUPABASE_SERVICE_ROLE_KEY="YOUR_SERVICE_ROLE_KEY"
export SUPABASE_BUCKET="love-photos"
export SECRET_KEY="a-long-random-secret"
export ADMIN_USERNAME="admin"
export ADMIN_PASSWORD_HASH="YOUR_HASH"
python app.py
```

## 2) Admin password hash তৈরি

```bash
python -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('ChaduSiam'))"
```

যে hash আসবে সেটি `ADMIN_PASSWORD_HASH` হিসেবে Render-এ দেবে।

## 3) Supabase

Supabase project তৈরি করে SQL Editor-এ `schema.sql`-এর SQL একবার run করো।

Storage-এ `love-photos` নামে bucket তৈরি করে Public bucket হিসেবে সেট করো, কারণ public website-এ photo URL সরাসরি দেখানো হচ্ছে।

## 4) Render

GitHub repo-তে `app.py`, `requirements.txt`, `render.yaml`, `schema.sql` রাখো।

Render → New → Web Service → GitHub repo connect.

Build:
`pip install -r requirements.txt`

Start:
`gunicorn app:app`

Environment variables:
- SUPABASE_URL
- SUPABASE_SERVICE_ROLE_KEY
- SUPABASE_BUCKET=love-photos
- SECRET_KEY
- ADMIN_USERNAME=admin
- ADMIN_PASSWORD_HASH

Deploy হলে:
`https://your-service-name.onrender.com`

Admin:
`https://your-service-name.onrender.com/admin`

## Security

SUPABASE_SERVICE_ROLE_KEY কখনো GitHub-এ commit করবে না এবং browser-side JavaScript-এ রাখবে না।
