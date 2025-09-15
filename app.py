from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from datetime import timedelta, datetime
import os
import re
import uuid
import bcrypt
import requests
import smtplib

from flask_login import (
    LoginManager, UserMixin,
    login_user, login_required,
    logout_user, current_user
)
from bs4 import BeautifulSoup
from werkzeug.utils import secure_filename
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

import config
from otp_handler import generate_otp, send_otp_email

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"  # redirect here if not logged in


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


app.secret_key = "supersecretkey"
# single combined DB file
# Example format from Supabase

EMAIL_ADDRESS = "studenttech404@gmail.com"
EMAIL_PASSWORD = "oata xwjd slng xmqq"

db = SQLAlchemy(app)



# --------------------
# Models (User + Testimonial)
# --------------------
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    is_subscribed = db.Column(db.Boolean, default=False)  # <--- NEW FIELD


def is_valid_email(email):
    if not email:
        return False
    return re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email)


class Testimonial(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    company = db.Column(db.String(120), nullable=True)
    position = db.Column(db.String(120), nullable=True)
    project = db.Column(db.String(255), nullable=True)
    project_link = db.Column(db.String(255), nullable=True)
    rating = db.Column(db.Integer, nullable=False, default=5)
    testimonial = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)



# --------------------
# Helpers
# --------------------




@app.route('/services')
def services():
    return render_template("services.html")


@app.route('/entrytest')
def entrytest():
    return render_template("entrytest.html")


@app.route("/entrytest/<exam>")
@login_required
def subjects(exam):
    return render_template("subjects.html", exam=exam)


@app.route("/notes/<exam>/<subject>")
@login_required
def notes(exam, subject):
    filename = f"{exam}_{subject}.pdf"
    user = current_user

    if user.is_subscribed:
        return render_template("fullnotes.html", exam=exam, subject=subject, filename=filename)
    else:
        return render_template("preview.html", exam=exam, subject=subject, filename=filename)


@app.route("/subscribe")
@login_required
def subscribe():
    user = current_user

    if not user.is_subscribed:
        user.is_subscribed = True
        db.session.commit()
        msg = "✅ Subscription activated! You now have access to all notes."
    else:
        msg = "ℹ️ You are already subscribed."
    return render_template("subscribe.html", message=msg)


@app.route('/service')
def service():
    return render_template("service.html")


def get_techcrunch_headlines():
    url = "https://techcrunch.com/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    headlines = []
    for article in soup.select("a.loop-card__title-link")[:5]:
        title = article.get_text(strip=True)
        link = article["href"]
        headlines.append({"title": title, "link": link})

    return headlines


def get_user_id():
    uid = session.get('user_id')
    if not uid:
        uid = str(uuid.uuid4())
        session['user_id'] = uid
    return uid


# --------------------
# Routes - pages & auth
# --------------------
@app.route('/')
@app.route('/home')
def home():
    try:
        headlines = get_techcrunch_headlines()
    except Exception as e:
        print(f"Error fetching TechCrunch headlines: {e}")
        headlines = []
    return render_template('home.html', headlines=headlines)


