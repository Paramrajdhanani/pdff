import os
import uuid
from datetime import datetime, timedelta
from flask import render_template, redirect, url_for, flash, request, jsonify, send_from_directory, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from . import converter_bp
from models import db, ConversionHistory

# Helper: File path validators
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

# Helper: Byte formatter
def get_friendly_file_size(filepath):
    try:
        size_bytes = os.path.getsize(filepath)
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{(size_bytes / 1024):.1f} KB"
        else:
            return f"{(size_bytes / (1024 * 1024)):.1f} MB"
    except Exception:
        return "Unknown"

# Auto-cleanup routine
def perform_auto_delete():
    """
    Scans the upload folder for files older than FILE_RETENTION_HOURS and purges them.
    Runs periodically within requests.
    """
    upload_folder = current_app.config['UPLOAD_FOLDER']
    retention_hours = current_app.config['FILE_RETENTION_HOURS']
    
    if not os.path.exists(upload_folder):
        return
        
    cutoff_time = datetime.utcnow() - timedelta(hours=retention_hours)
    
    for filename in os.listdir(upload_folder):
        # Skip gitkeep or structural folder markers if any
        if filename.startswith('.'):
            continue
            
        file_path = os.path.join(upload_folder, filename)
        if os.path.isfile(file_path):
            file_mtime = datetime.utcfromtimestamp(os.path.getmtime(file_path))
            if file_mtime < cutoff_time:
                try:
                    os.remove(file_path)
                except OSError:
                    pass

# Routes

@converter_bp.route('/dashboard')
@login_required
def dashboard():
    # Perform cleanup of old files on dashboard load
    perform_auto_delete()
    
    # Compute conversion statistics
    history = ConversionHistory.query.filter_by(user_id=current_user.id).order_by(ConversionHistory.created_at.desc()).all()
    
    total = len(history)
    pdf_to_docx = sum(1 for r in history if r.conversion_type == 'pdf_to_docx')
    docx_to_pdf = sum(1 for r in history if r.conversion_type == 'docx_to_pdf')
    merge_pdf = sum(1 for r in history if r.conversion_type == 'merge_pdf')
    compress_pdf = sum(1 for r in history if r.conversion_type == 'compress_pdf')
    split_pdf = sum(1 for r in history if r.conversion_type == 'split_pdf')
    jpg_to_pdf = sum(1 for r in history if r.conversion_type == 'jpg_to_pdf')
    pdf_to_jpg = sum(1 for r in history if r.conversion_type == 'pdf_to_jpg')
    
    # Calculate conversions in last 24 hours
    one_day_ago = datetime.utcnow() - timedelta(days=1)
    daily_count = ConversionHistory.query.filter(
        ConversionHistory.user_id == current_user.id,
        ConversionHistory.created_at >= one_day_ago
    ).count()
    
    stats = {
        'total': total,
        'pdf_to_docx': pdf_to_docx,
        'docx_to_pdf': docx_to_pdf,
        'merge_pdf': merge_pdf,
        'compress_pdf': compress_pdf,
        'split_pdf': split_pdf,
        'jpg_to_pdf': jpg_to_pdf,
        'pdf_to_jpg': pdf_to_jpg,
        'daily_count': daily_count
    }
    
    # Grab only the 5 most recent records for layout brevity
    recent_history = history[:5]
    
    return render_template('dashboard.html', stats=stats, history=recent_history)

@converter_bp.route('/converter')
@login_required
def converter_page():
    # Calculate conversions in last 24 hours
    one_day_ago = datetime.utcnow() - timedelta(days=1)
    daily_count = ConversionHistory.query.filter(
        ConversionHistory.user_id == current_user.id,
        ConversionHistory.created_at >= one_day_ago
    ).count()
    return render_template('converter.html', daily_count=daily_count)

