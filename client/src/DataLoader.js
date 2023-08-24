import React, { useState } from 'react';

const DataLoader = () => {
  const [selectedFiles, setSelectedFiles] = useState(null);
  const [uploadMessage, setUploadMessage] = useState('');
  const [uploadedFileUrl, setUploadedFileUrl] = useState('');

  const handleFileChange = (event) => {
    setSelectedFiles(event.target.files);
  };

  const handleUpload = async () => {
    if (!selectedFiles || selectedFiles.length === 0) {
      return;
    }

    setUploadMessage('Uploading and processing...');
    try {
      const formData = new FormData();
      for (let i = 0; i < selectedFiles.length; i++) {
        formData.append('files', selectedFiles[i]);
        // Log progress to console
        console.log(`Uploading file ${i + 1}/${selectedFiles.length}`);
      }

      const response = await fetch('http://localhost:5000/upload', {
        method: 'POST',
        body: formData,
        timeout: 6000000, // Set timeout to 10 minutes (600,000 milliseconds)
        });

      if (response.ok) {
        console.log("Got a response!");
        console.log(response);
        
        // const contentType = response.headers.get('content-type');
        // if (contentType && contentType.includes('application/json')) {
        //     const responseData = await response.json();
        //     // Handle the responseData as needed
        //     console.log("responseData:");
        //     console.log(responseData);
        //     const fileData = responseData.video;
        //     const fileUrl = URL.createObjectURL(convertBase64ToBlob(fileData));
        //     setUploadedFileUrl(fileUrl);
        //     setUploadMessage(responseData.message);
        //   } else {
        //     // Handle non-JSON response (e.g., video, image, or other types)
        //     console.log('Received non-JSON response');
        //   }
        const responseData = await response.json();
        console.log("responseData:");
        console.log(responseData);
        const fileData = responseData.video;
        const fileUrl = URL.createObjectURL(convertBase64ToBlob(fileData));
        setUploadedFileUrl(fileUrl);
        setUploadMessage(responseData.message);
      } else {
        setUploadMessage('Failed to upload and process file(s).');
      }
    } catch (error) {
      console.error(error);
    //   console.log(responseData);
      setUploadMessage('An error occurred during file(s) upload and processing.');
    }

    setSelectedFiles(null);
  };

  const convertBase64ToBlob = (base64Data) => {
    const byteCharacters = atob(base64Data);
    const byteArrays = [];

    for (let offset = 0; offset < byteCharacters.length; offset += 512) {
      const slice = byteCharacters.slice(offset, offset + 512);
      const byteNumbers = new Array(slice.length);
      for (let i = 0; i < slice.length; i++) {
        byteNumbers[i] = slice.charCodeAt(i);
      }
      const byteArray = new Uint8Array(byteNumbers);
      byteArrays.push(byteArray);
    }

    return new Blob(byteArrays, { type: 'video/mp4' });
  };

  return (
    <div>
      <h2>Upload Video or Folder of Images</h2>
      <input type="file" accept="video/*,image/*" multiple onChange={handleFileChange} />
      <button onClick={handleUpload}>Upload</button>
      {uploadMessage && <p>{uploadMessage}</p>}
      {uploadedFileUrl && <video className="video-player" src={uploadedFileUrl} controls />}
      {uploadedFileUrl && (
        <a className="download-button" href={uploadedFileUrl} download>
          Download Processed Video
        </a>
      )}
    </div>
  );
};

export default DataLoader;
