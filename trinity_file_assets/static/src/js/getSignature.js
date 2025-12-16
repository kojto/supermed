/**
 * Base signature functionality for NHIS message signing
 * This file contains the common logic used by all getSignatureXXXX.js files
 */

/**
 * Core signature function - creates and sends signature request
 * @param {string} messageType - The message type (e.g., 'P001', 'R001', 'X005', 'C013')
 * @param {string} fieldSuffix - The field suffix (e.g., '_0' or '')
 * @param {function} showLoadingFn - Function to show loading overlay
 * @param {function} hideLoadingFn - Function to hide loading overlay
 */
function createSignature(messageType, fieldSuffix = '_0', showLoadingFn = ShowLoading, hideLoadingFn = HideLoading) {
    showLoadingFn();
    const signatureEndpoint = "https://localhost:53952/sign";
    const xhr = new XMLHttpRequest();

    xhr.open("POST", signatureEndpoint, true);
    xhr.setRequestHeader("Accept", "application/json, text/javascript, */*; q=0.01");
    xhr.setRequestHeader("Content-Type", "application/json");

    // Get field values
    const signedInfoField = document.getElementById(`SignedInfo_${messageType}${fieldSuffix}`);
    const signedInfoSignatureField = document.getElementById(`SignedInfo_${messageType}_signature${fieldSuffix}`);
    const supermedCertField = document.getElementById(`supermed_certificate${fieldSuffix}`);
    const userTokenCertElement = document.querySelector('div[name="user_token_certificate"] > span');

    console.log(`Creating signature for ${messageType}${fieldSuffix}`);
    console.log('signedInfoField:', signedInfoField);
    console.log('signedInfoSignatureField:', signedInfoSignatureField);
    console.log('supermedCertField:', supermedCertField);
    console.log('userTokenCertElement:', userTokenCertElement);

    if (!signedInfoField) {
        console.error(`SignedInfo_${messageType}${fieldSuffix} field not found`);
        hideLoadingFn();
        return;
    }
    if (!signedInfoSignatureField) {
        console.error(`SignedInfo_${messageType}_signature${fieldSuffix} field not found`);
        hideLoadingFn();
        return;
    }
    if (!supermedCertField) {
        console.error(`supermed_certificate${fieldSuffix} field not found`);
        hideLoadingFn();
        return;
    }
    if (!userTokenCertElement) {
        console.error('user_token_certificate element not found');
        hideLoadingFn();
        return;
    }

    const requestData = {
        "version": "1.0",
        "signatureType": "signature",
        "contentType": "data",
        "hashAlgorithm": 'SHA256',
        "contents": [signedInfoField.value],
        "signedContents": [signedInfoSignatureField.value],
        "signedContentsCert": [supermedCertField.value],
        "signerCertificateB64": userTokenCertElement.textContent.trim()
    };

    console.log("Request data being sent:", {
        version: requestData.version,
        signatureType: requestData.signatureType,
        contentType: requestData.contentType,
        hashAlgorithm: requestData.hashAlgorithm,
        contentsLength: requestData.contents[0] ? requestData.contents[0].length : 0,
        signedContentsLength: requestData.signedContents[0] ? requestData.signedContents[0].length : 0,
        signedContentsCertLength: requestData.signedContentsCert[0] ? requestData.signedContentsCert[0].length : 0,
        signerCertificateB64Length: requestData.signerCertificateB64 ? requestData.signerCertificateB64.length : 0
    });

    xhr.onreadystatechange = function() {
        const signedXmlField = document.getElementById(`${messageType}${fieldSuffix}`);

        if (xhr.readyState === 4) {
            if (xhr.status === 200) {
                const responseObj = JSON.parse(xhr.responseText);
                const signatureValue = responseObj.signatures && responseObj.signatures[0];

                if (signatureValue && signedXmlField && signedXmlField.tagName === 'TEXTAREA') {
                    signedXmlField.value = signedXmlField.value.replace(
                        '<ds:SignatureValue>|---signatureValue---|</ds:SignatureValue>',
                        '<ds:SignatureValue>' + signatureValue + '</ds:SignatureValue>'
                    );

                    const event = new Event('input', {
                        'bubbles': true,
                        'cancelable': true
                    });
                    signedXmlField.dispatchEvent(event);

                    setFieldToSigned(messageType, fieldSuffix);

                } else {
                    console.error(`Issue with the received data or could not find textarea with id '${messageType}'.`);
                }

            } else {
                console.error("Failed to create signature:", xhr.status, xhr.statusText);
            }

            setTimeout(function() {
                hideLoadingFn();
            }, 2000);
        }
    };

    xhr.send(JSON.stringify(requestData));
}

/**
 * Sets the signed field to "signed" and triggers save and API request
 * @param {string} messageType - The message type (e.g., 'P001', 'R001', 'X005', 'C013')
 * @param {string} fieldSuffix - The field suffix (e.g., '_0' or '')
 */
