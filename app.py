from flask import Flask, render_template, request, redirect, url_for
import pywhatkit as kit
import os

app = Flask(__name__)

# जागतिक चल (Global variables)
tokens = []
next_token_no = 101
active_token = None

def get_actual_template(base_name):
    """
    हे फंक्शन तुमच्या 'templates' फोल्डरमधील फाईलचे अचूक नाव स्वतः शोधून काढते.
    त्यामुळे नाव 'index', 'index.html' किंवा 'index.html.html' असले तरी एरर येत नाही.
    """
    templates_dir = 'templates'
    if os.path.exists(templates_dir):
        for file in os.listdir(templates_dir):
            if file.startswith(base_name):
                return file
    return base_name

# --- १. होम पेज (HOME PAGE) ---
@app.route('/')
def index():
    return render_template(get_actual_template('index'))

# --- २. टोकन बुकिंग पेज (GET TOKEN PAGE) ---
@app.route('/get-token', methods=['GET', 'POST'])
def get_token():
    global next_token_no
    t_name = get_actual_template('get_token')
    
    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')

        if name and phone:
            token_no = next_token_no
            next_token_no += 1
            customer = {"token": token_no, "name": name, "phone": phone}
            tokens.append(customer)

            # व्हॉट्सॲपवर मेसेज पाठवणे
            try:
                formatted_phone = f"+91{phone}" if len(phone) == 10 and not phone.startswith('91') else f"+{phone}"
                msg_body = (
                    f"✨🛍️ *DIVYA COLLECTION* 🛍️✨\n"
                    f"━━━━━━━━━━━━━━━━━━━\n\n"
                    f"Hello {name},\n"
                    f"Your token has been successfully booked! 🎉\n\n"
                    f"🆔 *Token Number:* {token_no}\n\n"
                    f"Thank you for visiting our shop! 🙏"
                )
                kit.sendwhatmsg_instantly(formatted_phone, msg_body, wait_time=15, tab_close=True)
            except Exception as e:
                print(f"WhatsApp Error: {e}")

            return render_template(t_name, success=True, token_no=token_no)

    return render_template(t_name, success=False)

# --- ३. कलेक्शन पेज (OUR COLLECTION PAGE) ---
@app.route('/products')
def products():
    # 'product' किंवा 'products' दोन्ही नामांसाठी तपासणी
    template_file = get_actual_template('product')
    if not os.path.exists(os.path.join('templates', template_file)):
        template_file = get_actual_template('products')
    return render_template(template_file)

# --- ४. संपर्क पेज (CONTACT US PAGE) ---
@app.route('/contact')
def contact():
    return render_template(get_actual_template('contact'))

# --- ५. ॲडमिन पॅनेल (ADMIN PANEL) ---
@app.route('/admin')
def admin():
    global active_token
    shop_details = {"name": "Divya Collection"}
    return render_template(get_actual_template('admin'), tokens=tokens, active_token=active_token, shop_details=shop_details)

# --- ६. पुढील ग्राहक बटन (NEXT PERSON BUTTON) ---
@app.route('/next-person')
def next_person():
    global active_token
    if tokens:
        active_token = tokens.pop(0)
        phone = active_token['phone']
        name = active_token['name']
        token_no = active_token['token']

        try:
            formatted_phone = f"+91{phone}" if len(phone) == 10 and not phone.startswith('91') else f"+{phone}"
            msg_body = (
                f"✨🛍️ *DIVYA COLLECTION* 🛍️✨\n"
                f"━━━━━━━━━━━━━━━━━━━\n\n"
                f"Hello {name},\n"
                f"Your turn will come in 10 minutes! ⏳\n\n"
                f"🔢 *Token Number:* {token_no}\n\n"
                f"Please proceed to Counter 1. See you soon! 😊"
            )
            kit.sendwhatmsg_instantly(formatted_phone, msg_body, wait_time=15, tab_close=True)
        except Exception as e:
            print(f"WhatsApp Error: {e}")
    else:
        active_token = None
        
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(debug=True)