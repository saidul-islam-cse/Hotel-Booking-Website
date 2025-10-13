🏨 Hotel Booking Website (Django + React + Tailwind)
A complete Hotel Booking System where users can register, log in, browse hotels, make bookings, and manage wallet payments.
The backend is built with Django REST Framework, and the frontend is developed using React + Tailwind CSS.
________________________________________
🚀 Deployment Information
Frontend: React (Vite) hosted on Render
Backend: Django REST Framework hosted on Render
Database: SQLite (for demo purposes)
Authentication: JWT (Access + Refresh Tokens)
________________________________________
⚙️ Tech Stack
Layer	Technology Used
Frontend	React, Tailwind CSS
Backend	Django REST Framework
Authentication	JWT (SimpleJWT)
Deployment	Render
Database	SQLite
Email	Gmail SMTP (Local)
________________________________________
📧 SMTP Connection Test
✅ Gmail SMTP works perfectly in the local development server.
❌ SMTP connection fails on Render production server due to network restrictions.
🧪 Local Server Test Result
 
✅ SMTP connection successful!
☁️ Render Server Test Result
 
❌ SMTP connection failed: [Errno 101] Network is unreachable
⚠️ Note:
The free Render hosting environment blocks outbound SMTP connections (port 465/587) for security reasons.
Therefore, Gmail SMTP cannot be used directly on Render.
You can use one of these alternatives instead:
•	SendGrid
•	Mailgun
•	Brevo (Sendinblue)
________________________________________
🔗 Important URLs
Type	URL
Frontend	http://localhost:5173/
Backend	https://hotel-booking-website-46ia.onrender.com/
SMTP Check	/check-smtp/
________________________________________
👨‍💻 Developer
Name: Saidul Islam
Role: Full-Stack Developer
Stack: Django · React · Tailwind · REST API

