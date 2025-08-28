# Install required packages
!pip install cryptography pycryptodome ipywidgets ipympl

import os
import io
from cryptography.fernet import Fernet
from google.colab import files
from IPython.display import display, clear_output, HTML, Javascript
import ipywidgets as widgets
import base64
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import time
from datetime import datetime

# Global variables
uploaded_file = None
file_name = None
file_type = None
encryption_key = None
password_hash = None
encrypted_data = None
file_size = None
upload_time = None

# Add Font Awesome for icons
display(HTML('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">'))

# Custom CSS for styling
custom_css = """
<style>
    .file-sharing-container {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        max-width: 800px;
        margin: 0 auto;
        padding: 20px;
        background: linear-gradient(135deg, #f5f7fa 0%, #e4edf5 100%);
        border-radius: 10px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.15);
    }
    .step-header {
        color: #2c3e50;
        border-bottom: 2px solid #3498db;
        padding-bottom: 8px;
        margin-bottom: 20px;
    }
    .btn-primary {
        background-color: #3498db;
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 30px;
        cursor: pointer;
        font-size: 16px;
        transition: all 0.3s;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .btn-primary:hover {
        background-color: #2980b9;
        transform: translateY(-2px);
        box-shadow: 0 6px 8px rgba(0,0,0,0.15);
    }
    .file-info {
        background-color: white;
        padding: 20px;
        border-radius: 8px;
        margin: 15px 0;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }
    .key-display {
        background-color: #f8f9fa;
        border: 1px dashed #ccc;
        padding: 15px;
        word-break: break-all;
        font-family: monospace;
        margin: 15px 0;
        border-radius: 5px;
    }
    .status-message {
        padding: 12px 15px;
        border-radius: 5px;
        margin: 15px 0;
        display: flex;
        align-items: center;
    }
    .status-message i {
        margin-right: 10px;
        font-size: 18px;
    }
    .success {
        background-color: #d4edda;
        color: #155724;
        border-left: 4px solid #28a745;
    }
    .error {
        background-color: #f8d7da;
        color: #721c24;
        border-left: 4px solid #dc3545;
    }
    .warning {
        background-color: #fff3cd;
        color: #856404;
        border-left: 4px solid #ffc107;
    }
    .feature-card {
        flex: 1;
        background-color: white;
        border-radius: 8px;
        padding: 20px;
        margin: 0 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
        transition: all 0.3s;
    }
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 15px rgba(0,0,0,0.1);
    }
    .info-card {
        flex: 1;
        background-color: #eaf2f8;
        border-radius: 8px;
        padding: 20px;
        margin: 0 10px;
        border-left: 4px solid #3498db;
    }
    .spinner {
        border: 4px solid rgba(0, 0, 0, 0.1);
        width: 36px;
        height: 36px;
        border-radius: 50%;
        border-left-color: #09f;
        animation: spin 1s linear infinite;
        display: inline-block;
        vertical-align: middle;
        margin-left: 10px;
    }
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    .download-btn {
        display: inline-block;
        background-color: #2ecc71;
        color: white;
        text-decoration: none;
        padding: 15px 30px;
        border-radius: 30px;
        font-size: 18px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: all 0.3s;
        margin: 15px 0;
    }
    .download-btn:hover {
        background-color: #27ae60;
        transform: translateY(-2px);
        box-shadow: 0 6px 8px rgba(0,0,0,0.15);
    }
</style>
"""
# Display custom CSS
display(HTML(custom_css))

# Helper function to show modal
def show_modal(title, content, button_text="Close", callback=None):
    modal_id = f"modal_{int(time.time())}"
    button_callback = "document.getElementById('{}').style.display='none';".format(modal_id)
    if callback:
        button_callback += callback
    
    display(HTML(f"""
    <div id="{modal_id}" style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.5); display: flex; justify-content: center; align-items: center; z-index: 1000;">
        <div style="background-color: white; padding: 30px; border-radius: 10px; width: 80%; max-width: 600px; box-shadow: 0 10px 25px rgba(0,0,0,0.2);">
            <h2 style="margin-top: 0; color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px;">{title}</h2>
            <div style="margin: 20px 0;">{content}</div>
            <button onclick="{button_callback}" style="background-color: #3498db; color: white; border: none; padding: 12px 24px; border-radius: 30px; font-size: 16px; cursor: pointer; box-shadow: 0 4px 6px rgba(0,0,0,0.1); transition: all 0.3s;">
                {button_text}
            </button>
        </div>
    </div>
    """))

