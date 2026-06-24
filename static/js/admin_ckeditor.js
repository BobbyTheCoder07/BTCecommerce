document.addEventListener("DOMContentLoaded", function() {
    // Find the content textarea inside the topic change form
    const textarea = document.getElementById("id_content");
    if (textarea) {
        // Initialize CKEditor 5 ClassicEditor
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
                window.editor = editor;
                console.log("CKEditor 5 initialized successfully on field id_content");
            })
            .catch(error => {
                console.error("Error initializing CKEditor 5: ", error);
            });
    }
});
