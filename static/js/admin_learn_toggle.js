document.addEventListener("DOMContentLoaded", function() {
    const contentTypeSelect = document.getElementById("id_content_type");
    const contentRow = document.querySelector(".field-content");
    const contentCodeRow = document.querySelector(".field-content_code");

    if (contentTypeSelect) {
        function toggleFields() {
            const val = contentTypeSelect.value;
            if (val === "editor") {
                if (contentRow) contentRow.style.display = "";
                if (contentCodeRow) contentCodeRow.style.display = "none";
            } else if (val === "code") {
                if (contentRow) contentRow.style.display = "none";
                if (contentCodeRow) contentCodeRow.style.display = "";
            }
        }

        contentTypeSelect.addEventListener("change", toggleFields);
        toggleFields(); // Run initially
    }
});