@app.route("/submit", methods=["GET", "POST"])
def submit():
    if request.method == "POST":
        name = request.form["name"]
        phone = request.form["phone"]
        email = request.form["email"]
        country = request.form["country"]
        company = request.form["company"]
        project = request.form["project"]
        file = request.files["file"]

        # -------------------
        # 1. Email to YOU
        # -------------------
        subject = "New Project Submission"
        body = f"""
            New project submitted:

            Name: {name}
            Phone: {phone}
            Email: {email}
            Country: {country}
            Company/University: {company}
            Project Details: {project}
            """

        msg = MIMEMultipart()
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = EMAIL_ADDRESS
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        # Attach file if uploaded
        if file and file.filename != "":
            filename = secure_filename(file.filename)
            filepath = os.path.join("uploads", filename)
            file.save(filepath)

            with open(filepath, "rb") as f:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f"attachment; filename={filename}")
            msg.attach(part)

        # Send email to YOU
        try:
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                server.sendmail(EMAIL_ADDRESS, EMAIL_ADDRESS, msg.as_string())
        except Exception as e:
            flash(f"Error sending your project details: {str(e)}", "danger")

        # -------------------
        # 2. Acknowledgment Email to USER
        # -------------------
        try:
            ack_subject = "Thank You for Trusting StudentTech"
            ack_body = f"""
                Dear {name},

                Thank you for trusting StudentTech with your project submission. 
                Our team has successfully received your details and we’ll review your project carefully. 

                ✅ What happens next:
                - Our experts will evaluate your submission.
                - We’ll get back to you on {email} with further steps.

                Meanwhile, feel free to explore our services and resources:
                👉 https://studenttech.example.com/services

                Best regards,  
                StudentTech Team
                """

            ack_msg = MIMEText(ack_body, "plain")
            ack_msg["From"] = EMAIL_ADDRESS
            ack_msg["To"] = email
            ack_msg["Subject"] = ack_subject

            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                server.sendmail(EMAIL_ADDRESS, email, ack_msg.as_string())

        except Exception:
            # Fail silently if email is invalid or undeliverable
            pass

        # Flash + Redirect
        flash("✅ We have received your details and will contact you soon!", "success")
        return redirect(url_for("services"))

    return render_template("submit.html")


