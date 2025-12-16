function saveRecord() {
    var saveButton = document.querySelector(".o_form_button_save");
    if (saveButton) {
        saveButton.click();
    }
}

function formatDateToCustomFormat(date) {
    if (!(date instanceof Date) || isNaN(date.getTime())) {
        return 'Invalid Date';
    }
    const day = String(date.getDate()).padStart(2, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const year = date.getFullYear();
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    const seconds = String(date.getSeconds()).padStart(2, '0');
    return `${day}.${month}.${year} ${hours}:${minutes}:${seconds}`;
}

function checkTokenExpiration() {
    const field = document.querySelector("div[name='user_token_expiresOnDatetime'] span");

    if (!field || !field.innerText) {
        console.error("Expiration date field not found or empty.");
        return;
    }

    const dateTimeString = field.innerText.trim();
    const [datePart, timePart] = dateTimeString.split(' ');
    if (!datePart || !timePart) {
        console.error("Invalid date or time format in expiration field.");
        return;
    }

    let year, month, day;
    if (datePart.includes('-')) {
        [year, month, day] = datePart.split('-').map(Number);
    } else if (datePart.includes('.')) {
        [day, month, year] = datePart.split('.').map(Number);
    } else {
        console.error("Unknown date format.");
        return;
    }

    // Normalize time part: allow hh:mm, hh:mm:ss, hh,mm, hh,mm,ss
    const normalizedTimePart = timePart.replace(/,/g, ':');
    const timeComponents = normalizedTimePart.split(':').map(Number);
    let hours, minutes, seconds;

    if (timeComponents.length === 2) {
        [hours, minutes] = timeComponents;
        seconds = 0;
    } else if (timeComponents.length === 3) {
        [hours, minutes, seconds] = timeComponents;
    } else {
        console.error("Invalid time format. Expected hh:mm, hh:mm:ss, hh,mm, or hh,mm,ss");
        return;
    }

    if (
        isNaN(day) || isNaN(month) || isNaN(year) ||
        isNaN(hours) || isNaN(minutes) || isNaN(seconds)
    ) {
        console.error("Invalid date or time components.");
        return;
    }

    const fieldDateTime = new Date(year, month - 1, day, hours, minutes, seconds);
    if (isNaN(fieldDateTime.getTime())) {
        console.error("Invalid Date object created from expiration date.");
        return;
    }

    const currentDateTime = new Date();
    const isExpired = currentDateTime >= fieldDateTime;

    const checkbox = document.querySelector("#user_token_is_expired_0");
    if (!checkbox) {
        console.error("Checkbox not found.");
        return;
    }

    if (checkbox.checked !== isExpired) {
        checkbox.checked = isExpired;
        checkbox.dispatchEvent(new Event('change', { bubbles: true }));
        console.log(`Checkbox updated: isExpired = ${isExpired}`);
        saveRecord();
    }
}

setInterval(() => {
    checkTokenExpiration();
}, 500);

function getToken() {
    ShowLoading();

    console.log("=== Starting getToken() ===");

    const tokenRequestElement = document.getElementById('SignedInfo_tokenRequest_0');
    const tokenSignatureElement = document.getElementById('SignedInfo_tokenRequest_signature_0');
    const certificateElement = document.getElementById('supermed_certificate_0');
    const userTokenCertElement = document.querySelector('div[name="user_token_certificate"] > span');
    const signedXmlField = document.getElementById('tokenRequest_0');

    console.log("tokenRequestElement:", tokenRequestElement?.value);
    console.log("tokenSignatureElement:", tokenSignatureElement?.value);
    console.log("certificateElement:", certificateElement?.value);
    console.log("userTokenCertElement:", userTokenCertElement?.textContent?.trim());
    console.log("signedXmlField:", signedXmlField?.value);

    if (!tokenRequestElement || !tokenSignatureElement || !certificateElement || !userTokenCertElement || !signedXmlField) {
        console.error("One or more required elements are missing from the DOM.");
        HideLoading();
        return;
    }

    let previousValue = signedXmlField.value.trim();

    function handleResponse(responseObj) {
        console.log("Server response object:", responseObj);
        const signatureValue = responseObj.signatures && responseObj.signatures[0];
        if (signatureValue) {
            console.log("Signature value received:", signatureValue);
            signedXmlField.value = signedXmlField.value.replace(
                '<ds:SignatureValue>|---signatureValue---|</ds:SignatureValue>',
                `<ds:SignatureValue>${signatureValue}</ds:SignatureValue>`
            );
            signedXmlField.dispatchEvent(new Event('input', { bubbles: true, cancelable: true }));
            settokenRequestToSigned();
        } else {
            console.error("Invalid response data.");
        }
    }

    function checkForChange() {
        const currentValue = signedXmlField.value.trim();
        if (currentValue !== previousValue && currentValue !== '') {
            clearInterval(intervalId);
            previousValue = currentValue;

            const requestData = {
                "version": "1.0",
                "signatureType": "signature",
                "contentType": "data",
                "hashAlgorithm": 'SHA256',
                "contents": [tokenRequestElement.value],
                "signedContents": [tokenSignatureElement.value],
                "signedContentsCert": [certificateElement.value],
                "signerCertificateB64": userTokenCertElement.textContent.trim()
            };

            console.log("Request payload being sent to /sign:", requestData);

            const xhr = new XMLHttpRequest();
            xhr.open("POST", "https://localhost:53952/sign", true);
            xhr.setRequestHeader("Accept", "application/json, text/javascript, */*; q=0.01");
            xhr.setRequestHeader("Content-Type", "application/json");

            xhr.onreadystatechange = function() {
                if (xhr.readyState === 4) {
                    HideLoading();
                    console.log("XHR status:", xhr.status, xhr.statusText);
                    console.log("XHR raw response:", xhr.responseText);

                    if (xhr.status === 200) {
                        try {
                            const responseObj = JSON.parse(xhr.responseText);
                            handleResponse(responseObj);
                        } catch (e) {
                            console.error("Failed to parse response JSON:", e);
                        }
                    } else {
                        console.error("Failed to create signature:", xhr.status, xhr.statusText);
                        showCustomWarning("Проверете дали сте поставили електронния подпис!");
                    }
                }
            };

            try {
                xhr.send(JSON.stringify(requestData));
            } catch (err) {
                console.error("XHR send() error:", err);
            }
        }
    }

    const intervalId = setInterval(checkForChange, 500);
}

function showCustomWarning(message) {
    var overlayDiv = document.createElement("div");
    overlayDiv.style.cssText = 'position: fixed; top: 0; left: 0; width: 100%; height: 100%; background-color: rgba(0, 0, 0, 0.8); z-index: 1040;';

    var warningDiv = document.createElement("div");
    warningDiv.style.cssText = 'position: fixed; top: 40%; left: 50%; transform: translate(-50%, -50%); background-color: rgb(255, 255, 255); color: #0b5394; font-size: 14px; font-family: Arial; padding: 30px 40px; z-index: 1050; border-radius: 10px; border: 2px solid #0b5394;';

    var messageDiv = document.createElement("div");
    messageDiv.innerText = message;
    messageDiv.style.cssText = 'margin-bottom: 25px;';

    var closeButton = document.createElement("button");
    closeButton.innerText = "Затвори";
    closeButton.style.cssText = 'background-color: #0b5394; color: white; border: none; padding: 5px 10px; cursor: pointer; border-radius: 4px;';
    closeButton.onclick = function() {
        document.body.removeChild(warningDiv);
        document.body.removeChild(overlayDiv);
    };

    warningDiv.appendChild(messageDiv);
    warningDiv.appendChild(closeButton);

    document.body.appendChild(overlayDiv);
    document.body.appendChild(warningDiv);
}

function settokenRequestToSigned() {
    const tokenRequestSignedField = document.getElementById('tokenRequest_signed_0');
    if (tokenRequestSignedField) {
        tokenRequestSignedField.value = "signed";

        const event = new Event('input', {
            'bubbles': true,
            'cancelable': true
        });
        tokenRequestSignedField.dispatchEvent(event);

        const saveButton = document.querySelector('.o_form_button_save');
        if (saveButton) {
            saveButton.click();
        } else {
            console.error("Couldn't find the Save button.");
        }

        post_token_api_request();

    } else {
        console.error("Couldn't find the tokenRequest_signed field.");
    }
}

function post_token_api_request() {

    var button = document.querySelector('[name="post_token_api_request"]');

    if (button) {
        setTimeout(() => {
            button.click();
            HideLoading();
        }, 1000);
    } else {
        console.warn("Button not found");
        HideLoading();
    }
}

function ShowLoading() {
    const overlay = document.createElement('div');
    overlay.className = 'custom-loading-overlay';
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

    const spinner = document.createElement('div');
    spinner.className = "spinner-border";
    spinner.setAttribute('role', 'status');
    spinner.style.width = '3rem';
    spinner.style.height = '3rem';
    spinner.style.color = 'white';

    const message = document.createElement('p');
    message.style.color = 'white';
    message.className = "mt-3";
    message.innerText = "Изграждане на връзка с НЗИС...";

    overlay.appendChild(spinner);
    overlay.appendChild(message);
    document.body.appendChild(overlay);
}

function HideLoading() {
    const loadingOverlay = document.querySelector('.custom-loading-overlay');
    if (loadingOverlay) {
        loadingOverlay.style.opacity = '0';
        setTimeout(() => {
            loadingOverlay.remove();
        }, 1000);
    }
}

window.addEventListener('click', HideLoading);
