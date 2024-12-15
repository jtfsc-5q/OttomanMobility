document.addEventListener('DOMContentLoaded', function() {
    const dropzone = document.getElementById('dropzone-file');

    // Add event listener for the extract button
    document.getElementById('extract_data').addEventListener('click', function() {
        extractAppointmentDataFromText(document.getElementById('latinized_text').innerText).
        then(r => {} );
    });

    // Dropzone events.
    dropzone.addEventListener('dragover', function(event) {
        event.preventDefault();
    });

    dropzone.addEventListener('drop', function(event) {
        event.preventDefault();
        const files = event.dataTransfer.files;
        if (files.length > 0) {
            handleFileUpload(files[0]);
            displayImage(files[0]);  // New function to display the image in the div
        }
    });

    dropzone.addEventListener('change', function(event) {
        const files = event.target.files;
        if (files.length > 0) {
            handleFileUpload(files[0]);
            displayImage(files[0]);  // New function to display the image in the div
        }
    });

});

// Event listener for pasting an image
document.addEventListener('paste', function(event) {
    const items = event.clipboardData.items;
    for (let i = 0; i < items.length; i++) {
        if (items[i].type.indexOf('image') !== -1) {
            const file = items[i].getAsFile();
            handleFileUpload(file);  // Still upload the image file if needed
            displayImage(file);  // New function to display the image in the div
            break;
        }
    }
});