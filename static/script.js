document.addEventListener('DOMContentLoaded', () => {
    const uploadArea = document.getElementById('upload-area');
    const fileInput = document.getElementById('file-input');
    const progressSection = document.getElementById('progress-section');
    const resultSection = document.getElementById('result-section');
    const progressBar = document.getElementById('progress-bar');
    const uploadingName = document.getElementById('uploading-name');
    const uploadingPercent = document.getElementById('uploading-percent');
    const resultFilename = document.getElementById('result-filename');
    const resultSize = document.getElementById('result-size');
    
    const inputHost = document.getElementById('share-url-host');
    const inputLocal = document.getElementById('share-url-local');
    const copyBtns = document.querySelectorAll('.copy-btn');
    const uploadAnother = document.getElementById('upload-another');

    if (!uploadArea) return;

    ['dragenter', 'dragover'].forEach(evt => {
        uploadArea.addEventListener(evt, (e) => {
            e.preventDefault();
            e.stopPropagation();
            uploadArea.classList.add('drag-over');
        });
    });

    ['dragleave', 'drop'].forEach(evt => {
        uploadArea.addEventListener(evt, (e) => {
            e.preventDefault();
            e.stopPropagation();
            uploadArea.classList.remove('drag-over');
        });
    });

    uploadArea.addEventListener('drop', (e) => {
        const files = e.dataTransfer.files;
        if (files.length > 0) uploadFile(files[0]);
    });

    uploadArea.addEventListener('click', () => {
        fileInput.click();
    });

    fileInput.addEventListener('change', () => {
        if (fileInput.files.length > 0) uploadFile(fileInput.files[0]);
    });

    function uploadFile(file) {
        uploadArea.classList.add('hidden');
        progressSection.classList.remove('hidden');
        resultSection.classList.add('hidden');

        uploadingName.textContent = file.name;
        uploadingPercent.textContent = '0%';
        progressBar.style.width = '0%';

        const formData = new FormData();
        formData.append('file', file);

        const xhr = new XMLHttpRequest();
        xhr.open('POST', '/upload', true);

        xhr.upload.addEventListener('progress', (e) => {
            if (e.lengthComputable) {
                const pct = Math.round((e.loaded / e.total) * 100);
                progressBar.style.width = pct + '%';
                uploadingPercent.textContent = pct + '%';
            }
        });

        xhr.addEventListener('load', () => {
            if (xhr.status === 200) {
                const data = JSON.parse(xhr.responseText);
                showResult(data);
            } else {
                let msg = 'Upload failed';
                try { msg = JSON.parse(xhr.responseText).error || msg; } catch(_) {}
                showError(msg);
            }
        });

        xhr.addEventListener('error', () => {
            showError('Network error — please try again');
        });

        xhr.send(formData);
    }

    function showResult(data) {
        progressSection.classList.add('hidden');
        resultSection.classList.remove('hidden');
        resultFilename.textContent = data.name;
        resultSize.textContent = data.size;
        
        inputHost.value = data.url_host;
        inputLocal.value = data.url_local;
    }

    function showError(msg) {
        progressSection.classList.add('hidden');
        uploadArea.classList.remove('hidden');
        showToast(msg);
    }

    copyBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const targetId = btn.getAttribute('data-target');
            const input = document.getElementById(targetId);
            
            navigator.clipboard.writeText(input.value).then(() => {
                const originalText = btn.textContent;
                btn.textContent = 'Copied';
                
                setTimeout(() => {
                    btn.textContent = originalText;
                }, 2000);
            });
        });
    });

    uploadAnother.addEventListener('click', () => {
        resultSection.classList.add('hidden');
        uploadArea.classList.remove('hidden');
        fileInput.value = '';
    });

    function showToast(msg) {
        const existing = document.querySelector('.toast');
        if (existing) existing.remove();
        const toast = document.createElement('div');
        toast.className = 'toast';
        toast.textContent = msg;
        document.body.appendChild(toast);
        
        setTimeout(() => toast.style.opacity = '1', 10);
        
        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => toast.remove(), 300);
        }, 2500);
    }
});
