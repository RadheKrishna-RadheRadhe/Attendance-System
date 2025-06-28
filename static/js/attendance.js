document.getElementById('submitBtn').addEventListener('click', async () => {
    const fileInput = document.getElementById('fileInput');
    const message = document.getElementById('message');

    if (!fileInput.files.length) {
        message.textContent = 'Please select or capture a photo.';
        return;
    }

    const formData = new FormData();
    formData.append('image', fileInput.files[0]);

    try {
        const res = await fetch('/api/attendance_upload', {
            method: 'POST',
            body: formData
        });
        const data = await res.json();
        message.textContent = data.message;
    } catch (error) {
        message.textContent = 'Error uploading photo. Please try again.';
    }
});
