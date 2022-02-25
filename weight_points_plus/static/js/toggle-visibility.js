const toggleVisibility = (passwordElement, eyeOn, eyeOff, visibility) => {
  visibility.addEventListener("click", () => {
    if (passwordElement.type === "password") {
      passwordElement.type = "text";
    } else {
      passwordElement.type = "password";
    }
    eyeOn.classList.toggle("hidden");
    eyeOff.classList.toggle("hidden");
  });
};

const visibilityOne = document.querySelector("#visibility-icon-1");
const eyeOffOne = document.querySelector("#eye-off-1");
const eyeOnOne = document.querySelector("#eye-on-1");
toggleVisibility(password1, eyeOnOne, eyeOffOne, visibilityOne);

const visibilityTwo = document.querySelector("#visibility-icon-2");
if (!!visibilityTwo) {
  const eyeOffTwo = document.querySelector("#eye-off-2");
  const eyeOnTwo = document.querySelector("#eye-on-2");
  toggleVisibility(password2, eyeOnTwo, eyeOffTwo, visibilityTwo);
}

const visibilityOld = document.querySelector("#visibility-icon-old")
if (!!visibilityOld) {
  const eyeOffOld = document.querySelector("#eye-off-old");
  const eyeOnOld = document.querySelector("#eye-on-old");
  toggleVisibility(passwordOld, eyeOnOld, eyeOffOld, visibilityOld);
}
