# 📘 Blogger Autopost Bot – Product Requirements Document

## 🧭 Overview
Blogger Autopost Bot is a Flask-based automation platform for managing and posting content to multiple Blogger websites using scheduled tasks and AI-generated content from URLs, YouTube videos, PDFs, and images.

---

## 🧱 Key Features
- ✅ Add/manage multiple Blogger sites
- 🧠 Per-site AI model configuration (ChatGPT, Gemini, OpenRouter, etc.)
- 📅 Schedule-based automated posting (repeating and non-repeating)
- 🔗 Content Sources:
  1. Web URL (scraping)
  2. YouTube (transcription)
  3. PDF/Image (OCR)
- 🧩 Dynamic section loading using HTML partials
- 🖼️ Site-specific HTML post templates (multiple per site)
- 📥 Template selection (with preview cards) during schedule creation

---

## 🗂 Folder Structure
```
project-root/
├── main.py
├── config/
│   ├── sites_data.json          # Blogger site configurations
│   └── model_config.json        # Model preferences per site
├── templates/
│   ├── index.html               # Main layout (sidebar + topbar)
│   └── partials/
│       ├── create_site.html
│       ├── sites.html
│       ├── site_detail.html     👈 Loaded dynamically on site card click
│       ├── schedules.html
│       └── config.html
├── static/
│   └── templates/
│       └── <site_name>/         👈 Templates uploaded per site
│            ├── template1.html
│            ├── template2.html
├── utils/
│   ├── sites.py
│   ├── schedules.py
│   ├── config.py
│   ├── post_creator.py
│   ├── youtube_service.py
│   ├── pdf_image_service.py
│   └── ai_engine.py
```

---

## 👤 Site Creation & Viewing Workflow
1. Click “➕ Create Site” from sidebar.
2. Fill form fields:
   - Site name (used as slug/folder)
   - Blogger blog ID Auto-Generating
   - Blogger API key
   - Language drop down with Indian language(default: `en`)
3. POST to `/api/sites`:
   - Data saved to `config/sites_data.json`
   - Folder created in `static/templates/<site_name>/`
   - Renders in “Sites List” view as a card

### 🟨 Site Cards (`sites.html`)
- Display each site as a card (not table)
- Show logo (optional), name, and language
- On click:
  ```js
  fetch(`/load/site/${site_name}`)
  ```
- Loads `partials/site_detail.html` with injected context:
  ```py
  @app.route("/load/site/<site_name>")
  def load_site_detail(site_name):
      site = get_site_by_name(site_name)
      templates = list_site_templates(site_name)
      return render_template("partials/site_detail.html", site=site, templates=templates)
  ```

---

## 🔽 site_detail.html (Per-Site Panel)
When a site card is clicked:
- Source Type selector (`url`, `youtube`, `pdf`, `image`)
- Input fields for:
  - Web link or YouTube URL
  - PDF/Image upload
- Model selection dropdown
- "Post Now" button to trigger `/api/create_post`
- 📅 Schedule Creation Form:
  - Select posting time
  - Repetition checkbox
  - ✅ Select **template** via preview cards with checkboxes
  - Submit to `/api/schedules`

---

## 🎨 HTML Template Management (Per Site)
- Templates stored under: `static/templates/<site_name>/`
- Upload handled via optional drag-drop or file field (future feature)
- site_detail.html reads template filenames and shows:
  - Preview (small portion or rendered HTML)
  - Checkbox to select which one to use in schedule/post

---

## ⚙️ Configuration Panel
- Access: `/load/config`
- Fetches available AI models from OpenRouter/Gemini/static
- On save: POST to `/api/config/<site_name>` with selected model
- Updates `config/model_config.json`

---

## 🔁 Schedule Panel
- Access: `/load/schedules`
- List all scheduled jobs with:
  - Site name
  - Source type and input summary
  - Repeat status and scheduled time
  - Assigned model
  - Selected template name
- Allow edit/delete per schedule

---

## 🧠 AI Content Engines
| Content Source | Engine Used              | Logic                          |
|----------------|--------------------------|---------------------------------|
| URL            | BeautifulSoup            | Scrapes readable article text  |
| YouTube        | youtube_transcript_api   | Transcribes spoken content     |
| PDF            | pdfplumber               | Extracts structured text       |
| Image          | pytesseract              | OCR extraction from image      |
| AI Model       | ChatGPT / Gemini         | Formats clean post content     |

---

## 📡 API Endpoints Summary
| Endpoint                            | Method     | Purpose                                |
|-------------------------------------|------------|----------------------------------------|
| `/api/sites`                        | GET/POST   | Create or list Blogger sites           |
| `/api/sites/<name>`                 | PUT/DELETE | Update or delete a specific site       |
| `/api/schedules`                    | GET/POST   | Add or list all schedules              |
| `/api/schedules/<id>`               | PUT/DELETE | Modify or remove a schedule            |
| `/api/config/<site_name>`           | GET/POST   | Model preferences per site             |
| `/api/create_post`                  | POST       | Create post immediately                |
| `/api/ocr/pdf`, `/api/ocr/image`    | POST       | File-based input extraction            |
| `/api/youtube`                      | POST       | YouTube transcript extraction          |

---

## 🛠 Debugging & Logging
- All incoming requests printed via `print()` in `main.py`
- Responses include HTTP codes and structured error messages
- `utils/sites.py` ensures:
  - Folder `config/` auto-created
  - `sites_data.json` initialized if missing
- Template reading handled with error-tolerant fallback

---

## ✅ Final User Flow
1. Create a new site (name, API, blog ID)
2. See site card in dashboard
3. Click → open detailed input form
4. Upload or auto-detect content source
5. Select AI model and template
6. Either:
   - Post immediately via “Post Now”
   - Or schedule for future post
7. View and manage all schedules/configs anytime

