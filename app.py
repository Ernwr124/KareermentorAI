from flask import Flask, request, jsonify, render_template_string
import os
import requests
import PyPDF2
import docx
from werkzeug.utils import secure_filename
import io

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# === Исправленный HTML шаблон ===
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Карьерный Ментор AI</title>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <style>
    :root {
      --primary: #4361ee;
      --primary-dark: #3a56d4;
      --secondary: #7209b7;
      --success: #06d6a0;
      --warning: #ffd166;
      --danger: #ef476f;
      --dark: #1a1a2e;
      --light: #f8f9fa;
      --gray: #6c757d;
      --border: #e0e0e0;
      --shadow: 0 4px 20px rgba(0,0,0,0.08);
      --radius: 12px;
      --transition: all 0.3s ease;
    }

    * { 
      box-sizing: border-box; 
      margin: 0;
      padding: 0;
    }

    body {
      font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
      background: linear-gradient(135deg, #f5f7fa 0%, #e4edf5 100%);
      color: #333;
      line-height: 1.6;
      min-height: 100vh;
      padding: 20px;
    }

    .container {
      max-width: 900px;
      margin: 2rem auto;
      background: white;
      border-radius: var(--radius);
      box-shadow: var(--shadow);
      overflow: hidden;
    }

    header {
      background: linear-gradient(120deg, var(--primary), var(--secondary));
      color: white;
      padding: 2.5rem 2rem;
      text-align: center;
    }

    header h1 {
      font-size: 2.5rem;
      margin-bottom: 0.5rem;
      font-weight: 800;
    }

    header p {
      font-size: 1.1rem;
      opacity: 0.9;
      max-width: 600px;
      margin: 0 auto;
    }

    .content {
      padding: 2rem;
    }

    .upload-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 1.5rem;
      margin-bottom: 2rem;
    }

    @media (max-width: 768px) {
      .upload-grid {
        grid-template-columns: 1fr;
      }
    }

    .upload-card {
      background: #fafbff;
      border: 2px dashed var(--border);
      border-radius: var(--radius);
      padding: 1.5rem;
      text-align: center;
      transition: var(--transition);
      cursor: pointer;
    }

    .upload-card:hover {
      border-color: var(--primary);
      background: #f0f4ff;
    }

    .upload-card.active {
      border-style: solid;
      border-color: var(--primary);
      background: #e8f0fe;
    }

    .upload-icon {
      font-size: 2.5rem;
      color: var(--primary);
      margin-bottom: 1rem;
    }

    .upload-card h3 {
      color: var(--dark);
      margin-bottom: 0.5rem;
    }

    .upload-card p {
      color: var(--gray);
      font-size: 0.9rem;
    }

    .file-input {
      display: none;
    }

    .analyze-btn {
      width: 100%;
      padding: 1.2rem;
      background: linear-gradient(120deg, var(--primary), var(--secondary));
      color: white;
      border: none;
      border-radius: var(--radius);
      font-size: 1.1rem;
      font-weight: 600;
      cursor: pointer;
      transition: var(--transition);
      box-shadow: 0 4px 15px rgba(67, 97, 238, 0.3);
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 10px;
    }

    .analyze-btn:hover:not(:disabled) {
      transform: translateY(-2px);
      box-shadow: 0 6px 20px rgba(67, 97, 238, 0.4);
    }

    .analyze-btn:disabled {
      background: var(--gray);
      cursor: not-allowed;
      transform: none;
      box-shadow: none;
    }

    .loading {
      text-align: center;
      padding: 2rem;
      display: none;
    }

    .spinner {
      width: 50px;
      height: 50px;
      border: 5px solid rgba(67, 97, 238, 0.2);
      border-top: 5px solid var(--primary);
      border-radius: 50%;
      animation: spin 1s linear infinite;
      margin: 0 auto 1rem;
    }

    @keyframes spin {
      0% { transform: rotate(0deg); }
      100% { transform: rotate(360deg); }
    }

    .results {
      margin-top: 2rem;
      padding: 2rem;
      background: #f8f9ff;
      border-radius: var(--radius);
      display: none;
    }

    .results h2 {
      color: var(--dark);
      margin-bottom: 1.5rem;
      text-align: center;
      font-size: 1.8rem;
    }

    .error {
      background: #fff5f5;
      color: #c53030;
      padding: 1.5rem;
      border-radius: var(--radius);
      border-left: 4px solid var(--danger);
      margin: 1rem 0;
    }

    .file-name {
      font-size: 0.85rem;
      color: var(--primary);
      margin-top: 0.5rem;
      font-weight: 500;
    }

    footer {
      text-align: center;
      padding: 2rem;
      color: var(--gray);
      font-size: 0.9rem;
    }

    .ai-badge {
      display: inline-flex;
      align-items: center;
      gap: 5px;
      background: #e8f0fe;
      color: var(--primary);
      padding: 0.3rem 0.8rem;
      border-radius: 20px;
      font-size: 0.85rem;
      font-weight: 500;
      margin-top: 1rem;
    }
  </style>
