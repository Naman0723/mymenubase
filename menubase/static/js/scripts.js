/ get loaction
// Function to fetch location data from the Flask API
async function fetchLocationData() {
    try {
        const response = await fetch('http://127.0.0.1:5000/location');
        const data = await response.json();

        // Update the HTML with the location data
        document.getElementById('ip_address').textContent = data.ip_address || "Not Available";
        document.getElementById('city').textContent = data.city || "Not Available";
        document.getElementById('region').textContent = data.region || "Not Available";
        document.getElementById('country').textContent = data.country || "Not Available";
        document.getElementById('latitude').textContent = data.latitude || "Not Available";
        document.getElementById('longitude').textContent = data.longitude || "Not Available";
    } catch (error) {
        console.error('Error fetching location data:', error);
    }
}

// Call the function when the page loads
window.onload = fetchLocationData;


// to send an email
document.getElementById('emailForm').addEventListener('submit', async function(event) {
    event.preventDefault();

    const from_email = document.getElementById('from_email').value;
    const app_password = document.getElementById('app_password').value;
    const to_email = document.getElementById('to_email').value;
    const subject = document.getElementById('subject').value;
    const body = document.getElementById('body').value;

    const emailData = {
        from_email: from_email,
        app_password: app_password,
        to_email: to_email,
        subject: subject,
        body: body
    };

    try {
        const response = await fetch('http://127.0.0.1:5000/send_email', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(emailData)
        });

        const result = await response.json();

        document.getElementById('status').textContent = result.message;
        document.getElementById('status').style.color = result.status === 'success' ? 'green' : 'red';
    } catch (error) {
        document.getElementById('status').textContent = 'Failed to send email. Please try again.';
        document.getElementById('status').style.color = 'red';
        console.error('Error:', error);
    }
});



// to send bulk of emails
document.getElementById('emailForm').addEventListener('submit', async function(event) {
    event.preventDefault();

    const sender_email = document.getElementById('sender_email').value;
    const sender_password = document.getElementById('sender_password').value;
    const subject = document.getElementById('subject').value;
    const message = document.getElementById('message').value;
    const recipients = document.getElementById('recipients').value.split(',');

    const emailData = {
        sender_email: sender_email,
        sender_password: sender_password,
        subject: subject,
        message: message,
        recipients: recipients.map(email => email.trim())
    };

    try {
        const response = await fetch('http://127.0.0.1:5000/send_bulk_email', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(emailData)
        });

        const result = await response.json();

        document.getElementById('status').textContent = result.message;
        document.getElementById('status').style.color = result.status === 'success' ? 'green' : 'red';
    } catch (error) {
        document.getElementById('status').textContent = 'Failed to send emails. Please try again.';
        document.getElementById('status').style.color = 'red';
        console.error('Error:', error);
    }
});


// to set volume
document.addEventListener('DOMContentLoaded', function() {
    // Fetch the current volume when the page loads
    fetchCurrentVolume();

    // Set the volume when the button is clicked
    document.getElementById('set-volume-btn').addEventListener('click', function() {
        const volumeLevel = document.getElementById('volume-level').value;
        setVolume(volumeLevel);
    });
});

function fetchCurrentVolume() {
    const xhr = new XMLHttpRequest();
    xhr.open('GET', 'http://127.0.0.1:5000/get_volume', true);
    xhr.onload = function() {
        if (xhr.status === 200) {
            const response = JSON.parse(xhr.responseText);
            document.getElementById('current-volume').textContent = response.current_volume.toFixed(2);
        } else {
            document.getElementById('current-volume').textContent = 'Error';
        }
    };
    xhr.send();
}

function setVolume(level) {
    const xhr = new XMLHttpRequest();
    xhr.open('POST', 'http://127.0.0.1:5000/set_volume', true);
    xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
    xhr.onload = function() {
        const response = JSON.parse(xhr.responseText);
        document.getElementById('status').textContent = response.message;
        document.getElementById('status').style.color = response.status === 'success' ? 'green' : 'red';
        if (response.status === 'success') {
            document.getElementById('current-volume').textContent = level;
        }
    };
    xhr.send(JSON.stringify({ level: parseFloat(level) }));
}



// text to speech
document.getElementById('submitBtn').addEventListener('click', function() {
    const text = document.getElementById('text').value;
    const lang = document.getElementById('lang').value;
    const filename = document.getElementById('filename').value;

    const data = {
        text: text,
        lang: lang,
        filename: filename
    };

    fetch('/text_to_speech', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
        .then(response => response.blob())
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            a.click();
            window.URL.revokeObjectURL(url);
        })
        .catch(error => {
            document.getElementById('result').innerText = 'An error occurred: ' + error.message;
        });
});


