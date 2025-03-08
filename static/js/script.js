document.addEventListener('DOMContentLoaded', function() {
    // Global variables
    let uploadedFiles = [];
    let sessionId = null;
    let selectedTransition = 'left';
    let transitionDuration = 1.0;
    
    // DOM elements
    const dropArea = document.getElementById('drop-area');
    const fileInput = document.getElementById('file-input');
    const browseBtn = document.getElementById('browse-btn');
    const previewContainer = document.getElementById('preview-container');
    const thumbnailsContainer = document.getElementById('thumbnails-container');
    const fileCount = document.getElementById('file-count');
    const addMoreBtn = document.getElementById('add-more-btn');
    const clearBtn = document.getElementById('clear-btn');
    const transitionSlider = document.getElementById('transition-slider');
    const transitionValue = document.getElementById('transition-value');
    const optionBtns = document.querySelectorAll('.option-btn');
    const generateBtn = document.getElementById('generate-btn');
    const processingIndicator = document.getElementById('processing-indicator');
    const progressBar = document.getElementById('progress-bar');
    const stageScript = document.getElementById('stage-script');
    const stageVoice = document.getElementById('stage-voice');
    const stageVideo = document.getElementById('stage-video');
    const previewStep = document.getElementById('preview-step');
    const resultVideo = document.getElementById('result-video');
    const downloadBtn = document.getElementById('download-btn');
    const startOverBtn = document.getElementById('start-over-btn');
    
    // Additional DOM elements for new features
    const helpBtn = document.getElementById('help-btn');
    const helpModal = document.getElementById('help-modal');
    const closeModalBtn = helpModal.querySelector('.close-btn');
    const closeHelpBtn = document.getElementById('close-help-btn');
    const startNowBtn = document.getElementById('start-now-btn');
    const offlineNotification = document.getElementById('offline-notification');
    
    // Event listeners for file upload
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, preventDefaults, false);
    });
    
    ['dragenter', 'dragover'].forEach(eventName => {
        dropArea.addEventListener(eventName, highlight, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, unhighlight, false);
    });
    
    dropArea.addEventListener('drop', handleDrop, false);
    browseBtn.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', handleFileSelect);
    addMoreBtn.addEventListener('click', () => fileInput.click());
    clearBtn.addEventListener('click', clearFiles);
    
    // Event listeners for customization options
    transitionSlider.addEventListener('input', updateTransitionDuration);
    optionBtns.forEach(btn => {
        btn.addEventListener('click', selectTransitionStyle);
    });
    
    // Event listeners for generation and download
    generateBtn.addEventListener('click', generateVideo);
    downloadBtn.addEventListener('click', downloadVideo);
    startOverBtn.addEventListener('click', resetApp);
    
    // Help modal event listeners
    helpBtn.addEventListener('click', openHelpModal);
    closeModalBtn.addEventListener('click', closeHelpModal);
    closeHelpBtn.addEventListener('click', closeHelpModal);
    helpModal.addEventListener('click', function(e) {
        if (e.target === helpModal) {
            closeHelpModal();
        }
    });
    
    // Start now button scrolls to upload section
    startNowBtn.addEventListener('click', function() {
        document.getElementById('upload-step').scrollIntoView({
            behavior: 'smooth'
        });
    });
    
    // Network status detection
    window.addEventListener('online', updateOnlineStatus);
    window.addEventListener('offline', updateOnlineStatus);
    updateOnlineStatus();
    
    // Utility functions
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    function highlight() {
        dropArea.classList.add('highlight');
    }
    
    function unhighlight() {
        dropArea.classList.remove('highlight');
    }
    
    // Handle file uploads
    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFiles(files);
    }
    
    function handleFileSelect() {
        handleFiles(fileInput.files);
    }
    
    function handleFiles(files) {
        const validFiles = Array.from(files).filter(file => {
            const type = file.type;
            return type === 'image/jpeg' || type === 'image/png' || type === 'image/jpg';
        });
        
        if (validFiles.length === 0) {
            showToast('Please upload image files (JPG, JPEG, PNG)', 'error');
            return;
        }
        
        // Limit to 20 images
        if (uploadedFiles.length + validFiles.length > 20) {
            showToast('Maximum 20 images allowed', 'error');
            return;
        }
        
        // Add files to our collection
        uploadedFiles = [...uploadedFiles, ...validFiles];
        updateFilePreview();
        uploadFiles(validFiles);
    }
    
    function updateFilePreview() {
        if (uploadedFiles.length > 0) {
            previewContainer.style.display = 'block';
            fileCount.textContent = `(${uploadedFiles.length})`;
            generateBtn.disabled = false;
            
            // Clear and rebuild thumbnails
            thumbnailsContainer.innerHTML = '';
            uploadedFiles.forEach((file, index) => {
                const reader = new FileReader();
                reader.onload = function(e) {
                    const thumbnail = document.createElement('div');
                    thumbnail.className = 'thumbnail';
                    thumbnail.innerHTML = `
                        <img src="${e.target.result}" alt="Image ${index + 1}">
                        <button class="remove-btn" data-index="${index}">
                            <i class="fa-solid fa-xmark"></i>
                        </button>
                    `;
                    thumbnailsContainer.appendChild(thumbnail);
                    
                    // Add event listener to remove button
                    thumbnail.querySelector('.remove-btn').addEventListener('click', function() {
                        removeFile(parseInt(this.getAttribute('data-index')));
                    });

                    // Add animation to the thumbnail
                    setTimeout(() => {
                        thumbnail.style.opacity = '1';
                    }, index * 100);
                };
                reader.readAsDataURL(file);
            });
        } else {
            previewContainer.style.display = 'none';
            generateBtn.disabled = true;
        }
    }
    
    function removeFile(index) {
        uploadedFiles.splice(index, 1);
        updateFilePreview();
    }
    
    function clearFiles() {
        uploadedFiles = [];
        updateFilePreview();
        sessionId = null;
    }
    
    // Customization functions
    function updateTransitionDuration() {
        transitionDuration = parseFloat(transitionSlider.value);
        transitionValue.textContent = `${transitionDuration.toFixed(1)}s`;
        
        // Update slider background
        const percent = ((transitionDuration - 0.5) / 1.5) * 100;
        transitionSlider.style.background = `linear-gradient(to right, var(--primary-color) 0%, var(--primary-color) ${percent}%, var(--gray-300) ${percent}%, var(--gray-300) 100%)`;
    }
    
    function selectTransitionStyle(e) {
        const clicked = e.currentTarget;
        optionBtns.forEach(btn => btn.classList.remove('active'));
        clicked.classList.add('active');
        selectedTransition = clicked.getAttribute('data-slide');
        
        // Add animation effect
        clicked.classList.add('pulse');
        setTimeout(() => {
            clicked.classList.remove('pulse');
        }, 500);
    }
    
    // API interaction functions
    async function uploadFiles(files) {
        try {
            const formData = new FormData();
            files.forEach(file => {
                formData.append('files[]', file);
            });
            
            showToast('Uploading images...', 'info');
            
            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`Server responded with ${response.status}: ${errorText}`);
            }
            
            const data = await response.json();
            
            if (data.status === 'success') {
                sessionId = data.session_id;
                showToast(`${data.file_count} images uploaded successfully`, 'success');
            } else {
                showToast(data.error || 'Upload failed', 'error');
            }
        } catch (error) {
            console.error('Error uploading files:', error);
            showToast(`Error uploading files: ${error.message}`, 'error');
        }
    }
    
    async function generateVideo() {
        if (!sessionId) {
            showToast('Please upload images first', 'error');
            return;
        }
        
        try {
            // Show processing UI
            generateBtn.disabled = true;
            processingIndicator.style.display = 'block';
            
            // Start progress animation
            animateProgress();
            
            // Make API request with better error handling
            const response = await fetch('/api/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    session_id: sessionId,
                    transition: transitionDuration,
                    slide: selectedTransition
                })
            });
            
            if (!response.ok) {
                // If server returns 503 Service Unavailable, show specific message
                if (response.status === 503) {
                    const data = await response.json();
                    throw new Error(`Video generation is unavailable: ${data.error || 'Missing dependencies'}. ${data.solution || 'Run quickfix.bat to fix the issue.'}`);
                } else {
                    throw new Error(`Server responded with status ${response.status}`);
                }
            }
            
            const data = await response.json();
            
            if (data.status === 'success') {
                // Show preview
                resultVideo.src = data.video_url;
                previewStep.style.display = 'block';
                showToast('Video created successfully!', 'success');
                
                // Auto scroll to preview section
                previewStep.scrollIntoView({ behavior: 'smooth' });
                
                // Complete progress animation immediately
                progressBar.style.width = '100%';
                stageScript.classList.add('completed');
                stageVoice.classList.add('completed');
                stageVideo.classList.add('completed');

                // Add animated entrance for the preview step
                previewStep.classList.add('animate-in');
            } else {
                showToast(data.error || 'Failed to generate video', 'error');
                resetProcessingUI();
            }
        } catch (error) {
            console.error('Error generating video:', error);
            showToast(`Error: ${error.message}`, 'error');
            resetProcessingUI();
        }
    }
    
    function animateProgress() {
        // Stage 1: Script generation (0-30%)
        stageScript.classList.add('active');
        animateProgressTo(30, 0, 5000, () => {
            // Stage 2: Voice creation (30-60%)
            stageScript.classList.add('completed');
            stageVoice.classList.add('active');
            animateProgressTo(60, 30, 8000, () => {
                // Stage 3: Video building (60-95%)
                stageVoice.classList.add('completed');
                stageVideo.classList.add('active');
                animateProgressTo(95, 60, 10000);
            });
        });
    }
    
    function animateProgressTo(targetPercent, startPercent, duration, callback) {
        const startTime = performance.now();
        
        function updateProgress(currentTime) {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const currentPercent = startPercent + progress * (targetPercent - startPercent);
            
            progressBar.style.width = `${currentPercent}%`;
            
            if (progress < 1) {
                requestAnimationFrame(updateProgress);
            } else if (callback) {
                callback();
            }
        }
        
        requestAnimationFrame(updateProgress);
    }
    
    function resetProcessingUI() {
        generateBtn.disabled = false;
        processingIndicator.style.display = 'none';
        progressBar.style.width = '0%';
        stageScript.classList.remove('active', 'completed');
        stageVoice.classList.remove('active', 'completed');
        stageVideo.classList.remove('active', 'completed');
    }
    
    function downloadVideo() {
        if (!resultVideo.src) return;
        
        // Add download animation
        downloadBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Downloading...';
        
        // Create a temporary link to download the video
        const a = document.createElement('a');
        a.href = resultVideo.src;
        a.download = 'video.mp4';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        
        // Reset button after animation
        setTimeout(() => {
            downloadBtn.innerHTML = '<i class="fa-solid fa-download"></i> Download Video';
        }, 1500);
    }
    
    function resetApp() {
        // Reset all states
        uploadedFiles = [];
        sessionId = null;
        selectedTransition = 'left';
        transitionDuration = 1.0;
        
        // Reset UI
        clearFiles();
        resetProcessingUI();
        previewStep.style.display = 'none';
        resultVideo.src = '';
        transitionSlider.value = 1.0;
        updateTransitionDuration();
        optionBtns.forEach(btn => {
            btn.classList.remove('active');
            if (btn.getAttribute('data-slide') === 'left') {
                btn.classList.add('active');
            }
        });
        
        // Scroll to top with animation
        window.scrollTo({ top: 0, behavior: 'smooth' });
        
        // Show reset confirmation
        showToast('Ready to create a new video!', 'success');
    }
    
    // Toast notification
    function showToast(message, type = 'info') {
        const toast = document.getElementById('toast');
        toast.textContent = message;
        toast.className = `toast ${type} show`;
        
        // Add appropriate icon based on type
        const iconClass = type === 'success' ? 'fa-check-circle' : 
                          type === 'error' ? 'fa-exclamation-circle' : 
                          'fa-info-circle';
        
        toast.innerHTML = `
            <i class="fa-solid ${iconClass}"></i>
            <span>${message}</span>
        `;
        
        // Set timeout to hide toast
        setTimeout(() => {
            toast.classList.remove('show');
        }, 3000);
    }

    // Add animation classes when elements come into view
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    // Observe all workflow steps
    document.querySelectorAll('.workflow-step').forEach(step => {
        observer.observe(step);
    });

    // Initialize slider background
    updateTransitionDuration();
    
    // Modal functions
    function openHelpModal(e) {
        if (e) e.preventDefault();
        helpModal.classList.add('show');
        document.body.style.overflow = 'hidden'; // Prevent scrolling behind modal
    }
    
    function closeHelpModal() {
        helpModal.classList.remove('show');
        document.body.style.overflow = '';
    }
    
    // Network status function
    function updateOnlineStatus() {
        if (navigator.onLine) {
            offlineNotification.classList.remove('show');
            // Enable features that require network
            generateBtn.disabled = uploadedFiles.length === 0;
        } else {
            offlineNotification.classList.add('show');
            // Disable features that require network
            generateBtn.disabled = true;
            
            // Show toast with offline message
            showToast('You are offline. Please connect to the internet to generate videos.', 'error');
        }
    }
    
    // Register service worker for PWA support
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/static/service-worker.js')
            .then(function() {
                console.log('Service Worker registered successfully');
            })
            .catch(function(error) {
                console.log('Service Worker registration failed:', error);
            });
    }

    // Add status checking functionality
    async function checkProcessingStatus() {
        if (!sessionId) return;
        
        try {
            const response = await fetch(`/api/status/${sessionId}`);
            if (!response.ok) return;
            
            const data = await response.json();
            if (data.status === "complete") {
                // Processing completed while checking
                progressBar.style.width = '100%';
                stageScript.classList.add('completed');
                stageVoice.classList.add('completed');
                stageVideo.classList.add('completed');
            }
        } catch (error) {
            console.error("Error checking status:", error);
        }
    }
});
