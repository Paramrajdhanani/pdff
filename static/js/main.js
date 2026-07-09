// Main JavaScript for PDF <=> Word Converter Pro (Anti-Gravity Theme)

document.addEventListener('DOMContentLoaded', () => {
    // 1. Initialize Anti-Gravity Canvas Particles
    initAntiGravityParticles();

    // 2. Initialize Drag & Drop Zone if it exists
    initDragAndDrop();

    // 3. Initialize Conversion Form Submission with Progress Tracking
    initConversionForm();

    // 4. Initialize Toggle Selector for Conversion Type
    initConverterTypeSelector();

    // 5. Initialize Magnetic Hover Buttons
    initMagneticButtons();
});

/**
 * Creates a canvas particle system simulating floating anti-gravity dust/nebula particles.
 */
function initAntiGravityParticles() {
    const canvas = document.getElementById('particle-canvas');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    
    // Timeline tracking variables (orbit angle)
    let orbitAngle = 0; 
    const cycleSpeed = 0.003; // Speeds of day-night cycles (~40 seconds per cycle)
    
    // Pausing states (stops at center apex for 1 minute)
    let isPaused = false;
    let pauseEndTime = 0;

    // Weather variation counters (moves)
    let moonCycleCount = 1;
    let sunCycleCount = 1;
    let hasTriggeredMoonCycleIncrement = false;
    let hasTriggeredSunCycleIncrement = false;

    // Twinkling stars collection
    let stars = [];

    // Snowflakes collection (active on moon cycle % 3 === 0)
    let snowflakes = [];
    const snowflakeCount = 95; // More dense, realistic snowfall
    for (let i = 0; i < snowflakeCount; i++) {
        // Size maps to depth: larger flakes are closer, move faster, and are more opaque (3D parallax)
        const size = Math.random() * 3.2 + 0.8;
        const depth = size / 4.0; // 0.2 to 1.0 depth factor
        snowflakes.push({
            x: Math.random() * window.innerWidth,
            y: Math.random() * window.innerHeight,
            size: size,
            depth: depth,
            speedY: depth * 1.4 + 0.4, // closer flakes fall faster
            speedX: -0.3 - depth * 0.4, // sway leftward with wind direction
            phase: Math.random() * Math.PI * 2,
            phaseSpeed: Math.random() * 0.03 + 0.01
        });
    }

    // Wind streaks collection (active on sun cycle % 3 === 0)
    let windStreaks = [];
    const windStreakCount = 20; // Increase count for higher air turbulence density
    for (let i = 0; i < windStreakCount; i++) {
        windStreaks.push({
            x: Math.random() * window.innerWidth,
            y: Math.random() * (window.innerHeight * 0.65), 
            length: Math.random() * 110 + 60,
            speedX: Math.random() * 9 + 8, // fast wind speed
            phase: Math.random() * Math.PI * 2,
            phaseSpeed: Math.random() * 0.04 + 0.02,
            amplitude: Math.random() * 14 + 4, // height of sine wave oscillation (turbulence)
            opacity: Math.random() * 0.08 + 0.02
        });
    }
    // Drifting clouds collection
    let clouds = [];
    
    function resizeCanvas() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    // Populate stars randomly scattered in the upper sky
    const starCount = 80;
    for (let i = 0; i < starCount; i++) {
        stars.push({
            x: Math.random() * canvas.width,
            y: Math.random() * (canvas.height * 0.65), 
            size: Math.random() * 2 + 0.4,
            twinkleSpeed: Math.random() * 0.04 + 0.01,
            phase: Math.random() * Math.PI
        });
    }

    // Cloud class template
    class Cloud {
        constructor() {
            this.reset();
            // Scatter horizontally at start
            this.x = Math.random() * canvas.width;
        }

        reset() {
            this.x = -300;
            this.y = Math.random() * (canvas.height * 0.35) - 30;
            this.radius = Math.random() * 150 + 80;
            this.speedX = Math.random() * 0.15 + 0.05; // Slow drifting movement
            this.baseOpacity = Math.random() * 0.8 + 0.5;
        }

        update() {
            this.x += this.speedX;
            if (this.x - this.radius > canvas.width) {
                this.reset();
            }
        }

        draw(dayFactor) {
            ctx.save();
            
            // Interpolate cloud color based on dayFactor:
            // Night: Dark grey-blue (15, 15, 30)
            // Sunset: Pinkish-orange (210, 110, 95)
            // Day: Bright white (245, 245, 245)
            let r, g, b, cloudOpacity;
            if (dayFactor < 0.25) {
                let f = dayFactor / 0.25;
                r = Math.round(15 + (210 - 15) * f);
                g = Math.round(15 + (110 - 15) * f);
                b = Math.round(30 + (95 - 30) * f);
                cloudOpacity = (0.22 + f * 0.08) * this.baseOpacity;
            } else {
                let f = (dayFactor - 0.25) / 0.75;
                r = Math.round(210 + (245 - 210) * f);
                g = Math.round(110 + (245 - 110) * f);
                b = Math.round(95 + (245 - 95) * f);
                cloudOpacity = (0.3 - f * 0.1) * this.baseOpacity; // slightly thinner white clouds
            }

            let gradient = ctx.createRadialGradient(
                this.x, this.y, 10,
                this.x, this.y, this.radius
            );
            
            gradient.addColorStop(0, `rgba(${r}, ${g}, ${b}, ${cloudOpacity})`);
            gradient.addColorStop(0.5, `rgba(${r}, ${g}, ${b}, ${cloudOpacity * 0.3})`);
            gradient.addColorStop(1, 'rgba(0,0,0,0)');
            
            ctx.fillStyle = gradient;
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
            ctx.fill();
            ctx.restore();
        }
    }

    // Populate clouds
    const cloudCount = 8;
    for (let i = 0; i < cloudCount; i++) {
        clouds.push(new Cloud());
    }



    // Helper to interpolate between two RGB colors
    function lerpColor(c1, c2, f) {
        let r = Math.round(c1.r + (c2.r - c1.r) * f);
        let g = Math.round(c1.g + (c2.g - c1.g) * f);
        let b = Math.round(c1.b + (c2.b - c1.b) * f);
        return `rgb(${r}, ${g}, ${b})`;
    }

    // Animation Loop
    function animate() {
        // Increment timeline angle
        orbitAngle = (orbitAngle + cycleSpeed) % (Math.PI * 2);

        // Orbital pivot points configuration
        const centerX = canvas.width / 2;
        const centerY = canvas.height * 0.95; // Pivot below screen horizon
        const orbitRadiusX = canvas.width * 0.45;
        const orbitRadiusY = canvas.height * 0.65;

        // Position coordinates of Sun
        const sunX = centerX + orbitRadiusX * Math.cos(orbitAngle);
        const sunY = centerY + orbitRadiusY * Math.sin(orbitAngle);

        // Position coordinates of Moon (opposite of Sun)
        const moonX = centerX + orbitRadiusX * Math.cos(orbitAngle + Math.PI);
        const moonY = centerY + orbitRadiusY * Math.sin(orbitAngle + Math.PI);

        // Cycle rise increments tracking
        if (moonY < centerY) {
            if (!hasTriggeredMoonCycleIncrement) {
                moonCycleCount++;
                hasTriggeredMoonCycleIncrement = true;
                hasTriggeredSunCycleIncrement = false;
            }
        } else {
            if (!hasTriggeredSunCycleIncrement) {
                sunCycleCount++;
                hasTriggeredSunCycleIncrement = true;
                hasTriggeredMoonCycleIncrement = false;
            }
        }

        // Calculate daytime fraction (0.0 = night, 1.0 = mid-day)
        // Sun is up when sin(orbitAngle) is negative
        let dayFactor = 0;
        if (orbitAngle > Math.PI && orbitAngle < Math.PI * 2) {
            dayFactor = -Math.sin(orbitAngle);
        }

        // 1. Draw Sky Background (interpolating natural sky colors)
        ctx.save();
        let skyGradient = ctx.createLinearGradient(0, 0, 0, canvas.height);
        
        let topColor, bottomColor;
        if (dayFactor < 0.25) {
            // Night transitioning into Dawn/Dusk
            let f = dayFactor / 0.25;
            topColor = lerpColor({r:2, g:2, b:15}, {r:45, g:25, b:75}, f);
            bottomColor = lerpColor({r:5, g:5, b:30}, {r:225, g:95, b:65}, f);
        } else {
            // Dawn/Dusk transitioning into bright Blue Sky
            let f = (dayFactor - 0.25) / 0.75;
            topColor = lerpColor({r:45, g:25, b:75}, {r:62, g:142, b:225}, f);
            bottomColor = lerpColor({r:225, g:95, b:65}, {r:145, g:215, b:245}, f);
        }
        
        skyGradient.addColorStop(0, topColor);
        skyGradient.addColorStop(0.75, `#020202`); // Deep ground shadow fading
        skyGradient.addColorStop(1, bottomColor);
        
        ctx.fillStyle = skyGradient;
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.restore();

        // 2. Draw Twinkling Stars (only visible during night factor)
        const nightFactor = 1 - dayFactor;
        if (nightFactor > 0.05) {
            ctx.save();
            stars.forEach(star => {
                star.phase += star.twinkleSpeed;
                let starOpacity = (Math.sin(star.phase) * 0.4 + 0.6) * nightFactor * 0.8;
                
                ctx.globalAlpha = starOpacity;
                ctx.fillStyle = '#ffffff';
                ctx.beginPath();
                ctx.arc(star.x, star.y, star.size, 0, Math.PI * 2);
                ctx.fill();
            });
            ctx.restore();
        }



        // 5. Draw drifting clouds (boost speeds during daytime cycle 3, 6, 9... representing "fast air")
        const cloudSpeedMultiplier = (sunY < centerY && sunCycleCount % 3 === 0) ? 6 : 1;
        clouds.forEach(c => {
            c.x += c.speedX * (cloudSpeedMultiplier - 1); // Extra speed boost
            c.update();
            c.draw(dayFactor);
        });

        // 6. Fast Air Wind Streaks (Only active on Sun cycle % 3 === 0 during the day)
        const isWindActive = (sunY < centerY) && (sunCycleCount % 3 === 0);
        if (isWindActive) {
            ctx.save();
            windStreaks.forEach(w => {
                w.x += w.speedX;
                w.phase += w.phaseSpeed;
                
                if (w.x > canvas.width) {
                    w.x = -w.length;
                    w.y = Math.random() * (canvas.height * 0.65);
                    w.phase = Math.random() * Math.PI * 2;
                }

                // Draw wind streak as a smooth wave (turbulence) with tapered ends
                ctx.beginPath();
                ctx.lineWidth = 1.0;
                
                let wispGrad = ctx.createLinearGradient(w.x, w.y, w.x + w.length, w.y);
                const currentOpacity = w.opacity * dayFactor;
                wispGrad.addColorStop(0, 'rgba(255, 255, 255, 0)');
                wispGrad.addColorStop(0.5, `rgba(255, 255, 255, ${currentOpacity})`);
                wispGrad.addColorStop(1, 'rgba(255, 255, 255, 0)');
                ctx.strokeStyle = wispGrad;
                
                for (let dx = 0; dx < w.length; dx += 10) {
                    let px = w.x + dx;
                    let py = w.y + Math.sin((px * 0.015) + w.phase) * w.amplitude;
                    
                    if (dx === 0) {
                        ctx.moveTo(px, py);
                    } else {
                        ctx.lineTo(px, py);
                    }
                }
                ctx.stroke();
            });
            ctx.restore();
        }

        // 7. Snow rendering (Only active on Moon cycle % 3 === 0 during the night)
        const isSnowActive = (moonY < centerY) && (moonCycleCount % 3 === 0);
        if (isSnowActive) {
            ctx.save();
            snowflakes.forEach(s => {
                s.y += s.speedY;
                s.phase += s.phaseSpeed;
                s.x += s.speedX + Math.sin(s.phase) * 0.35;

                // Reset snowflake boundaries
                if (s.y > canvas.height) {
                    s.y = -10;
                    s.x = Math.random() * canvas.width;
                }
                if (s.x > canvas.width) s.x = 0;
                if (s.x < 0) s.x = canvas.width;

                // Opacity is tied to depth (3D Parallax effect)
                let snowOpacity = s.depth * 0.75 * nightFactor;
                ctx.fillStyle = `rgba(255, 255, 255, ${snowOpacity})`;
                ctx.beginPath();
                ctx.arc(s.x, s.y, s.size, 0, Math.PI * 2);
                ctx.fill();
            });
            ctx.restore();
        }

        // 8. Draw Horizon Line Divider
        ctx.save();
        ctx.strokeStyle = `rgba(255, 255, 255, ${0.02 + dayFactor * 0.03})`;
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(0, centerY);
        ctx.lineTo(canvas.width, centerY);
        ctx.stroke();
        ctx.restore();

        requestAnimationFrame(animate);
    }
    animate();
}

