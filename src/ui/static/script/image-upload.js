// image selection
document.addEventListener('DOMContentLoaded', function () {
    const uploadText = document.getElementById('uploadText');
    const uploadIcon = document.querySelector('.icon');
    
    document.getElementById('imageUpload').addEventListener('change', function(event) {
        const file = event.target.files[0];
        const uploadButton = document.getElementById('uploadButton');

        if (file) {
            // Hide the upload icon and text
            uploadText.style.display = 'none'; 
            uploadIcon.style.display = 'none'; 

            // Show the preview image
            const preview = document.getElementById('preview');
            const reader = new FileReader();

            reader.onload = function(e) {
                preview.src = e.target.result;
                preview.style.display = 'block'; // Show the preview
            };

            reader.readAsDataURL(file);

            // Enable the upload button
            uploadButton.disabled = false;
        } else {
            // Reset text and disable the upload button
            uploadText.innerText = 'Choose an image (.jpeg, .png)';
            uploadButton.disabled = true;
            uploadText.style.display = 'block'; // Show upload text
            uploadIcon.style.display = 'block'; // Show upload icon
            document.getElementById('preview').style.display = 'none'; // Hide preview
        }
    });

    // upload 
    document.getElementById('uploadButton').addEventListener('click', function() {
        document.getElementById('imageUploadForm').submit();
    });
});
