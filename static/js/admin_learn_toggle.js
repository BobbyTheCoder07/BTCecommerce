document.addEventListener("DOMContentLoaded", function() {
    function handleToggle(selectEl) {
        if (!selectEl) return;
        const val = selectEl.value;
        
        // Find container: either .inline-related (for subtopic inlines) or the main form
        const inlineContainer = selectEl.closest(".inline-related");
        if (inlineContainer) {
            const contentRow = inlineContainer.querySelector(".field-content");
            const contentCodeRow = inlineContainer.querySelector(".field-content_code");
            if (val === "editor") {
                if (contentRow) contentRow.style.display = "";
                if (contentCodeRow) contentCodeRow.style.display = "none";
            } else if (val === "code") {
                if (contentRow) contentRow.style.display = "none";
                if (contentCodeRow) contentCodeRow.style.display = "";
            }
        } else {
            // Standalone form
            const contentRow = document.querySelector(".field-content");
            const contentCodeRow = document.querySelector(".field-content_code");
            if (val === "editor") {
                if (contentRow) contentRow.style.display = "";
                if (contentCodeRow) contentCodeRow.style.display = "none";
            } else if (val === "code") {
                if (contentRow) contentRow.style.display = "none";
                if (contentCodeRow) contentCodeRow.style.display = "";
            }
        }
    }

    // Delegate changes on the document body to catch dynamically added inline forms
    document.body.addEventListener("change", function(e) {
        if (e.target && (e.target.id === "id_content_type" || e.target.id.endsWith("-content_type"))) {
            handleToggle(e.target);
        }
    });

    // Run initially for all selectors
    document.querySelectorAll("select[id='id_content_type'], select[id$='-content_type']").forEach(handleToggle);

    // Watch for dynamically added forms to toggle initially
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            mutation.addedNodes.forEach(function(node) {
                if (node.nodeType === 1) {
                    node.querySelectorAll("select[id$='-content_type']").forEach(handleToggle);
                }
            });
        });
    });
    const targetNode = document.querySelector('#content-main') || document.body;
    observer.observe(targetNode, { childList: true, subtree: true });
});