/**
 * Configures Drag and Drop operations for upload cards.
 */
/**
 * Configures Drag and Drop operations for upload cards and file previews.
 */
function initDragAndDrop() {
    const dropzone = document.getElementById('dropzone');
    const fileInput = document.getElementById('file-input');
    const selectedFileText = document.getElementById('selected-file-text');
    const filePreviewWrapper = document.getElementById('file-preview-wrapper');
    const filePreviewList = document.getElementById('file-preview-list');

    if (!dropzone || !fileInput) return;

    // Trigger click on input when clicking dropzone
    dropzone.addEventListener('click', () => {
        fileInput.click();
    });

    fileInput.addEventListener('change', () => {
        handleFileSelect(fileInput.files);
    });

    // Prevent default behaviors for drag-drop events
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropzone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    // Add visual indicator on dragover
    ['dragenter', 'dragover'].forEach(eventName => {
        dropzone.addEventListener(eventName, () => {
            dropzone.classList.add('dragover');
        }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropzone.addEventListener(eventName, () => {
            dropzone.classList.remove('dragover');
        }, false);
    });

    // Handle dropped files
    dropzone.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        if (files && files.length > 0) {
            fileInput.files = files;
            handleFileSelect(files);
        }
    });

    // Handle multiple file previews and individual removals
    function handleFileSelect(files) {
        if (!files || files.length === 0) {
            if (filePreviewWrapper) filePreviewWrapper.classList.add('d-none');
            const type = document.getElementById('conversion-type').value;
            resetDropzoneLabel(type);
            return;
        }

        const type = document.getElementById('conversion-type').value;
        let filesToProcess = files;

        // If the active tool only supports 1 file, truncate the selection to the first file!
        const singleFileTools = ['pdf_to_docx', 'docx_to_pdf', 'compress_pdf', 'split_pdf', 'pdf_to_jpg'];
        if (singleFileTools.includes(type)) {
            if (files.length > 1) {
                const dt = new DataTransfer();
                dt.items.add(files[0]);
                fileInput.files = dt.files;
                filesToProcess = fileInput.files;
            }
        }

        if (filePreviewWrapper && filePreviewList) {
            filePreviewWrapper.classList.remove('d-none');
            let html = '';
            for (let i = 0; i < filesToProcess.length; i++) {
                const file = filesToProcess[i];
                const ext = file.name.split('.').pop().toLowerCase();
                let iconClass = 'fa-file-pdf text-danger';
                if (ext === 'docx') iconClass = 'fa-file-word text-primary';
                else if (['jpg', 'jpeg', 'png'].includes(ext)) iconClass = 'fa-file-image text-warning';

                html += `
                <div class="file-preview-item">
                    <div class="file-preview-meta">
                        <i class="fa-solid ${iconClass} file-preview-icon"></i>
                        <div>
                            <div class="file-preview-name" title="${file.name}">${file.name}</div>
                            <div class="file-preview-size">${(file.size / (1024 * 1024)).toFixed(2)} MB</div>
                        </div>
                    </div>
                    <button type="button" class="file-preview-remove" data-index="${i}">
                        <i class="fa-solid fa-xmark"></i>
                    </button>
                </div>
                `;
            }
            filePreviewList.innerHTML = html;

            // Bind click handlers to individual file removal buttons
            const removeButtons = filePreviewList.querySelectorAll('.file-preview-remove');
            removeButtons.forEach(btn => {
                btn.addEventListener('click', (e) => {
                    e.stopPropagation(); // Avoid triggering dropzone click
                    const idxToRemove = parseInt(btn.getAttribute('data-index'));
                    removeFileFromInput(idxToRemove);
                });
            });
        }

        // Visual highlights for dropzone
        selectedFileText.innerHTML = `<strong class="text-white">${filesToProcess.length} file(s) selected</strong> <span class="d-block text-muted small mt-1">Payload ready for transformation</span>`;
        dropzone.style.borderColor = '#9d4edd';
        dropzone.style.boxShadow = '0 0 25px rgba(157, 78, 221, 0.25) inset';
    }

    // Programmatically remove a file from fileInput list using DataTransfer
    function removeFileFromInput(index) {
        const dt = new DataTransfer();
        const { files } = fileInput;
        for (let i = 0; i < files.length; i++) {
            if (i !== index) {
                dt.items.add(files[i]);
            }
        }
        fileInput.files = dt.files;
        handleFileSelect(fileInput.files);
    }
}