# Opening Window with Enhanced Visuals and buttons
def show_opening_window():
    clear_output()
    display(HTML("""
    <style>
        .dark-mode {
            background-color: #1a1a1a;
            color: #ffffff;
        }
        .dark-mode .file-sharing-container {
            background: linear-gradient(135deg, #2d2d2d 0%, #1e1e1e 100%);
            color: #ffffff;
        }
        .dark-mode .step-header {
            color: #ffffff;
            border-bottom: 2px solid #4a90e2;
        }
        .dark-mode .file-info {
            background-color: #2d2d2d;
            color: #ffffff;
        }
        .dark-mode .feature-card {
            background-color: #2d2d2d;
            color: #ffffff;
        }
        .dark-mode .feature-card h3 {
            color: #ffffff !important;
        }
        .dark-mode .feature-card p {
            color: #aaaaaa !important;
        }
        .dark-mode .btn-primary {
            background-color: #4a90e2;
        }
        .dark-mode .info-card, .dark-mode div[style*="background-color: #eaf2f8"] {
            background-color: #2d2d2d !important;
            border-left: 4px solid #4a90e2;
        }
        .dark-mode ol, .dark-mode ul, .dark-mode p, .dark-mode h3 {
            color: #ffffff !important;
        }
        .dark-toggle {
            position: absolute;
            top: 20px;
            right: 20px;
            z-index: 1000;
            background-color: #2c3e50;
            color: white;
            border: none;
            padding: 8px 12px;
            border-radius: 20px;
            cursor: pointer;
            transition: all 0.3s;
        }
        .dark-toggle:hover {
            background-color: #1a2530;
            transform: translateY(-2px);
        }
    </style>
    <button onclick="document.body.classList.toggle('dark-mode'); localStorage.setItem('darkMode', document.body.classList.contains('dark-mode'));" class="dark-toggle">
        <i class="fas fa-moon"></i> Toggle Dark Mode
    </button>
    <script>
        // Check for saved dark mode preference
        if(localStorage.getItem('darkMode') === 'true') {
            document.body.classList.add('dark-mode');
        }
    </script>
    """))
    
    opening_content = """
    <div class='file-sharing-container'>
        <div style="text-align: center; margin-bottom: 30px;">
            <div style="font-size: 48px; margin-bottom: 10px; color: #3498db;">
                <i class="fas fa-shield-alt"></i>
            </div>
            <h1 style="color: #2c3e50; margin: 0; font-size: 32px;">Secure File Sharing</h1>
            <p style="color: #7f8c8d; font-style: italic;">End-to-end encryption for your sensitive files</p>
        </div>
        
        <div style="display: flex; justify-content: space-between; margin: 40px 0; flex-wrap: wrap;">
            <div class="feature-card" style="min-width: 150px; margin-bottom: 15px;">
                <div style="font-size: 36px; color: #3498db; margin-bottom: 15px;">
                    <i class="fas fa-upload"></i>
                </div>
                <h3 style="margin: 0; color: #2c3e50;">Upload</h3>
                <p style="color: #7f8c8d;">Select any file from your device</p>
            </div>
            
            <div class="feature-card" style="min-width: 150px; margin-bottom: 15px;">
                <div style="font-size: 36px; color: #3498db; margin-bottom: 15px;">
                    <i class="fas fa-lock"></i>
                </div>
                <h3 style="margin: 0; color: #2c3e50;">Encrypt</h3>
                <p style="color: #7f8c8d;">Secure with strong encryption</p>
            </div>
            
            <div class="feature-card" style="min-width: 150px; margin-bottom: 15px;">
                <div style="font-size: 36px; color: #3498db; margin-bottom: 15px;">
                    <i class="fas fa-share-alt"></i>
                </div>
                <h3 style="margin: 0; color: #2c3e50;">Share</h3>
                <p style="color: #7f8c8d;">Share files with confidence</p>
            </div>
            
            <div class="feature-card" style="min-width: 150px; margin-bottom: 15px;">
                <div style="font-size: 36px; color: #3498db; margin-bottom: 15px;">
                    <i class="fas fa-unlock"></i>
                </div>
                <h3 style="margin: 0; color: #2c3e50;">Decrypt</h3>
                <p style="color: #7f8c8d;">Easily decrypt with key or password</p>
            </div>
        </div>
        
        <div style="background-color: #eaf2f8; border-radius: 8px; padding: 20px; margin-top: 20px; border-left: 4px solid #3498db;">
            <h3 style="margin-top: 0; color: #2c3e50;">How it works:</h3>
            <ol style="color: #34495e; margin-bottom: 0;">
                <li>Upload your file of any format</li>
                <li>Set a password (optional for added security)</li>
                <li>Download the encrypted file and save your secret key</li>
                <li>Share the encrypted file through any platform</li>
                <li>Use the key or password to decrypt when needed</li>
            </ol>
        </div>
    """
    display(HTML(opening_content))
    
    # Replace JavaScript button with a Python widget
    get_started_btn = widgets.Button(
        description="Get Started",
        button_style='primary',
        icon='arrow-right',
        layout=widgets.Layout(width='150px')
    )
    get_started_btn.on_click(lambda b: show_upload_step())
    
    # Center the button
    center_box = widgets.HBox([get_started_btn], layout=widgets.Layout(
        display='flex',
        flex_flow='column',
        align_items='center',
        width='100%',
        margin='30px 0 0 0'
    ))
    display(center_box)
    
    display(HTML("""
        <div style="text-align: center; margin-top: 30px; font-size: 12px; color: #95a5a6;">
            <p>Your files are encrypted directly in your browser. We never store your files or encryption keys.</p>
        </div>
    </div>
    """))

# Helper function to format file size
def format_file_size(size):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} TB"

