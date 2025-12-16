function getSignaturefr_nhif() {
    ShowLoading();
    const maxRetries = 10;
    let retryCount = 0;

    function checkFields() {
        const contentField = document.getElementById('SignedInfo_fr_nhif_0');
        const signatureField = document.getElementById('SignedInfo_fr_nhif_signature_0');
        const certificateField = document.getElementById('supermed_certificate_0');
        
        if (contentField && signatureField && certificateField) {
            proceedWithRequest(contentField, signatureField, certificateField);
        } else {
            if (retryCount < maxRetries) {
                retryCount++;
                setTimeout(checkFields, 1000);
            } else {
                HideLoading();
            }
        }
    }

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
            const signedXmlField = document.getElementById('fr_nhif_0');

            if (xhr.readyState === 4) {
                if (xhr.status === 200) {
                    const responseObj = JSON.parse(xhr.responseText);
                    const signatureValue = responseObj.signatures && responseObj.signatures[0];

                    if (signatureValue && signedXmlField && signedXmlField.tagName === 'TEXTAREA') {
                        signedXmlField.value = signedXmlField.value.replace('<ds:SignatureValue>|---signatureValue---|</ds:SignatureValue>', '<ds:SignatureValue>' + signatureValue + '</ds:SignatureValue>');

                        const event = new Event('input', {
                            'bubbles': true,
                            'cancelable': true
                        });
                        signedXmlField.dispatchEvent(event);
                        setfr_nhifToSigned();
                    }
                }
                HideLoading();
            }
        };

        xhr.send(JSON.stringify(requestData));
    }
    
    checkFields();
}

function setfr_nhifToSigned() {
    const fr_nhifSignedField = document.getElementById('fr_nhif_signed_0');
    if (fr_nhifSignedField) {
        fr_nhifSignedField.value = "signed";
        
        const event = new Event('input', {
            'bubbles': true,
            'cancelable': true
        });
        fr_nhifSignedField.dispatchEvent(event);

        const saveButton = document.querySelector('.o_form_button_save');
        if (saveButton) {
            saveButton.click();
        }
        
        clickButton();
    }
}

function clickButton() {
    var button = document.querySelector('[name="download_xml"]');
    if (button) {
        setTimeout(function () {
            button.click();
        }, 500);
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
    message.innerText = "Създаване и подписване на отчет ...";

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