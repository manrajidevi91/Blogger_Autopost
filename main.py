from flask import Flask, render_template, request, jsonify
import os
from utils.config import (
    load_sites_data,
    save_sites_data,
    load_ai_config,
    save_ai_config,
    get_credentials_dir,
    save_client_secret,
)
from utils.sites import get_site_by_name, list_site_templates
from utils.post_creator import create_post
from utils.schedules import (
    load_schedules_data,
    save_schedules_data,
    register_jobs,
)
from apscheduler.schedulers.background import BackgroundScheduler
from utils.youtube_service import get_youtube_transcript
from utils.pdf_image_service import extract_text_from_pdf, extract_text_from_image
import shutil

app = Flask(__name__)

# Initialize scheduler
scheduler = BackgroundScheduler()

# Register existing jobs with the scheduler
def load_jobs():
    register_jobs(scheduler)

# Log each request method and path
@app.before_request
def log_request_info():
    print(f"{request.method} {request.path}")

@app.route('/')
def index():
    return render_template('index.html', initial_site_name=None)


@app.route('/sites')
@app.route('/create_site')
@app.route('/schedules')
@app.route('/config')
@app.route('/templates')
def spa_routes():
    """Serve the SPA entry point for top-level pages."""
    return render_template('index.html', initial_site_name=None)


@app.route('/sites/<site_name>')
def site_page(site_name):
    if not get_site_by_name(site_name):
        return render_template('index.html', initial_site_name=None), 404
    return render_template('index.html', initial_site_name=site_name)

@app.route('/templates/<site_name>')
def templates_page(site_name):
    if not get_site_by_name(site_name):
        return render_template('index.html', initial_site_name=None), 404
    return render_template('index.html', initial_site_name=None)

@app.route('/api/sites', methods=['GET', 'POST'])
def api_sites():
    if request.method == 'POST':
        site_name = request.form.get('name')
        if not site_name:
            return jsonify({'error': 'Site name is required'}), 400

        blog_id = request.form.get('blog_id')
        language = request.form.get('language')

        cred_dir = get_credentials_dir(site_name)
        os.makedirs(cred_dir, exist_ok=True)

        cred_path = None
        if 'client_secret' in request.files:
            file = request.files['client_secret']
            if file.filename:
                cred_path = save_client_secret(site_name, file)

        logo_url = None
        if 'site_logo' in request.files:
            logo_file = request.files['site_logo']
            if logo_file.filename:
                logos_dir = os.path.join('static', 'logos')
                os.makedirs(logos_dir, exist_ok=True)
                logo_path = os.path.join(logos_dir, f"{site_name}.png")
                logo_file.save(logo_path)
                logo_url = f"/static/logos/{site_name}.png"

        site_data = {
            'name': site_name,
            'blog_id': blog_id,
            'language': language,
            'credential_path': cred_path,
        }
        if logo_url:
            site_data['logo'] = logo_url

        sites = load_sites_data()
        sites[site_name] = site_data
        save_sites_data(sites)

        # Create site-specific template folder
        site_template_path = os.path.join('static', 'templates', site_name)
        os.makedirs(site_template_path, exist_ok=True)

        return jsonify({'message': 'Site created successfully', 'site': site_data}), 201

    elif request.method == 'GET':
        sites = load_sites_data()
        return jsonify(sites)

@app.route('/api/sites/<name>', methods=['PUT', 'DELETE'])
def api_sites_name(name):
    sites = load_sites_data()
    if request.method == 'PUT':
        site_data = request.json
        if name not in sites:
            return jsonify({'error': 'Site not found'}), 404
        sites[name].update(site_data)
        save_sites_data(sites)
        return jsonify({'message': f'Site {name} updated successfully', 'site': sites[name]}), 200
    elif request.method == 'DELETE':
        if name not in sites:
            return jsonify({'error': 'Site not found'}), 404
        del sites[name]
        save_sites_data(sites)
        # Also remove the site-specific template folder
        site_template_path = os.path.join('static', 'templates', name)
        if os.path.exists(site_template_path):
            import shutil
            shutil.rmtree(site_template_path)
        return jsonify({'message': f'Site {name} deleted successfully'}), 200

@app.route("/load/site/<site_name>")
def load_site_detail(site_name):
    site = get_site_by_name(site_name)
    templates = list_site_templates(site_name)
    return render_template("partials/site_detail.html", site=site, templates=templates)