# Step 1: File Upload
def show_upload_step():
    clear_output()
    display(HTML("""
    <style>
        .dark-mode {
            background-color: #1a1a1a;
            color: #ffffff;
        }
        .dark-mode .file-sharing-container {
            background: linear-gradient(135deg, #2d2d2d 0%, #1e1e1e 100%);
            color: #ffffff;
        }
        .dark-mode .step-header {
            color: #ffffff;
            border-bottom: 2px solid #4a90e2;
        }
        .dark-mode .file-info {
            background-color: #2d2d2d;
            color: #ffffff;
        }
        .dark-mode .file-info h3 {
            color: #ffffff !important;
        }
        .dark-mode .file-info p {
            color: #aaaaaa !important;
        }
        .dark-mode .status-message.success {
            background-color: #1e4620;
            color: #8eff9e;
        }
        .dark-mode .status-message.error {
            background-color: #4c1c1c;
            color: #ff8e8e;
        }
        .dark-mode .btn-primary {
            background-color: #4a90e2;
        }
        .dark-mode div[style*="margin-top: 30px"] {
            color: #aaaaaa !important;
        }
        .dark-mode div[style*="margin-top: 30px"] p {
            color: #aaaaaa !important;
        }
        .dark-toggle {
            position: absolute;
            top: 20px;
            right: 20px;
            z-index: 1000;
            background-color: #2c3e50;
            color: white;
            border: none;
            padding: 8px 12px;
            border-radius: 20px;
            cursor: pointer;
            transition: all 0.3s;
        }
        .dark-toggle:hover {
            background-color: #1a2530;
            transform: translateY(-2px);
        }
    </style>
    <button onclick="document.body.classList.toggle('dark-mode'); localStorage.setItem('darkMode', document.body.classList.contains('dark-mode'));" class="dark-toggle">
        <i class="fas fa-moon"></i> Toggle Dark Mode
    </button>
    <script>
        // Check for saved dark mode preference
        if(localStorage.getItem('darkMode') === 'true') {
            document.body.classList.add('dark-mode');
        }
    </script>
    
    <div class='file-sharing-container'>
        <h2 class='step-header'>
            <i class="fas fa-upload" style="margin-right: 10px;"></i>
            STEP 1: Upload Your File
        </h2>
        <p>Select a file from your device to encrypt. We support files of any format and size (limited by your browser memory).</p>
    """))
    
    def on_upload(b):
        global uploaded_file, file_name, file_type, file_size, upload_time
        uploaded = files.upload()
        if uploaded:
            file_name = list(uploaded.keys())[0]
            uploaded_file = uploaded[file_name]
            file_type = file_name.split('.')[-1].lower()
            file_size = len(uploaded_file)
            upload_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            file_info = f"""
            <div class='file-info'>
                <div style="display: flex; align-items: center; margin-bottom: 15px;">
                    <div style="font-size: 30px; color: #3498db; margin-right: 15px;">
                        <i class="fas fa-file-alt"></i>
                    </div>
                    <div>
                        <h3 style="margin: 0; color: #2c3e50;">{file_name}</h3>
                        <p style="margin: 5px 0 0 0; color: #7f8c8d;">Ready for encryption</p>
                    </div>
                </div>
                <div style="display: flex; flex-wrap: wrap;">
                    <div style="flex: 1; min-width: 150px; margin-bottom: 10px;">
                        <p style="margin: 0; color: #7f8c8d;">Type:</p>
                        <p style="margin: 5px 0 0 0; color: #2c3e50; font-weight: bold;">{file_type.upper()}</p>
                    </div>
                    <div style="flex: 1; min-width: 150px; margin-bottom: 10px;">
                        <p style="margin: 0; color: #7f8c8d;">Size:</p>
                        <p style="margin: 5px 0 0 0; color: #2c3e50; font-weight: bold;">{format_file_size(file_size)}</p>
                    </div>
                    <div style="flex: 1; min-width: 150px; margin-bottom: 10px;">
                        <p style="margin: 0; color: #7f8c8d;">Uploaded:</p>
                        <p style="margin: 5px 0 0 0; color: #2c3e50; font-weight: bold;">{upload_time}</p>
                    </div>
                </div>
            </div>
            <div class='status-message success'>
                <i class="fas fa-check-circle"></i> File uploaded successfully!
            </div>
            """
            display(HTML(file_info))
            time.sleep(1)
            show_password_step()
        else:
            display(HTML("<div class='status-message error'><i class='fas fa-exclamation-circle'></i> Please select a file to upload</div>"))
    
    upload_btn = widgets.Button(
        description="Select File to Upload", 
        layout=widgets.Layout(width='220px'),
        button_style='primary',
        icon='upload'
    )
    upload_btn.on_click(on_upload)
    display(upload_btn)
    display(HTML("""
        <div style="margin-top: 30px; font-size: 14px; color: #7f8c8d;">
            <p><i class="fas fa-info-circle" style="color: #3498db;"></i> Your file will be processed locally in your browser. No data is sent to our servers.</p>
        </div>
    </div>
    """))

