document.addEventListener("DOMContentLoaded", function() {
    const contentTypeSelect = document.getElementById("id_content_type");
    const markdownRow = document.querySelector(".field-content_markdown");
    const htmlRow = document.querySelector(".field-content_html");

    if (contentTypeSelect) {
        function toggleFields() {
            const val = contentTypeSelect.value;
            if (val === "markdown") {
                if (markdownRow) markdownRow.style.display = "";
                if (htmlRow) htmlRow.style.display = "none";
            } else if (val === "html") {
                if (markdownRow) markdownRow.style.display = "none";
                if (htmlRow) htmlRow.style.display = "";
            }
        }

        contentTypeSelect.addEventListener("change", toggleFields);
        toggleFields(); // Run initially
    }
});
