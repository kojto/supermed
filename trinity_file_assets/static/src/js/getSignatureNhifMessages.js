/**
 * @requires getSignature.js - Base signature functionality must be loaded first
 *
 * Combined NHIF message signature functionality
 * Includes all message types: C013, C015, C041, C045, H001, P001, P007, P017, R001, R007, R009, R015, X005, X007, X009, X013
 */

// H001 - Request to fetch E-hospitalization
function getSignatureH001() {
    waitForXmlGeneration('H001', '_0', function() {
        createSignature('H001');
    });
}

function setH001ToSigned() {
    setFieldToSigned('H001');
}

function H001_api_request() {
    triggerApiRequest('H001');
}

// C013 - Request to create E-prescription
function getSignatureC013() {
    createSignature('C013');
}

function setC013ToSigned() {
    setFieldToSigned('C013');
}

function C013_api_request() {
    triggerApiRequest('C013');
}

// C015 - Request to reverse fulfilled E-prescription
function getSignatureC015() {
    createSignature('C015');
}

function setC015ToSigned() {
    setFieldToSigned('C015');
}

function C015_api_request() {
    triggerApiRequest('C015');
}

// C041 - NHIF message type
function getSignatureC041() {
    createSignature('C041');
}

function setC041ToSigned() {
    setFieldToSigned('C041');
}

function C041_api_request() {
    triggerApiRequest('C041');
}

// C045 - NHIF message type
function getSignatureC045() {
    createSignature('C045');
}

function setC045ToSigned() {
    setFieldToSigned('C045');
}

function C045_api_request() {
    triggerApiRequest('C045');
}

// P001 - Request to create E-prescription
function getSignatureP001() {
    createSignature('P001');
}

function setP001ToSigned() {
    setFieldToSigned('P001');
}

function P001_api_request() {
    triggerApiRequest('P001');
}

// P007 - Request to cancel E-prescription
function getSignatureP007() {
    createSignature('P007');
}

function setP007ToSigned() {
    setFieldToSigned('P007');
}

function P007_api_request() {
    triggerApiRequest('P007');
}

// P017 - Request to retrieve E-prescription
function getSignatureP017() {
    createSignature('P017');
}

function setP017ToSigned() {
    setFieldToSigned('P017');
}

function P017_api_request() {
    triggerApiRequest('P017');
}

// R001 - NHIF message type
function getSignatureR001() {
    createSignature('R001');
}

function setR001ToSigned() {
    setFieldToSigned('R001');
}

function R001_api_request() {
    triggerApiRequest('R001');
}

// R007 - NHIF message type
function getSignatureR007() {
    createSignature('R007');
}

function setR007ToSigned() {
    setFieldToSigned('R007');
}

function R007_api_request() {
    triggerApiRequest('R007');
}

// R009 - NHIF message type
function getSignatureR009() {
    createSignature('R009');
}

function setR009ToSigned() {
    setFieldToSigned('R009');
}

function R009_api_request() {
    triggerApiRequest('R009');
}

// R015 - NHIF message type
function getSignatureR015() {
    createSignature('R015');
}

function setR015ToSigned() {
    setFieldToSigned('R015');
}

function R015_api_request() {
    triggerApiRequest('R015');
}

// X001 - NHIF message type
function getSignatureX001() {
    createSignature('X001');
}

function setX001ToSigned() {
    setFieldToSigned('X001');
}

function X001_api_request() {
    triggerApiRequest('X001');
}

// X003 - NHIF message type
function getSignatureX003() {
    createSignature('X003');
}

function setX003ToSigned() {
    setFieldToSigned('X003');
}

function X003_api_request() {
    triggerApiRequest('X003');
}

// X005 - NHIF message type
function getSignatureX005() {
    createSignature('X005');
}

function setX005ToSigned() {
    setFieldToSigned('X005');
}

function X005_api_request() {
    triggerApiRequest('X005');
}

// X007 - NHIF message type
function getSignatureX007() {
    createSignature('X007');
}

function setX007ToSigned() {
    setFieldToSigned('X007');
}

function X007_api_request() {
    triggerApiRequest('X007');
}

function getSignatureX009() {
    createSignature('X009');
}

function setX009ToSigned() {
    setFieldToSigned('X009');
}

function X009_api_request() {
    triggerApiRequest('X009');
}

function getSignatureX013() {
    createSignature('X013');
}

function setX013ToSigned() {
    setFieldToSigned('X013');
}

function X013_api_request() {
    triggerApiRequest('X013');
}
