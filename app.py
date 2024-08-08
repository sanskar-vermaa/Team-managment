from flask import Flask, request, render_template, send_file
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part"
    file = request.files['file']
    if file.filename == '':
        return "No selected file"
    if file:
        df = pd.read_excel(file)
        if 'Dev' not in df.columns or 'BA' not in df.columns or 'DA' not in df.columns:
            return "The uploaded file does not contain the required columns: 'Dev', 'BA', 'DA'"
        teams = generate_teams(df)
        pdf = create_pdf(teams)
        return send_file(pdf, as_attachment=True, download_name='teams.pdf')

def generate_teams(df):
    devs = df['Dev'].dropna().tolist()
    bas = df['BA'].dropna().tolist()
    das = df['DA'].dropna().tolist()

    teams = []
    while len(devs) >= 3 and len(bas) >= 1 and len(das) >= 1:
        team = {
            'Dev': devs[:3],
            'BA': bas[:1],
            'DA': das[:1]
        }
        teams.append(team)
        devs = devs[3:]
        bas = bas[1:]
        das = das[1:]
    
    return teams

def create_pdf(teams):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    c.drawString(100, height - 40, "Team Compositions")
    c.drawString(100, height - 60, "-----------------")
    
    y = height - 100
    for i, team in enumerate(teams):
        c.drawString(100, y, f"Team {i + 1}")
        y -= 20
        for role in team:
            for member in team[role]:
                c.drawString(100, y, f"{member} - {role}")
                y -= 20
        y -= 20  # Add some space between teams
    
    c.save()
    buffer.seek(0)
    return buffer

if __name__ == '__main__':
    app.run(debug=True)
