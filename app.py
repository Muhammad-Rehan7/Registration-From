from flask import Flask, render_template, request, jsonify
from flask import send_from_directory
from twilio.rest import Client
from dotenv import load_dotenv
import os


app = Flask(__name__)
load_dotenv()

# ✅ Load Twilio credentials
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
twilio_whatsapp = os.getenv("TWILIO_WHATSAPP_NUMBER")  # fixed variable name
admin_whatsapp = os.getenv("ADMIN_WHATSAPP_NUMBER")

client = Client(account_sid, auth_token)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/send", methods=["POST"])
def send_message():
    try:
        # collect form data
        
        team_name = request.form.get("team_name")
        team_topic = request.form.get("team_topic")
        member_count = int(request.form.get("member_count"))

        # msg = f"📢 *New Team Submission*\n\n🏆 Team Name: {team_name}\n🎯 Topic: {team_topic}\n"

        members = []
        for i in range(1, member_count + 1):
            if request.form.get(f"member{i}_name"):  # check if name exists
                members.append({
                    "name": request.form.get(f"member{i}_name"),
                    "roll": request.form.get(f"member{i}_roll"),
                    "department": request.form.get(f"member{i}_dept"),
                    "semester": request.form.get(f"member{i}_semester"),
                    "contact": request.form.get(f"member{i}_contact"),
                })

        msg = f"📢 *New Team Submission*\n\n🏆 Team Name: {team_name}\n🎯 Topic: {team_topic}\n👥 Number of Members = {member_count}\n"
        for i, m in enumerate(members, start=1):
            msg += (
                f"\n{i}) Name  : {m['name']}\n"
                f"    Roll no  : {m['roll']}\n"
                f"    Dept     : {m['department']}\n"
                f"    Sem      : {m['semester']}\n"
                f"    Contact  : {m['contact']}\n"
            )

        # ✅ Handle uploaded file
        image = request.files.get("screenshot")
        if image:
            # Extract the file extension
            ext = os.path.splitext(image.filename)[1]  # e.g., ".png" or ".jpg"
    
            # Make a safe filename from the team name
            safe_team_name = team_name.replace(" ", "_")  # replace spaces with underscores
            filename = f"{safe_team_name}{ext}"  # e.g., "AlphaTeam.png"

            upload_path = os.path.join("static", "uploads", filename)
            os.makedirs(os.path.dirname(upload_path), exist_ok=True)
            image.save(upload_path)
            media_url = f"https://unnegated-tawnya-unapologetically.ngrok-free.dev/static/uploads/{filename}"  # use your LAN IP
        else:
            media_url = None

        # ✅ Send message via Twilio
        client.messages.create(
            from_=twilio_whatsapp,
            body=msg,
            to=admin_whatsapp,
            media_url=media_url
        )

        print("✅ WhatsApp message sent successfully!")
        return jsonify({"status": "success"}), 200

    except Exception as e:
        print("❌ Twilio Error:", e)
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/static/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory('static/uploads', filename)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)


