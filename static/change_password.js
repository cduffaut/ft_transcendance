const resetButton = document.querySelector('.reset-button');
resetButton.addEventListener('click', function () {
	const newPassword = document.getElementById('new-password').value;
	const confirmPassword = document.getElementById('confirm-new-password').value;
	const errorMessage = document.getElementById('error-message');
	const userInfo = document.getElementById('userInfo');
	const resetMessageLink = document.getElementById('reset-message-link');

    const username = userInfo.dataset.username;
    const token = userInfo.dataset.myemail;

	errorMessage.style.display = 'none';
	errorMessage.innerHTML = '';

	if (!newPassword || !confirmPassword) {
		errorMessage.textContent = 'Please complete all fields.';
		errorMessage.style.display = 'block';
	} else if (newPassword !== confirmPassword) {
		errorMessage.textContent = 'Two different passwords.';
		errorMessage.style.display = 'block';
	} else {
		console.log(JSON.stringify({
			username: username,
			token: token,
			new_password: newPassword,
		}))
		// Envoyer la requête POST
        fetch('/api/reset_password/change/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                username: username,
                token: token,
                new_password: newPassword
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                window.location.href = '/login';
                return;
            }
            throw new Error(data.error);
        })
        .then(() => {
            console.log('Réinitialisation du mot de passe réussie');
            resetButton.disabled = true;
            resetButton.style.backgroundColor = '#ccc';
            errorMessage.style.display = 'none';
            resetMessageLink.textContent = 'Mot de passe réinitialisé, veuillez vous connecter!';
            resetMessageLink.style.display = 'block';
        })
        .catch(error => {
            console.error('Erreur :', error);
            errorMessage.textContent = error.message;
            errorMessage.style.display = 'block';
        });        
	}
});

function getCookie(name) {
	let cookieValue = null;
	if (document.cookie && document.cookie !== '') {
		const cookies = document.cookie.split(';');
		for (let i = 0; i < cookies.length; i++) {
			const cookie = cookies[i].trim();
			if (cookie.substring(0, name.length + 1) === (name + '=')) {
				cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
				break;
			}
		}
	}
	return cookieValue;
}
