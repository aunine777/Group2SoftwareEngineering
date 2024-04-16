// This function will run once the document is fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Select all elements with the class 'notification-link'
    const notificationLinks = document.querySelectorAll('.notification-link');

    // Add a click event listener to each notification link
    notificationLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
            e.preventDefault(); // Prevent the default anchor link behavior
            const notificationId = this.dataset.notificationId; // Get the notification ID from the data attribute

            // Perform an AJAX POST request to the server to clear the notification
            fetch(`/clear_notification/${notificationId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'), // Retrieve the CSRF token
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ 'notification_id': notificationId })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json(); // Parse the JSON response
            })
            .then(data => {
                if(data.status === 'success') {
                    // If the response indicates success, remove the notification from the UI
                    this.closest('.notification-item').remove(); // Assumes notification link is within '.notification-item'
                } else {
                    // Handle the situation where the server didn't return a status of 'success'
                    console.error('Failed to clear notification:', data);
                }
            })
            .catch((error) => {
                // Log any errors to the console
                console.error('Error:', error);
            });
        });
    });
});

// Helper function to get the value of a named cookie
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Find the cookie with the specified name
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
