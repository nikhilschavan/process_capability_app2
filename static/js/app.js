function uploadFile() {
    let fileInput = document.getElementById('file-upload');
    let file = fileInput.files[0];
    let usl = document.getElementById('usl').value;
    let lsl = document.getElementById('lsl').value;
    
    if (!file) {
        alert('Please select a file!');
        return;
    }
    
    if (!usl || !lsl) {
        alert('Please enter both USL and LSL values!');
        return;
    }

    // Show the progress bar while uploading
    document.getElementById('progress-bar').style.display = 'block';
    
    let formData = new FormData();
    formData.append('file', file);
    formData.append('usl', usl);
    formData.append('lsl', lsl);

    $.ajax({
        url: '/upload',
        type: 'POST',
        data: formData,
        processData: false,
        contentType: false,
        xhr: function() {
            let xhr = new XMLHttpRequest();
            xhr.upload.addEventListener('progress', function(e) {
                if (e.lengthComputable) {
                    let percent = (e.loaded / e.total) * 100;
                    $('#progress').val(percent);
                }
            });
            return xhr;
        },
        success: function(response) {
            // Hide the progress bar
            document.getElementById('progress-bar').style.display = 'none';
            
            // Show download link
            document.getElementById('download-link').style.display = 'block';
            document.getElementById('download-report').href = response.report_url;
        },
        error: function() {
            alert('An error occurred while uploading the file.');
            document.getElementById('progress-bar').style.display = 'none';
        }
    });
}
