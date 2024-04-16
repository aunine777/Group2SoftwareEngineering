document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('form');
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        console.log('Form Submitted...');

        // Simulate form data sending
        const formData = new FormData(form);
        fetch(form.action, {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (response.ok) {
                return response.json();  // Assuming the response is JSON
            }
            throw new Error('Network response was not ok.');
        })
        .then(data => {
            console.log('Success:', data);
            // Assuming the server sends back a JSON with a redirect URL
            window.location.href = data.redirectUrl; 
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Failed to process checkout.');
        });
    });
});
