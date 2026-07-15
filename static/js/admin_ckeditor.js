document.addEventListener("DOMContentLoaded", function() {
    // Select all textareas matching content, description, content_html, and dynamically created inline content textareas
    function initCKEditor(textarea) {
        if (textarea && !textarea.dataset.ckeditorInitialized) {
            ClassicEditor
                .create(textarea, {
                    toolbar: {
                        items: [
                            'heading', '|',
                            'bold', 'italic', 'underline', 'strikethrough', '|',
                            'bulletedList', 'numberedList', '|',
                            'outdent', 'indent', '|',
                            'insertTable', 'blockQuote', 'codeBlock', '|',
                            'undo', 'redo'
                        ]
                    },
                    language: 'en',
                    table: {
                        contentToolbar: [
                            'tableColumn',
                            'tableRow',
                            'mergeTableCells'
                        ]
                    }
                })
                .then(editor => {
                    textarea.dataset.ckeditorInitialized = "true";
                    console.log("CKEditor 5 initialized successfully on " + textarea.id);
                })
                .catch(error => {
                    console.error("Error initializing CKEditor 5 on " + textarea.id + ": ", error);
                });
        }
    }

    // Initialize existing textareas
    const selector = 'textarea[id$="-content"], textarea[id="id_content"], textarea[id="id_description"], textarea[id="id_content_html"]';
    document.querySelectorAll(selector).forEach(initCKEditor);

    // Watch for dynamically added inline forms (Django admin inlines)
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            mutation.addedNodes.forEach(function(node) {
                if (node.nodeType === 1) { // Element node
                    // Check if the added node itself is a textarea matching our selector or contains one
                    if (node.matches && node.matches(selector)) {
                        initCKEditor(node);
                    }
                    node.querySelectorAll(selector).forEach(initCKEditor);
                }
            });
        });
    });

    // Start observing the admin form or document body
    const targetNode = document.querySelector('#content-main') || document.body;
    observer.observe(targetNode, { childList: true, subtree: true });
});
