document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector("form");
    const passwordInput = document.querySelector("input[name='password']");

    // Add toggle password feature
    const toggle = document.createElement("span");
    toggle.textContent = "Show Password";
    toggle.classList.add("toggle-password");
    passwordInput.insertAdjacentElement("afterend", toggle);

    toggle.addEventListener("click", () => {
        if (passwordInput.type === "password") {
            passwordInput.type = "text";
            toggle.textContent = "Hide Password";
        } else {
            passwordInput.type = "password";
            toggle.textContent = "Show Password";
        }
    });

    // Form validation
    form.addEventListener("submit", (e) => {
        const username = document.querySelector("input[name='username']").value.trim();
        const password = passwordInput.value.trim();

        let errorMessage = document.querySelector(".error");
        if (!errorMessage) {
            errorMessage = document.createElement("div");
            errorMessage.classList.add("error");
            form.appendChild(errorMessage);
        }

        if (username.length < 3) {
            e.preventDefault();
            errorMessage.textContent = "Username must be at least 3 characters.";
        } else if (password.length < 5) {
            e.preventDefault();
            errorMessage.textContent = "Password must be at least 5 characters.";
        } else {
            errorMessage.textContent = "";
        }
    });
});
