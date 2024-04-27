document.getElementById("signupForm").addEventListener("submit", function(event) {
    event.preventDefault();
    var formData = {
        username: document.getElementById("id_username").value,
        email: document.getElementById("id_email").value,
        password: document.getElementById("id_password1").value,
        confirmPassword: document.getElementById("id_password2").value
    };
    if (formData.password !== formData.confirmPassword) {
        document.getElementById('error-message').textContent = "The passwords do not match.";
        document.getElementById('error-message').style.display = 'block';
        return;
    }
    fetch('/api/signup/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify(formData)
    })
    .then(response => {
        if (!response.ok) {
            response.json().then(data => {
                // Itérer sur chaque clé de l'objet d'erreur et concaténer les messages
                let errorMessage = "";
                Object.keys(data).forEach(key => {
                    if(Array.isArray(data[key])) {
                        errorMessage += data[key].join(" ") + " ";
                    } else {
                        errorMessage += data[key] + " ";
                    }
                });
                document.getElementById('error-message').textContent = errorMessage.trim();
                document.getElementById('error-message').style.display = 'block';
            });
        }
        else
        {
            window.history.pushState(null, null, '/email_sent/');
            fetchPage('/email_sent/')
        }
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('error-message').textContent = "Registration error. Please try again.";
        document.getElementById('error-message').style.display = 'block';
    });
});
