document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('registerForm');
    const nameInput = document.getElementById('name');
    const regInput = document.getElementById('reg_number');
    const imageInput = document.getElementById('image');
    const previewImage = document.getElementById('previewImage');
    const statusDiv = document.getElementById('status');

    // Show image preview
    imageInput.addEventListener('change', () => {
        if (imageInput.files.length) {
            previewImage.src = URL.createObjectURL(imageInput.files[0]);
            previewImage.style.display = 'block';
        } else {
            previewImage.style.display = 'none';
        }
    });

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const name = nameInput.value.trim();
        const reg_number = regInput.value.trim();

        if (!name || !reg_number) {
            alert('Please enter BOTH name and registration number!');
            return;
        }

        if (!imageInput.files.length) {
            alert('Please select the face image!');
            return;
        }

        const formData = new FormData();
        formData.append('name', name);
        formData.append('reg_number', reg_number);
        formData.append('image', imageInput.files[0]);

        statusDiv.textContent = 'Uploading image... please wait.';
        statusDiv.style.color = 'black';

        try {
            const res = await fetch('/api/register', {
                method: 'POST',
                body: formData
            });
            const data = await res.json();

            if (data.status === 'success') {
                statusDiv.textContent = '✅ Registration successful!';
                statusDiv.style.color = 'green';

                form.reset();
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
