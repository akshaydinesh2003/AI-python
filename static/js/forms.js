document.addEventListener("DOMContentLoaded", function() {
    // Login form validation
    const loginForm = document.querySelector('.form');
    loginForm.addEventListener('submit', function(e) {
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        if (!username || !password) {
            alert('Please fill out both fields.');
            e.preventDefault();
        }
    });

    // Signup form validation
    const signupForm = document.querySelector('.form');
    if (signupForm) {
        signupForm.addEventListener('submit', function(e) {
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            const confirmPassword = document.getElementById('confirm_password').value;
            if (!username || !password || password !== confirmPassword) {
                alert('Please ensure all fields are filled correctly and passwords match.');
                e.preventDefault();
            }
        });
    }
});