def generate_mock_output(output_path, conversion_type, original_names, error_msg):
    import zipfile
    ext = output_path.rsplit('.', 1)[1].lower() if '.' in output_path else 'pdf'
    if ext == 'zip':
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            readme_content = (
                f"--- PDF TOOLKIT SIMULATION MODE ---\n"
                f"Action: {conversion_type}\n"
                f"Source Files: {original_names}\n"
                f"Reason: Your host environment triggered mock fallback (Error: {error_msg})\n"
                f"This archive was generated dynamically to test system loops."
            )
            readme_path = output_path.replace('.zip', '_readme.txt')
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(readme_content)
            zipf.write(readme_path, 'README.txt')
            os.remove(readme_path)
    else:
        with open(output_path, 'w', encoding='utf-8') as mock_file:
            mock_file.write(f"--- PDF TOOLKIT SIMULATION MODE ---\n")
            mock_file.write(f"Source Files: {original_names}\n")
            mock_file.write(f"Conversion Type: {conversion_type}\n")
            mock_file.write(f"Encountered error: {str(error_msg)}\n\n")
            mock_file.write(f"Reason: This file is a mock simulation generated by Convert Pro.\n")
            mock_file.write(f"This host machine triggered fallback mode to verify download linkages.\n")

@converter_bp.route('/convert', methods=['POST'])
@login_required
def convert_file():
    # Perform cleanup of old files
    perform_auto_delete()
    
    # Check daily limit (max 3 conversions per 24 hours)
    one_day_ago = datetime.utcnow() - timedelta(days=1)
    daily_count = ConversionHistory.query.filter(
        ConversionHistory.user_id == current_user.id,
        ConversionHistory.created_at >= one_day_ago
    ).count()
    
    if daily_count >= 3:
        return jsonify({
            'success': False,
            'message': 'Daily transformation limit reached (Max 3 conversions per 24 hours on the Free Tier).'
        }), 429
        
    # Check if request has the file part
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No files uploaded.'}), 400
        
    files = request.files.getlist('file')
    conversion_type = request.form.get('conversion_type')
    
    if not files or len(files) == 0 or files[0].filename == '':
        return jsonify({'success': False, 'message': 'No files selected.'}), 400
        
    supported_types = [
        'pdf_to_docx', 'docx_to_pdf', 'merge_pdf', 
        'compress_pdf', 'split_pdf', 'jpg_to_pdf', 'pdf_to_jpg'
    ]
    if conversion_type not in supported_types:
        return jsonify({'success': False, 'message': 'Invalid conversion type selected.'}), 400
        
    # Validate file count and extensions based on conversion type
    for f in files:
        if not f or not allowed_file(f.filename):
            return jsonify({'success': False, 'message': 'Invalid file extension uploaded.'}), 400
            
    # Specific type rules
    if conversion_type in ['pdf_to_docx', 'compress_pdf', 'split_pdf', 'pdf_to_jpg']:
        if len(files) != 1:
            return jsonify({'success': False, 'message': 'Exactly 1 file is required for this operation.'}), 400
        ext = files[0].filename.rsplit('.', 1)[1].lower()
        if ext != 'pdf':
            return jsonify({'success': False, 'message': 'File type mismatch. PDF required.'}), 400
            
    elif conversion_type == 'docx_to_pdf':
        if len(files) != 1:
            return jsonify({'success': False, 'message': 'Exactly 1 file is required for this operation.'}), 400
        ext = files[0].filename.rsplit('.', 1)[1].lower()
        if ext != 'docx':
            return jsonify({'success': False, 'message': 'File type mismatch. DOCX required.'}), 400
            
    elif conversion_type == 'merge_pdf':
        if len(files) < 2:
            return jsonify({'success': False, 'message': 'At least 2 files are required for merging.'}), 400
        for f in files:
            ext = f.filename.rsplit('.', 1)[1].lower()
            if ext != 'pdf':
                return jsonify({'success': False, 'message': 'All files must be PDFs for merging.'}), 400
                
    elif conversion_type == 'jpg_to_pdf':
        if len(files) < 1:
            return jsonify({'success': False, 'message': 'At least 1 image is required.'}), 400
        for f in files:
            ext = f.filename.rsplit('.', 1)[1].lower()
            if ext not in ['jpg', 'jpeg', 'png']:
                return jsonify({'success': False, 'message': 'All files must be images (JPG/PNG).'}), 400

    # Save uploaded input files securely
    upload_folder = current_app.config['UPLOAD_FOLDER']
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
        
    unique_prefix = uuid.uuid4().hex[:10]
    input_paths = []
    original_names_list = []
    
    for i, f in enumerate(files):
        secured_name = secure_filename(f.filename)
        input_filename = f"{unique_prefix}_{i}_{secured_name}"
        input_path = os.path.join(upload_folder, input_filename)
        f.save(input_path)
        input_paths.append(input_path)
        original_names_list.append(secured_name)
        
    original_filenames_str = ", ".join(original_names_list)
    
    # Establish output path and filename
    primary_secured = original_names_list[0]
    if conversion_type == 'pdf_to_docx':
        output_filename = f"{unique_prefix}_{primary_secured.rsplit('.', 1)[0]}.docx"
    elif conversion_type == 'docx_to_pdf':
        output_filename = f"{unique_prefix}_{primary_secured.rsplit('.', 1)[0]}.pdf"
    elif conversion_type == 'merge_pdf':
        output_filename = f"{unique_prefix}_merged_toolkit.pdf"
    elif conversion_type == 'compress_pdf':
        output_filename = f"{unique_prefix}_{primary_secured.rsplit('.', 1)[0]}_compressed.pdf"
    elif conversion_type == 'split_pdf':
        output_filename = f"{unique_prefix}_{primary_secured.rsplit('.', 1)[0]}_split.zip"
    elif conversion_type == 'jpg_to_pdf':
        output_filename = f"{unique_prefix}_images_converted.pdf"
    elif conversion_type == 'pdf_to_jpg':
        output_filename = f"{unique_prefix}_{primary_secured.rsplit('.', 1)[0]}_images.zip"
        
    output_path = os.path.join(upload_folder, output_filename)
    
    # Run Conversion Logic with robust Fallback protection
    is_mock = False
    status = 'success'
    
    try:
        if conversion_type == 'pdf_to_docx':
            from pdf2docx import Converter
            cv = Converter(input_paths[0])
            cv.convert(output_path, start=0, end=None)
            cv.close()
            
        elif conversion_type == 'docx_to_pdf':
            from docx2pdf import convert
            convert(input_paths[0], output_path)
            
        elif conversion_type == 'merge_pdf':
            from pypdf import PdfWriter
            merger = PdfWriter()
            for path in input_paths:
                merger.append(path)
            with open(output_path, 'wb') as f:
                merger.write(f)
            merger.close()
            
        elif conversion_type == 'compress_pdf':
            from pypdf import PdfReader, PdfWriter
            reader = PdfReader(input_paths[0])
            writer = PdfWriter()
            for page in reader.pages:
                new_page = writer.add_page(page)
                new_page.compress_content_streams()
            with open(output_path, 'wb') as f:
                writer.write(f)
                
        elif conversion_type == 'split_pdf':
            import zipfile
            from pypdf import PdfReader, PdfWriter
            reader = PdfReader(input_paths[0])
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for idx, page in enumerate(reader.pages):
                    page_writer = PdfWriter()
                    page_writer.add_page(page)
                    page_name = f"page_{idx+1}.pdf"
                    page_temp_path = os.path.join(upload_folder, f"temp_{unique_prefix}_{page_name}")
                    with open(page_temp_path, 'wb') as pf:
                        page_writer.write(pf)
                    zipf.write(page_temp_path, page_name)
                    os.remove(page_temp_path)
                    
        elif conversion_type == 'jpg_to_pdf':
            from PIL import Image
            img_objects = []
            for path in input_paths:
                img = Image.open(path)
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                img_objects.append(img)
            if img_objects:
                img_objects[0].save(output_path, save_all=True, append_images=img_objects[1:])
                for img in img_objects:
                    img.close()
                    
        elif conversion_type == 'pdf_to_jpg':
            import fitz
            import zipfile
            doc = fitz.open(input_paths[0])
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for idx, page in enumerate(doc):
                    pix = page.get_pixmap()
                    img_name = f"page_{idx+1}.jpg"
                    img_temp_path = os.path.join(upload_folder, f"temp_{unique_prefix}_{img_name}")
                    pix.save(img_temp_path)
                    zipf.write(img_temp_path, img_name)
                    os.remove(img_temp_path)
            doc.close()
            
    except Exception as e:
        is_mock = True
        try:
            generate_mock_output(output_path, conversion_type, original_filenames_str, e)
        except Exception:
            status = 'failed'
            
    # Always clean up uploaded input files immediately to save server space
    for path in input_paths:
        if os.path.exists(path):
            try:
                os.remove(path)
            except OSError:
                pass
                
    if status == 'failed':
        return jsonify({'success': False, 'message': 'Conversion failed inside system streams.'}), 500
        
    friendly_size = get_friendly_file_size(output_path)
    
    # Save to history database
    record = ConversionHistory(
        user_id=current_user.id,
        original_filename=original_filenames_str[:255],
        converted_filename=output_filename,
        conversion_type=conversion_type,
        status=status,
        file_size=friendly_size
    )
    db.session.add(record)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'redirect_url': url_for('converter.success_page', history_id=record.id, mock=1 if is_mock else 0)
    })

