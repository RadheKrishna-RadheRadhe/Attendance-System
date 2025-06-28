document.getElementById('generateBtn').addEventListener('click', async () => {
    const res = await fetch('/api/generate_qr');
    const data = await res.json();
    const qrResult = document.getElementById('qrResult');
    const qrGallery = document.getElementById('qrGallery');

    // Hide gallery when generating new QR
    qrGallery.innerHTML = '';
    qrResult.innerHTML = '';

    if (data.status === 'success') {
        const img = document.createElement('img');
        img.src = data.qr_image_url;
        img.alt = 'Generated QR Code';
        qrResult.appendChild(img);

        // Add modal open on click
        img.addEventListener('click', () => {
            openImageModal(data.qr_image_url);
        });
    } else {
        qrResult.textContent = data.message;
    }
});

document.getElementById('showBtn').addEventListener('click', async () => {
    // Clear generated QR code
    document.getElementById('qrResult').innerHTML = '';

    const res = await fetch('/api/list_qrs');
    const data = await res.json();
    const qrGallery = document.getElementById('qrGallery');
    qrGallery.innerHTML = '';

    if (data.status === 'success') {
        data.files.forEach(file => {
            const wrapper = document.createElement('div');
            wrapper.classList.add('qr-item');

            const img = document.createElement('img');
            img.src = file.url;
            img.alt = 'QR Code';

            const date = document.createElement('div');
            date.classList.add('qr-date');
            date.textContent = file.date;

            // Delete button
            const deleteBtn = document.createElement('button');
            deleteBtn.classList.add('qr-delete-btn');
            deleteBtn.textContent = '🗑️ Delete';
            deleteBtn.addEventListener('click', async (e) => {
                e.stopPropagation();  // Don't trigger zoom
                if (confirm('Are you sure you want to delete this QR code?')) {
                    await deleteQr(file.url);
                    // Refresh the gallery
                    document.getElementById('showBtn').click();
                }
            });

            // Zoom on click
            img.addEventListener('click', () => {
                openImageModal(file.url);
            });

            wrapper.appendChild(img);
            wrapper.appendChild(date);
            wrapper.appendChild(deleteBtn);
            qrGallery.appendChild(wrapper);
        });
    } else {
        qrGallery.textContent = data.message;
    }
});

async function deleteQr(fileUrl) {
    try {
        // Extract filename from URL
        const parts = fileUrl.split('/');
        const filename = parts[parts.length - 1];

        await fetch('/api/delete_qr', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ filename: filename })
        });
    } catch (err) {
        console.error('Error deleting QR:', err);
    }
}

function openImageModal(src) {
    const modal = document.getElementById('qrModal');
    const modalImg = document.getElementById('qrModalImg');
    modal.style.display = 'flex';
    modalImg.src = src;
}

document.getElementById('qrModal').addEventListener('click', () => {
    document.getElementById('qrModal').style.display = 'none';
});

// THEME TOGGLE with icon + label update
const themeToggle = document.getElementById('themeToggle');
const themeIcon = themeToggle.querySelector('.theme-icon');
const themeLabel = themeToggle.querySelector('.theme-label');

function updateThemeButton() {
    const isDark = document.body.classList.contains('dark');
    if (isDark) {
        themeIcon.textContent = '☀️';
        themeLabel.textContent = 'Light';
    } else {
        themeIcon.textContent = '🌙';
        themeLabel.textContent = 'Dark';
    }
}

themeToggle.addEventListener('click', () => {
    document.body.classList.toggle('dark');
    updateThemeButton();
});

// Initialize button on page load
updateThemeButton();
