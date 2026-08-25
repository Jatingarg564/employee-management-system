(function () {
    "use strict";

    const STORAGE_KEY = "ems-swagger-theme";
    const BUTTON_ID = "swagger-theme-toggle";
    const DARK_CLASS = "swagger-dark";


    /* ========================================================
       Get saved theme
       ======================================================== */

    function getSavedTheme() {
        return (
            localStorage.getItem(STORAGE_KEY) ||
            "light"
        );
    }


    /* ========================================================
       Apply theme
       ======================================================== */

    function applyTheme(theme) {

        const root =
            document.documentElement;

        root.classList.toggle(
            DARK_CLASS,
            theme === "dark"
        );

        /*
         * Remove the temporary loading class.
         */

        root.classList.remove(
            "swagger-dark-pending"
        );

        updateToggleButton(theme);
    }


    /* ========================================================
       Update toggle button
       ======================================================== */

    function updateToggleButton(theme) {

        const button =
            document.getElementById(
                BUTTON_ID
            );

        if (!button) {
            return;
        }

        const icon =
            button.querySelector(
                ".swagger-theme-toggle-icon"
            );

        const text =
            button.querySelector(
                ".swagger-theme-toggle-text"
            );


        if (theme === "dark") {

            icon.textContent = "☀";

            text.textContent = "Light Mode";

            button.setAttribute(
                "aria-label",
                "Switch to light mode"
            );

        } else {

            icon.textContent = "☾";

            text.textContent = "Dark Mode";

            button.setAttribute(
                "aria-label",
                "Switch to dark mode"
            );
        }
    }


    /* ========================================================
       Toggle theme
       ======================================================== */

    function toggleTheme() {

        const currentTheme =
            document.documentElement.classList.contains(
                DARK_CLASS
            )
                ? "dark"
                : "light";


        const newTheme =
            currentTheme === "dark"
                ? "light"
                : "dark";


        localStorage.setItem(
            STORAGE_KEY,
            newTheme
        );


        applyTheme(newTheme);
    }


    /* ========================================================
       Create toggle button
       ======================================================== */

    function createToggleButton() {

        if (
            document.getElementById(
                BUTTON_ID
            )
        ) {
            return true;
        }


        const swaggerContainer =
            document.getElementById(
                "swagger-ui"
            );


        if (!swaggerContainer) {
            return false;
        }


        const button =
            document.createElement(
                "button"
            );


        button.id = BUTTON_ID;

        button.type = "button";

        button.className =
            "swagger-theme-toggle";


        button.innerHTML = `
            <span
                class="swagger-theme-toggle-icon"
                aria-hidden="true"
            ></span>

            <span
                class="swagger-theme-toggle-text"
            ></span>
        `;


        button.addEventListener(
            "click",
            toggleTheme
        );


        swaggerContainer.appendChild(
            button
        );


        updateToggleButton(
            getSavedTheme()
        );


        return true;
    }


    /* ========================================================
       Initialize
       ======================================================== */

    function initialize() {

        /*
         * IMPORTANT:
         *
         * Apply the saved theme immediately.
         */

        const savedTheme =
            getSavedTheme();


        applyTheme(
            savedTheme
        );


        /*
         * Swagger UI renders dynamically.
         */

        if (
            createToggleButton()
        ) {
            return;
        }


        /*
         * Wait until #swagger-ui exists.
         */

        const observer =
            new MutationObserver(
                function () {

                    if (
                        createToggleButton()
                    ) {

                        observer.disconnect();
                    }
                }
            );


        observer.observe(
            document.body,
            {
                childList: true,
                subtree: true,
            }
        );


        /*
         * Fallback check.
         */

        let attempts = 0;


        const interval =
            setInterval(
                function () {

                    attempts++;


                    if (
                        createToggleButton()
                    ) {

                        clearInterval(
                            interval
                        );

                        observer.disconnect();

                        return;
                    }


                    if (
                        attempts >= 20
                    ) {

                        clearInterval(
                            interval
                        );
                    }

                },
                500
            );
    }


    /* ========================================================
       Start
       ======================================================== */

    if (
        document.readyState === "loading"
    ) {

        document.addEventListener(
            "DOMContentLoaded",
            initialize
        );

    } else {

        initialize();
    }

})();