# Step 2: Password Setup (Optional)
def show_password_step():
    clear_output()
    display(HTML("""
    <style>
        .dark-mode {
            background-color: #1a1a1a;
            color: #ffffff;
        }
        .dark-mode .file-sharing-container {
            background: linear-gradient(135deg, #2d2d2d 0%, #1e1e1e 100%);
            color: #ffffff;
        }
        .dark-mode .step-header {
            color: #ffffff;
            border-bottom: 2px solid #4a90e2;
        }
        .dark-mode .file-info {
            background-color: #2d2d2d;
            color: #ffffff;
        }
        .dark-mode .file-info h3 {
            color: #ffffff !important;
        }
        .dark-mode .file-info p {
            color: #aaaaaa !important;
        }
        .dark-mode .status-message.success {
            background-color: #1e4620;
            color: #8eff9e;
        }
        .dark-mode .status-message.error {
            background-color: #4c1c1c;
            color: #ff8e8e;
        }
        .dark-mode .status-message.warning {
            background-color: #4c4c1c;
            color: #ffff8e;
        }
        .dark-mode .btn-primary {
            background-color: #4a90e2;
        }
        .dark-mode div[style*="background-color: #eaf2f8"] {
            background-color: #2d2d2d !important;
            border-left: 4px solid #4a90e2;
        }
        .dark-mode div[style*="background-color: #eaf2f8"] h4 {
            color: #ffffff !important;
        }
        .dark-mode div[style*="background-color: #eaf2f8"] ul {
            color: #aaaaaa !important;
        }
        .dark-toggle {
            position: absolute;
            top: 20px;
            right: 20px;
            z-index: 1000;
            background-color: #2c3e50;
            color: white;
            border: none;
            padding: 8px 12px;
            border-radius: 20px;
            cursor: pointer;
            transition: all 0.3s;
        }
        .dark-toggle:hover {
            background-color: #1a2530;
            transform: translateY(-2px);
        }
    </style>
    <button onclick="document.body.classList.toggle('dark-mode'); localStorage.setItem('darkMode', document.body.classList.contains('dark-mode'));" class="dark-toggle">
        <i class="fas fa-moon"></i> Toggle Dark Mode
    </button>
    <script>
        // Check for saved dark mode preference
        if(localStorage.getItem('darkMode') === 'true') {
            document.body.classList.add('dark-mode');
        }
    </script>
    """))
    
    display(HTML(f"""
    <div class='file-sharing-container'>
        <h2 class='step-header'>
            <i class="fas fa-key" style="margin-right: 10px;"></i>
            STEP 2: Set Password (Optional)
        </h2>
        <p>Adding a password provides an extra layer of security. If you skip this step, you'll need the secret key for decryption.</p>
        
        <div class='file-info'>
            <div style="display: flex; align-items: center;">
                <div style="font-size: 30px; color: #3498db; margin-right: 15px;">
                    <i class="fas fa-file-alt"></i>
                </div>
                <div>
                    <h3 style="margin: 0; color: #2c3e50;">{file_name}</h3>
                    <p style="margin: 5px 0 0 0; color: #7f8c8d;">Ready for password protection</p>
                </div>
            </div>
        </div>
    """))
    
    password_input = widgets.Password(
        description="Password:", 
        placeholder="Enter a strong password",
        layout=widgets.Layout(width='350px')
    )
    confirm_input = widgets.Password(
        description="Confirm:", 
        placeholder="Confirm your password",
        layout=widgets.Layout(width='350px')
    )
    
    next_btn = widgets.Button(
        description="Continue with Password", 
        layout=widgets.Layout(width='200px'),
        button_style='primary',
        icon='check'
    )
    skip_btn = widgets.Button(
        description="Skip Password", 
        layout=widgets.Layout(width='150px'),
        button_style='warning',
        icon='forward'
    )

    def on_next(b):
        global password_hash
        if password_input.value:
            if password_input.value == confirm_input.value:
                password_hash = hashlib.sha256(password_input.value.encode()).hexdigest()
                display(HTML("<div class='status-message success'><i class='fas fa-check-circle'></i> Password set successfully</div>"))
                time.sleep(1)
                show_encrypt_step()
            else:
                display(HTML("<div class='status-message error'><i class='fas fa-exclamation-circle'></i> Passwords don't match!</div>"))
        else:
            display(HTML("<div class='status-message warning'><i class='fas fa-exclamation-triangle'></i> No password set (decryption will require secret key only)</div>"))
            time.sleep(1)
            show_encrypt_step()

    def on_skip(b):
        global password_hash
        password_hash = None
        display(HTML("<div class='status-message warning'><i class='fas fa-exclamation-triangle'></i> No password set (decryption will require secret key only)</div>"))
        time.sleep(1)
        show_encrypt_step()

    next_btn.on_click(on_next)
    skip_btn.on_click(on_skip)
    buttons = widgets.HBox([next_btn, skip_btn])
    display(widgets.VBox([password_input, confirm_input, buttons]))
    
    display(HTML("""
        <div style="background-color: #eaf2f8; border-radius: 8px; padding: 15px; margin-top: 20px; border-left: 4px solid #3498db;">
            <h4 style="margin-top: 0; color: #2c3e50;"><i class="fas fa-lightbulb" style="color: #f39c12;"></i> Password Tips:</h4>
            <ul style="color: #34495e; margin-bottom: 0;">
                <li>Use a combination of letters, numbers, and special characters</li>
                <li>Avoid easily guessable information like birthdays or names</li>
                <li>Longer passwords provide better security</li>
            </ul>
        </div>
    </div>
    """))

