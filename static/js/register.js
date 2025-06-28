document.getElementById('registerBtn').addEventListener('click', async () => {
    const nameInput = document.getElementById('nameInput');
    const fileInput = document.getElementById('fileInput');
    const message = document.getElementById('message');

    if (!nameInput.value.trim()) {
        message.textContent = 'Please enter a name.';
        return;
    }

    if (!fileInput.files.length) {
        message.textContent = 'Please select or capture a photo.';
        return;
    }

    const formData = new FormData();
    formData.append('name', nameInput.value.trim());
    formData.append('image', fileInput.files[0]);

    try {
        const res = await fetch('/api/register', {
            method: 'POST',
            body: formData
        });
        const data = await res.json();
        message.textContent = data.message;
    } catch (error) {
        console.error('Error:', error);
        message.textContent = 'Error registering user. Please try again.';
    }
});