function setFieldToSigned(messageType, fieldSuffix = '_0') {
    const signedField = document.getElementById(`${messageType}_signed${fieldSuffix}`);
    if (signedField) {
        signedField.value = "signed";

        const event = new Event('input', {
            'bubbles': true,
            'cancelable': true
        });
        signedField.dispatchEvent(event);

        const saveButton = document.querySelector('.o_form_button_save');
        if (saveButton) {
            saveButton.click();
        } else {
            console.error("Couldn't find the Save button.");
        }

        triggerApiRequest(messageType);

    } else {
        console.error(`Couldn't find the ${messageType}_signed field.`);
    }
}

/**
 * Triggers the API request button click
 * @param {string} messageType - The message type (e.g., 'P001', 'R001', 'X005', 'C013')
 */
function triggerApiRequest(messageType) {
    console.log(`Entering ${messageType}_api_request function.`);

    const button = document.querySelector(`[name="${messageType}_api_request"]`);
    console.log(`Searching for button with name '${messageType}_api_request'...`);

    if (button) {
        console.log("Button found:", button);

        setTimeout(function() {
            button.click();
            console.log(`Button ${messageType}_api_request clicked after 500 ms delay.`);
        }, 500);
    } else {
        console.warn("Button not found");
    }
}

/**
 * Wait for XML generation to complete by monitoring createdOn timestamp changes
 * @param {string} messageType - The message type (e.g., 'H001', 'C013', 'P001')
 * @param {string} fieldSuffix - The field suffix (e.g., '_0' or '')
 * @param {function} callback - Function to call when XML is ready (e.g., createSignature)
 * @param {number} maxWaitTime - Maximum wait time in milliseconds (default: 10000)
 * @param {number} checkInterval - Check interval in milliseconds (default: 100)
 */
function waitForXmlGeneration(messageType, fieldSuffix = '_0', callback, maxWaitTime = 10000, checkInterval = 100) {
    ShowLoading();

    const xmlField = document.getElementById(`${messageType}${fieldSuffix}`);
    if (!xmlField) {
        console.error(`${messageType} field not found`);
        HideLoading();
        return;
    }

    // Function to extract createdOn timestamp from XML
    function extractCreatedOn(xmlString) {
        if (!xmlString || xmlString.trim() === '') {
            return null;
        }
        try {
            // Use regex to extract createdOn value, handling namespace
            const match = xmlString.match(/<nhis:createdOn\s+value="([^"]+)"/);
            return match ? match[1] : null;
        } catch (e) {
            console.error("Error parsing XML:", e);
            return null;
        }
    }

    // Get initial createdOn value (if exists)
    let previousCreatedOn = extractCreatedOn(xmlField.value);
    const initialTime = Date.now();

    console.log(`Waiting for compute_${messageType} to generate new ${messageType} with updated createdOn...`);

    function checkForNewXml() {
        const currentValue = xmlField.value.trim();
        const currentCreatedOn = extractCreatedOn(currentValue);
        const elapsedTime = Date.now() - initialTime;

        // Check if we have a new timestamp
        if (currentCreatedOn && currentCreatedOn !== previousCreatedOn && currentValue !== '') {
            console.log(`New ${messageType} detected with createdOn:`, currentCreatedOn);
            clearInterval(intervalId);
            HideLoading();

            // Call the callback function
            if (callback && typeof callback === 'function') {
                callback();
            }
            return;
        }

        // Timeout check
        if (elapsedTime > maxWaitTime) {
            console.warn(`Timeout waiting for compute_${messageType} to complete`);
            clearInterval(intervalId);
            HideLoading();

            // Still try to proceed if there's content
            if (currentValue && currentValue !== '') {
                console.log(`Proceeding with existing ${messageType} content despite timeout`);
                if (callback && typeof callback === 'function') {
                    callback();
                }
            } else {
                console.error(`No ${messageType} content available`);
            }
            return;
        }
    }

    const intervalId = setInterval(checkForNewXml, checkInterval);
}

/**
 * Default loading overlay functions
 * Individual files can override these with their own implementations
 */
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
    `;

    const contentDiv = document.createElement('div');
    contentDiv.style.cssText = 'text-align: center;';

    const spinner = document.createElement('div');
    spinner.className = 'spinner-border';
    spinner.setAttribute('role', 'status');
    spinner.style.cssText = 'width: 3rem; height: 3rem; color:rgb(255, 255, 255); margin: 0 auto 1rem;';

    const message = document.createElement('p');
    message.style.color = 'rgb(255, 255, 255)';
    message.textContent = 'Изпращане към НЗИС...';

    contentDiv.appendChild(spinner);
    contentDiv.appendChild(message);
    overlay.appendChild(contentDiv);
    document.body.appendChild(overlay);
}

function HideLoading() {
    const loadingOverlays = document.querySelectorAll('.custom-loading-overlay');
    loadingOverlays.forEach(overlay => overlay.remove());
}

window.addEventListener('dblclick', HideLoading);

