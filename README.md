# ✍️ MUJ Assignment Agent

**Automatically solve assignments and generate realistic handwritten PDFs.**

Read → Solve (AI) → Handwritten PDF

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure
Copy `.env.example` to `.env` and set your **Gemini API key**:
```bash
copy .env.example .env
```
Edit `.env` and add your API key:
```
GEMINI_API_KEY=your_key_here
```
> Get a free key at: https://aistudio.google.com/apikey

### 3. Add Your Student Info
Edit `.env` with your details:
```
STUDENT_NAME=Shiva Kumar
STUDENT_REG_NO=23BSIT001
STUDENT_SECTION=A
STUDENT_COURSE=B.Tech CSE
```

### 4. Run
```bash
python main.py
```

---

## 📁 Project Structure

```
hand writing/
├── main.py                  # CLI entry point (interactive menu)
├── assignment_reader.py     # Reads PDF/DOCX/TXT assignments
├── ai_solver.py             # Gemini AI solver
├── handwriting_generator.py # Handwritten PDF generator
├── config.py                # Settings & configuration
├── test_render.py           # Quick test (no API key needed)
├── requirements.txt         # Python dependencies
├── .env.example             # Config template
├── .env                     # Your config (git-ignored)
├── fonts/                   # Handwriting fonts (.ttf)
│   ├── Caveat.ttf
│   └── IndieFlower-Regular.ttf
├── input/                   # Drop assignment files here
└── output/                  # Generated PDFs appear here
```

---

## 🎯 Usage Modes

### Interactive Mode (recommended)
```bash
python main.py
```
Presents a menu with options:
1. **Full Pipeline** — Read assignment → AI solve → Handwritten PDF
2. **Convert Only** — Text/file → Handwritten PDF (no AI)
3. **Solve Only** — Get AI answers as text (no PDF)
4. **Preview** — Read and display assignment content

### Command Line
```bash
# Full pipeline
python main.py full input/assignment.pdf --subject "Data Structures"

# Solve only (text output)
python main.py solve input/homework.docx

# Convert text to handwritten PDF
python main.py convert input/my_answers.txt
```

### Test Rendering (no API key needed)
```bash
python test_render.py
```

---

## ✍️ Customizing Handwriting

### Fonts
- Place any `.ttf` handwriting font in the `fonts/` folder
- The first font found will be used
- Pre-installed: **Caveat** (cursive) and **Indie Flower** (print)
- Find more at: [Google Fonts](https://fonts.google.com/?category=Handwriting)

### Ink & Style
Edit `.env`:
```ini
# Ink color (dark blue ballpoint)
INK_COLOR_R=15
INK_COLOR_G=25
INK_COLOR_B=105

# Font size
FONT_SIZE=38

# Paper style: blank, lined, ruled
PAGE_STYLE=lined
```

---

## 🤖 How It Works

1. **Read**: Extracts text from PDF/DOCX/TXT assignment files
2. **Solve**: Sends questions to Google Gemini AI with a student persona prompt
3. **Render**: Generates handwriting page-by-page with:
   - Character-level position jitter (natural variation)
   - Ink color/density variation (pen pressure simulation)
   - Lined paper background with subtle texture
   - Proper header with student info
   - Multi-page support with page numbers
4. **Export**: Saves as high-quality PDF

---

## ⚠️ Notes

- This tool is for **educational/personal use only**
- Always review AI-generated answers before submission
- The handwriting quality depends on the font you choose
- For best results, use fonts like Caveat, Indie Flower, or your own handwriting font
