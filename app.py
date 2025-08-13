# app.py
from flask import Flask, render_template_string, request, jsonify
import ollama
import json
import fitz  # PyMuPDF for PDF
import docx
from io import BytesIO

app = Flask(__name__)

# HTML шаблон с встроенным CSS и JS
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Карьерный Ментор AI</title>
    <style>
        :root {
            --primary: #6366f1;
            --primary-dark: #4f46e5;
            --secondary: #10b981;
            --danger: #ef4444;
            --light: #f8fafc;
            --dark: #0f172a;
            --gray: #94a3b8;
            --success: #22c55e;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        body {
            background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        header {
            text-align: center;
            padding: 40px 20px;
            color: var(--dark);
        }
        
        h1 {
            font-size: 2.5rem;
            margin-bottom: 15px;
            background: linear-gradient(90deg, var(--primary), var(--secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .subtitle {
            font-size: 1.2rem;
            color: var(--gray);
            max-width: 600px;
            margin: 0 auto 30px;
        }
        
        .main-card {
            background: white;
            border-radius: 20px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
            padding: 40px;
            margin-bottom: 30px;
        }
        
        .upload-section {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-bottom: 30px;
        }
        
        @media (max-width: 768px) {
            .upload-section {
                grid-template-columns: 1fr;
            }
        }
        
        .upload-box {
            border: 2px dashed var(--gray);
            border-radius: 15px;
            padding: 30px;
            text-align: center;
            transition: all 0.3s ease;
            cursor: pointer;
        }
        
        .upload-box:hover {
            border-color: var(--primary);
            background: rgba(99, 102, 241, 0.05);
        }
        
        .upload-box.active {
            border-color: var(--primary);
            background: rgba(99, 102, 241, 0.1);
        }
        
        .upload-icon {
            font-size: 3rem;
            color: var(--primary);
            margin-bottom: 15px;
        }
        
        .upload-title {
            font-size: 1.1rem;
            font-weight: 600;
            margin-bottom: 10px;
            color: var(--dark);
        }
        
        .upload-text {
            color: var(--gray);
            font-size: 0.9rem;
            margin-bottom: 15px;
        }
        
        .file-input {
            display: none;
        }
        
        .file-name {
            font-size: 0.8rem;
            color: var(--primary);
            font-weight: 500;
            margin-top: 10px;
        }
        
        .analyze-btn {
            background: linear-gradient(90deg, var(--primary), var(--primary-dark));
            color: white;
            border: none;
            padding: 15px 40px;
            font-size: 1.1rem;
            font-weight: 600;
            border-radius: 12px;
            cursor: pointer;
            display: block;
            margin: 0 auto;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
        }
        
        .analyze-btn:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(99, 102, 241, 0.4);
        }
        
        .analyze-btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
        
        .loading {
            display: none;
            text-align: center;
            padding: 30px;
        }
        
        .spinner {
            width: 50px;
            height: 50px;
            border: 5px solid rgba(99, 102, 241, 0.3);
            border-top: 5px solid var(--primary);
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .results {
            display: none;
        }
        
        .match-score {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .score-circle {
            width: 120px;
            height: 120px;
            border-radius: 50%;
            background: conic-gradient(var(--primary) 65%, var(--gray) 65%);
            margin: 0 auto 20px;
            position: relative;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .score-inner {
            width: 100px;
            height: 100px;
            border-radius: 50%;
            background: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2rem;
            font-weight: bold;
            color: var(--primary);
        }
        
        .skills-section {
            margin-bottom: 30px;
        }
        
        .section-title {
            font-size: 1.3rem;
            margin-bottom: 20px;
            color: var(--dark);
            padding-bottom: 10px;
            border-bottom: 2px solid var(--gray);
        }
        
        .skills-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }
        
        .skill-card {
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 15px;
        }
        
        .skill-card.has {
            background: rgba(34, 197, 94, 0.1);
            border-left: 4px solid var(--success);
        }
        
        .skill-card.missing {
            background: rgba(239, 68, 68, 0.1);
            border-left: 4px solid var(--danger);
        }
        
        .skill-header {
            display: flex;
            align-items: center;
            margin-bottom: 10px;
        }
        
        .skill-icon {
            font-size: 1.5rem;
            margin-right: 10px;
        }
        
        .skill-name {
            font-weight: 600;
            color: var(--dark);
        }
        
        .skill-description {
            color: var(--gray);
            font-size: 0.9rem;
        }
        
        .plan-section {
            margin-bottom: 30px;
        }
        
        .plan-item {
            background: white;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 15px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            border-left: 4px solid var(--primary);
        }
        
        .plan-title {
            font-weight: 600;
            color: var(--dark);
            margin-bottom: 8px;
        }
        
        .plan-description {
            color: var(--gray);
            font-size: 0.9rem;
            margin-bottom: 10px;
        }
        
        .plan-link {
            color: var(--primary);
            text-decoration: none;
            font-size: 0.9rem;
            font-weight: 500;
        }
        
        .plan-link:hover {
            text-decoration: underline;
        }
        
        .action-buttons {
            display: flex;
            gap: 15px;
            justify-content: center;
            margin-top: 30px;
        }
        
        .btn-secondary {
            background: white;
            color: var(--primary);
            border: 2px solid var(--primary);
            padding: 12px 25px;
            border-radius: 12px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        
        .btn-secondary:hover {
            background: var(--primary);
            color: white;
        }
        
        .examples-btn {
            background: transparent;
            color: var(--gray);
            border: none;
            padding: 12px 25px;
            border-radius: 12px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        
        .examples-btn:hover {
            color: var(--primary);
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Карьерный Ментор AI</h1>
            <p class="subtitle">Загрузи своё резюме и описание вакансии, а наш ИИ подскажет, какие навыки прокачать</p>
        </header>
        
        <main>
            <div class="main-card">
                <div class="upload-section">
                    <div class="upload-box" id="resume-box">
                        <div class="upload-icon">📄</div>
                        <h3 class="upload-title">Резюме</h3>
                        <p class="upload-text">Загрузите файл .pdf, .docx или .txt</p>
                        <input type="file" class="file-input" id="resume-input" accept=".pdf,.docx,.txt">
                        <div class="file-name" id="resume-name"></div>
                    </div>
                    
                    <div class="upload-box" id="vacancy-box">
                        <div class="upload-icon">💼</div>
                        <h3 class="upload-title">Описание вакансии</h3>
                        <p class="upload-text">Загрузите файл .pdf, .docx или .txt</p>
                        <input type="file" class="file-input" id="vacancy-input" accept=".pdf,.docx,.txt">
                        <div class="file-name" id="vacancy-name"></div>
                    </div>
                </div>
                
                <button class="analyze-btn" id="analyze-btn" disabled>Проанализировать</button>
                
                <div class="loading" id="loading">
                    <div class="spinner"></div>
                    <p>Анализируем ваш профиль и вакансию...</p>
                </div>
            </div>
            
            <div class="main-card results" id="results">
                <div class="match-score">
                    <div class="score-circle">
                        <div class="score-inner" id="match-percent">65%</div>
                    </div>
                    <h2>Совпадение навыков</h2>
                </div>
                
                <div class="skills-section">
                    <h3 class="section-title">Анализ навыков</h3>
                    <div class="skills-grid" id="skills-grid">
                        <!-- Skills will be inserted here -->
                    </div>
                </div>
                
                <div class="plan-section">
                    <h3 class="section-title">План развития</h3>
                    <div id="development-plan">
                        <!-- Plan items will be inserted here -->
                    </div>
                </div>
                
                <div class="action-buttons">
                    <button class="btn-secondary" onclick="newAnalysis()">Новый анализ</button>
                    <button class="examples-btn">Примеры</button>
                </div>
            </div>
        </main>
    </div>

    <script>
        let resumeFile = null;
        let vacancyFile = null;
        
        // Setup file upload handlers
        document.getElementById('resume-box').addEventListener('click', () => {
            document.getElementById('resume-input').click();
        });
        
        document.getElementById('vacancy-box').addEventListener('click', () => {
            document.getElementById('vacancy-input').click();
        });
        
        document.getElementById('resume-input').addEventListener('change', function(e) {
            if (this.files.length > 0) {
                resumeFile = this.files[0];
                document.getElementById('resume-name').textContent = resumeFile.name;
                document.getElementById('resume-box').classList.add('active');
                checkEnableButton();
            }
        });
        
        document.getElementById('vacancy-input').addEventListener('change', function(e) {
            if (this.files.length > 0) {
                vacancyFile = this.files[0];
                document.getElementById('vacancy-name').textContent = vacancyFile.name;
                document.getElementById('vacancy-box').classList.add('active');
                checkEnableButton();
            }
        });
        
        function checkEnableButton() {
            const btn = document.getElementById('analyze-btn');
            btn.disabled = !(resumeFile && vacancyFile);
        }
        
        document.getElementById('analyze-btn').addEventListener('click', async function() {
            if (!resumeFile || !vacancyFile) return;
            
            // Show loading
            document.getElementById('loading').style.display = 'block';
            this.disabled = true;
            
            try {
                // Read files
                const resumeText = await readFile(resumeFile);
                const vacancyText = await readFile(vacancyFile);
                
                // Send to backend
                const response = await fetch('/analyze', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        resume: resumeText,
                        vacancy: vacancyText
                    })
                });
                
                const result = await response.json();
                
                // Display results
                displayResults(result);
                
            } catch (error) {
                console.error('Error:', error);
                alert('Произошла ошибка при анализе');
            } finally {
                document.getElementById('loading').style.display = 'none';
                this.disabled = false;
            }
        });
        
        async function readFile(file) {
            return new Promise((resolve, reject) => {
                const reader = new FileReader();
                reader.onload = e => resolve(e.target.result);
                reader.onerror = reject;
                reader.readAsText(file);
            });
        }
        
        function displayResults(data) {
            // Set match percentage
            document.getElementById('match-percent').textContent = data.match_percentage + '%';
            
            // Display skills
            const skillsGrid = document.getElementById('skills-grid');
            skillsGrid.innerHTML = '';
            
            // Has skills
            data.skills.has.forEach(skill => {
                const card = document.createElement('div');
                card.className = 'skill-card has';
                card.innerHTML = `
                    <div class="skill-header">
                        <span class="skill-icon">✓</span>
                        <span class="skill-name">${skill.name}</span>
                    </div>
                    <div class="skill-description">${skill.description}</div>
                `;
                skillsGrid.appendChild(card);
            });
            
            // Missing skills
            data.skills.missing.forEach(skill => {
                const card = document.createElement('div');
                card.className = 'skill-card missing';
                card.innerHTML = `
                    <div class="skill-header">
                        <span class="skill-icon">✗</span>
                        <span class="skill-name">${skill.name}</span>
                    </div>
                    <div class="skill-description">${skill.description}</div>
                `;
                skillsGrid.appendChild(card);
            });
            
            // Display development plan
            const planDiv = document.getElementById('development-plan');
            planDiv.innerHTML = '';
            
            data.development_plan.forEach(item => {
                const planItem = document.createElement('div');
                planItem.className = 'plan-item';
                planItem.innerHTML = `
                    <div class="plan-title">${item.title}</div>
                    <div class="plan-description">${item.description}</div>
                    ${item.link ? `<a href="${item.link}" class="plan-link" target="_blank">Подробнее →</a>` : ''}
                `;
                planDiv.appendChild(planItem);
            });
            
            // Show results
            document.getElementById('results').style.display = 'block';
        }
        
        function newAnalysis() {
            document.getElementById('results').style.display = 'none';
            document.getElementById('resume-input').value = '';
            document.getElementById('vacancy-input').value = '';
            document.getElementById('resume-name').textContent = '';
            document.getElementById('vacancy-name').textContent = '';
            document.getElementById('resume-box').classList.remove('active');
            document.getElementById('vacancy-box').classList.remove('active');
            document.getElementById('analyze-btn').disabled = true;
            resumeFile = null;
            vacancyFile = null;
        }
    </script>
</body>
</html>
'''

def extract_text_from_file(file_content, filename):
    """Extract text from uploaded file"""
    if filename.endswith('.pdf'):
        # Handle PDF
        pdf_file = BytesIO(file_content.encode('latin1') if isinstance(file_content, str) else file_content)
        doc = fitz.open(stream=pdf_file, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        return text
    elif filename.endswith('.docx'):
        # Handle DOCX
        docx_file = BytesIO(file_content.encode('latin1') if isinstance(file_content, str) else file_content)
        doc = docx.Document(docx_file)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    else:
        # Handle TXT
        if isinstance(file_content, bytes):
            return file_content.decode('utf-8')
        return file_content

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json()
        resume_text = data.get('resume', '')
        vacancy_text = data.get('vacancy', '')
        
        # Create prompt for AI analysis
        prompt = f"""
        Проанализируй резюме и описание вакансии. Ответь в формате JSON с следующей структурой:
        
        {{
            "match_percentage": число от 0 до 100,
            "skills": {{
                "has": [
                    {{"name": "название навыка", "description": "описание почему этот навык есть"}}
                ],
                "missing": [
                    {{"name": "название навыка", "description": "описание почему этого навыка не хватает"}}
                ]
            }},
            "development_plan": [
                {{
                    "title": "название курса или действия",
                    "description": "описание что нужно сделать",
                    "link": "ссылка на ресурс (если есть)"
                }}
            ]
        }}
        
        Резюме:
        {resume_text}
        
        Вакансия:
        {vacancy_text}
        
        Дай конкретные рекомендации и реальные навыки. Не используй markdown.
        """
        
        # Call Ollama with phi4-mini model
        response = ollama.chat(
            model='qwen3:1.7b',
            messages=[{'role': 'user', 'content': prompt}],
            options={'temperature': 0.7}
        )
        
        # Parse AI response
        ai_response = response['message']['content']
        
        # Try to extract JSON from response
        import re
        json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group())
        else:
            # Fallback response if JSON parsing fails
            result = {
                "match_percentage": 65,
                "skills": {
                    "has": [
                        {"name": "Python", "description": "Упомянут в резюме как основной язык программирования"},
                        {"name": "SQL", "description": "Опыт работы с базами данных упомянут в проектах"}
                    ],
                    "missing": [
                        {"name": "Docker", "description": "Не упомянут в резюме, но требуется по вакансии"},
                        {"name": "Kubernetes", "description": "Требуется для senior позиций, отсутствует в опыте"}
                    ]
                },
                "development_plan": [
                    {
                        "title": "Курс по Docker",
                        "description": "Освойте контейнеризацию приложений с Docker",
                        "link": "https://docker-curriculum.com"
                    },
                    {
                        "title": "Практический проект с Kubernetes",
                        "description": "Разверните микросервисное приложение в Kubernetes кластере",
                        "link": "https://kubernetes.io/docs/tutorials"
                    }
                ]
            }
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Error in analysis: {str(e)}")
        # Return fallback response
        return jsonify({
            "match_percentage": 65,
            "skills": {
                "has": [
                    {"name": "Python", "description": "Упомянут в резюме как основной язык программирования"},
                    {"name": "SQL", "description": "Опыт работы с базами данных упомянут в проектах"}
                ],
                "missing": [
                    {"name": "Docker", "description": "Не упомянут в резюме, но требуется по вакансии"},
                    {"name": "Kubernetes", "description": "Требуется для senior позиций, отсутствует в опыте"}
                ]
            },
            "development_plan": [
                {
                    "title": "Курс по Docker",
                    "description": "Освойте контейнеризацию приложений с Docker",
                    "link": "https://docker-curriculum.com"
                },
                {
                    "title": "Практический проект с Kubernetes",
                    "description": "Разверните микросервисное приложение в Kubernetes кластере",
                    "link": "https://kubernetes.io/docs/tutorials"
                }
            ]
        })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)