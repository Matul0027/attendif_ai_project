const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const context = canvas.getContext('2d');
const preview = document.getElementById('preview');
let capturedImage = null;

// Start webcam
navigator.mediaDevices.getUserMedia({ video: true })
  .then(stream => { video.srcObject = stream; })
  .catch(err => { alert("Please allow camera access!"); });

// Capture face
document.getElementById('captureBtn').addEventListener('click', () => {
  context.drawImage(video, 0, 0, canvas.width, canvas.height);
  capturedImage = canvas.toDataURL('image/png');
  if (capturedImage) {
    preview.src = capturedImage;
    preview.style.display = 'block';
    document.getElementById('status').innerText = "✅ Face captured!";
  }
});

// Submit form
document.getElementById('studentForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  if (!capturedImage) { alert("Capture face first!"); return; }
  const data = {
    name: document.getElementById('name').value,
    roll: document.getElementById('roll').value,
    class_name: document.getElementById('class_name').value,
    section: document.getElementById('section').value,
    image: capturedImage
  };
  try {
    const res = await fetch('/save_student', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    const result = await res.json();
    document.getElementById('status').innerText = result.message;
  } catch (err) {
    document.getElementById('status').innerText = "❌ Server error.";
  }
});