# Step 3: Encryption
def show_encrypt_step():
    clear_output()
    display(HTML("""
    <style>
        .dark-mode {
            background-color: #1a1a1a;
            color: #ffffff;
        }
        .dark-mode .file-sharing-container {
            background: linear-gradient(135deg, #2d2d2d 0%, #1e1e1e 100%);
            color: #ffffff;
        }
        .dark-mode .step-header {
            color: #ffffff;
            border-bottom: 2px solid #4a90e2;
        }
        .dark-mode .file-info {
            background-color: #2d2d2d;
            color: #ffffff;
        }
        .dark-mode .file-info h3 {
            color: #ffffff !important;
        }
        .dark-mode .file-info p {
            color: #aaaaaa !important;
        }
        .dark-mode .key-display {
            background-color: #333333;
            color: #ffffff;
            border: 1px dashed #666;
        }
        .dark-mode .status-message.success {
            background-color: #1e4620;
            color: #8eff9e;
        }
        .dark-mode .btn-primary {
            background-color: #4a90e2;
        }
        .dark-mode div[style*="background-color: #eaf2f8"] {
            background-color: #2d2d2d !important;
            border-left: 4px solid #4a90e2;
        }
        .dark-mode div[style*="background-color: #eaf2f8"] h4 {
            color: #ffffff !important;
        }
        .dark-mode div[style*="background-color: #eaf2f8"] ul {
            color: #aaaaaa !important;
        }
        .dark-mode div[style*="background-color: white"] {
            background-color: #2d2d2d !important;
        }
        .dark-mode div[style*="background-color: white"] h3 {
            color: #ffffff !important;
        }
        .dark-toggle {
            position: absolute;
            top: 20px;
            right: 20px;
            z-index: 1000;
            background-color: #2c3e50;
            color: white;
            border: none;
            padding: 8px 12px;
            border-radius: 20px;
            cursor: pointer;
            transition: all 0.3s;
        }
        Here's the remaining part of the code to complete the file:

Copy        .dark-toggle:hover {
            background-color: #1a2530;
            transform: translateY(-2px);
        }
    </style>
    <button onclick="document.body.classList.toggle('dark-mode'); localStorage.setItem('darkMode', document.body.classList.contains('dark-mode'));" class="dark-toggle">
        <i class="fas fa-moon"></i> Toggle Dark Mode
    </button>
    <script>
        // Check for saved dark mode preference
        if(localStorage.getItem('darkMode') === 'true') {
            document.body.classList.add('dark-mode');
        }
    </script>
    """))
    
    display(HTML(f"""
    <div class='file-sharing-container'>
        <h2 class='step-header'>
            <i class="fas fa-lock" style="margin-right: 10px;"></i>
            STEP 3: Encrypt Your File
        </h2>
        <p>Click the button below to encrypt your file with secure encryption. You'll receive a secret key that you'll need for decryption.</p>
        
        <div class='file-info'>
            <div style="display: flex; align-items: center;">
                <div style="font-size: 30px; color: #3498db; margin-right: 15px;">
                    <i class="fas fa-file-alt"></i>
                </div>
                <div>
                    <h3 style="margin: 0; color: #2c3e50;">{file_name}</h3>
                    <p style="margin: 5px 0 0 0; color: #7f8c8d;">Ready for encryption</p>
                </div>
            </div>
            <div style="display: flex; flex-wrap: wrap; margin-top: 15px;">
                <div style="flex: 1; min-width: 150px; margin-bottom: 10px;">
                    <p style="margin: 0; color: #7f8c8d;">Size:</p>
                    <p style="margin: 5px 0 0 0; color: #2c3e50; font-weight: bold;">{format_file_size(file_size)}</p>
                </div>
                <div style="flex: 1; min-width: 150px; margin-bottom: 10px;">
                    <p style="margin: 0; color: #7f8c8d;">Password Protection:</p>
                    <p style="margin: 5px 0 0 0; color: #2c3e50; font-weight: bold;">{("Yes" if password_hash else "No")}</p>
                </div>
                <div style="flex: 1; min-width: 150px; margin-bottom: 10px;">
                    <p style="margin: 0; color: #7f8c8d;">Encryption Method:</p>
                    <p style="margin: 5px 0 0 0; color: #2c3e50; font-weight: bold;">Fernet (AES-128)</p>
                </div>
            </div>
        </div>
    """))
    
    encrypt_btn = widgets.Button(
        description="Encrypt Now", 
        layout=widgets.Layout(width='150px'),
        button_style='primary',
        icon='lock'
    )

    def on_encrypt(b):
        global uploaded_file, encryption_key, encrypted_data
        # Show loading animation
        display(HTML("""
            <div id='loading' style='margin: 20px 0; display: flex; align-items: center;'>
                <span style='margin-right: 15px;'>Encrypting file...</span>
                <div class='spinner'></div>
            </div>
        """))
        # Generate a key for encryption
        key = Fernet.generate_key()
        cipher = Fernet(key)
        # Encrypt the file data
        encrypted_data = cipher.encrypt(uploaded_file)
        encryption_key = key.decode()
        # Hide loading animation
        display(Javascript("document.getElementById('loading').style.display='none'"))
        key_display = f"""
        <div class='status-message success'>
            <i class="fas fa-check-circle"></i> File encrypted successfully!
        </div>
        <div style='margin: 20px 0; background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.1);'>
            <div style="display: flex; align-items: center; margin-bottom: 15px;">
                <div style="font-size: 30px; color: #e74c3c; margin-right: 15px;">
                    <i class="fas fa-key"></i>
                </div>
                <div>
                    <h3 style="margin: 0; color: #2c3e50;">Your Secret Key</h3>
                    <p style="margin: 5px 0 0 0; color: #7f8c8d;">Store this in a secure location</p>
                </div>
            </div>
            <div class='key-display'>{encryption_key}</div>
            <p style='color: #e74c3c; font-weight: bold; margin-top: 15px;'>
                <i class="fas fa-exclamation-triangle"></i> WARNING: You won't be able to decrypt the file without this key!
            </p>
        </div>
        """
        display(HTML(key_display))
        # Show download button for encrypted file
        b64 = base64.b64encode(encrypted_data).decode()
        filename = f"encrypted_{file_name}"
        display(HTML(
            f'<a href="data:application/octet-stream;base64,{b64}" download="{filename}" '
            'class="download-btn">'
            '<i class="fas fa-download" style="margin-right: 10px;"></i> Download Encrypted File</a>'
        ))
        # Show next step button
        next_btn = widgets.Button(
            description="Proceed to Decryption", 
            layout=widgets.Layout(width='200px'),
            button_style='info',
            icon='arrow-right'
        )
        next_btn.on_click(lambda b: show_decrypt_step())
        display(next_btn)

    encrypt_btn.on_click(on_encrypt)
    display(encrypt_btn)
    display(HTML("""
        <div style="background-color: #eaf2f8; border-radius: 8px; padding: 15px; margin-top: 20px; border-left: 4px solid #3498db;">
            <h4 style="margin-top: 0; color: #2c3e50;"><i class="fas fa-shield-alt" style="color: #3498db;"></i> Security Information:</h4>
            <ul style="color: #34495e; margin-bottom: 0;">
                <li>We use Fernet symmetric encryption (based on AES-128)</li>
                <li>The encryption process happens entirely in your browser</li>
                <li>Neither your file nor your encryption key are stored on our servers</li>
            </ul>
        </div>
    </div>
    """))

