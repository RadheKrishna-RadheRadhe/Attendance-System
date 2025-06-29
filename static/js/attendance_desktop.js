document.addEventListener('DOMContentLoaded', () => {
    const video = document.getElementById('video');
    const canvas = document.getElementById('canvas');
    const preview = document.getElementById('preview');
    const captureBtn = document.getElementById('captureBtn');
    const result = document.getElementById('result');
    const themeToggle = document.getElementById('themeToggle');

    // Set initial icon
    let isDark = false;
    themeToggle.textContent = '🌙';

    // Theme toggle
    themeToggle.addEventListener('click', () => {
        document.body.classList.toggle('dark');
        document.body.classList.toggle('light');
        isDark = !isDark;
        themeToggle.textContent = isDark ? '🌞' : '🌙';
    });

    // Start the camera
    navigator.mediaDevices.getUserMedia({ video: true })
        .then(stream => {
            video.srcObject = stream;
        })
        .catch(err => {
            showResult('❌ Error accessing camera: ' + err, 'red');
        });

    // Capture and upload
    captureBtn.addEventListener('click', async () => {
        // Draw frame to canvas
        const context = canvas.getContext('2d');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        context.drawImage(video, 0, 0, canvas.width, canvas.height);

        // Show preview
        preview.src = canvas.toDataURL('image/jpeg');
        preview.style.display = 'block';

        // Convert to blob and send
        canvas.toBlob(async (blob) => {
            if (!blob) {
                showResult('❌ Error capturing image.', 'red');
                return;
            }

            const formData = new FormData();
            formData.append('image', blob, 'attendance.jpg');

            showResult('⏳ Uploading...', 'black');

            try {
                const response = await fetch('/api/attendance_upload', {
                    method: 'POST',
                    body: formData
                });
                const data = await response.json();

                if (data.status === 'success') {
                    showResult(`✅ Attendance marked for ${data.name}!`, 'green');
                } else {
                    showResult(`❌ ${data.message}`, 'red');
                }
            } catch (err) {
                console.error(err);
                showResult('❌ Upload failed. Please try again.', 'red');
            }
        }, 'image/jpeg');
    });

    // Helper to show result with fade-in
    function showResult(message, color) {
        result.textContent = message;
        result.style.color = color;
        result.classList.add('show');
        setTimeout(() => result.classList.remove('show'), 5000);
    }
});