@app.route('/aboutus')
def aboutus():
    return render_template('aboutus.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        otp = generate_otp()

        if send_otp_email(email, otp):
            session['email'] = email
            session['password'] = password
            session['otp'] = otp
            return redirect(url_for('verify'))
        else:
            flash("Failed to send OTP. Please check your email settings.", "danger")
    return render_template('signup.html')


@app.route('/verify', methods=['GET', 'POST'])
def verify():
    return render_template('verify.html')
#     if request.method == 'POST':
#         user_otp = request.form.get('otp')
#
#         # Ensure both are strings
#         if user_otp and str(user_otp).strip() == str(session.get('otp')).strip():
#             email = session.get('email')
#             password = session.get('password')
#
#             if User.query.filter_by(email=email).first():
#                 flash("This email is already registered. Please log in.", "warning")
#                 return redirect(url_for('login'))
#
#             hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
#             try:
#                 new_user = User(
#                      email=email,
#                     password_hash=hashed_pw.decode('utf-8'),
#                     is_subscribed=False
#                 )
#                 db.session.add(new_user)
#                 db.session.commit()
#                 # ✅ Auto login after signup
#                 login_user(new_user)
#                 flash("Signup successful. You are now logged in.", "success")
#                 return redirect(url_for('home'))
#
#             except Exception as e:
#                 db.session.rollback()
#                 flash(f"Error: {str(e)}", "danger")
#         else:
#             flash("Invalid OTP. Try again.", "danger")
#
#     return render_template('verify.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember')

        user = User.query.filter_by(email=email).first()
        if user and bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
            login_user(user, remember=bool(remember))  # ✅ Proper Flask-Login login
            flash("Login successful!", "success")
            return redirect(url_for('home'))  # or wherever you want
        else:
            flash("Invalid email or password.", "danger")
    return render_template('login.html')


@app.route('/logout')
def logout():
    return render_template('home.html')


@app.route('/testimonials', methods=['GET'])
def testimonials():
    items = Testimonial.query.order_by(Testimonial.created_at.desc()).all()
    return render_template('testimonials.html', testimonials=items)


@app.route('/submit_testimonial', methods=['POST'])
def submit_testimonial():
    full_name = request.form.get('full_name') or "Anonymous"
    email = request.form.get('email') or "no-reply@example.com"
    company = request.form.get('company', '')
    position = request.form.get('position', '')
    project = request.form.get('project') or request.form.get('project_name', '')
    project_link = request.form.get('project_link', '')

    try:
        rating = int(request.form.get('rating', 5))
        if rating < 1 or rating > 5:
            rating = 5
    except ValueError:
        rating = 5

    testimonial_text = request.form.get('testimonial', '').strip()
    if not testimonial_text:
        flash("Testimonial cannot be empty.", "warning")
        return redirect(url_for('testimonials'))

    t = Testimonial(
        full_name=full_name,
        email=email,
        company=company,
        position=position,
        project=project,
        project_link=project_link,
        rating=rating,
        testimonial=testimonial_text
    )

    try:
        db.session.add(t)
        db.session.commit()
        flash("Thank you! Your testimonial has been submitted.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error saving testimonial: {str(e)}", "danger")

    return redirect(url_for('testimonials'))


@app.route('/testimonials')
def testimonials_list():
    all_testimonials = Testimonial.query.order_by(Testimonial.id.desc()).all()
    return render_template('testimonials.html', testimonials=all_testimonials)


# --------------------
# Contact route
# --------------------

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        priority = request.form.get("priority")
        subject = request.form.get("subject")
        message = request.form.get("message")

        # 📩 Email to YOU (admin)
        admin_msg = f"""
            📬 New Contact Form Submission:

            Name: {name}
            Email: {email}
            Phone: {phone}
            Priority: {priority}
            Subject: {subject}
            Message:
            {message}
            """

        msg_to_admin = MIMEText(admin_msg, "plain")
        msg_to_admin["Subject"] = f"New Contact Form: {subject}"
        msg_to_admin["From"] = config.EMAIL_ADDRESS
        msg_to_admin["To"] = config.EMAIL_ADDRESS

        # 📩 Auto-reply to USER (only if valid email)
        msg_to_user = None
        if is_valid_email(email):
            reply_msg = f"""
                Hi {name},

                Thank you for contacting us! We have received your message and will respond shortly.

                Your submitted details:
                - Phone: {phone}
                - Priority: {priority}
                - Subject: {subject}
                - Message: {message}

                Regards,  
                StudentTech Team
                """

            msg_to_user = MIMEText(reply_msg, "plain")
            msg_to_user["Subject"] = "We received your message!"
            msg_to_user["From"] = config.EMAIL_ADDRESS
            msg_to_user["To"] = email

        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(config.EMAIL_ADDRESS, config.EMAIL_PASSWORD)
                server.send_message(msg_to_admin)
                if msg_to_user:
                    server.send_message(msg_to_user)

            flash("✅ Message sent successfully!", "success")
        except Exception as e:
            flash(f"❌ Failed to send message: {str(e)}", "danger")

        return redirect(url_for("contact"))

    return render_template("contact.html")


# --------------------
# Other pages
# --------------------
@app.route("/electrical")
def electrical():
    return render_template("electrical.html")


@app.route("/traffic")
def traffic():
    return render_template("traffic.html")


@app.route("/scooty_charger")
def scooty_charger():
    return render_template("scooty_charger.html")


@app.route("/dc_motor_control")
def dc_motor_control():
    return render_template("dc_motor_control.html")


@app.route("/mechanical")
def mechanical():
    return render_template("mechanical.html")


@app.route("/cybersecurity")
def cybersecurity():
    return render_template("cybersecurity.html")


@app.route("/computerscience")
def computerscience():
    return render_template("computerscience.html")


@app.route("/virtualpet")
def virtualpet():
    return render_template("virtualpet.html")


@app.route("/digitalmemoryjar")
def digitalmemoryjar():
    return render_template("digitalmemoryjar.html")


@app.route("/ecommercewebsite")
def ecommercewebsite():
    return render_template("ecommercewebsite.html")


@app.route("/todolistapp")
def todolistapp():
    return render_template("todolistapp.html")


@app.route("/fingergesture")
def fingergesture():
    return render_template("fingergesture.html")


@app.route("/gameboy")
def gameboy():
    return render_template("gameboy.html")


@app.route("/plantsvszombies")
def plantsvszombies():
    return render_template("plantsvszombies.html")


@app.route("/xonixgame")
def xonixgame():
    return render_template("xonixgame.html")


@app.route("/zumagame")
def zumagame():
    return render_template("zumagame.html")


@app.route("/gear_box")
def gear_box():
    return render_template("gear_box.html")


@app.route("/automatic_car_jack")
def automatic_car_jack():
    return render_template("automatic_car_jack.html")


@app.route("/hydraulic_scissor_lift")
def hydraulic_scissor_lift():
    return render_template("hydraulic_scissor_lift.html")


@app.route("/pedal_powered_water_pump")
def pedal_powered_water_pump():
    return render_template("pedal_powered_water_pump.html")


@app.route("/wind_powered_charger")
def wind_powered_charger():
    return render_template("wind_powered_charger.html")


@app.route("/computervision")
def computervision():
    return render_template("computervision.html")


@app.route("/facedetector")
def facedetector():
    return render_template("facedetector.html")


@app.route("/ppe")
def ppe():
    return render_template("ppe.html")


@app.route("/bolts")
def bolts():
    return render_template("bolts.html")


@app.route("/apply", methods=["GET", "POST"])
def apply():
    skills_list = [
        "Python", "Java", "C++", "C#", "JavaScript", "HTML", "CSS", "Flask", "Django",
        "React", "Node.js", "Angular", "SQL", "NoSQL", "MongoDB", "MySQL", "PostgreSQL",
        "Machine Learning", "Deep Learning", "AI", "Computer Vision", "Data Science",
        "NLP", "Embedded Systems", "IoT", "Robotics", "Cybersecurity", "Ethical Hacking",
        "Cloud Computing", "AWS", "Azure", "Google Cloud", "Docker", "Kubernetes",
        "Git", "GitHub", "Linux", "Bash", "MATLAB", "Arduino", "Raspberry Pi", "Electronics",
        "Mechanical Design", "SolidWorks", "AutoCAD", "Figma", "UI/UX", "Mobile Development",
        "Android", "iOS", "Game Development", "Unity", "Unreal Engine"
    ]

    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        university = request.form.get("university")
        department = request.form.get("department")
        semester = request.form.get("semester")
        skills = request.form.getlist("skills")
        comment = request.form.get("comment")

        # -------------------
        # Email to Admin
        # -------------------
        admin_subject = "New Engineer Application"
        admin_body = f"""
        New engineer applied:

        Name: {name}
        Email: {email}
        Phone: {phone}
        University: {university}
        Department: {department}
        Semester: {semester}
        Skills: {', '.join(skills)}
        Comment: {comment}
        """

        msg = MIMEMultipart()
        msg["From"] = config.EMAIL_ADDRESS
        msg["To"] = config.EMAIL_ADDRESS
        msg["Subject"] = admin_subject
        msg.attach(MIMEText(admin_body, "plain"))

        # -------------------
        # Acknowledgment Email to Applicant
        # -------------------
        ack_subject = "Thank You for Applying to Student Tech"
        ack_body = f"""
        Dear {name},

        Thank you for applying to join Student Tech! We have received your application and will contact you soon for an interview.

        Your submitted details:
        - Phone: {phone}
        - University: {university}
        - Department: {department}
        - Semester: {semester}
        - Skills: {', '.join(skills)}
        - Comment: {comment}

        Best regards,
        Student Tech Team
        """

        ack_msg = MIMEText(ack_body, "plain")
        ack_msg["From"] = config.EMAIL_ADDRESS
        ack_msg["To"] = email
        ack_msg["Subject"] = ack_subject

        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(config.EMAIL_ADDRESS, config.EMAIL_PASSWORD)
                server.sendmail(config.EMAIL_ADDRESS, config.EMAIL_ADDRESS, msg.as_string())
                server.sendmail(config.EMAIL_ADDRESS, email, ack_msg.as_string())

            flash("✅ Your application has been submitted successfully!", "success")
        except Exception as e:
            flash(f"❌ Failed to send application: {str(e)}", "danger")

        return redirect(url_for("apply"))

    return render_template("apply.html", skills_list=skills_list)

    # --------------------
    # Startup
    # --------------------


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001)