</head>
<body>
  <div class="container">
    <header>
      <h1><i class="fas fa-rocket"></i> Карьерный Ментор AI</h1>
      <p>Твой путь к работе мечты — с искусственным интеллектом</p>
      <div class="ai-badge">
        <i class="fas fa-brain"></i> Powered by PHI4
      </div>
    </header>

    <div class="content">
      <div class="upload-grid">
        <div class="upload-card" id="resume-card">
          <div class="upload-icon">
            <i class="fas fa-file-alt"></i>
          </div>
          <h3>Резюме кандидата</h3>
          <p>Загрузите PDF, DOCX или TXT файл</p>
          <input type="file" id="resume" class="file-input" accept=".txt,.pdf,.docx" />
          <div class="file-name" id="resume-name">Файл не выбран</div>
        </div>

        <div class="upload-card" id="vacancy-card">
          <div class="upload-icon">
            <i class="fas fa-briefcase"></i>
          </div>
          <h3>Описание вакансии</h3>
          <p>Загрузите PDF, DOCX или TXT файл</p>
          <input type="file" id="vacancy" class="file-input" accept=".txt,.pdf,.docx" />
          <div class="file-name" id="vacancy-name">Файл не выбран</div>
        </div>
      </div>

      <button id="analyze-btn" class="analyze-btn" disabled>
        <i class="fas fa-chart-line"></i> Проанализировать карьерные перспективы
      </button>

      <div class="loading" id="loading">
        <div class="spinner"></div>
        <h3>Анализируем ваш профиль...</h3>
        <p>Искусственный интеллект изучает ваше резюме и требования вакансии</p>
      </div>

      <div class="results" id="results">
        <h2><i class="fas fa-chart-pie"></i> Результаты анализа</h2>
        <div id="results-content"></div>
      </div>
    </div>

    <footer>
      <p>© 2025 Карьерный Ментор AI | Интеллектуальный анализ карьерных возможностей</p>
    </footer>
  </div>

  <script>
    const resumeInput = document.getElementById("resume");
    const vacancyInput = document.getElementById("vacancy");
    const resumeCard = document.getElementById("resume-card");
    const vacancyCard = document.getElementById("vacancy-card");
    const resumeName = document.getElementById("resume-name");
    const vacancyName = document.getElementById("vacancy-name");
    const analyzeBtn = document.getElementById("analyze-btn");
    const loading = document.getElementById("loading");
    const results = document.getElementById("results");
    const resultsContent = document.getElementById("results-content");

    // Добавляем обработчики кликов на карточки
    resumeCard.addEventListener("click", () => resumeInput.click());
    vacancyCard.addEventListener("click", () => vacancyInput.click());

    // Обработчики выбора файлов
    resumeInput.addEventListener("change", function() {
      if (this.files.length) {
        resumeName.textContent = this.files[0].name;
        resumeCard.classList.add("active");
      } else {
        resumeName.textContent = "Файл не выбран";
        resumeCard.classList.remove("active");
      }
      checkFiles();
    });

    vacancyInput.addEventListener("change", function() {
      if (this.files.length) {
        vacancyName.textContent = this.files[0].name;
        vacancyCard.classList.add("active");
      } else {
        vacancyName.textContent = "Файл не выбран";
        vacancyCard.classList.remove("active");
      }
      checkFiles();
    });

    function checkFiles() {
      analyzeBtn.disabled = !(resumeInput.files.length && vacancyInput.files.length);
    }

    analyzeBtn.addEventListener("click", async () => {
      const resume = resumeInput.files[0];
      const vacancy = vacancyInput.files[0];

      const formData = new FormData();
      formData.append("resume", resume);
      formData.append("vacancy", vacancy);

      resultsContent.innerHTML = "";
      loading.style.display = "block";
      results.style.display = "none";
      analyzeBtn.disabled = true;

      try {
        const response = await fetch("/analyze", {
          method: "POST",
          body: formData,
        });

        const data = await response.json();

        loading.style.display = "none";

        if (data.error) {
          resultsContent.innerHTML = `<div class="error"><i class="fas fa-exclamation-triangle"></i> <strong>Ошибка:</strong> ${data.error}</div>`;
        } else {
          resultsContent.innerHTML = `<pre>${data.result}</pre>`;
        }
        
        results.style.display = "block";
      } catch (err) {
        loading.style.display = "none";
        resultsContent.innerHTML = `<div class="error"><i class="fas fa-exclamation-triangle"></i> <strong>Ошибка соединения:</strong> ${err.message}</div>`;
        results.style.display = "block";
      } finally {
        analyzeBtn.disabled = false;
      }
    });
  </script>