@app.route('/load/sites')
def load_sites():
    sites = load_sites_data()
    return render_template('partials/sites.html', sites=sites)

@app.route('/load/create_site')
def load_create_site():
    return render_template('partials/create_site.html')

@app.route('/load/templates')
def load_templates():
    sites = load_sites_data()
    return render_template('partials/templates.html', sites=sites)

@app.route('/load/templates/<site_name>')
def load_site_templates(site_name):
    site = get_site_by_name(site_name)
    templates = list_site_templates(site_name)
    return render_template('partials/site_templates.html', site=site, templates=templates)

@app.route('/api/create_post', methods=['POST'])
def api_create_post():
    data = request.json
    site_name = data.get('site_name')
    content_source = data.get('content_source')
    ai_model = data.get('ai_model')
    template = data.get('template')
    source_input = data.get('source_input') # e.g., URL, YouTube URL, PDF/Image file

    if not all([site_name, content_source, ai_model, template, source_input]):
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        # This function will handle the logic of fetching content, generating with AI, and posting
        result = create_post(site_name, content_source, ai_model, template, source_input)
        return jsonify({'message': 'Post creation initiated', 'result': result}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/schedules', methods=['GET', 'POST'])
def api_schedules():
    if request.method == 'POST':
        schedule_data = request.json
        schedules = load_schedules_data()
        schedule_id = str(len(schedules) + 1) # Simple ID generation
        schedules[schedule_id] = schedule_data
        save_schedules_data(schedules)
        return jsonify({'message': 'Schedule created successfully', 'schedule': schedule_data}), 201

    elif request.method == 'GET':
        schedules = load_schedules_data()
        return jsonify(schedules)

@app.route('/api/upload_template', methods=['POST'])
def upload_template():
    if 'template_file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['template_file']
    site_name = request.form.get('site_name')

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if not site_name:
        return jsonify({'error': 'Site name is missing'}), 400

    if file and file.filename.endswith('.html'):
        site_template_path = os.path.join('static', 'templates', site_name)
        os.makedirs(site_template_path, exist_ok=True)
        filepath = os.path.join(site_template_path, file.filename)
        file.save(filepath)
        return jsonify({'message': 'Template uploaded successfully'}), 200
    else:
        return jsonify({'error': 'Invalid file type. Only HTML files are allowed.'}), 400

@app.route('/api/templates/<site_name>/<template_name>', methods=['GET', 'PUT', 'DELETE'])
def api_template(site_name, template_name):
    """Fetch, update, or delete a site template."""
    template_path = os.path.join('static', 'templates', site_name, template_name)

    if request.method == 'GET':
        if os.path.exists(template_path):
            with open(template_path, 'r', encoding='utf-8') as f:
                return jsonify({'content': f.read()})
        return jsonify({'error': 'Template not found'}), 404

    if request.method == 'PUT':
        data = request.json or {}
        content = data.get('content')
        if content is None:
            return jsonify({'error': 'No content provided'}), 400
        os.makedirs(os.path.dirname(template_path), exist_ok=True)
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return jsonify({'message': 'Template updated successfully'}), 200

    if request.method == 'DELETE':
        if os.path.exists(template_path):
            os.remove(template_path)
            return jsonify({'message': 'Template deleted successfully'}), 200
        return jsonify({'error': 'Template not found'}), 404


@app.route('/api/templates/<site_name>/<template_name>/replace', methods=['POST'])
def replace_template(site_name, template_name):
    """Replace an existing template with an uploaded file."""
    if 'template_file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['template_file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if not file.filename.endswith('.html'):
        return jsonify({'error': 'Invalid file type. Only HTML files are allowed.'}), 400

    template_path = os.path.join('static', 'templates', site_name, template_name)
    os.makedirs(os.path.dirname(template_path), exist_ok=True)
    file.save(template_path)
    return jsonify({'message': 'Template replaced successfully'}), 200

@app.route('/load/schedules')
def load_schedules():
    schedules = load_schedules_data()
    return render_template('partials/schedules.html', schedules=schedules)

@app.route('/api/schedules/<schedule_id>', methods=['PUT', 'DELETE'])
def api_schedules_id(schedule_id):
    schedules = load_schedules_data()
    if request.method == 'PUT':
        schedule_data = request.json
        if schedule_id not in schedules:
            return jsonify({'error': 'Schedule not found'}), 404
        schedules[schedule_id].update(schedule_data)
        save_schedules_data(schedules)
        return jsonify({'message': f'Schedule {schedule_id} updated successfully', 'schedule': schedules[schedule_id]}), 200
    elif request.method == 'DELETE':
        if schedule_id in schedules:
            del schedules[schedule_id]
            save_schedules_data(schedules)
            return jsonify({'message': f'Schedule {schedule_id} deleted successfully'}), 200
        else:
            return jsonify({'error': f'Schedule {schedule_id} not found'}), 404

@app.route('/load/config')
def load_config():
    ai_config = load_ai_config()
    available_providers = ['OpenAI', 'Gemini', 'OpenRouter', 'Ollama']
    return render_template(
        'partials/config.html',
        ai_config=ai_config,
        available_providers=available_providers,
    )

@app.route('/api/config', methods=['POST'])
def api_config():
    """Save global AI provider and API key."""
    data = request.json
    provider = data.get('provider')
    api_key = data.get('api_key')

    if not provider or not api_key:
        return jsonify({'error': 'Provider and API key are required'}), 400

    save_ai_config({'provider': provider, 'api_key': api_key})

    return jsonify({'message': 'AI configuration saved successfully'}), 200

@app.route('/api/ocr/pdf', methods=['POST'])
def api_ocr_pdf():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and file.filename.endswith('.pdf'):
        filepath = os.path.join('uploads', file.filename)
        os.makedirs('uploads', exist_ok=True)
        file.save(filepath)
        extracted_text = extract_text_from_pdf(filepath)
        os.remove(filepath) # Clean up the uploaded file
        if extracted_text:
            return jsonify({'content': extracted_text}), 200
        else:
            return jsonify({'error': 'Failed to extract text from PDF'}), 500
    else:
        return jsonify({'error': 'Invalid file type. Only PDF files are allowed.'}), 400

@app.route('/api/ocr/image', methods=['POST'])
def api_ocr_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
        filepath = os.path.join('uploads', file.filename)
        os.makedirs('uploads', exist_ok=True)
        file.save(filepath)
        extracted_text = extract_text_from_image(filepath)
        os.remove(filepath) # Clean up the uploaded file
        if extracted_text:
            return jsonify({'content': extracted_text}), 200
        else:
            return jsonify({'error': 'Failed to extract text from image'}), 500
    else:
        return jsonify({'error': 'Invalid file type. Only image files are allowed.'}), 400

@app.route('/api/youtube', methods=['POST'])
def api_youtube():
    data = request.json
    youtube_url = data.get('url')
    if not youtube_url:
        return jsonify({'error': 'YouTube URL is required'}), 400

    try:
        # Simple parsing to get video ID
        video_id = youtube_url.split('v=')[-1].split('&')[0]
        transcript = get_youtube_transcript(video_id)
        if transcript:
            return jsonify({'transcript': transcript}), 200
        else:
            return jsonify({'error': 'Failed to get YouTube transcript'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/models/<provider>', methods=['GET'])
def get_models_for_provider(provider):
    from utils.config import load_ai_config
    import requests

    cfg = load_ai_config()
    api_key = cfg.get("api_key")

    try:
        if provider == "openai":
            headers = {"Authorization": f"Bearer {api_key}"}
            res = requests.get("https://api.openai.com/v1/models", headers=headers, timeout=10)
            model_ids = [m['id'] for m in res.json().get("data", []) if m["id"].startswith("gpt-")]
            return jsonify(sorted(set(model_ids)))

        elif provider == "openrouter":
            headers = {"Authorization": f"Bearer {api_key}"}
            res = requests.get("https://openrouter.ai/api/v1/models", headers=headers, timeout=10)
            model_ids = [m["id"] for m in res.json().get("data", [])]
            return jsonify(model_ids)

        elif provider == "ollama":
            res = requests.get("http://localhost:11434/api/tags", timeout=5)
            model_names = [m["name"] for m in res.json().get("models", [])]
            return jsonify(model_names)

        elif provider == "gemini":
            # Gemini does not support dynamic listing (hardcoded fallback)
            return jsonify(["gemini-pro", "gemini-pro-vision"])

        else:
            return jsonify([])

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    load_jobs()
    scheduler.start()
    app.run(port=3000, debug=True)