/**
 * Handles Form AJAX post with real-time file upload progress indicators.
 */
function initConversionForm() {
    const form = document.getElementById('converter-form');
    if (!form) return;

    const fileInput = document.getElementById('file-input');
    const submitBtn = document.getElementById('submit-btn');
    const progressWrapper = document.getElementById('progress-wrapper');
    const progressBar = document.getElementById('progress-bar');
    const progressText = document.getElementById('progress-text');
    const spinnerSection = document.getElementById('spinner-section');
    const spinnerTitle = document.getElementById('spinner-title');
    const errorAlert = document.getElementById('converter-error-alert');

    form.addEventListener('submit', (e) => {
        e.preventDefault();

        // 1. Basic validation
        if (!fileInput || fileInput.files.length === 0) {
            showError("Please select or drop files to proceed.");
            return;
        }

        const files = fileInput.files;
        const conversionType = document.getElementById('conversion-type').value;

        // Validation based on tool type
        if (conversionType in {'pdf_to_docx': 1, 'compress_pdf': 1, 'split_pdf': 1, 'pdf_to_jpg': 1, 'unlock_pdf': 1, 'lock_pdf': 1, 'watermark_pdf': 1, 'remove_watermark': 1, 'add_page_numbers': 1}) {
            if (files.length !== 1) {
                showError("Exactly 1 PDF file is required for this operation.");
                return;
            }
            const ext = files[0].name.split('.').pop().toLowerCase();
            if (ext !== 'pdf') {
                showError("File type mismatch. PDF file required.");
                return;
            }
        } else if (conversionType === 'docx_to_pdf') {
            if (files.length !== 1) {
                showError("Exactly 1 DOCX file is required for this operation.");
                return;
            }
            const ext = files[0].name.split('.').pop().toLowerCase();
            if (ext !== 'docx') {
                showError("File type mismatch. Word Document (.docx) required.");
                return;
            }
        } else if (conversionType === 'jpg_to_pdf') {
            if (files.length < 1) {
                showError("Select at least 1 image file for conversion.");
                return;
            }
            for (let i = 0; i < files.length; i++) {
                const ext = files[i].name.split('.').pop().toLowerCase();
                if (!['jpg', 'jpeg', 'png'].includes(ext)) {
                    showError("All selected files must be images (JPG/PNG).");
                    return;
                }
            }
        }

        // Hide prior errors and prepare UI states
        hideError();
        submitBtn.disabled = true;
        progressWrapper.style.display = 'block';
        progressBar.style.width = '0%';
        progressText.innerText = 'Initializing upload...';

        // Configure spinner titles based on toolkit mode
        let activeSpinnerMsg = 'TRANSLATING DOCUMENT GEOMETRY...';
        if (conversionType === 'docx_to_pdf') activeSpinnerMsg = 'COMPILING PDF STRUCTURE...';
        else if (conversionType === 'compress_pdf') activeSpinnerMsg = 'COMPRESSING STREAM DENSITIES...';
        else if (conversionType === 'split_pdf') activeSpinnerMsg = 'DISASSEMBLING PAGES ARCHIVE...';
        else if (conversionType === 'jpg_to_pdf') activeSpinnerMsg = 'BINDING IMAGES TO PDF GRID...';
        else if (conversionType === 'pdf_to_jpg') activeSpinnerMsg = 'RENDERING PAGES TO JPG IMAGES...';
        else if (conversionType === 'unlock_pdf') activeSpinnerMsg = 'DECRYPTING PDF DOCUMENT...';
        else if (conversionType === 'lock_pdf') activeSpinnerMsg = 'ENCRYPTING PDF DOCUMENT...';

        if (spinnerTitle) spinnerTitle.innerText = activeSpinnerMsg;

        // 2. Build Form Data
        const formData = new FormData(form);
        // Clean and append files list (in case of multiple)
        formData.delete('file');
        for (let i = 0; i < files.length; i++) {
            formData.append('file', files[i]);
        }

        // 3. Initiate XMLHttpRequest for progress events
        const xhr = new XMLHttpRequest();
        xhr.open('POST', form.action, true);

        // Track upload progress
        xhr.upload.addEventListener('progress', (event) => {
            if (event.lengthComputable) {
                const percent = Math.round((event.loaded / event.total) * 100);
                progressBar.style.width = percent + '%';
                progressText.innerText = `Uploading: ${percent}%`;
                
                if (percent >= 100) {
                    progressText.innerText = 'Upload complete! Reformatting particles...';
                    spinnerSection.classList.remove('d-none');
                }
            }
        });

        // Track request completion
        xhr.onreadystatechange = () => {
            if (xhr.readyState === XMLHttpRequest.DONE) {
                spinnerSection.classList.add('d-none');
                submitBtn.disabled = false;
                
                if (xhr.status === 200) {
                    try {
                        const response = JSON.parse(xhr.responseText);
                        if (response.success) {
                            window.location.href = response.redirect_url;
                        } else {
                            showError(response.message || "An unexpected error occurred during conversion.");
                            progressWrapper.style.display = 'none';
                        }
                    } catch (err) {
                        showError("Failed to parse server response. Verify conversion module.");
                        progressWrapper.style.display = 'none';
                    }
                } else {
                    let errMsg = "Server connection lost. Please try again.";
                    try {
                        const errObj = JSON.parse(xhr.responseText);
                        errMsg = errObj.message || errMsg;
                    } catch(e) {}
                    showError(errMsg);
                    progressWrapper.style.display = 'none';
                }
            }
        };

        xhr.send(formData);
    });

    function showError(msg) {
        if (!errorAlert) return;
        errorAlert.innerText = msg;
        errorAlert.classList.remove('d-none');
        errorAlert.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    function hideError() {
        if (!errorAlert) return;
        errorAlert.classList.add('d-none');
    }
}

// Reset Dropzone UI text labels when changing tools
function resetDropzoneLabel(type) {
    const selectedFileText = document.getElementById('selected-file-text');
    const acceptText = document.getElementById('accept-file-text');
    const dropzone = document.getElementById('dropzone');
    const fileInput = document.getElementById('file-input');

    if (!selectedFileText || !acceptText || !dropzone || !fileInput) return;

    // Default borders
    dropzone.style.borderColor = 'rgba(0, 242, 254, 0.3)';
    dropzone.style.boxShadow = 'none';

    // Set labels
    if (type === 'pdf_to_docx') {
        selectedFileText.innerText = 'Drag & Drop PDF here or click to browse';
        acceptText.innerText = 'Supported format: PDF (.pdf) - Max 200MB';
        fileInput.setAttribute('accept', '.pdf');
    } else if (type === 'docx_to_pdf') {
        selectedFileText.innerText = 'Drag & Drop Word file here or click to browse';
        acceptText.innerText = 'Supported format: Word Document (.docx) - Max 200MB';
        fileInput.setAttribute('accept', '.docx');
    } else if (type === 'compress_pdf') {
        selectedFileText.innerText = 'Drag & Drop PDF here or click to browse';
        acceptText.innerText = 'Supported format: PDF (.pdf) - Max 200MB';
        fileInput.setAttribute('accept', '.pdf');
    } else if (type === 'unlock_pdf' || type === 'lock_pdf' || type === 'watermark_pdf' || type === 'remove_watermark' || type === 'add_page_numbers') {
        selectedFileText.innerText = 'Drag & Drop PDF here or click to browse';
        acceptText.innerText = 'Supported format: PDF (.pdf) - Max 200MB';
        fileInput.setAttribute('accept', '.pdf');
    } else if (type === 'split_pdf') {
        selectedFileText.innerText = 'Drag & Drop PDF here or click to browse';
        acceptText.innerText = 'Supported format: PDF (.pdf) - Will extract all pages as a ZIP';
        fileInput.setAttribute('accept', '.pdf');
    } else if (type === 'jpg_to_pdf') {
        selectedFileText.innerText = 'Drag & Drop images here or click to browse';
        acceptText.innerText = 'Supported formats: JPG, JPEG, PNG - Select 1 or more files';
        fileInput.setAttribute('accept', '.jpg,.jpeg,.png');
    } else if (type === 'pdf_to_jpg') {
        selectedFileText.innerText = 'Drag & Drop PDF here or click to browse';
        acceptText.innerText = 'Supported format: PDF (.pdf) - Will convert pages to ZIP of JPGs';
        fileInput.setAttribute('accept', '.pdf');
    }
}

/**
 * Handles style changing and input updating on the conversion type select options.
 */
function initConverterTypeSelector() {
    const buttons = document.querySelectorAll('.converter-selector-btn');
    const typeInput = document.getElementById('conversion-type');
    const fileInput = document.getElementById('file-input');
    const filePreviewWrapper = document.getElementById('file-preview-wrapper');
    const submitBtnText = document.getElementById('submit-btn-text');

    if (buttons.length === 0 || !typeInput) return;

    // Helper: configure active states and labels for selected type
    function selectTool(type, activeBtn) {
        // Remove active state from all buttons
        buttons.forEach(b => b.classList.remove('active'));

        // Set active state on clicked
        if (activeBtn) activeBtn.classList.add('active');

        // Update hidden input type
        typeInput.value = type;

        // Clear file input and previews
        if (fileInput) fileInput.value = '';
        if (filePreviewWrapper) filePreviewWrapper.classList.add('d-none');

        // Reset dropzone parameters
        resetDropzoneLabel(type);

        // Update submit button text based on tool selected
        if (submitBtnText) {
            let label = 'Launch Transformation Sequence';
            if (type === 'pdf_to_docx') label = 'Convert PDF to Word';
            else if (type === 'docx_to_pdf') label = 'Convert Word to PDF';
            else if (type === 'compress_pdf') label = 'Compress PDF';
            else if (type === 'split_pdf') label = 'Split PDF Pages';
            else if (type === 'jpg_to_pdf') label = 'Convert Images to PDF';
            else if (type === 'pdf_to_jpg') label = 'Convert PDF to Images';
            else if (type === 'unlock_pdf') label = 'Unlock PDF';
            else if (type === 'lock_pdf') label = 'Lock PDF';
            else if (type === 'watermark_pdf') label = 'Watermark PDF';
            else if (type === 'remove_watermark') label = 'Remove Watermark';
            else if (type === 'add_page_numbers') label = 'Add Page Numbers';
            submitBtnText.innerText = label;
        }
    }

    buttons.forEach(btn => {
        btn.addEventListener('click', () => {
            const type = btn.getAttribute('data-type');
            selectTool(type, btn);
        });
    });

    // Check query string parameters to pre-select tool from home / dashboard cards
    const urlParams = new URLSearchParams(window.location.search);
    const preselectedTool = urlParams.get('tool');
    if (preselectedTool) {
        const matchingBtn = document.querySelector(`.converter-selector-btn[data-type="${preselectedTool}"]`);
        if (matchingBtn) {
            selectTool(preselectedTool, matchingBtn);
        }
    }
}

/**
 * Implements magnetic hover effects for CTAs and launchpad cards using GSAP animations.
 */
function initMagneticButtons() {
    // Select the navbar brand, dashboard links, launchpad cards, and cyber-themed buttons
    const targets = document.querySelectorAll('.btn-cyber, .navbar-brand, .toolkit-launchpad-card, .hero-tab');
    
    targets.forEach(el => {
        // Capture default styles or transformations
        el.addEventListener('mousemove', (e) => {
            const rect = el.getBoundingClientRect();
            // Calculate cursor offset distance from the element's exact midpoint
            const x = e.clientX - rect.left - rect.width / 2;
            const y = e.clientY - rect.top - rect.height / 2;
            
            // Adjust factor based on whether it is a small button or large card
            const factor = el.classList.contains('toolkit-launchpad-card') ? 0.15 : 0.3;

            gsap.to(el, {
                x: x * factor,
                y: y * factor,
                scale: 1.025,
                duration: 0.3,
                ease: 'power2.out',
                overwrite: 'auto'
            });
        });

        el.addEventListener('mouseleave', () => {
            // Snap back weightlessly to the origin point
            gsap.to(el, {
                x: 0,
                y: 0,
                scale: 1,
                duration: 0.5,
                ease: 'elastic.out(1, 0.3)',
                overwrite: 'auto'
            });
        });
    });
}
