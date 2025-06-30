# 📘 Blogger Autopost Bot – Product Requirements Document (PRD)

## 🗭 Overview

Blogger Autopost Bot is a Flask-based automation system designed to manage and schedule AI-powered content posting to multiple Blogger websites. It uses templates, schedule rules, and content sources like URLs, PDFs, YouTube videos, and images.

---

## 🧱 Key Features

- ✅ Add/manage Blogger sites
- 🎨 Upload logo per site (shown in site card)
- 🧐 AI model selection per site (ChatGPT, Gemini, etc.)
- 🗓 Schedule-based posting (once or repeat)
- 🔗 Sources:
  - Web URL (article scraping)
  - YouTube (transcription)
  - PDF/Image (OCR)
- 🎨 Multiple HTML templates per site for formatting posts
- 📅 Template previews shown as cards during schedule creation
- 🔹 Dynamic partial-based UI loading

---

## 🗂 Folder Structure

```
project-root/
├── main.py                        # Main Flask app
├── config/
│   ├── sites_data.json            # Saved site details
│   └── model_config.json          # AI model per site
├── static/
│   └── logos/                     # Uploaded site logos
├── templates_repo/
│   └── <site_name>/              # Templates per site
│       ├── template1.html
│       └── template2.html
├── templates/
│   ├── index.html                 # Layout (sidebar + topbar)
│   └── partials/                  # Dynamic sections
│       ├── sites.html
│       ├── create_site.html
│       ├── site_detail.html
│       ├── schedules.html
│       └── config.html
├── utils/                         # All core functionality
│   ├── sites.py
│   ├── schedules.py
│   ├── config.py
│   ├── post_creator.py
│   ├── youtube_service.py
│   ├── pdf_image_service.py
│   └── ai_engine.py
```

---

## 👤 Site Creation & Logo Upload

- Access via “➕ Create Site”
- Inputs:
  - Site name (used as ID and folder slug)
  - Blogger blog ID
  - Blogger API key
  - Language dropdown (default: `en`)
  - Logo upload (optional)
- On submission:
  - POST to `/api/sites`
  - Logo saved as `static/logos/<site_name>.png`
  - Entry stored in `sites_data.json`
  - Directory created: `templates_repo/<site_name>/`

---

## 📈 Sites List (`sites.html`)

- Displays all sites as **cards** (not tables)
- Card contains:
  - Logo
  - Site name
  - Language
- Click card: dynamically loads site panel using:

```js
fetch(`/load/site/<site_name>`)
```

Backed by Flask:

```py
@app.route("/load/site/<site_name>")
def load_site_detail(site_name):
    site = get_site_by_name(site_name)
    templates = list_site_templates(site_name)
    return render_template("partials/site_detail.html", site=site, templates=templates)
```

---

## 🔻 site\_detail.html (Site Dashboard Panel)

When a site is clicked:

- Source type selector (`url`, `youtube`, `pdf`, `image`)
- Input fields:
  - URL or YouTube link
  - PDF or image upload
- AI model selector (loaded from config)
- ⏰ Schedule Creator:
  - Time picker
  - Repeat checkbox
  - **Template selector**:
    - Preview HTML snippets of each `templateX.html`
    - Select via checkbox
- Submit schedule: POST `/api/schedules`
- Or "Post Now": POST `/api/create_post`

---

## 🖌 HTML Templates (Per-Site)

- Stored under `templates_repo/<site_name>/`
- Loaded dynamically using `os.listdir()`
- Previewed using iframe/snippet in UI
- Can be uploaded (optional future feature)
- Used to format final post content

---

## ⚙️ AI Model Configuration (`config.html`)

- URL: `/load/config`
- On load: fetches AI model list (from OpenRouter/Gemini/static)
- POST to `/api/config/<site_name>` with model selection
- Updates `model_config.json`

---

## 🔄 Schedules Management (`schedules.html`)

- URL: `/load/schedules`
- Display all scheduled jobs with:
  - Site name
  - Source type
  - Input summary
  - Scheduled time
  - Repeat status
  - AI model
  - Template name
- Edit/Delete options

---

## 🧬 AI Engine Mapping

| Source  | Module Used           | Description                  |
| ------- | --------------------- | ---------------------------- |
| URL     | `bs4` (BeautifulSoup) | Clean article scraping       |
| YouTube | `youtube_transcript`  | Transcript from spoken video |
| PDF     | `pdfplumber`          | PDF content extraction       |
| Image   | `pytesseract`         | OCR image reading            |
| AI      | `ChatGPT`, `Gemini`   | Content generation/cleaning  |

---

## 📶 Main API Endpoints

| Endpoint                       | Method     | Purpose                    |
| ------------------------------ | ---------- | -------------------------- |
| `/api/sites`                   | GET/POST   | Add or list Blogger sites  |
| `/api/sites/<site_name>`       | PUT/DELETE | Edit/delete site           |
| `/api/config/<site_name>`      | GET/POST   | Model config per site      |
| `/api/create_post`             | POST       | Manually create post       |
| `/api/schedules`               | GET/POST   | Add/list schedules         |
| `/api/schedules/<id>`          | PUT/DELETE | Edit/delete schedule       |
| `/api/ocr/pdf` or `/ocr/image` | POST       | OCR file processing        |
| `/api/youtube`                 | POST       | Extract YouTube transcript |

---

## 🛠️ Debugging & Error Handling

- `main.py` logs all incoming request data
- Missing or invalid data returns HTTP 400/500 with JSON error
- `utils/sites.py` creates `config/` and required JSON files automatically
- Template reading logic ignores missing/invalid templates gracefully

---

## ✅ Final End-to-End Flow

1. User creates a site + logo
2. Bot stores config and renders it in dashboard
3. Clicking card shows inputs and templates
4. User selects content source, model, and template
5. Either:
   - Posts immediately
   - Or creates a schedule
6. Posts are formatted using selected template + model and sent to Blogger
7. User can manage/edit schedules and configuration anytime