// top google search
document.getElementById('searchForm').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent the form from submitting the traditional way

    var query = document.getElementById('query').value;
    var resultsContainer = document.getElementById('results');

    // Clear previous results
    resultsContainer.innerHTML = '';

    // Perform AJAX request
    var xhr = new XMLHttpRequest();
    xhr.open('GET', `http://127.0.0.1:5000/search?query=${encodeURIComponent(query)}&num_results=5`, true);
    xhr.onload = function() {
        if (xhr.status >= 200 && xhr.status < 300) {
            var response = JSON.parse(xhr.responseText);

            if (response.status === 'success') {
                var results = response.results;
                results.forEach(function(result) {
                    var resultItem = document.createElement('div');
                    resultItem.className = 'result-item';
                    resultItem.innerHTML = `
                      <h3>${result.title}</h3>
                      <a href="${result.link}" target="_blank">${result.link}</a>
                      <p>${result.snippet}</p>
                  `;
                    resultsContainer.appendChild(resultItem);
                });
            } else {
                resultsContainer.innerHTML = `<p>${response.message}</p>`;
            }
        } else {
            resultsContainer.innerHTML = `<p>Error: ${xhr.statusText}</p>`;
        }
    };
    xhr.onerror = function() {
        resultsContainer.innerHTML = '<p>Request failed. Please try again later.</p>';
    };
    xhr.send();
});



// send whatsaap
document.getElementById('send-button').addEventListener('click', function() {
    const phoneNumber = document.getElementById('phone_number').value;
    const message = document.getElementById('message').value;
    const hour = parseInt(document.getElementById('hour').value);
    const minute = parseInt(document.getElementById('minute').value);

    if (!phoneNumber || !message || isNaN(hour) || isNaN(minute)) {
        alert('Please fill in all fields correctly.');
        return;
    }

    const data = {
        phone_number: phoneNumber,
        message: message,
        hour: hour,
        minute: minute
    };

    fetch('http://127.0.0.1:5000/send_whatsapp', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(result => {
            const resultDiv = document.getElementById('result');
            if (result.status === 'success') {
                resultDiv.innerHTML = `<p>${result.message}</p>`;
            } else {
                resultDiv.innerHTML = `<p style="color: red;">Error: ${result.message}</p>`;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            document.getElementById('result').innerHTML = `<p style="color: red;">An error occurred while sending the message.</p>`;
        });
});





// ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
//  -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
// =====================================================================MACHINE LEARNING========================================================================================================================================================================================================================================================================================================
//  ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
//  ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



// dataprocessing
document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('uploadForm');
    const resultsOutput = document.getElementById('resultsOutput');
    const downloadButton = document.getElementById('downloadButton');

    form.addEventListener('submit', (event) => {
        event.preventDefault(); // Prevent form from submitting the traditional way

        const formData = new FormData(form);

        fetch('http://127.0.0.1:5000/process', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    resultsOutput.textContent = `Error: ${data.error}`;
                } else {
                    resultsOutput.textContent = JSON.stringify(data, null, 2);
                }
            })
            .catch(error => {
                resultsOutput.textContent = `Error: ${error.message}`;
            });
    });

    downloadButton.addEventListener('click', () => {
        fetch('http://127.0.0.1:5000/download-plot')
            .then(response => {
                if (response.ok) {
                    return response.blob();
                }
                throw new Error('Network response was not ok.');
            })
            .then(blob => {
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'plot.png';
                document.body.appendChild(a);
                a.click();
                a.remove();
            })
            .catch(error => {
                alert(`Error: ${error.message}`);
            });
    });
});




// to apply filters 
document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('uploadForm');
    const imagesDiv = document.getElementById('images');

    form.addEventListener('submit', (event) => {
        event.preventDefault(); // Prevent the form from submitting the traditional way

        const formData = new FormData(form);

        fetch('/upload', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert(`Error: ${data.error}`);
                } else {
                    imagesDiv.innerHTML = ''; // Clear previous images
                    for (const [filter, url] of Object.entries(data)) {
                        const img = document.createElement('img');
                        img.src = url;
                        img.alt = filter;
                        img.title = filter;
                        imagesDiv.appendChild(img);
                    }
                }
            })
            .catch(error => {
                alert(`Error: ${error.message}`);
            });
    });
});





// to crop photo
document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('generateForm');
    const imageContainer = document.getElementById('imageContainer');

    form.addEventListener('submit', (event) => {
        event.preventDefault();

        const formData = new FormData(form);
        const params = new URLSearchParams();
        formData.forEach((value, key) => params.append(key, value));

        fetch('/generate_images?' + params.toString())
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert(`Error: ${data.error}`);
                } else {
                    imageContainer.innerHTML = '';
                    Object.keys(data).forEach(imageType => {
                        const img = document.createElement('img');
                        img.src = data[imageType];
                        img.alt = imageType;
                        img.title = imageType;
                        img.addEventListener('click', () => {
                            window.location.href = `/download/${imageType}`;
                        });
                        imageContainer.appendChild(img);
                    });
                }
            })
            .catch(error => {
                alert(`Error: ${error.message}`);
            });
    });
});




// selfie
document.getElementById('captureButton').addEventListener('click', () => {
    fetch('/capture_face')
        .then(response => {
            if (response.ok) {
                return response.blob();
            } else {
                throw new Error('Error capturing face');
            }
        })
        .then(blob => {
            const url = URL.createObjectURL(blob);
            const resultImage = document.getElementById('resultImage');
            resultImage.src = url;
            resultImage.style.display = 'block';
        })
        .catch(error => {
            alert(`Error: ${error.message}`);
        });
});