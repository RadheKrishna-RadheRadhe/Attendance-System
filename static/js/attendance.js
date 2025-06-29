document.addEventListener('DOMContentLoaded', () => {
    const step = document.getElementById('step');
    const imageInput = document.getElementById('image');
    const previewImage = document.getElementById('previewImage');
    const statusDiv = document.getElementById('status');

    // Preview selected image
    imageInput.addEventListener('change', () => {
        if (imageInput.files.length) {
            previewImage.src = URL.createObjectURL(imageInput.files[0]);
            previewImage.style.display = 'block';
        } else {
            previewImage.style.display = 'none';
        }
    });

    document.getElementById('attendanceForm').addEventListener('submit', async (e) => {
        e.preventDefault();

        if (!imageInput.files.length) {
            alert('Please select an image!');
            return;
        }

        const formData = new FormData();
        formData.append('image', imageInput.files[0]);

        statusDiv.textContent = 'Uploading image... please wait.';
        statusDiv.style.color = 'black';

        try {
            const res = await fetch('/api/attendance_upload', {
                method: 'POST',
                body: formData
            });
            const data = await res.json();

            if (data.status === 'success') {
                statusDiv.textContent = `✅ Attendance marked for ${data.name}!`;
                statusDiv.style.color = 'green';

                document.getElementById('attendanceForm').reset();
                previewImage.src = '';
                previewImage.style.display = 'none';
            } else {
                statusDiv.textContent = `❌ Error: ${data.message}`;
                statusDiv.style.color = 'red';
            }
        } catch (err) {
            console.error(err);
            statusDiv.textContent = '❌ Upload failed. Please try again.';
            statusDiv.style.color = 'red';
        }
    });
});