# Step 4: Decryption with Enhanced Visuals and Download Button
def show_decrypt_step():
    clear_output()
    display(HTML("""
    <style>
        .dark-mode {
            background-color: #1a1a1a;
            color: #ffffff;
        }
        .dark-mode .file-sharing-container {
            background: linear-gradient(135deg, #2d2d2d 0%, #1e1e1e 100%);
            color: #ffffff;
        }
        .dark-mode .step-header {
            color: #ffffff;
            border-bottom: 2px solid #4a90e2;
        }
        .dark-mode .file-info {
            background-color: #2d2d2d;
            color: #ffffff;
        }
        .dark-mode .key-display {
            background-color: #333333;
            color: #ffffff;
            border: 1px dashed #666;
        }
        .dark-mode .btn-primary {
            background-color: #4a90e2;
        }
        .dark-mode .info-card {
            background-color: #2d2d2d;
            border-left: 4px solid #4a90e2;
        }
        .dark-mode div[style*="background-color: white"] {
            background-color: #2d2d2d !important;
        }
        .dark-mode div[style*="background-color: white"] h3 {
            color: #ffffff !important;
        }
        .dark-mode div[style*="background-color: white"] p {
            color: #aaaaaa !important;
        }
        .dark-mode div[style*="background-color: #eaf2f8"] {
            background-color: #2d2d2d !important;
            border-left: 4px solid #4a90e2;
        }
        .dark-mode div[style*="background-color: #eaf2f8"] h4 {
            color: #ffffff !important;
        }
        .dark-mode div[style*="background-color: #eaf2f8"] ul {
            color: #aaaaaa !important;
        }
        .dark-toggle {
            position: absolute;
            top: 20px;
            right: 20px;
            z-index: 1000;
            background-color: #2c3e50;
            color: white;
            border: none;
            padding: 8px 12px;
            border-radius: 20px;
            cursor: pointer;
            transition: all 0.3s;
        }
        .dark-toggle:hover {
            background-color: #1a2530;
            transform: translateY(-2px);
        }
    </style>
    <button onclick="document.body.classList.toggle('dark-mode'); localStorage.setItem('darkMode', document.body.classList.contains('dark-mode'));" class="dark-toggle">
        <i class="fas fa-moon"></i> Toggle Dark Mode
    </button>
    <script>
        // Check for saved dark mode preference
        if(localStorage.getItem('darkMode') === 'true') {
            document.body.classList.add('dark-mode');
        }
    </script>
    <div class='file-sharing-container'>
        <h2 class='step-header'>
            <i class="fas fa-unlock" style="margin-right: 10px;"></i>
            STEP 4: Decrypt File
        </h2>
        <p>Provide either the secret key or the password to decrypt your file.</p>
        
        <div style="display: flex; flex-wrap: wrap; margin: 20px -10px;">
            <div style="flex: 1; min-width: 300px; background-color: white; border-radius: 8px; padding: 20px; margin: 0 10px 20px 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); border-top: 4px solid #3498db;">
                <div style="display: flex; align-items: center; margin-bottom: 15px;">
                    <div style="font-size: 24px; color: #3498db; margin-right: 15px;">
                        <i class="fas fa-key"></i>
                    </div>
                    <div>
                        <h3 style="margin: 0; color: #2c3e50;">Option 1: Use Secret Key</h3>
                        <p style="margin: 5px 0 0 0; color: #7f8c8d;">Paste the key provided during encryption</p>
                    </div>
                </div>
                <div id="key-input-area"></div>
            </div>
            
            <div style="flex: 1; min-width: 300px; background-color: white; border-radius: 8px; padding: 20px; margin: 0 10px 20px 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); border-top: 4px solid #3498db;">
                <div style="display: flex; align-items: center; margin-bottom: 15px;">
                    <div style="font-size: 24px; color: #3498db; margin-right: 15px;">
                        <i class="fas fa-lock"></i>
                    </div>
                    <div>
                        <h3 style="margin: 0; color: #2c3e50;">Option 2: Use Password</h3>
                        <p style="margin: 5px 0 0 0; color: #7f8c8d;">Enter the password you set during encryption</p>
                    </div>
                </div>
                <div id="password-input-area"></div>
            </div>
        </div>
    """))
    
    key_input = widgets.Text(
        description="Secret Key:", 
        placeholder="Paste your secret key here",
        layout=widgets.Layout(width='400px')
    )
    password_input = widgets.Password(
        description="Password:", 
        placeholder="Enter your password",
        layout=widgets.Layout(width='400px')
    )
    decrypt_btn = widgets.Button(
        description="Decrypt File", 
        layout=widgets.Layout(width='150px'),
        button_style='success',
        icon='unlock'
    )

    def on_decrypt(b):
        global encrypted_data, password_hash
        key_to_use = None
        # Show loading animation
        display(HTML("""
            <div id='loading' style='margin: 20px 0; display: flex; align-items: center; justify-content: center;'>
                <span style='margin-right: 15px;'>Decrypting file...</span>
                <div class='spinner'></div>
            </div>
        """))
        
        # Try with secret key first
        if key_input.value:
            try:
                key_to_use = key_input.value.encode()
                cipher = Fernet(key_to_use)
                decrypted_data = cipher.decrypt(encrypted_data)
                display(Javascript("document.getElementById('loading').style.display='none'"))
                display(HTML("<div class='status-message success'><i class='fas fa-check-circle'></i> File decrypted successfully with secret key!</div>"))
                
                # Provide download link for decrypted file
                orig_filename = file_name
                if orig_filename.startswith("encrypted_"):
                    orig_filename = orig_filename[10:]  # Remove 'encrypted_' prefix
                
                # Create download button (similar to encryption step)
                b64 = base64.b64encode(decrypted_data).decode()
                filename = orig_filename
                display(HTML(
                    f'<a href="data:application/octet-stream;base64,{b64}" download="{filename}" '
                    'class="download-btn">'
                    '<i class="fas fa-download" style="margin-right: 10px;"></i> Download Decrypted File</a>'
                ))
                
                # Show restart button
                restart_btn = widgets.Button(
                    description="Start New Session",
                    button_style='info',
                    icon='refresh',
                    layout=widgets.Layout(width='150px')
                )
                restart_btn.on_click(lambda b: show_opening_window())
                display(restart_btn)
                return
            except Exception as e:
                display(Javascript("document.getElementById('loading').style.display='none'"))
                display(HTML("<div class='status-message error'><i class='fas fa-exclamation-circle'></i> Invalid secret key! Please try again.</div>"))
        
        # Try with password if provided and password hash exists
        elif password_input.value and password_hash:
            try:
                input_password_hash = hashlib.sha256(password_input.value.encode()).hexdigest()
                if input_password_hash == password_hash:
                    # If using the original encryption key saved in the session
                    if encryption_key:
                        cipher = Fernet(encryption_key.encode())
                        decrypted_data = cipher.decrypt(encrypted_data)
                        display(Javascript("document.getElementById('loading').style.display='none'"))
                        display(HTML("<div class='status-message success'><i class='fas fa-check-circle'></i> File decrypted successfully with password!</div>"))
                        
                        # Provide download link for decrypted file
                        orig_filename = file_name
                        if orig_filename.startswith("encrypted_"):
                            orig_filename = orig_filename[10:]  # Remove 'encrypted_' prefix
                        
                        # Create download button (similar to encryption step)
                        b64 = base64.b64encode(decrypted_data).decode()
                        filename = orig_filename
                        display(HTML(
                            f'<a href="data:application/octet-stream;base64,{b64}" download="{filename}" '
                            'class="download-btn">'
                            '<i class="fas fa-download" style="margin-right: 10px;"></i> Download Decrypted File</a>'
                        ))
                        
                        # Show restart button
                        restart_btn = widgets.Button(
                            description="Start New Session",
                            button_style='info',
                            icon='refresh',
                            layout=widgets.Layout(width='150px')
                        )
                        restart_btn.on_click(lambda b: show_opening_window())
                        display(restart_btn)
                        return
                    else:
                        display(Javascript("document.getElementById('loading').style.display='none'"))
                        display(HTML("<div class='status-message error'><i class='fas fa-exclamation-circle'></i> Password is correct, but the encryption key is not available in this session. Please use the secret key instead.</div>"))
                else:
                    display(Javascript("document.getElementById('loading').style.display='none'"))
                    display(HTML("<div class='status-message error'><i class='fas fa-exclamation-circle'></i> Incorrect password! Please try again.</div>"))
            except Exception as e:
                display(Javascript("document.getElementById('loading').style.display='none'"))
                display(HTML(f"<div class='status-message error'><i class='fas fa-exclamation-circle'></i> Error during decryption: {str(e)}</div>"))
        else:
            display(Javascript("document.getElementById('loading').style.display='none'"))
            display(HTML("<div class='status-message error'><i class='fas fa-exclamation-circle'></i> Please provide either a secret key or a password!</div>"))

    # Display widgets
    display(key_input)
    display(password_input)
    display(decrypt_btn)
    
    # Add a restart button
    restart_btn = widgets.Button(
        description="Start Over",
        button_style='info',
        icon='refresh',
        layout=widgets.Layout(width='150px')
    )
    restart_btn.on_click(lambda b: show_opening_window())
    display(restart_btn)
    
    decrypt_btn.on_click(on_decrypt)
    
    display(HTML("""
        <div style="background-color: #eaf2f8; border-radius: 8px; padding: 15px; margin-top: 20px; border-left: 4px solid #3498db;">
            <h4 style="margin-top: 0; color: #2c3e50;"><i class="fas fa-info-circle" style="color: #3498db;"></i> Decryption Help:</h4>
            <ul style="color: #34495e; margin-bottom: 0;">
                <li>If you encrypted with a password, you can use either the password or the secret key</li>
                <li>If you skipped the password step, you must use the secret key</li>
                <li>The decryption happens entirely in your browser - no data is sent to our servers</li>
            </ul>
        </div>
    </div>
    """))

