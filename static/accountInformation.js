var colorData = {};

document.querySelectorAll(".button-8").forEach((button) => {
  if (typeof Pickr == 'undefined') {
    return;
  }
  const pickr = new Pickr({
    default: "#42445a",

    el: button,
    theme: "monolith",
    swatches: [
      "rgba(244, 67, 54, 1)",
      "rgba(233, 30, 99, 1)",
      "rgba(156, 39, 176, 1)",
      "rgba(103, 58, 183, 1)",
    ],
    components: {
      preview: true,
      hue: true,
      interaction: {
        hex: true,
        rgba: true,
        hsla: true,
        hsva: true,
        cmyk: true,
        input: true,
        save: true,
      },
    },
  });

  pickr.on("save", (color, instance) => {
    const colorValue = color.toRGBA().toString();
    button.style.backgroundColor = colorValue;
    console.log(button.getAttribute("id") + " changed to " + colorValue);
    pickr.hide();
    const colorId = button.getAttribute("id");
    colorData[colorId] = color.toHEXA().toString().substring(0, 7);
  });
});

fetch("/api/colors/")
  .then((response) => {
    if (response.ok) {
      return response.json();
    }
    throw new Error();
  })
  .then((data) => {
    Object.entries(data).forEach(([key, value]) => {
      const colorPicker = document.getElementById(key);
      if (colorPicker) {
        colorPicker.style.backgroundColor = value;
        colorPicker.setAttribute("data-color", value);
      }
    });
  })
  .catch((error) => {
    console.error("Error:", error); // Log any errors
  });

document
  .getElementById("color_btn")
  .addEventListener("click", function (event) {
    console.log(JSON.stringify(colorData));

    const finalColorData = {
      ball_color: colorData["BallColor"],
      paddle_color: colorData["MyPaddleColor"],
      enemy_paddle_color: colorData["EnemyPaddleColor"],
      frame_color: colorData["CadreColor"],
      background_color: colorData["BgColor"],
    };

    fetch("/api/colors/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCookie("csrftoken"),
      },
      body: JSON.stringify(finalColorData),
    })
      .then((response) => {
        if (response.ok) {
          return response.json();
        } else {
          throw new Error("Failed to update colors");
        }
      })
      .then((data) => {
        console.log(data.message); // Log success message
      })
      .catch((error) => {
        console.error("Error:", error); // Log any errors
      });
  });





document
.getElementById("updateInfoForm")
.addEventListener("submit", update_Info);

function update_Info(event)
{
event.preventDefault();
  var formData = new FormData(this);

  fetch("/api/update_profile/", {
    method: "POST",
    body: formData,
  });
}


document
  .getElementById("passwordChangeForm")
  .addEventListener("submit", function (event) {
    event.preventDefault();

    var formData = new FormData(this);

    fetch("/api/change_password/", {
      method: "POST",
      body: formData,
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.error) {
          var passwordError = document.getElementById("passwordError");
          passwordError.textContent = data.error;
          passwordError.style.display = "block";
        } else {
          var passwordSuccess = document.getElementById("passwordSuccess");
          passwordSuccess.textContent =
            "Your password has been successfully changed.";
          passwordSuccess.style.display = "block";
        }
      })

      .catch((error) => {
        console.error("Error:", error);
        var passwordError = document.getElementById("passwordError");
        passwordError.textContent =
          "An unexpected error occurred. Please try again later.";
        passwordError.style.display = "block";
      });
  });

function submitForm() {
  var formData = new FormData();
  var fileInput = document.getElementById("profilePicture");
  var file = fileInput.files[0];
  formData.append("profile_picture", file);

  fetch("/api/upload_profile/", {
    method: "POST",
    body: formData,
    headers: { "X-CSRFToken": getCookie("csrftoken") },
  })
    .then((response) => response.json())
    .then((data) => {
      refresh_image();
    })
    .catch((error) => {
      console.error("Error:", error);
    });
}

function refresh_image() {
  fetch("/api/profile_pic/")
    .then((response) => response.blob())
    .then((blob) => {
      return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onloadend = () => resolve(reader.result);
        reader.onerror = reject;
        reader.readAsDataURL(blob);
      });
    })
    .then((data) => {
      document.getElementById("profile-pic").src = data;
    });
}
refresh_image();
