// image selection
document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('imageUpload').addEventListener('change', function(event) {
        const file = event.target.files[0];
        const uploadText = document.getElementById('uploadText');
        const uploadButton = document.getElementById('uploadButton');

        if (file) {
            // Update text with the selected file name
            uploadText.innerText = file.name;
            // Enable the upload button
            uploadButton.disabled = false;
        } else {
            // Reset text and disable the upload button
            uploadText.innerText = 'Choose an image (.jpeg, .png)';
            uploadButton.disabled = true;
        }
    });

    // upload 
    document.getElementById('uploadButton').addEventListener('click', function() {
        window.location.href = '/upload';
    });

});