</body>
</html>
'''

# === Функции обработки файлов ===

def read_pdf(file_stream):
    """Чтение PDF файла"""
    try:
        reader = PyPDF2.PdfReader(file_stream)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text.strip()
    except Exception as e:
        raise Exception(f"Ошибка чтения PDF: {str(e)}")

def read_docx(file_stream):
    """Чтение DOCX файла"""
    try:
        doc = docx.Document(file_stream)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text.strip()
    except Exception as e:
        raise Exception(f"Ошибка чтения DOCX: {str(e)}")

def read_txt(file_stream):
    """Чтение TXT файла"""
    try:
        content = file_stream.read()
        # Попробуем разные кодировки
        try:
            return content.decode('utf-8').strip()
        except UnicodeDecodeError:
            return content.decode('windows-1251').strip()
    except Exception as e:
        raise Exception(f"Ошибка чтения TXT: {str(e)}")

def read_file_from_request(file_obj):
    """Универсальная функция чтения файла из запроса"""
    if not file_obj or not file_obj.filename:
        return None
    
    filename = secure_filename(file_obj.filename)
    _, ext = os.path.splitext(filename)
    
    # Перемещаем указатель в начало
    file_obj.seek(0)
    
    try:
        if ext.lower() == '.pdf':
            return read_pdf(file_obj)
        elif ext.lower() == '.docx':
            return read_docx(file_obj)
        elif ext.lower() == '.txt':
            return read_txt(file_obj)
        else:
            # Попробуем как текст
            file_obj.seek(0)
            content = file_obj.read()
            try:
                return content.decode('utf-8').strip()
            except:
                return content.decode('windows-1251').strip()
    except Exception as e:
        raise Exception(f"Не удалось прочитать файл {filename}: {str(e)}")

def ask_ollama(prompt, model="phi4-mini:3.8b"):
    """Запрос к Ollama"""
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False
            },
            timeout=300  # 5 минут таймаут
        )
        if response.status_code == 200:
            return response.json()["response"].strip()
        else:
            return f"Ошибка Ollama: {response.status_code} - {response.text}"
    except requests.exceptions.ConnectionError:
        return "Ошибка: Не удалось подключиться к Ollama. Убедитесь, что он запущен."
    except requests.exceptions.Timeout:
        return "Ошибка: Таймаут при подключении к Ollama."
    except Exception as e:
        return f"Ошибка подключения к Ollama: {str(e)}"

def build_prompt(resume_text, vacancy_text):
    """Формирование промпта для LLM"""
    return f"""
Ты — эксперт по карьерному развитию и подбору персонала. Проанализируй резюме кандидата и описание вакансии, и дай структурированный ответ на русском языке.

РЕЗЮМЕ:
{resume_text}

ВАКАНСИЯ:
{vacancy_text}

Выполни следующие шаги:

1. Извлеки из резюме:
   - Навыки (hard и soft skills)
   - Опыт работы (должности, компании, длительность)
   - Образование
   - Проекты (если есть)

2. Извлеки из вакансии:
   - Обязательные навыки
   - Желаемый опыт
   - Требуемое образование
   - Ключевые обязанности

3. Сравни и определи:
   - Какие навыки из вакансии уже есть у кандидата (список)
   - Каких навыков или опыта не хватает (список)
   - Оценка соответствия: в процентах (объясни кратко, как считал)

4. Составь ПЛАН РАЗВИТИЯ:
   - 3–5 курсов (с названиями и темами, без ссылок)
   - 2–3 книги или статьи
   - 1–2 практических проекта, которые помогут закрыть пробелы

Формат ответа (ТОЧНО СОБЛЮДАЙ РАЗМЕТКУ):

### ОЦЕНКА СООТВЕТСТВИЯ
[XX%] — краткое объяснение

### НАВЫКИ ЕСТЬ
- [навык 1]
- [навык 2]

### НАВЫКИ НЕ ХВАТАЕТ
- [навык 1]
- [навык 2]

### ПЛАН РАЗВИТИЯ
**Курсы:**
- [курс 1] — [тема]
- [курс 2] — [тема]

**Книги и статьи:**
- [книга 1]
- [статья 1]

**Проекты:**
- [проект 1]: [описание]
- [проект 2]: [описание]
""".strip()

# === Маршруты ===

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        resume_file = request.files.get("resume")
        vacancy_file = request.files.get("vacancy")

        if not resume_file or not resume_file.filename:
            return jsonify({"error": "Резюме не загружено"}), 400

        if not vacancy_file or not vacancy_file.filename:
            return jsonify({"error": "Описание вакансии не загружено"}), 400

        # Читаем файлы
        resume_text = read_file_from_request(resume_file)
        vacancy_text = read_file_from_request(vacancy_file)

        if not resume_text:
            return jsonify({"error": "Не удалось прочитать резюме"}), 400

        if not vacancy_text:
            return jsonify({"error": "Не удалось прочитать описание вакансии"}), 400

        # Формируем промпт и отправляем в Ollama
        prompt = build_prompt(resume_text, vacancy_text)
        ai_response = ask_ollama(prompt)

        return jsonify({"result": ai_response})

    except Exception as e:
        return jsonify({"error": f"Ошибка обработки: {str(e)}"}), 500

if __name__ == "__main__":
    print("🚀 Карьерный Ментор AI запускается...")
    print("📝 Убедитесь, что Ollama запущен: ollama run llama3")
    app.run(debug=True, host='0.0.0.0', port=5000)