# Closing Window with Dark Mode Support
def show_closing_window():
    clear_output()
    display(HTML("""
    <style>
        .dark-mode {
            background-color: #1a1a1a;
            color: #ffffff;
        }
        .dark-mode .file-sharing-container {
            background: linear-gradient(135deg, #2d2d2d 0%, #1e1e1e 100%);
            color: #ffffff;
        }
        .dark-mode .success-message {
            color: #ffffff;
        }
        .dark-mode .security-reminder {
            background-color: #2d2d2d;
            color: #ffffff;
            border-left: 4px solid #4a90e2;
        }
        .dark-mode .security-tip {
            background-color: #333333;
        }
        .dark-toggle {
            position: absolute;
            top: 20px;
            right: 20px;
            z-index: 1000;
            background-color: #2c3e50;
            color: white;
            border: none;
            padding: 8px 12px;
            border-radius: 20px;
            cursor: pointer;
            transition: all 0.3s;
        }
        .dark-toggle:hover {
            background-color: #1a2530;
            transform: translateY(-2px);
        }
        .security-tip {
            background-color: #f8f9fa;
            border-radius: 8px;
            padding: 15px;
            margin: 15px 0;
            border-left: 4px solid #ffc107;
        }
        .tip-header {
            display: flex;
            align-items: center;
            margin-bottom: 10px;
        }
        .tip-icon {
            font-size: 24px;
            color: #ffc107;
            margin-right: 10px;
        }
    </style>
    <button onclick="document.body.classList.toggle('dark-mode'); localStorage.setItem('darkMode', document.body.classList.contains('dark-mode'));" class="dark-toggle">
        <i class="fas fa-moon"></i> Toggle Dark Mode
    </button>
    <script>
        // Check for saved dark mode preference
        if(localStorage.getItem('darkMode') === 'true') {
            document.body.classList.add('dark-mode');
        }
    </script>
    <div class='file-sharing-container' style='text-align: center;'>
        <div style="font-size: 72px; color: #2ecc71; margin-bottom: 20px;">
            <i class="fas fa-check-circle"></i>
        </div>
        <h1 class="success-message" style="color: #2c3e50; margin-bottom: 10px;">Secure Transfer Complete!</h1>
        <p class="success-message" style="color: #7f8c8d; font-size: 18px; margin-bottom: 30px;">
            Your file has been successfully processed and downloaded to your device.
        </p>
        
        <div class="security-reminder" style="background-color: #eaf2f8; border-radius: 8px; padding: 20px; margin: 0 auto 20px auto; max-width: 600px;">
            <h3 style="margin-top: 0; color: #2c3e50;"><i class="fas fa-shield-alt" style="color: #3498db;"></i> Security Checklist</h3>
            <ul style="text-align: left; color: #34495e; padding-left: 20px;">
                <li style="margin-bottom: 8px;">Verify the downloaded file integrity</li>
                <li style="margin-bottom: 8px;">Store your encryption keys in a secure password manager</li>
                <li style="margin-bottom: 8px;">Delete temporary encrypted files from insecure locations</li>
                <li style="margin-bottom: 8px;">Consider using secure deletion tools for sensitive files</li>
                <li>Audit your sharing permissions if file was sent to others</li>
            </ul>
        </div>
        
        <div class="security-tip">
            <div class="tip-header">
                <div class="tip-icon">
                    <i class="fas fa-lightbulb"></i>
                </div>
                <h3 style="margin: 0; color: #2c3e50;">Pro Tip: Secure Key Management</h3>
            </div>
            <p style="text-align: left; color: #34495e; margin-bottom: 0;">
                For maximum security, store your encryption keys separately from your encrypted files. 
                Consider using a trusted password manager or physical secure storage for your keys. 
                Never share keys through the same channel you shared the encrypted file.
            </p>
        </div>
        
        <div style="margin: 30px 0;">
            <button onclick="window.location.reload()" style="background-color: #3498db; color: white; border: none; padding: 15px 30px; border-radius: 30px; font-size: 18px; cursor: pointer; box-shadow: 0 4px 6px rgba(0,0,0,0.1); transition: all 0.3s; margin: 0 10px;">
                <i class="fas fa-redo" style="margin-right: 10px;"></i> Start New Session
            </button>
            <button onclick="show_modal('Need Help?', 'For assistance with secure file sharing:<br><br>1. Check our FAQ section<br>2. Contact our support team<br>3. Review the encryption documentation', 'Got it')" 
            style="background-color: #6c757d; color: white; border: none; padding: 15px 30px; border-radius: 30px; font-size: 18px; cursor: pointer; box-shadow: 0 4px 6px rgba(0,0,0,0.1); transition: all 0.3s; margin: 0 10px;">
                <i class="fas fa-question-circle" style="margin-right: 10px;"></i> Get Help
            </button>
        </div>
        
        <div style="margin-top: 40px; color: #95a5a6; font-size: 14px;">
            <p><i class="fas fa-clock"></i> Session ended: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</p>
            <p>Thank you for using our secure file sharing service. Your files were processed locally and never stored on our servers.</p>
        </div>
    </div>
    """))

# Upload a file for encryption
def upload_for_encryption():
    global uploaded_file, file_name, file_type, file_size, upload_time
    uploaded = files.upload()
    if uploaded:
        file_name = list(uploaded.keys())[0]
        uploaded_file = uploaded[file_name]
        file_type = file_name.split('.')[-1].lower()
        file_size = len(uploaded_file)
        upload_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return True
    return False

# Upload a file for decryption
def upload_for_decryption():
    global encrypted_data, file_name
    uploaded = files.upload()
    if uploaded:
        file_name = list(uploaded.keys())[0]
        encrypted_data = uploaded[file_name]
        return True
    return False

# Start the application
show_opening_window()
        