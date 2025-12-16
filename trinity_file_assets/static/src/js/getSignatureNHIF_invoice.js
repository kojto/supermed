function getSignaturenhif_invoice() {
    ShowLoading();
    
    // Define the maximum number of retries
    const maxRetries = 10;
    let retryCount = 0;

    // Function to check if all required fields are available
    function checkFields() {
        const contentField = document.getElementById('SignedInfo_nhif_invoice_0');
        const signatureField = document.getElementById('SignedInfo_nhif_invoice_signature_0');
        const certificateField = document.getElementById('supermed_certificate_0');
        
        // Check if all fields are present
        if (contentField && signatureField && certificateField) {
            proceedWithRequest(contentField, signatureField, certificateField);
        } else {
            // Retry if not all fields are found
            if (retryCount < maxRetries) {
                retryCount++;
                console.log(`Fields not found, retrying... Attempt ${retryCount}/${maxRetries}`);
                setTimeout(checkFields, 1000); // Retry after 1 second
            } else {
                console.error("Fields not found after 10 attempts.");
                HideLoading();
            }
        }
    }

    // Function to proceed with the request once all fields are available
    function proceedWithRequest(contentField, signatureField, certificateField) {
        const signatureEndpoint = "https://localhost:53952/sign";
        const xhr = new XMLHttpRequest();

        xhr.open("POST", signatureEndpoint, true);
        xhr.setRequestHeader("Accept", "application/json, text/javascript, */*; q=0.01");
        xhr.setRequestHeader("Content-Type", "application/json");

        const requestData = {
            "version": "1.0",
            "signatureType": "signature",
            "contentType": "data",
            "hashAlgorithm": 'SHA256',
            "contents": [contentField.value],
            "signedContents": [signatureField.value],
            "signedContentsCert": [certificateField.value],
            "signerCertificateB64": document.querySelector('div[name="user_token_certificate"] > span').textContent.trim()
        };

        xhr.onreadystatechange = function() {
            const signedXmlField = document.getElementById('nhif_invoice_0');

            if (xhr.readyState === 4) {
                if (xhr.status === 200) {
                    const responseObj = JSON.parse(xhr.responseText);
                    const signatureValue = responseObj.signatures && responseObj.signatures[0];

                    if (signatureValue && signedXmlField && signedXmlField.tagName === 'TEXTAREA') {
                        signedXmlField.value = signedXmlField.value.replace('<ds:SignatureValue>|---signatureValue---|</ds:SignatureValue>', '<ds:SignatureValue>' + signatureValue + '</ds:SignatureValue>');

                        // Dispatch the input event to notify of the change
                        const event = new Event('input', {
                            'bubbles': true,
                            'cancelable': true
                        });
                        signedXmlField.dispatchEvent(event);

                        // Call the function to set nhif_invoice_signed field to "signed"
                        setnhif_invoiceToSigned();

                    } else {
                        console.error("Issue with the received data or could not find textarea with id 'nhif_invoice'.");
                    }

                } else {
                    console.error("Failed to create signature:", xhr.status, xhr.statusText);
                }

                // Hide the loading spinner after processing the request
                HideLoading();
            }
        };

        xhr.send(JSON.stringify(requestData));
    }
	
    checkFields();
}

function setnhif_invoiceToSigned() {
    const nhif_invoiceSignedField = document.getElementById('nhif_invoice_signed_0');
    if (nhif_invoiceSignedField) {
        nhif_invoiceSignedField.value = "signed";
        
        // Dispatch the input event to notify of the change
        const event = new Event('input', {
            'bubbles': true,
            'cancelable': true
        });
        nhif_invoiceSignedField.dispatchEvent(event);

        // Assuming the Save button in Odoo has a class `o_form_button_save`
        const saveButton = document.querySelector('.o_form_button_save');
        if (saveButton) {
            saveButton.click(); // Trigger the Save action
        } else {
            console.error("Couldn't find the Save button.");
        }
        
		clickButton();
        
    } else {
        console.error("Couldn't find the nhif_invoice_signed field.");
    }
}

function clickButton() {
    // Find the button by its name
    var button = document.querySelector('[name="save_nhif_invoice_as_binary"]');

    // Check if the button exists
    if (button) {
        console.log("Button found:", button);

        // Delay the click by 500 ms
        setTimeout(function () {
            button.click();
            console.log("Button clicked after 500 ms delay.");
        }, 500);
    } else {
        console.warn("Button not found");
    }
}

function ShowLoading() {
    // Create a loading overlay
    const overlay = document.createElement('div');
    overlay.className = 'custom-loading-overlay'; // Add class for easier selection in HideLoading
    overlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0, 0, 0, 0.8);
        z-index: 1040;
        display: flex;
        justify-content: center;
        align-items: center;
        flex-direction: column;
        opacity: 1;
        transition: opacity 5s ease;
    `;

    // Create the spinner using the provided Bootstrap code
    const spinner = document.createElement('div');
    spinner.className = "spinner-border"; // Bootstrap spinner class
    spinner.setAttribute('role', 'status');
    spinner.style.width = '3rem';  // Increase size of spinner
    spinner.style.height = '3rem'; // Increase size of spinner
    spinner.style.color = 'white'; // Light blue color (Bootstrap's primary light blue)

    // Create the loading message
    const message = document.createElement('p');
    message.style.color = 'white'; // Set text color to light blue
    message.className = "mt-3"; // Margin-top for spacing
    message.innerText = "Създаване и подписване на отчет ...";

    // Append spinner and message to the overlay
    overlay.appendChild(spinner);
    overlay.appendChild(message);
    document.body.appendChild(overlay);
}

// Function to hide the loading overlay with a smooth transition
function HideLoading() {
    const loadingOverlay = document.querySelector('.custom-loading-overlay'); // Select by class
    if (loadingOverlay) {
        loadingOverlay.style.opacity = '0'; // Set opacity to 0 to start fade-out
        // Wait for the transition to complete before removing the overlay
        setTimeout(() => {
            loadingOverlay.remove(); // Use .remove() for cleaner removal
        }, 1000); // Matches the 1-second fade-out transition
    }
}

window.addEventListener('click', HideLoading);