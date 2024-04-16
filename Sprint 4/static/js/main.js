document.addEventListener('DOMContentLoaded', () => {
    
    // Form validation example
    const form = document.querySelector('form');
    form.addEventListener('submit', (e) => {
        const email = form.querySelector('input[type="email"]');
        if (!email.value.includes('@')) {
            e.preventDefault(); // Prevent form submission
            alert('Please enter a valid email address.');
            email.focus(); // Focus on the email field for the user to correct
        }
    });

    // Dynamic content loading example
    document.querySelectorAll('.load-content').forEach(button => {
        button.addEventListener('click', () => {
            const contentId = button.dataset.contentId; // Assume data-content-id attribute holds the content identifier
            fetch(`/get-content/${contentId}/`) // Fetch content from the server
                .then(response => response.text())
                .then(html => document.querySelector('#content-area').innerHTML = html)
                .catch(error => console.error('Error loading content:', error));
        });
    });

    // User interaction feedback example
    document.querySelectorAll('button').forEach(button => {
        button.addEventListener('click', () => {
            button.classList.add('button-clicked');
            setTimeout(() => button.classList.remove('button-clicked'), 200);
        });
    });
    
    // Animation example using CSS classes
    const animateElements = () => {
        document.querySelectorAll('.animatable').forEach(el => {
            el.classList.add('run-animation');
        });
    }

    // Run animations on page load
    animateElements();
});
