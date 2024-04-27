document.getElementById('login-form').addEventListener('submit', function (event) {
	event.preventDefault();

	// Serialize form data
	const formData = new FormData(this);

	// Send a POST request to the login API
	fetch('/api/login/', {
		method: 'POST',
		body: formData,
	})
		.then(response => {
			if (response.ok) {
				// Redirect upon successful login
				window.history.pushState(null, null, '/dashboard/');
				fetchPage('/dashboard/')
			} else {
				// Display error message if login fails
				response.json().then(data => {
					const errorMessageElement = document.getElementById('error-message');
					errorMessageElement.textContent = data.error || 'An unexpected error occurred'; // Assume 'data.error' is the error message
					errorMessageElement.style.display = 'block'; // Make the error message visible
				});
			}
		})
		.catch(error => {
			const errorMessageElement = document.getElementById('error-message');
			errorMessageElement.textContent = 'Failed to connect. Please try again.';
			errorMessageElement.style.display = 'block';
			console.error('Error:', error);
		});
});
	