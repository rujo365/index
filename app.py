from flask import Flask, render_template_string, request, jsonify
import os
import json
from datetime import datetime

app = Flask(__name__)
# উইন্ডোজের নিজস্ব লোকাল স্টোরেজ ফাইল
DB_FILE = "rajesh_database.txt"

# ফাইল ও স্টোরেজ চেক করার ফাংশন
def init_storage():
    if not os.path.exists(DB_FILE):
        default_data = {"collections": {}, "expenses": []}
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(default_data, f, ensure_ascii=False, indent=4)

# স্টোরেজ থেকে ডাটা পড়ার ফাংশন
def read_storage():
    init_storage()
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"collections": {}, "expenses": []}

# text ফাইলে ডাটা লেখার ফাংশন
def write_storage(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# ডেট-টাইম জেনারেটর
def get_clean_datetime():
    now = datetime.now()
    return {
        "date_only": now.strftime("%d/%m/%Y"),
        "full_stamp": now.strftime("%d/%m/%Y %H:%M")
    }

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

# ১. নতুন কালেকশন এন্ট্রি ও সেভ করা
@app.route('/api/collection', methods=['POST'])
def add_collection():
    data = request.json
    name = data.get('name', '').strip()
    amount = float(data.get('amount', 0))
    
    if not name or amount <= 0:
        return jsonify({"status": "error"}), 400
        
    dt = get_clean_datetime()
    storage = read_storage()
    
    if name not in storage["collections"]:
        storage["collections"][name] = {
            "count": 1,
            "total": amount,
            "history": [f"₹{amount} - {dt['full_stamp']}"],
            "lastDate": dt["date_only"]
        }
    else:
        storage["collections"][name]["count"] += 1
        storage["collections"][name]["total"] += amount
        storage["collections"][name]["history"].append(f"₹{amount} - {dt['full_stamp']}")
        storage["collections"][name]["lastDate"] = dt["date_only"]
        
    write_storage(storage)
    return jsonify({"status": "success"})

# ২. নতুন খরচা এন্ট্রি ও সেভ করা
@app.route('/api/expense', methods=['POST'])
def add_expense():
    data = request.json
    reason = data.get('reason', '').strip()
    amount = float(data.get('amount', 0))
    
    if not reason or amount <= 0:
        return jsonify({"status": "error"}), 400
        
    dt = get_clean_datetime()
    storage = read_storage()
    
    storage["expenses"].insert(0, {
        "reason": reason,
        "amount": amount,
        "timestamp": dt["full_stamp"],
        "dateOnly": dt["date_only"]
    })
    
    write_storage(storage)
    return jsonify({"status": "success"})

# ৩. লাইভ ড্যাশবোর্ডের জন্য ডাটা পাঠানো
@app.route('/api/data', methods=['GET'])
def get_data():
    storage = read_storage()
    return jsonify({
        "recoveryData": storage["collections"],
        "expenseData": storage["expenses"],
        "today_str": datetime.now().strftime("%d/%m/%Y")
    })

# ৪. কাস্টমার ডিলিট করা
@app.route('/api/collection/delete', methods=['POST'])
def delete_customer():
    name = request.json.get('name')
    storage = read_storage()
    if name in storage["collections"]:
        del storage["collections"][name]
        write_storage(storage)
    return jsonify({"status": "success"})

# ৫. খরচা ডিলিট করা
@app.route('/api/expense/delete', methods=['POST'])
def delete_expense():
    idx = request.json.get('index')
    storage = read_storage()
    if 0 <= idx < len(storage["expenses"]):
        storage["expenses"].pop(idx)
        write_storage(storage)
    return jsonify({"status": "success"})


# HTML ও ফ্রন্টএন্ড জাভাস্ক্রিপ্ট ডিজাইন (ত্রুটিমুক্ত সংস্করণ)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>লোন কালেকশন ও খরচা খাতা | Rajesh Digital 24</title>
    <link href="https://fonts.googleapis.com/css2?family=Hind+Siliguri:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        :root { --blue: #1e3a8a; --red: #ef4444; --bg: #f1f5f9; --white: #ffffff; --orange: #f97316; }
        body { margin: 0; font-family: 'Hind Siliguri', sans-serif; background: var(--bg); padding: 20px; display: flex; justify-content: center; }
        .container { width: 100%; max-width: 1000px; }
        .headline { background: var(--red); color: white; padding: 10px; font-weight: bold; font-size: 16px; border-bottom: 2px solid #fff; text-align: center; border-radius: 10px 10px 0 0; }
        header { background: var(--white); padding: 15px 25px; display: flex; justify-content: space-between; align-items: center; border-bottom: 3px solid var(--blue); }
        .card { background: white; padding: 25px; border-radius: 0 0 20px 20px; box-shadow: 0 5px 15px rgba(0,0,0,0.05); margin-bottom: 25px; }
        .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 15px; }
        .grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }
        .inp { width: 100%; padding: 12px; margin: 5px 0; border: 1px solid #ddd; border-radius: 8px; box-sizing: border-box; font-size: 15px; outline: none; }
        .btn-auth { width: 100%; padding: 12px; background: var(--blue); color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; font-size: 16px; transition: 0.3s; margin-top: 5px; }
        .btn-auth:hover { background: #1e40af; }
        .btn-exp { background: var(--orange); }
        .btn-exp:hover { background: #ea580c; }
        .report-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 20px; }
        .rep-card { padding: 12px; border-radius: 10px; color: white; text-align: center; font-weight: bold; font-size: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
        .tables-section { display: grid; grid-template-columns: 55% 42%; gap: 3%; margin-top: 25px; }
        table { width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; margin-top: 10px; }
        th, td { border: 1px solid #eee; padding: 10px; text-align: left; font-size: 14px; }
        th { background: var(--blue); color: white; }
        .exp-th { background: var(--orange); }
        .btn-delete { background: var(--red); color: white; border: none; padding: 4px 8px; border-radius: 4px; cursor: pointer; font-size: 11px; font-weight: bold; }
        .btn-delete:hover { background: #b91c1c; }
        .form-box { background: #f8fafc; padding: 15px; border-radius: 12px; border: 1px solid #e2e8f0; }
        @media print { .no-print, .btn-delete { display: none !important; } body { background: white; padding: 0; } .card { box-shadow: none; } .tables-section { grid-template-columns: 1fr; gap: 30px; } }
    </style>
</head>
<body>
<div class="container">
    <div class="headline no-print"><span>💰 লোন কালেকশন ও দৈনিক খরচা খাতা - রাজেশ ডিজিটাল ২৪ 💰</span></div>
    <header>
        <b style="font-size:22px; color:var(--blue)">RAJESH DIGITAL 24</b>
        <div id="clock" style="font-weight:bold; color: #555;"></div>
    </header>
    <div class="card">
        <div class="report-grid">
            <div class="rep-card" style="background: #22c55e;">আজকের কালেকশন<br>₹ <span id="today-total">0</span></div>
            <div class="rep-card" style="background: #3b82f6;">সর্বমোট রিকভারি<br>₹ <span id="all-total">0</span></div>
            <div class="rep-card" style="background: var(--orange);">আজকের মোট খরচা<br>₹ <span id="expense-total">0</span></div>
            <div class="rep-card" style="background: #94a3b8; color: #1e293b;">ক্যাশ ইন হ্যান্ড<br>₹ <span id="rem-total">0</span></div>
        </div>
        <div class="grid-2 no-print">
            <form id="frm-collection" class="form-box" style="border-left: 5px solid #22c55e;" onsubmit="saveCollection(event)">
                <h3 style="margin-top: 0; color: #15803d; font-size: 16px;">📥 নতুন কালেকশন এন্ট্রি (জমা)</h3>
                <div class="grid-3">
                    <input type="text" id="rec-name" class="inp" placeholder="কাস্টমারের নাম" required autocomplete="off">
                    <input type="number" id="rec-amt" class="inp" placeholder="টাকা (₹)" required autocomplete="off" step="any">
                    <button type="submit" class="btn-auth">জমা নিন</button>
                </div>
            </form>
            <form id="frm-expense" class="form-box" style="border-left: 5px solid var(--orange);" onsubmit="saveExpense(event)">
                <h3 style="margin-top: 0; color: #c2410c; font-size: 16px;">📤 নতুন খরচা এন্ট্রি (ডেবিট)</h3>
                <div class="grid-3">
                    <input type="text" id="exp-reason" class="inp" placeholder="খরচার বিবরণ" required autocomplete="off">
                    <input type="number" id="exp-amt" class="inp" placeholder="টাকা (₹)" required autocomplete="off" step="any">
                    <button type="submit" class="btn-auth btn-exp">খরচা সেভ</button>
                </div>
            </form>
        </div>
        <div style="text-align: right; margin-top: 20px;" class="no-print">
            <button type="button" class="btn-auth" onclick="window.print()" style="width: auto; padding: 8px 20px; background: #10b981;">🖨️ আজকের রিপোর্ট প্রিন্ট করুন</button>
        </div>
        <div class="tables-section">
            <div>
                <h3 style="margin: 0; color: var(--blue);">📜 কাস্টমার কালেকশন লেজার</h3>
                <table>
                    <thead>
                        <tr><th>কাস্টমারের নাম</th><th>সংখ্যা</th><th>তারিখ ও জমার হিস্ট্রি</th><th>মোট জমা</th><th class="no-print">অ্যাকশন</th></tr>
                    </thead>
                    <tbody id="recovery-body"></tbody>
                </table>
            </div>
            <div>
                <h3 style="margin: 0; color: #c2410c;">📜 দৈনিক খরচার তালিকা</h3>
                <table>
                    <thead>
                        <tr><th class="exp-th">খরচার বিবরণ</th><th class="exp-th">তারিখ ও সময়</th><th class="exp-th">টাকা</th><th class="exp-th no-print">অ্যাকশন</th></tr>
                    </thead>
                    <tbody id="expense-body"></tbody>
                </table>
            </div>
        </div>
    </div>
</div>
<script>
    const TOTAL_INVESTMENT = 100000;

    document.addEventListener("DOMContentLoaded", function() {
        setInterval(function() {
            const d = new Date();
            document.getElementById('clock').innerText = d.toLocaleDateString('en-GB') + " " + d.toLocaleTimeString();
        }, 1000);
        loadDataFromServer();
    });

    function loadDataFromServer() {
        fetch('/api/data')
        .then(res => res.json())
        .then(data => {
            const todayStr = data.today_str;
            let overallRecovered = 0;
            let todayRecovered = 0;
            let todayExpense = 0;

            const recBody = document.getElementById('recovery-body');
            recBody.innerHTML = '';
            if (Object.keys(data.recoveryData).length === 0) {
                recBody.innerHTML = '<tr><td colspan="5" style="text-align:center; color:#aaa;">কোনো কালেকশন রেকর্ড নেই</td></tr>';
            } else {
                for (let k in data.recoveryData) {
                    const d = data.recoveryData[k];
                    overallRecovered += d.total;
                    d.history.forEach(item => {
                        if(item.indexOf(todayStr) !== -1) {
                            todayRecovered += parseFloat(item.split(' - ')[0].replace('₹', '')) || 0;
                        }
                    });
                    
                    // এখানে ব্যাকস্ল্যাশ মুক্ত ফ্রেশ জাভাস্ক্রিপ্ট কোড দেওয়া হলো
                    recBody.innerHTML += `<tr>
                        <td><b>${k}</b></td>
                        <td>${d.count} বার</td>
                        <td style="font-size:12px; color:#555;">${d.history.join('<br>')}</td>
                        <td style="color:green; font-weight:bold;">₹ ${d.total}</td>
                        <td class="no-print"><button class="btn-delete" onclick="deleteCustomer('${k}')">❌</button></td>
                    </tr>`;
                }
            }

            const expBody = document.getElementById('expense-body');
            expBody.innerHTML = '';
            if (data.expenseData.length === 0) {
                expBody.innerHTML = '<tr><td colspan="4" style="text-align:center; color:#aaa;">কোনো খরচার রেকর্ড নেই</td></tr>';
            } else {
                data.expenseData.forEach((item, index) => {
                    if(item.dateOnly === todayStr) todayExpense += item.amount;
                    expBody.innerHTML += `<tr>
                        <td><b>${item.reason}</b></td>
                        <td style="font-size:12px; color:#666;">${item.timestamp}</td>
                        <td style="color:#c2410c; font-weight:bold;">₹ ${item.amount}</td>
                        <td class="no-print"><button class="btn-delete" onclick="deleteExpense(${index})">❌</button></td>
                    </tr>`;
                });
            }

            document.getElementById('today-total').innerText = todayRecovered;
            document.getElementById('all-total').innerText = overallRecovered;
            document.getElementById('expense-total').innerText = todayExpense;
            let netRemaining = TOTAL_INVESTMENT - overallRecovered - todayExpense;
            document.getElementById('rem-total').innerText = netRemaining < 0 ? 0 : netRemaining;
        });
    }

    function saveCollection(e) {
        e.preventDefault();
        const name = document.getElementById('rec-name').value.trim();
        const amount = document.getElementById('rec-amt').value;

        fetch('/api/collection', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({name: name, amount: amount})
        }).then(() => {
            document.getElementById('rec-name').value = '';
            document.getElementById('rec-amt').value = '';
            document.getElementById('rec-name').focus();
            loadDataFromServer();
        });
    }

    function saveExpense(e) {
        e.preventDefault();
        const reason = document.getElementById('exp-reason').value.trim();
        const amount = document.getElementById('exp-amt').value;

        fetch('/api/expense', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({reason: reason, amount: amount})
        }).then(() => {
            document.getElementById('exp-reason').value = '';
            document.getElementById('exp-amt').value = '';
            document.getElementById('exp-reason').focus();
            loadDataFromServer();
        });
    }

    function deleteCustomer(name) {
        if(confirm(`"${name}" এর সমস্ত রেকর্ড ফাইল থেকে ডিলিট করতে চান?`)) {
            fetch('/api/collection/delete', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({name: name})
            }).then(() => loadDataFromServer());
        }
    }

    function deleteExpense(index) {
        if(confirm("এই খরচার এন্ট্রিটি ডিলিট করতে চান?")) {
            fetch('/api/expense/delete', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({index: index})
            }).then(() => loadDataFromServer());
        }
    }
</script>
</body>
</html>
"""
import os

if __name__ == '__main__':
    # রেন্ডার সার্ভারের দরজা (Port) চেনার জন্য এই কোডটুকু জরুরি
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
