document.addEventListener('DOMContentLoaded', () => {
    const gallery = document.getElementById('gallery');
    const statusDiv = document.getElementById('status');
    const themeToggle = document.getElementById('themeToggle');

    const modal = document.getElementById('qrModal');
    const modalImg = document.getElementById('modalImg');
    const closeModal = document.getElementsByClassName('close')[0];

    // Theme toggle
    themeToggle.addEventListener('click', () => {
        document.body.classList.toggle('dark');
    });

    // Load existing Registration QR codes
    async function loadQrs() {
        gallery.innerHTML = 'Loading QR codes...';
        try {
            const res = await fetch('/api/list_register_qrs');
            const data = await res.json();
            if (data.status !== 'success') {
                gallery.innerHTML = 'Failed to load QR codes.';
                return;
            }

            const files = data.files;
            gallery.innerHTML = '';

            if (!files.length) {
                gallery.innerHTML = 'No registration QR codes found.';
                return;
            }

            // Show QR cards
            files.forEach(file => {
                const card = document.createElement('div');
                card.className = 'qr-card';

                const img = document.createElement('img');
                img.src = file.url;
                img.alt = 'Registration QR Code';

                // Zoom on click
                img.addEventListener('click', () => {
                    modal.style.display = 'block';
                    modalImg.src = img.src;
                });

                const link = document.createElement('a');
                link.href = '/static/register.html';
                link.className = 'qr-link';
                link.textContent = '📲 Open Registration Link';
                link.target = '_blank';

                card.appendChild(img);
                card.appendChild(link);
                gallery.appendChild(card);
            });
        } catch (err) {
            console.error(err);
            gallery.innerHTML = 'Error loading QR codes.';
        }
    }

    // Modal events
    closeModal.onclick = () => {
        modal.style.display = 'none';
    };

    window.onclick = (event) => {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    };

    loadQrs();
});