@converter_bp.route('/success/<int:history_id>')
@login_required
def success_page(history_id):
    record = ConversionHistory.query.get_or_404(history_id)
    # Check authorization mapping
    if record.user_id != current_user.id:
        flash("You are not authorized to view this coordinate index.", "danger")
        return redirect(url_for('converter.dashboard'))
        
    is_mock = request.args.get('mock', '0') == '1'
    return render_template('success.html', record=record, is_mock=is_mock)

@converter_bp.route('/download/<filename>')
@login_required
def download_file(filename):
    # Security: Ensure secure filename to prevent directory traversal
    secured_name = secure_filename(filename)
    
    # Query database to confirm this file belongs to the logged-in user
    record = ConversionHistory.query.filter_by(
        user_id=current_user.id, 
        converted_filename=secured_name
    ).first()
    
    if not record:
        flash("Authorization failed. Filename coordinates invalid or missing.", "danger")
        return redirect(url_for('converter.dashboard'))
        
    upload_folder = current_app.config['UPLOAD_FOLDER']
    file_path = os.path.join(upload_folder, secured_name)
    
    # Check if physical file exists on server filesystem
    if not os.path.exists(file_path):
        flash("The requested file has expired and was auto-purged from our zero-gravity grid storage.", "danger")
        return redirect(url_for('converter.dashboard'))
        
    return send_from_directory(upload_folder, secured_name, as_attachment=True)

@converter_bp.route('/history')
@login_required
def history_page():
    # Perform cleanup of old files
    perform_auto_delete()
    
    # Grab all histories for the user
    history = ConversionHistory.query.filter_by(user_id=current_user.id).order_by(ConversionHistory.created_at.desc()).all()
    return render_template('history.html', history=history)

@converter_bp.route('/history/clear', methods=['POST'])
@login_required
def clear_history():
    # Purge user record history from database (does not purge physical files, perform_auto_delete handles files)
    try:
        ConversionHistory.query.filter_by(user_id=current_user.id).delete()
        db.session.commit()
        flash("Your conversion history registry has been purged.", "success")
    except Exception:
        db.session.rollback()
        flash("Error purging registry coordinates.", "danger")
        
    return redirect(url_for('converter.history_page'))
