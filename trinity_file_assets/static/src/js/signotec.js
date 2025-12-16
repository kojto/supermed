
        var signoPADAPIWeb = null;

        var searchStates = {
            setPadType: 0,
            search: 1,
            getInfo: 2,
            getVersion: 3,
            getDeviceCapabilities: 4
        };
        var searchState = searchStates.setPadType;

        var openStates = {
            openPad: 0,
            setColor: 1,
            getDisplayWidth: 2,
            getDisplayHeight: 3,
            getResolution: 4,
            getSampleRate: 5
        };
        var openState = openStates.openPad;

        var preparationStates = {
            setDisplayRotation: 0,
            getDisplayRotation: 1,
            setBackgroundTarget: 2,
            setBackgroundImage: 3,
            setCancelButton: 4,
            setRetryButton: 5,
            setConfirmButton: 6,
            setSignRect: 7,
            setFieldName: 8,
            setCustomText: 9,
            setForegroundTarget: 10,
            switchBuffers: 11,
            startSignature: 12
        };
        var preparationState = preparationStates.setDisplayRotation;

        var pdfDialoStartStates = {
            pdfLoad: 0,
            pdfGetPageCount: 1,
            pdfGetWidth: 2,
            pdfGetHeight: 3,
            displaySetTargetOverlay: 4,
            displaySetToolbarImage: 5,
            sensorAddCancelHotSpot: 6,
            sensorAddConfirmHotSpot: 7,
            displaySetTargetBackground: 8,
            displaySetPdfBackgroundImage: 9,
            displaySetPDF: 10,
            displaySetOverlayRect: 11,
            displaySetTargetForeground: 12,
            displaySetImageFromStoreBackground: 13,
            sensorSetScrollArea: 14,
            sensorSetPenScrollingEnabledTrue: 15
        };
        var pdfDialoStartState = pdfDialoStartStates.pdfLoad;

        var pdfDialoEndStates = {
            sensorSetPenScrollingEnabledFalse: 0,
            sensorClearHotSpots: 1,
            displayErase: 3
        };
        var pdfDialoEndState = pdfDialoEndStates.sensorSetPenScrollingEnabledFalse;

        var setTargetStates = {
            setPdfToolbar: 0,
            setPdf: 1,
            setTargetForeground: 2
        };
        var setTargetState = setTargetStates.setPdfToolbar;

        var addHotSpotStates = {
            addCancel: 0,
            addConfirm: 1
        };
        var addHotSpotState = addHotSpotStates.addCancel;

        var displaySetImageStates = {
            sensorAddHotSpot: 0,
            displaySetPdf: 1
        };
        var displaySetImageState = displaySetImageStates.sensorAddHotSpot;

        var encryptionCertDochashStates = {
            getEncryptionCertID: 0,
            setEncryptionCertPw: 1,
            setDochash: 2
        };
        var encryptionCertDochashState = encryptionCertDochashStates.getEncryptionCertID;

        var rsaSignGetSignDataStates = {
            rsaSign: 0,
            getEncryptionCertId: 1,
            rsaGetSignData: 2
        };
        var rsaSignGetSignDataState = rsaSignGetSignDataStates.rsaSign;

        var padStates = {
            closed: 0,
            opened: 1
        };
        var padState = padStates.closed;

        var getEncryptionCertIDStates = {
            encryptionCertDochash: 0,
            rsaSignGetSignData: 1
        };
        var getEncryptionCertIDState = getEncryptionCertIDStates.encryptionCertDochash;

        var dialogTypes = {
            signatur: 0,
            pdf: 1
        };
        var dialogType = dialogTypes.signatur;

        var padModes = {
            Default: 0,
            API: 1
        };
        var padMode = padModes.Default;

        var padTypes = {
            sigmaUSB: 1,
            sigmaSerial: 2,
            zetaUSB: 5,
            zetaSerial: 6,
            omegaUSB: 11,
            omegaSerial: 12,
            gammaUSB: 15,
            gammaSerial: 16,
            deltaUSB: 21,
            deltaSerial: 22,
            deltaIP: 23,
            alphaUSB: 31,
            alphaSerial: 32,
            alphaIP: 33
        }
        var padType = 0;

        var deviceCapabilities = {
            HasColorDisplay: 0x00000001,
            HasBacklight: 0x00000002,
            SupportsVerticalScrolling: 0x00000004,
            SupportsHorizontalScrolling: 0x00000008,
            SupportsPenScrolling: 0x00000010,
            SupportsServiceMenu: 0x00000020,
            SupportsRSA: 0x00000040,
            SupportsContentSigning: 0x00000080,
            SupportsH2ContentSigning: 0x00000100,
            CanGenerateSignKey: 0x00000200,
            CanStoreSignKey: 0x00000400,
            CanStoreEncryptKey: 0x00000800,
            CanSignExternalHash: 0x00001000,
            SupportsRSAPassword: 0x00002000,
            SupportsSecureModePassword: 0x00004000,
            Supports4096BitKeys: 0x00008000,
            HasNFCReader: 0x00010000,
            SupportsKeyPad: 0x00020000,
            SupportsKeyPad32: 0x00040000,
            HasDisplay: 0x00080000,
            SupportsRSASignPassword: 0x00100000
        };

        var docHashes = {
            kSha256: 1
        };

        var RsaScheme = {
            None: "NONE",
            NoOID: "NO_HASH_OID",
            PKCS1_V1_5: "PKCS1_V1_5",
            PSS: "PSS"
        };

        var CertType = {
            kCert_DER: "CERT_DER",
            kCSR_DER: "CSR_DER",
            kCert_PEM: "CERT_PEM",
            kCSR_PEM: "CSR_PEM"
        };

        var HashValue = {
            kCombination: "COMBINATION",
            kHash1: "HASH1",
            kHash2: "HASH2"
        };

        var cancelButton = -1;
        var retryButton = -1;
        var confirmButton = -1;
        var buttonDiff = 0;
        var buttonLeft = 0;
        var buttonTop = 0;
        var buttonSize = 0;
        var backgroundImage;
        var scaleFactorX = 1.0;
        var scaleFactorY = 1.0;

        var supportsRSA = false;
        var canStoreEncryptKey = false;

        var field_name = "Signature 1";
        var custom_text = "Please sign!";
        var encryption = "TRUE";
        var default_dochash;
        var api_dochash;
        var docHash_type = docHashes.kSha256;
        var sha256_dochash = document.getElementById("signPen_X_message_hash_sha256_0")?.value;
        var encryption_cert = "MIICqTCCAZGgAwIBAgIBATANBgkqhkiG9w0BAQUFADAYMRYwFAYDVQQKEw1EZW1vIHNpZ25vdGVjMB4XDTE1MTAwNzA5NDc1MFoXDTI1MTAwNDA5NDc1MFowGDEWMBQGA1UEChMNRGVtbyBzaWdub3RlYzCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBAOFFpsZexYW28Neznn26Bp9NVCJywFFj1QYXg3DDsaSyr6ubuqXKSC4jkenIGBnom/zKPxwPDtNXuy+nyDYFXYNn87TUdh/51CCr3uk9kR9hvRIzBKwkOx0DGLdCoSGAKDOPHwx1rE0m/SOqYOQh6XFjlybw+KzDZcPvhf2Fq/IFNXHpk8m0YHMAReW8q34CYjk9ZtcIlrcYGTikQherOtYM8CaEUPDd6vdJgosGWEnDeNXDCAIWTFc5ECJm9Hh7a47eF3BG5Pjl1QfOSA8lQBV5eTjQc1n1rWCWULt143nIbN5yCFrn0D8W6+eKJV5urETxWUQ208iqgeU1bIgKSEUCAwEAATANBgkqhkiG9w0BAQUFAAOCAQEAt2ax8iwLFoOmlAOZTQcRQtjxseQAhgOTYL/vEP14rPZhF1/gkI9ZzhESdkqR8mHIIl7FnfBg9A2v9ZccC7YgRb4bCXNzv6TIEyz4EYXNkIq8EaaQpvsX4+A5jKIP0PRNZUaLJaDRcQZudd6FMyHxrHtCUTEvORzrgGtRnhBDhAMiSDmQ958t8RhET6HL8C7EnL7f8XBMMFR5sDC60iCu/HeIUkCnx/a2waZ13QvhEIeUBmTRi9gEjZEsGd1iZmgf8OapTjefZMXlbl7CJBymKPJgXFe5mD9/yEMFKNRy5Xfl3cB2gJka4wct6PSIzcQVPaCts6I0V9NfEikXy1bpSA==";
        var encryption_cert_only_when_empty = "TRUE";
        var rsa_scheme = RsaScheme.PSS;
        var certtype = CertType.kCert_DER;

        var padIndex = 0;
        var padConnectionType;
        var sampleRate;

        var wsUri = "wss://local.signotecwebsocket.de:49494";

        var state = document.getElementById("status");
        var sigcanvas = document.getElementById("sigCanvas");

        var os = "Unknown";
		var OS_WINDOWS = "Windows";
		var OS_LINUX = "Linux";

        var pdf_dialog_toolbar_height = 56;
        var pdf_page_index = 0;
        var pdf_page_count = 0;
        var height_of_all_pdf_pages = 0.0;
        var pdf_pages_separator = 30;
        var pdf_page_width = 0.0;
        var pdf_page_height = 0;
        var pdf_scale = 0.0;
        var y_pos = 0;
        var sensor_pen_scrolling_enabled = false;
        var stpad_error_rsanokey = false;

        if (window.WebSocket === undefined) {
            state.innerHTML = "sockets not supported " + evt.target.url;
            state.className = "fail";
        } else {
            if (typeof String.prototype.startsWith != "function") {
                String.prototype.startsWith = function(str) {
                    return this.indexOf(str) == 0;
                };
            }
        }

        function onMainWindowLoad() {
            try {
                signoPADAPIWeb = new ActiveXObject("signotec.STPadActiveXServer");
                state.className = "success";
                state.innerHTML = "ActiveX loaded";
            } catch (e) {
                signoPADAPIWeb = new WebSocket(wsUri);
                signoPADAPIWeb.onopen = onOpen;
                signoPADAPIWeb.onclose = onClose;
                signoPADAPIWeb.onerror = onError;
            }

            signoPADAPIWeb.onmessage = onMessage;

            clearSignature();
        }

        function onMainWindowBeforeUnload() {
            close_pad();
        }

        function onOpen(evt) {
            state.className = "success";
            if ((evt.target === undefined) || (evt.target.url === undefined)) {
                state.innerHTML = "ActiveX loaded";
            } else {
                state.innerHTML = "Connected to " + evt.target.url;
                get_server_version();
            }
        }

        function onClose(evt) {
            state.className = "fail";
            if ((evt.target === undefined) || (evt.target.url === undefined)) {
                state.innerHTML = "ActiveX unloaded";
            } else {
                state.innerHTML = "Disconnected from " + evt.target.url;
            }
        }

        function onError(evt) {
            state.className = "fail";
            if ((evt.target === undefined) || (evt.target.url === undefined)) {
                state.innerHTML = "Communication error";
            } else {
                state.innerHTML = "Communication error " + evt.target.url;
            }
        }

        function logMessage(msg) {
            log.innerHTML = "<li>" + msg + "</li>";
        }

        function drawStrokeStartPoint(canvasContext, softCoordX, softCoordY) {

            canvasContext.beginPath();
            canvasContext.arc(softCoordX, softCoordY, 0.1, 0, 2 * Math.PI, true);
            canvasContext.fill();
            canvasContext.stroke();
            canvasContext.moveTo(softCoordX, softCoordY);
        }

        function drawStrokePoint(canvasContext, softCoordX, softCoordY) {

            canvasContext.lineTo(softCoordX, softCoordY);
            canvasContext.stroke();
        }

        function disconnect_send(index) {
            var msg = "The pad (index: " + index + ") has been disconnected.";
            alert(msg);

            resetUserInterface();
            resetStates();
        }

        function signature_point_send(x, y, p) {
            var ctx = sigcanvas.getContext("2d");

            ctx.fillStyle = "#000";

            ctx.lineWidth = 4.5;
            ctx.lineCap = "round";

            if (p == 0) {
                drawStrokeStartPoint(ctx, x * scaleFactorX, y * scaleFactorY);
            } else {
                drawStrokePoint(ctx, x * scaleFactorX, y * scaleFactorY);
            }
        }

        function signature_retry_send() {
            var message;
            if (padMode == padModes.Default) {

                message = '{ "TOKEN_TYPE":"TOKEN_TYPE_REQUEST", "TOKEN_CMD":"TOKEN_CMD_SIGNATURE_RETRY" }';
            } else if (padMode == padModes.API) {

                message = '{ "TOKEN_TYPE":"TOKEN_TYPE_REQUEST", "TOKEN_CMD":"TOKEN_CMD_API_SIGNATURE_RETRY" }';
            } else {
                alert("invalid padMode");
                close_pad();
                return;
            }
            signoPADAPIWeb.send(message);
            logMessage(message);
        }

        function signature_retry_response(obj) {

            var ret = obj.TOKEN_PARAM_RETURN_CODE;
            if (ret < 0) {
                alert("Failed to restart signature process. Reason: " + obj.TOKEN_PARAM_ERROR_DESCRIPTION);
                close_pad();
                return;
            }

            var ctx = sigcanvas.getContext("2d");
            ctx.clearRect(0, 0, sigcanvas.width, sigcanvas.height);
        }

        function signature_confirm_send() {
            var message;
            if (padMode == padModes.Default) {

                message = '{ "TOKEN_TYPE":"TOKEN_TYPE_REQUEST", "TOKEN_CMD":"TOKEN_CMD_SIGNATURE_CONFIRM" }';
            } else if (padMode == padModes.API) {

                message = '{ "TOKEN_TYPE":"TOKEN_TYPE_REQUEST", "TOKEN_CMD":"TOKEN_CMD_API_SIGNATURE_CONFIRM" }';
            } else {
                alert("invalid padMode");
                close_pad();
                return;
            }
            signoPADAPIWeb.send(message);
            logMessage(message);
        }

        function signature_confirm_response(obj) {

            var ret = obj.TOKEN_PARAM_RETURN_CODE;

            if (ret < 0) {
                alert("Failed to confirm the signature. Reason: " + obj.TOKEN_PARAM_ERROR_DESCRIPTION);
                close_pad();
                return;
            }

            var signatureDuration = ret / sampleRate;

            if (signatureDuration <= 0.2) {
                alert("The signature is too short. Please sign again!");
                signature_retry_send();
                return;
            }

            if (supportsRSA) {
                signing_cert();
            } else {
                if (os == OS_WINDOWS) {
                    signature_image();
                } else if (os == OS_LINUX) {
                    signature_sign_data();
                } else {

                }
            }
        }

        function signing_cert() {
            var message;
            if (padMode == padModes.Default) {

                message = '{ "TOKEN_TYPE":"TOKEN_TYPE_REQUEST", "TOKEN_CMD":"TOKEN_CMD_SIGNING_CERT" }';
            } else if (padMode == padModes.API) {

                message = '{ "TOKEN_TYPE":"TOKEN_TYPE_REQUEST", "TOKEN_CMD":"TOKEN_CMD_API_RSA_SAVE_SIGNING_CERT_AS_STREAM' +
                    '", "TOKEN_PARAM_CERTTYPE":"' + certtype +
                    '" }';
            } else {
                alert("invalid padMode");
                close_pad();
                return;
            }
            signoPADAPIWeb.send(message);
            logMessage(message);
        }

        function signing_cert_response(obj) {
            var signing_cert;

            if (padMode == padModes.Default) {

                var ret = obj.TOKEN_PARAM_RETURN_CODE;
                if (ret < 0) {
                    alert("Failed to get signing cert. Reason: " + obj.TOKEN_PARAM_ERROR_DESCRIPTION);
                    close_pad();
                    return;
                }

                signing_cert = obj.TOKEN_PARAM_SIGNING_CERT;
                document.getElementById("signatureCert_0").value = signing_cert;
                var signatureCert_element = document.getElementById("signatureCert_0");
                signatureCert_element.dispatchEvent(new Event("input"));

                signature_image();
            } else if (padMode == padModes.API) {

                var ret = obj.TOKEN_PARAM_RETURN_CODE;
                if (ret < 0) {
                    alert("Failed to get signing cert. Reason: " + obj.TOKEN_PARAM_ERROR_DESCRIPTION);
                    close_pad();
                    return;
                }

                signing_cert = obj.TOKEN_PARAM_SIGNING_CERT;
                document.getElementById("signatureCert_0").value = signing_cert;
                var signatureCert_element = document.getElementById("signatureCert_0");
                signatureCert_element.dispatchEvent(new Event("input"));

                signature_image();
            } else {
                alert("invalid padMode");
                close_pad();
                return;
            }
        }

		function signature_image() {
			var message;

			if (padMode == padModes.Default) {

				message = '{ "TOKEN_TYPE":"TOKEN_TYPE_REQUEST", "TOKEN_CMD":"TOKEN_CMD_SIGNATURE_IMAGE' +
					'", "TOKEN_PARAM_FILE_TYPE":"' + '1' +
					'", "TOKEN_PARAM_PEN_WIDTH":"' + '5' +
					'" }';
			} else if (padMode == padModes.API) {

				message = '{ "TOKEN_TYPE":"TOKEN_TYPE_REQUEST", "TOKEN_CMD":"TOKEN_CMD_API_SIGNATURE_SAVE_AS_STREAM_EX' +
					'", "TOKEN_PARAM_RESOLUTION":"' + '300' +
					'", "TOKEN_PARAM_WIDTH":"' + '0' +
					'", "TOKEN_PARAM_HEIGHT":"' + '0' +
					'", "TOKEN_PARAM_FILE_TYPE":"' + '1' +
					'", "TOKEN_PARAM_PEN_WIDTH":"' + '5' +
					'", "TOKEN_PARAM_PEN_COLOR":"' + '0xFF0000' +
					'", "TOKEN_PARAM_OPTIONS":"' + '0x1400' +
					'" }';
			} else {
				alert("invalid padMode");
				close_pad();
				return;
			}
			signoPADAPIWeb.send(message);
			logMessage(message);
		}

        function signature_image_response(obj) {

            if (obj.TOKEN_CMD_ORIGIN == "TOKEN_CMD_SIGNATURE_IMAGE") {

                var ret = obj.TOKEN_PARAM_RETURN_CODE;
                if (ret < 0) {
                    alert("Failed to get signature image. Reason: " + obj.TOKEN_PARAM_ERROR_DESCRIPTION);
                    close_pad();
                    return;
                }

                document.getElementById("Signature_0").src = "data:image/png;base64," + obj.TOKEN_PARAM_FILE;

                document.getElementById("Signature_b64_0").value = obj.TOKEN_PARAM_FILE;
				var Signature_0_b64_element = document.getElementById("Signature_b64_0");
				Signature_0_b64_element.dispatchEvent(new Event("input"));


                signature_sign_data();
            } else if (obj.TOKEN_CMD_ORIGIN == "TOKEN_CMD_API_SIGNATURE_SAVE_AS_STREAM_EX") {

                var ret = obj.TOKEN_PARAM_RETURN_CODE;
                if (ret < 0) {
                    alert("Failed to get signature image. Reason: " + obj.TOKEN_PARAM_ERROR_DESCRIPTION);
                    close_pad();
                    return;
                }

                document.getElementById("Signature_0").src = "data:image/png;base64," + obj.TOKEN_PARAM_IMAGE;

                document.getElementById("Signature_b64_0").value = obj.TOKEN_PARAM_FILE;
				var Signature_0_b64_element = document.getElementById("Signature_b64_0");
				Signature_0_b64_element.dispatchEvent(new Event("input"));

                if (supportsRSA) {
                    api_rsa_sign_get_sign_data();
                } else {
                    signature_sign_data();
                }
            } else {

            }
        }

        function signature_sign_data() {
            var message;
            if (padMode == padModes.Default) {

                message = '{ "TOKEN_TYPE":"TOKEN_TYPE_REQUEST", "TOKEN_CMD":"TOKEN_CMD_SIGNATURE_SIGN_DATA' +
                    '", "TOKEN_PARAM_SIGNATURE_RSA_SCHEME":"' + rsa_scheme +
                    '" }';
            } else if (padMode == padModes.API) {

                message = '{ "TOKEN_TYPE":"TOKEN_TYPE_REQUEST", "TOKEN_CMD":"TOKEN_CMD_API_SIGNATURE_GET_SIGN_DATA" }';
            } else {
                alert("invalid padMode");
                close_pad();
                return;
            }
            signoPADAPIWeb.send(message);
            logMessage(message);
        }

        function signature_sign_data_response(obj) {

            if (obj.TOKEN_CMD_ORIGIN == "TOKEN_CMD_SIGNATURE_SIGN_DATA") {

                var ret = obj.TOKEN_PARAM_RETURN_CODE;
                if (ret < 0) {
                    alert("Failed to get signature SignData. Reason: " + obj.TOKEN_PARAM_ERROR_DESCRIPTION);
                    close_pad();
                    return;
                }

                if (supportsRSA) {

                    var certId = obj.TOKEN_PARAM_CERT_ID;
                    document.getElementById("biometryCertID_0").value = certId;
                    var biometryCertID_element = document.getElementById("biometryCertID_0");
                    biometryCertID_element.dispatchEvent(new Event("input"));

                    document.getElementById("RSAScheme_0").value = rsa_scheme;
                    var RSAScheme_element = document.getElementById("RSAScheme_0");
                    RSAScheme_element.dispatchEvent(new Event("input"));

                    var rsaSignature = obj.TOKEN_PARAM_SIGNATURE_RSA_SIGNATURE;
                    document.getElementById("RsaSignature_0").value = rsaSignature;
                    var RsaSignature_element = document.getElementById("RsaSignature_0");
                    RsaSignature_element.dispatchEvent(new Event("input"));

                } else {

                    document.getElementById("biometryCertID_0").value = "";
                    var biometryCertID_element = document.getElementById("biometryCertID_0");
                    biometryCertID_element.dispatchEvent(new Event("input"));

                    document.getElementById("RSAScheme_0").value = "";
                    var RSAScheme_element = document.getElementById("RSAScheme_0");
                    RSAScheme_element.dispatchEvent(new Event("input"));

                    document.getElementById("RsaSignature_0").value = "";
                    var RsaSignature_element = document.getElementById("RsaSignature_0");
                    RsaSignature_element.dispatchEvent(new Event("input"));
                }

                var signData = obj.TOKEN_PARAM_SIGNATURE_SIGN_DATA;
                document.getElementById("SignData_0").value = signData;
                var element = document.getElementById("SignData_0");
                element.dispatchEvent(new Event("input"));


                close_pad();
            } else if (obj.TOKEN_CMD_ORIGIN == "TOKEN_CMD_API_SIGNATURE_GET_SIGN_DATA") {

                var ret = obj.TOKEN_PARAM_RETURN_CODE;
                if (ret < 0) {
                    alert("Failed to get signature SignData. Reason: " + obj.TOKEN_PARAM_ERROR_DESCRIPTION);
                    close_pad();
                    return;
                }

                if (supportsRSA) {

                } else {

                    document.getElementById("biometryCertID_0").value = "";
                    var biometryCertID_element = document.getElementById("biometryCertID_0");
                    biometryCertID_element.dispatchEvent(new Event("input"));

                    document.getElementById("RSAScheme_0").value = "";
                    var RSAScheme_element = document.getElementById("RSAScheme_0");
                    RSAScheme_element.dispatchEvent(new Event("input"));

                    document.getElementById("RsaSignature_0").value = "";
                    var RsaSignature_element = document.getElementById("RsaSignature_0");
                    RsaSignature_element.dispatchEvent(new Event("input"));
                }

                var signData = obj.TOKEN_PARAM_SIGN_DATA;
                document.getElementById("SignData_0").value = signData;


                close_pad();
            } else {

            }
        }

        function api_rsa_sign_get_sign_data() {
            var message;
            var hash_value;
            var options;
            var sign_password;
            switch (rsaSignGetSignDataState) {
                case rsaSignGetSignDataStates.rsaSign:
                    if (api_dochash === undefined || api_dochash === null) {
                        hash_value = HashValue.kHash2;
                    } else {
                        hash_value = HashValue.kCombination;
                    }
                    options = 0;
                    sign_password = "";
                    message = '{ "TOKEN_TYPE":"TOKEN_TYPE_REQUEST", "TOKEN_CMD":"TOKEN_CMD_API_RSA_SIGN_PW' +
                        '", "TOKEN_PARAM_RSA_SCHEME":"' + rsa_scheme +
                        '", "TOKEN_PARAM_HASHVALUE":"' + hash_value +
                        '", "TOKEN_PARAM_OPTIONS":"' + options +
                        '", "TOKEN_PARAM_SIGN_PASSWORD":"' + sign_password +
                        '" }';
                    break;
                case rsaSignGetSignDataStates.getEncryptionCertId:
                    getEncryptionCertIDState = getEncryptionCertIDStates.rsaSignGetSignData;
                    message = '{ "TOKEN_TYPE":"TOKEN_TYPE_REQUEST", "TOKEN_CMD":"TOKEN_CMD_API_RSA_GET_ENCRYPTION_CERT_ID' +
                        '" }';
                    break;
                case rsaSignGetSignDataStates.rsaGetSignData:
                    options = 0;
                    message = '{ "TOKEN_TYPE":"TOKEN_TYPE_REQUEST", "TOKEN_CMD":"TOKEN_CMD_API_RSA_GET_SIGN_DATA' +
                        '", "TOKEN_PARAM_OPTIONS":"' + options +
                        '" }';
                    break;
                default:
                    alert("invalid rsaSignGetSignDataState");
                    close_pad();
                    return;
            }
            signoPADAPIWeb.send(message);
            logMessage(message);
        }

        function api_rsa_sign_get_sign_data_responses(obj) {
            var encryption_cert_id;
            if (obj.TOKEN_CMD_ORIGIN == "TOKEN_CMD_API_RSA_SIGN_PW") {

                var ret = obj.TOKEN_PARAM_RETURN_CODE;
                if (ret < 0) {
                    alert("Failed to rsa sign pw. Reason: " + obj.TOKEN_PARAM_ERROR_DESCRIPTION);
                    close_pad();
                    return;
                }

                document.getElementById("RSAScheme_0").value = rsa_scheme;
                document.getElementById("RsaSignature_0").value = obj.TOKEN_PARAM_RSA_SIGNATURE;

                rsaSignGetSignDataState = rsaSignGetSignDataStates.getEncryptionCertId;
                api_rsa_sign_get_sign_data();
            } else if (obj.TOKEN_CMD_ORIGIN == "TOKEN_CMD_API_RSA_GET_ENCRYPTION_CERT_ID") {

                var ret = obj.TOKEN_PARAM_RETURN_CODE;
                if (ret < 0 && ret != -28  ) {
                    alert("Failed to get encryption cert id. Reason: " + obj.TOKEN_PARAM_ERROR_DESCRIPTION);
                    close_pad();
                    return;
                }

                switch (getEncryptionCertIDState) {
                    case getEncryptionCertIDStates.encryptionCertDochash:

                        break;

                    case getEncryptionCertIDStates.rsaSignGetSignData:
                        encryption_cert_id = obj.TOKEN_PARAM_ENCRYPTION_CERT_ID;
                        document.getElementById("biometryCertID_0").value = encryption_cert_id;

                        rsaSignGetSignDataState = rsaSignGetSignDataStates.rsaGetSignData;
                        api_rsa_sign_get_sign_data();
                        break;

                    default:
                        alert("invalid getEncryptionCertIDState");
                        close_pad();
                        return;
                }
            } else if (obj.TOKEN_CMD_ORIGIN == "TOKEN_CMD_API_RSA_GET_SIGN_DATA") {

                var ret = obj.TOKEN_PARAM_RETURN_CODE;
                if (ret < 0) {
                    alert("Failed to get rsa sign data. Reason: " + obj.TOKEN_PARAM_ERROR_DESCRIPTION);
                    close_pad();
                    return;
                }
                document.getElementById("SignData_0").value = obj.TOKEN_PARAM_SIGN_DATA;
                close_pad();
            } else {

            }
        }

        function signature_cancel_send() {
            var message;
            if (padMode == padModes.Default) {

                message = '{ "TOKEN_TYPE":"TOKEN_TYPE_REQUEST", "TOKEN_CMD":"TOKEN_CMD_SIGNATURE_CANCEL" }';
            } else if (padMode == padModes.API) {

                message = '{ "TOKEN_TYPE":"TOKEN_TYPE_REQUEST", "TOKEN_CMD":"TOKEN_CMD_API_SIGNATURE_CANCEL", "TOKEN_PARAM_ERASE":"0" }';
            } else {
                alert("invalid padMode");
                close_pad();
                return;
            }
            signoPADAPIWeb.send(message);
            logMessage(message);
        }

        function signature_cancel_response(obj) {

            var ret = obj.TOKEN_PARAM_RETURN_CODE;
            if (ret < 0) {
                alert("Failed to cancel signature process. Reason: " + obj.TOKEN_PARAM_ERROR_DESCRIPTION);
                close_pad();
                return;
            }

            var ctx = sigcanvas.getContext("2d");
            ctx.clearRect(0, 0, sigcanvas.width, sigcanvas.height);

            close_pad();
        }

        function selection_confirm_send() {
            signature_start();
        }

        function selection_cancel_send() {
            if (padMode == padModes.Default) {

                var ctx = sigcanvas.getContext("2d");
                ctx.clearRect(0, 0, sigcanvas.width, sigcanvas.height);

                close_pad();
            } else if (padMode == padModes.API) {

            } else {
                alert("invalid padMode");
                close_pad();
                return;
            }
        }

        function error_send(error_context, return_code, error_description) {
            var ret = return_code;
            if (ret < 0) {
                alert("Failed to confirm the signature. Reason: " + error_description + ", Context: " + error_context);
            }
        }

        function api_sensor_hot_spot_pressed_send(button) {
            switch (button) {

                case cancelButton:
                    if (dialogType == dialogTypes.pdf) {
                        close_pad();
                    } else if (dialogType == dialogTypes.signatur) {
                        signature_cancel_send();
                    } else {
                        alert("invalid dialogType");
                        close_pad();
                        return;
                    }
                    break;

                case retryButton:
                    signature_retry_send();
                    break;

                case confirmButton:
                    if (dialogType == dialogTypes.pdf) {
                        api_pdf_dialog_end();
                    } else if (dialogType == dialogTypes.signatur) {
                        signature_confirm_send();
                    } else {
                        alert("invalid dialogType");
                        close_pad();
                        return;
                    }
                    break;

                default:
                    alert("unknown button id: " + button);
            }
        }

        function api_display_scroll_pos_changed_send(xPos, yPos) {
        }

        function getSignature() {

            resetUserInterface();
            resetStates();

            var padConnectionTypeList = "USB";

            if (padConnectionTypeList == "USB") {

                padConnectionType = "HID";
            } else {

                padConnectionType = "All";
            }

            if (padMode == padModes.Default) {

                search_for_pads();
            } else if (padMode == padModes.API) {

                api_search_for_pads();
            } else {
                alert("invalid padMode");
                close_pad();
                return;
            }
        }

        function search_for_pads() {
            var message;

            message = '{ "TOKEN_TYPE":"TOKEN_TYPE_REQUEST", "TOKEN_CMD":"TOKEN_CMD_SEARCH_FOR_PADS", "TOKEN_PARAM_PAD_SUBSET":"' + padConnectionType + '" }';

            if (signoPADAPIWeb.readyState === WebSocket.OPEN) {

                signoPADAPIWeb.send(message);
                logMessage(message);

            } else {

            }
        }

        function search_for_pads_response(obj) {
            if (obj.TOKEN_CMD_ORIGIN == "TOKEN_CMD_SEARCH_FOR_PADS") {

                var ret = obj.TOKEN_PARAM_RETURN_CODE;
                if (ret < 0) {
                    alert("The search for pads failed. Reason: " + obj.TOKEN_PARAM_ERROR_DESCRIPTION);
                    close_pad();
                    return;
                }

                if (obj.TOKEN_PARAM_CONNECTED_PADS == null) {
                    alert("No connected pads have been found.");
                    resetStates();
                    return;
                }

                padType = parseInt(obj.TOKEN_PARAM_CONNECTED_PADS[0].TOKEN_PARAM_PAD_TYPE);

                var padTypeReadable = getReadableType(padType);
                var serialNumber = obj.TOKEN_PARAM_CONNECTED_PADS[0].TOKEN_PARAM_PAD_SERIAL_NUMBER;
                var firmwareVersion = obj.TOKEN_PARAM_CONNECTED_PADS[0].TOKEN_PARAM_PAD_FIRMWARE_VERSION;

                document.getElementById("PadType_0").value = padTypeReadable;
                document.getElementById("SerialNumber_0").value = serialNumber;
                document.getElementById("FirmwareVersion_0").value = firmwareVersion;

                if (obj.TOKEN_PARAM_CONNECTED_PADS[0].TOKEN_PARAM_PAD_CAPABILITIES & deviceCapabilities.SupportsRSA) {
                    if (os == OS_WINDOWS) {
                        supportsRSA = true;
                    } else if (os == OS_LINUX) {

                        supportsRSA = false;
                    } else {

                    }
                } else {
                    supportsRSA = false;
                }

                if (obj.TOKEN_PARAM_CONNECTED_PADS[0].TOKEN_PARAM_PAD_CAPABILITIES & deviceCapabilities.CanStoreEncryptKey) {
                    if (os == OS_WINDOWS) {
                        canStoreEncryptKey = true;
                    } else if (os == OS_LINUX) {

                        canStoreEncryptKey = false;
                    } else {

                    }
                } else {
                    canStoreEncryptKey = false;
                }

                var rsaSupport = supportsRSA ? "Yes" : "No";
                if (supportsRSA) {
                    document.getElementById("RSASupport_0").value = "Yes";
                } else {
                    document.getElementById("RSASupport_0").value = "No";
                }

                open_pad();
            } else {

            }
        }

        function open_pad() {
            var message;

            message = '{ "TOKEN_TYPE":"TOKEN_TYPE_REQUEST", "TOKEN_CMD":"TOKEN_CMD_OPEN_PAD", "TOKEN_PARAM_PAD_INDEX":"' + padIndex + '" }';

            signoPADAPIWeb.send(message);
            logMessage(message);
        }

        function open_pad_response(obj) {
            if (obj.TOKEN_CMD_ORIGIN == "TOKEN_CMD_OPEN_PAD") {

                var ret = obj.TOKEN_PARAM_RETURN_CODE;
                if (ret < 0) {
                    alert("Failed to open pad. Reason: " + obj.TOKEN_PARAM_ERROR_DESCRIPTION);
                    resetStates();
                    return;
                }

                padState = padStates.opened;

                sigcanvas.width = obj.TOKEN_PARAM_PAD_DISPLAY_WIDTH;
                sigcanvas.height = obj.TOKEN_PARAM_PAD_DISPLAY_HEIGHT;

                scaleFactorX = obj.TOKEN_PARAM_PAD_DISPLAY_WIDTH / obj.TOKEN_PARAM_PAD_X_RESOLUTION;
                scaleFactorY = obj.TOKEN_PARAM_PAD_DISPLAY_HEIGHT / obj.TOKEN_PARAM_PAD_Y_RESOLUTION;

                sampleRate = obj.TOKEN_PARAM_PAD_SAMPLING_RATE;


                selection_dialog();
            } else {

            }
        }

        function selection_dialog() {
            signature_start();
        }

        function selection_dialog_response(obj) {
            if (obj.TOKEN_CMD_ORIGIN == "TOKEN_CMD_SELECTION_DIALOG") {

                var ret = obj.TOKEN_PARAM_RETURN_CODE;
                if (ret < 0) {
                    alert("Failed to selection dialog process. Reason: " + obj.TOKEN_PARAM_ERROR_DESCRIPTION);
                    close_pad();
                    return;
                }
            } else {

            }
        }

        function signature_start() {
            var hashValue = document.getElementById("signPen_X_message_hash_sha256_0")?.value;
            if (hashValue) {
                sha256_dochash = hashValue;
            }

            if (!sha256_dochash || sha256_dochash === "") {
                var attempt = 0;
                function checkHash() {
                    var hashField = document.getElementById("signPen_X_message_hash_sha256_0");
                    var hashVal = hashField ? hashField.value : null;

                    if (hashVal && hashVal.trim() !== "") {
                        sha256_dochash = hashVal;
                        signature_start();
                    } else if (attempt++ < 30) {
                        setTimeout(checkHash, 100);
                    } else {
                        alert("Грешка: Първо генерирайте X013 съобщение преди да подписвате!");
                        close_pad();
                    }
                }
                setTimeout(checkHash, 100);
                return;
            }

            var message;
            switch (docHash_type) {
                case docHashes.kSha256:
                    default_dochash = sha256_dochash;
                    break;
                default:
                    alert("unknown doc hash");
                    return;
            }

            if (supportsRSA) {
                if (canStoreEncryptKey) {
                    message = '{ "TOKEN_TYPE":"TOKEN_TYPE_REQUEST", "TOKEN_CMD":"TOKEN_CMD_SIGNATURE_START' +
                        '", "TOKEN_PARAM_FIELD_NAME":"' + field_name +
                        '", "TOKEN_PARAM_CUSTOM_TEXT":"' + custom_text +
                        '", "TOKEN_PARAM_PAD_ENCRYPTION":"' + encryption +
                        '", "TOKEN_PARAM_DOCHASH":"' + default_dochash +
                        '", "TOKEN_PARAM_ENCRYPTION_CERT":"' + encryption_cert +
                        '", "TOKEN_PARAM_ENCRYPTION_CERT_ONLY_WHEN_EMPTY":"' + encryption_cert_only_when_empty +
                        '" }';
                } else {
                    message = '{ "TOKEN_TYPE":"TOKEN_TYPE_REQUEST", "TOKEN_CMD":"TOKEN_CMD_SIGNATURE_START' +
                        '", "TOKEN_PARAM_FIELD_NAME":"' + field_name +
                        '", "TOKEN_PARAM_CUSTOM_TEXT":"' + custom_text +
                        '", "TOKEN_PARAM_PAD_ENCRYPTION":"' + encryption +
                        '", "TOKEN_PARAM_DOCHASH":"' + default_dochash +
                        '" }';
                }
            } else {
                message = '{ "TOKEN_TYPE":"TOKEN_TYPE_REQUEST", "TOKEN_CMD":"TOKEN_CMD_SIGNATURE_START' +
                    '", "TOKEN_PARAM_FIELD_NAME":"' + field_name +
                    '", "TOKEN_PARAM_CUSTOM_TEXT":"' + custom_text +
                    '" }';
            }
            signoPADAPIWeb.send(message);
            logMessage(message);
        }

        function signature_start_response(obj) {
            if (obj.TOKEN_CMD_ORIGIN == "TOKEN_CMD_SIGNATURE_START") {

                var ret = obj.TOKEN_PARAM_RETURN_CODE;
                if (ret < 0) {
                    alert("Failed to start signature process. Reason: " + obj.TOKEN_PARAM_ERROR_DESCRIPTION);
                    close_pad();
                    return;
                }
            } else {

            }
        }

        function close_pad() {
            var message;
            if (padState == padStates.opened) {
                if (padMode == padModes.Default) {

                    message = '{ "TOKEN_TYPE":"TOKEN_TYPE_REQUEST", "TOKEN_CMD":"TOKEN_CMD_CLOSE_PAD", "TOKEN_PARAM_PAD_INDEX":"' + padIndex + '" }';
                } else if (padMode == padModes.API) {

                    message = '{ "TOKEN_TYPE":"TOKEN_TYPE_REQUEST", "TOKEN_CMD":"TOKEN_CMD_API_DEVICE_CLOSE", "TOKEN_PARAM_INDEX":"' + padIndex + '" }';
                } else {
                    alert("invalid padMode");
                    return;
                }
                signoPADAPIWeb.send(message);
                logMessage(message);
            }
        }

        function close_pad_response(obj) {

            if ((obj.TOKEN_CMD_ORIGIN == "TOKEN_CMD_CLOSE_PAD") || (obj.TOKEN_CMD_ORIGIN == "TOKEN_CMD_API_DEVICE_CLOSE")) {
                if (padState == padStates.opened) {

                    var ret = obj.TOKEN_PARAM_RETURN_CODE;
                    if (ret < 0) {
                        alert("Failed to close pad. Reason: " + obj.TOKEN_PARAM_ERROR_DESCRIPTION);
                    } else {
                    }
                    resetStates();
                    padState = padStates.closed;
                }
            } else {

            }
        }

        function api_search_for_pads() {
            var message;

            switch (searchState) {
                case searchStates.setPadType:
                    message = '{ "TOKEN_TYPE":"TOKEN_TYPE_REQUEST", "TOKEN_CMD":"TOKEN_CMD_API_DEVICE_SET_COM_PORT", "TOKEN_PARAM_PORT_LIST":"' + padConnectionType + '" }';
                    break;

                case searchStates.search:
                    message = '{ "TOKEN_TYPE":"TOKEN_TYPE_REQUEST", "TOKEN_CMD":"TOKEN_CMD_API_DEVICE_GET_COUNT" }';
                    break;

                case searchStates.getInfo:

                    message = '{ "TOKEN_TYPE":"TOKEN_TYPE_REQUEST", "TOKEN_CMD":"TOKEN_CMD_API_DEVICE_GET_INFO", "TOKEN_PARAM_INDEX":"' + padIndex + '" }';
                    break;

                case searchStates.getVersion:

                    message = '{ "TOKEN_TYPE":"TOKEN_TYPE_REQUEST", "TOKEN_CMD":"TOKEN_CMD_API_DEVICE_GET_VERSION", "TOKEN_PARAM_INDEX":"' + padIndex + '" }';
                    break;

                case searchStates.getDeviceCapabilities:

                    message = '{ "TOKEN_TYPE":"TOKEN_TYPE_REQUEST", "TOKEN_CMD":"TOKEN_CMD_API_DEVICE_GET_CAPABILITIES", "TOKEN_PARAM_INDEX":"' + padIndex + '" }';
                    break;

                default:
                    alert("invalid searchState");
                    close_pad();
                    return;
            }
            signoPADAPIWeb.send(message);
            logMessage(message);
        }

        function api_search_for_pads_responses(obj) {
            if (obj.TOKEN_CMD_ORIGIN == "TOKEN_CMD_API_DEVICE_SET_COM_PORT") {

                var ret = obj.TOKEN_PARAM_RETURN_CODE;
                if (ret < 0) {
                    alert("Failed to set pad type. Reason: " + obj.TOKEN_PARAM_ERROR_DESCRIPTION);
                    close_pad();
                    return;
                }

                searchState = searchStates.search;
                api_search_for_pads();
            } else if (obj.TOKEN_CMD_ORIGIN == "TOKEN_CMD_API_DEVICE_GET_COUNT") {

                var ret = obj.TOKEN_PARAM_RETURN_CODE;
                if (ret < 0) {
                    alert("The search for pads failed. Reason: " + obj.TOKEN_PARAM_ERROR_DESCRIPTION);
                    close_pad();
                    return;
                }

                if (ret == 0) {
                    alert("No connected pads have been found.");
                    resetStates();
                    return;
                }

                searchState = searchStates.getInfo;
                api_search_for_pads();
            } else if (obj.TOKEN_CMD_ORIGIN == "TOKEN_CMD_API_DEVICE_GET_INFO") {

                var ret = obj.TOKEN_PARAM_RETURN_CODE;
                if (ret < 0) {
                    alert("Failed to get device info. Reason: " + obj.TOKEN_PARAM_ERROR_DESCRIPTION);
                    close_pad();
                    return;
                }

                padType = parseInt(obj.TOKEN_PARAM_TYPE);
                switch (padType) {
                    case padTypes.sigmaUSB:
                    case padTypes.sigmaSerial:
                        getBackgroundImage("Sigma");
                        buttonSize = 36;
                        buttonTop = 2;
                        break;

                    case padTypes.zetaUSB:
                    case padTypes.zetaSerial:
                        getBackgroundImage("Zeta");
                        buttonSize = 36;
                        buttonTop = 2;
                        break;

                    case padTypes.omegaUSB:
                    case padTypes.omegaSerial:
                        getBackgroundImage("Omega");
                        buttonSize = 48;
                        buttonTop = 4;
                        break;

                    case padTypes.gammaUSB:
                    case padTypes.gammaSerial:
                        getBackgroundImage("Gamma");
                        buttonSize = 48;
                        buttonTop = 4;
                        break;

                    case padTypes.deltaUSB:
                    case padTypes.deltaSerial:
                    case padTypes.deltaIP:
                        getBackgroundImage("Delta");
                        buttonSize = 48;
                        buttonTop = 4;
                        break;

                    case padTypes.alphaUSB:
                    case padTypes.alphaSerial:
                    case padTypes.alphaIP:
                        getBackgroundImage("Alpha");
                        buttonSize = 80;
                        buttonTop = 10;
                        break;
                }

                document.getElementById("PadType_0").value = getReadableType(padType);
                document.getElementById("SerialNumber_0").value = obj.TOKEN_PARAM_SERIAL;

                searchState = searchStates.getVersion;
                api_search_for_pads();
            } else if (obj.TOKEN_CMD_ORIGIN == "TOKEN_CMD_API_DEVICE_GET_VERSION") {

                var ret = obj.TOKEN_PARAM_RETURN_CODE;
                if (ret < 0) {
                    alert("Failed to get device version. Reason: " + obj.TOKEN_PARAM_ERROR_DESCRIPTION);
                    close_pad();
                    return;
                }

                document.getElementById("FirmwareVersion_0").value = obj.TOKEN_PARAM_VERSION;

                searchState = searchStates.getDeviceCapabilities;
                api_search_for_pads();
            } else if (obj.TOKEN_CMD_ORIGIN == "TOKEN_CMD_API_DEVICE_GET_CAPABILITIES") {

                var ret = obj.TOKEN_PARAM_RETURN_CODE;
                if (ret < 0) {
                    alert("Failed to get device version. Reason: " + obj.TOKEN_PARAM_ERROR_DESCRIPTION);
                    close_pad();
                    return;
                }

                if (obj.TOKEN_PARAM_RETURN_CODE & deviceCapabilities.SupportsRSA) {
                    if (os == OS_WINDOWS) {
                        supportsRSA = true;
                    } else if (os == OS_LINUX) {

                        supportsRSA = false;
                    } else {

                    }
                } else {
                    supportsRSA = false;
                }

                if (obj.TOKEN_PARAM_RETURN_CODE & deviceCapabilities.CanStoreEncryptKey) {
                    if (os == OS_WINDOWS) {
                        canStoreEncryptKey = true;
                    } else if (os == OS_LINUX) {

                        canStoreEncryptKey = false;
                    } else {

                    }
                } else {
                    canStoreEncryptKey = false;
                }

                if (supportsRSA) {
                    document.getElementById("RSASupport_0").value = "Yes";
                } else {
                    document.getElementById("RSASupport_0").value = "No";
                }

                api_device_open();
            } else {

            }
        }

        function api_device_open() {
            var message;

            switch (openState) {
                case openStates.openPad:
                    message = '{ "TOKEN_TYPE":"TOKEN_TYPE_REQUEST", "TOKEN_CMD":"TOKEN_CMD_API_DEVICE_OPEN", "TOKEN_PARAM_INDEX":"' + padIndex + '", "TOKEN_PARAM_ERASE_DISPLAY":"FALSE" }';
                    break;

                case openStates.setColor:
                    message = '{ "TOKEN_TYPE":"TOKEN_TYPE_REQUEST", "TOKEN_CMD":"TOKEN_CMD_API_DISPLAY_CONFIG_PEN' +
                        '", "TOKEN_PARAM_WIDTH":"' + '3' +
						'", "TOKEN_PARAM_PEN_COLOR":"' + '0xFF0000' +
                        '" }';
                    break;

                case openStates.getDisplayWidth:
                    message = '{ "TOKEN_TYPE":"TOKEN_TYPE_REQUEST", "TOKEN_CMD":"TOKEN_CMD_API_DISPLAY_GET_WIDTH" }';
                    break;

                case openStates.getDisplayHeight:
                    message = '{ "TOKEN_TYPE":"TOKEN_TYPE_REQUEST", "TOKEN_CMD":"TOKEN_CMD_API_DISPLAY_GET_HEIGHT" }';
                    break;

                case openStates.getResolution:
                    message = '{ "TOKEN_TYPE":"TOKEN_TYPE_REQUEST", "TOKEN_CMD":"TOKEN_CMD_API_SIGNATURE_GET_RESOLUTION" }';
                    break;

                case openStates.getSampleRate:
                    message = '{ "TOKEN_TYPE":"TOKEN_TYPE_REQUEST", "TOKEN_CMD":"TOKEN_CMD_API_SENSOR_GET_SAMPLE_RATE_MODE" }';
                    break;

                default:
                    alert("invalid openState");
                    close_pad();
                    return;
            }
            signoPADAPIWeb.send(message);
            logMessage(message);
        }

        function api_device_open_responses(obj) {
            if (obj.TOKEN_CMD_ORIGIN == "TOKEN_CMD_API_DEVICE_OPEN") {

                var ret = obj.TOKEN_PARAM_RETURN_CODE;
                if (ret < 0) {
                    alert("Failed to open pad. Reason: " + obj.TOKEN_PARAM_ERROR_DESCRIPTION);
                    resetStates();
                    return;
                }

                padState = padStates.opened;

                openState = openStates.setColor;
                api_device_open();
            } else if (obj.TOKEN_CMD_ORIGIN == "TOKEN_CMD_API_DISPLAY_CONFIG_PEN") {

                var ret = obj.TOKEN_PARAM_RETURN_CODE;
                if (ret < 0) {
                    alert("Failed to set color. Reason: " + obj.TOKEN_PARAM_ERROR_DESCRIPTION);
                    close_pad();
                    return;
                }

                openState = openStates.getDisplayWidth;
                api_device_open();
            } else if (obj.TOKEN_CMD_ORIGIN == "TOKEN_CMD_API_DISPLAY_GET_WIDTH") {

                var ret = obj.TOKEN_PARAM_RETURN_CODE;
                if (ret < 0) {
                    alert("Failed to get display width. Reason: " + obj.TOKEN_PARAM_ERROR_DESCRIPTION);
                    close_pad();
                    return;
                }

                sigcanvas.width = ret;

                openState = openStates.getDisplayHeight;
                api_device_open();
            } else if (obj.TOKEN_CMD_ORIGIN == "TOKEN_CMD_API_DISPLAY_GET_HEIGHT") {

                var ret = obj.TOKEN_PARAM_RETURN_CODE;
                if (ret < 0) {
                    alert("Failed to get display height. Reason: " + obj.TOKEN_PARAM_ERROR_DESCRIPTION);
                    close_pad();
                    return;
                }

                sigcanvas.height = ret;

                openState = openStates.getResolution;
                api_device_open();
            } else if (obj.TOKEN_CMD_ORIGIN == "TOKEN_CMD_API_SIGNATURE_GET_RESOLUTION") {

                var ret = obj.TOKEN_PARAM_RETURN_CODE;
                if (ret < 0) {
                    alert("Failed to get signature resolution. Reason: " + obj.TOKEN_PARAM_ERROR_DESCRIPTION);
                    close_pad();
                    return;
                }

                scaleFactorX = sigcanvas.width / obj.TOKEN_PARAM_PAD_X_RESOLUTION;
                scaleFactorY = sigcanvas.height / obj.TOKEN_PARAM_PAD_Y_RESOLUTION;

                openState = openStates.getSampleRate;
                api_device_open();
            } else if (obj.TOKEN_CMD_ORIGIN == "TOKEN_CMD_API_SENSOR_GET_SAMPLE_RATE_MODE") {

                var ret = obj.TOKEN_PARAM_RETURN_CODE;
                if (ret < 0) {
                    alert("Failed to get sample rate. Reason: " + obj.TOKEN_PARAM_ERROR_DESCRIPTION);
                    close_pad();
                    return;
                }

                switch (parseInt(obj.TOKEN_PARAM_RETURN_CODE)) {
                    case 0:
                        sampleRate = 125;
                        break;
                    case 1:
                        sampleRate = 250;
                        break;
                    case 2:
                        sampleRate = 500;
                        break;
                    case 3:
                        sampleRate = 280;
                        break;
                    default:
                        alert("Failed to get sample rate. Reason: Unexpected sample rate mode: " + obj.TOKEN_PARAM_RETURN_CODE);
                        close_pad();
                        return;
                }

                if (os == OS_LINUX) {
                    api_signature_start();
                } else if (os == OS_WINDOWS) {
                    if (padType == padTypes.deltaUSB || padType == padTypes.deltaSerial || padType == padTypes.deltaIP) {
                        api_pdf_dialog_start();
                    } else {
                        if (supportsRSA) {
                            if (canStoreEncryptKey) {
                                if (encryption_cert_only_when_empty == "TRUE") {
                                    api_encryption_cert_dochash();
                                } else {
                                    encryptionCertDochashState = encryptionCertDochashStates.setEncryptionCertPw;
                                    api_encryption_cert_dochash();
                                }
                            } else {
                                encryptionCertDochashState = encryptionCertDochashStates.setDochash;
                                api_encryption_cert_dochash();
                            }
                        } else {
                            api_signature_start();
                        }
                    }
                } else {
                    alert("The OS is unknown");
                    close_pad();
                    return;
                }
            } else {

            }
        }

        function api_pdf_dialog_start() {
            var message;

            dialogType = dialogTypes.pdf;

            switch (pdfDialoStartState) {
                case pdfDialoStartStates.pdfLoad:

                    cancelButton = -1;
                    retryButton = -1;
                    confirmButton = -1;

                    clearArray(pdf_page_sizes);

                    pdf_page_index = 0;
                    pdf_page_count = 0;
                    height_of_all_pdf_pages = 0.0;
                    pdf_page_width = 0.0;
                    pdf_page_height = 0.0;
                    y_pos = 0.0;

                    message = '{ "TOKEN_TYPE":"TOKEN_TYPE_REQUEST", "TOKEN_CMD":"TOKEN_CMD_API_PDF_LOAD' +
                        '", "TOKEN_PARAM_DOCUMENT":"' + demo_pdf +
                        '", "TOKEN_PARAM_PASSWORD":"' + '' +
                        '" }';
                    break;
                case pdfDialoStartStates.pdfGetPageCount:
                    message = '{ "TOKEN_TYPE":"TOKEN_TYPE_REQUEST", "TOKEN_CMD":"TOKEN_CMD_API_PDF_GET_PAGE_COUNT' +
                        '" }';
                    break;
                case pdfDialoStartStates.pdfGetWidth:
                    pdf_page_index = 1;
                    message = '{ "TOKEN_TYPE":"TOKEN_TYPE_REQUEST", "TOKEN_CMD":"TOKEN_CMD_API_PDF_GET_WIDTH' +
                        '", "TOKEN_PARAM_PAGE":"' + pdf_page_index +
                        '", "TOKEN_PARAM_UNIT":"' + '0' +
                        '" }';
                    break;
                case pdfDialoStartStates.pdfGetHeight:
                    message = '{ "TOKEN_TYPE":"TOKEN_TYPE_REQUEST", "TOKEN_CMD":"TOKEN_CMD_API_PDF_GET_HEIGHT' +
                        '", "TOKEN_PARAM_PAGE":"' + pdf_page_index +
                        '", "TOKEN_PARAM_UNIT":"' + '0' +
                        '" }';
                    break;
                case pdfDialoStartStates.displaySetTargetOverlay:
                    setTargetState = setTargetStates.setPdfToolbar;
                    message = '{ "TOKEN_TYPE":"TOKEN_TYPE_REQUEST", "TOKEN_CMD":"TOKEN_CMD_API_DISPLAY_SET_TARGET' +
                        '", "TOKEN_PARAM_TARGET":"' + '2' +
                        '" }';
                    break;
                case pdfDialoStartStates.displaySetToolbarImage:
                    message = '{ "TOKEN_TYPE":"TOKEN_TYPE_REQUEST", "TOKEN_CMD":"TOKEN_CMD_API_DISPLAY_SET_IMAGE' +
                        '", "TOKEN_PARAM_X_POS":"' + '0' +
                        '", "TOKEN_PARAM_Y_POS":"' + '0' +
                        '", "TOKEN_PARAM_BITMAP":"' + pdf_dialog_toolbar_image +
                        '" }';
                    break;
                case pdfDialoStartStates.sensorAddCancelHotSpot:
                    addHotSpotState = addHotSpotStates.addCancel;
                    message = '{ "TOKEN_TYPE":"TOKEN_TYPE_REQUEST", "TOKEN_CMD":"TOKEN_CMD_API_SENSOR_ADD_HOT_SPOT' +
                        '", "TOKEN_PARAM_LEFT":"' + '189' +
                        '", "TOKEN_PARAM_TOP":"' + '4' +
                        '", "TOKEN_PARAM_WIDTH":"' + '49' +
                        '", "TOKEN_PARAM_HEIGHT":"' + '49' +
                        '" }';
                    break;
                case pdfDialoStartStates.sensorAddConfirmHotSpot:
                    addHotSpotState = addHotSpotStates.addConfirm;
                    message = '{ "TOKEN_TYPE":"TOKEN_TYPE_REQUEST", "TOKEN_CMD":"TOKEN_CMD_API_SENSOR_ADD_HOT_SPOT' +
                        '", "TOKEN_PARAM_LEFT":"' + '1043' +
                        '", "TOKEN_PARAM_TOP":"' + '4' +
                        '", "TOKEN_PARAM_WIDTH":"' + '49' +
                        '", "TOKEN_PARAM_HEIGHT":"' + '49' +
                        '" }';
                    break;
                case pdfDialoStartStates.displaySetTargetBackground:
                    setTargetState = setTargetStates.setPdf;
                    message = '{ "TOKEN_TYPE":"TOKEN_TYPE_REQUEST", "TOKEN_CMD":"TOKEN_CMD_API_DISPLAY_SET_TARGET' +
                        '", "TOKEN_PARAM_TARGET":"' + '1' +
                        '" }';
                    break;
                case pdfDialoStartStates.displaySetPdfBackgroundImage:
                    var pdf_dialog_background_image_canvas = document.createElement("canvas");
                    pdf_dialog_background_image_canvas.width = sigcanvas.width;
                    pdf_dialog_background_image_canvas.height = parseInt(height_of_all_pdf_pages, 10) + pdf_pages_separator * (pdf_page_count - 1);
                    var pdf_dialog_background_image_context = pdf_dialog_background_image_canvas.getContext("2d");
                    pdf_dialog_background_image_context.fillStyle = "#555555";
                    pdf_dialog_background_image_context.fillRect(0, 0, pdf_dialog_background_image_canvas.width, pdf_dialog_background_image_canvas.height);
                    var dataURL = pdf_dialog_background_image_canvas.toDataURL("image/png");
                    var pdf_dialog_background_image = dataURL.replace(/^data:image\/(png|jpg);base64,/, "");
                    displaySetImageState = displaySetImageStates.displaySetPdf;
                    message = '{ "TOKEN_TYPE":"TOKEN_TYPE_REQUEST", "TOKEN_CMD":"TOKEN_CMD_API_DISPLAY_SET_IMAGE' +
                        '", "TOKEN_PARAM_X_POS":"' + '0' +
                        '", "TOKEN_PARAM_Y_POS":"' + pdf_dialog_toolbar_height +
                        '", "TOKEN_PARAM_BITMAP":"' + pdf_dialog_background_image +
                        '" }';
                    break;
                case pdfDialoStartStates.displaySetPDF:
                    var x_pos = 0;
                    pdf_page_index = 1;
                    x_pos = Math.round((sigcanvas.width - pdf_page_sizes[pdf_page_index - 1].width) / 2);
                    y_pos = pdf_dialog_toolbar_height;
                    message = '{ "TOKEN_TYPE":"TOKEN_TYPE_REQUEST", "TOKEN_CMD":"TOKEN_CMD_API_DISPLAY_SET_PDF' +
                        '", "TOKEN_PARAM_X_POS":"' + x_pos +
                        '", "TOKEN_PARAM_Y_POS":"' + y_pos +
                        '", "TOKEN_PARAM_PAGE":"' + pdf_page_index +
                        '", "TOKEN_PARAM_SCALE":"' + pdf_scale +
                        '", "TOKEN_PARAM_OPTIONS":"' + '1' +
                        '" }';
                    break;
                case pdfDialoStartStates.displaySetOverlayRect:
                    message = '{ "TOKEN_TYPE":"TOKEN_TYPE_REQUEST", "TOKEN_CMD":"TOKEN_CMD_API_DISPLAY_SET_OVERLAY_RECT' +
                        '", "TOKEN_PARAM_LEFT":"' + '0' +
                        '", "TOKEN_PARAM_TOP":"' + '0' +
                        '", "TOKEN_PARAM_WIDTH":"' + sigcanvas.width +
                        '", "TOKEN_PARAM_HEIGHT":"' + pdf_dialog_toolbar_height +
                        '" }';
                    break;
                case pdfDialoStartStates.displaySetTargetForeground:
                    setTargetState = setTargetStates.setTargetForeground;
                    message = '{ "TOKEN_TYPE":"TOKEN_TYPE_REQUEST", "TOKEN_CMD":"TOKEN_CMD_API_DISPLAY_SET_TARGET' +
                        '", "TOKEN_PARAM_TARGET":"' + '0' +
                        '" }';
                    break;
                case pdfDialoStartStates.displaySetImageFromStoreBackground:
                    message = '{ "TOKEN_TYPE":"TOKEN_TYPE_REQUEST", "TOKEN_CMD":"TOKEN_CMD_API_DISPLAY_SET_IMAGE_FROM_STORE' +
                        '", "TOKEN_PARAM_STORE_ID":"' + '1' +
                        '" }';
                    break;
                case pdfDialoStartStates.sensorSetScrollArea:
                    message = '{ "TOKEN_TYPE":"TOKEN_TYPE_REQUEST", "TOKEN_CMD":"TOKEN_CMD_API_SENSOR_SET_SCROLL_AREA' +
                        '", "TOKEN_PARAM_LEFT":"' + '0' +
                        '", "TOKEN_PARAM_TOP":"' + '0' +
                        '", "TOKEN_PARAM_WIDTH":"' + sigcanvas.width +
                        '", "TOKEN_PARAM_HEIGHT":"' + (parseInt(height_of_all_pdf_pages, 10) + pdf_pages_separator * (pdf_page_count - 1) + pdf_dialog_toolbar_height) +
                        '" }';
                    break;
                case pdfDialoStartStates.sensorSetPenScrollingEnabledTrue:
                    sensor_pen_scrolling_enabled = true;
                    message = '{ "TOKEN_TYPE":"TOKEN_TYPE_REQUEST", "TOKEN_CMD":"TOKEN_CMD_API_SENSOR_SET_PEN_SCROLLING_ENABLED' +
                        '", "TOKEN_PARAM_ENABLE":"' + 'TRUE' +
                        '" }';
                    break;
                default:
                    alert("invalid pdfDialoStartState");
                    close_pad();
                    return;
            }

            signoPADAPIWeb.send(message);
            logMessage(message);
        }

        function api_pdf_get_width() {
            var message;

            pdf_page_index++;
            message = '{ "TOKEN_TYPE":"TOKEN_TYPE_REQUEST", "TOKEN_CMD":"TOKEN_CMD_API_PDF_GET_WIDTH' +
                '", "TOKEN_PARAM_PAGE":"' + pdf_page_index +
                '", "TOKEN_PARAM_UNIT":"' + '0' +
                '" }';
            signoPADAPIWeb.send(message);
            logMessage(message);
        }

        function api_display_set_pdf() {
            var message;
            var x_pos = 0;
            pdf_page_index++;
            x_pos = Math.round((sigcanvas.width - pdf_page_sizes[pdf_page_index - 1].width) / 2);
            y_pos += Math.round(pdf_page_sizes[pdf_page_index - 2].height + pdf_pages_separator);
            message = '{ "TOKEN_TYPE":"TOKEN_TYPE_REQUEST", "TOKEN_CMD":"TOKEN_CMD_API_DISPLAY_SET_PDF' +
                '", "TOKEN_PARAM_X_POS":"' + x_pos +
                '", "TOKEN_PARAM_Y_POS":"' + y_pos +
                '", "TOKEN_PARAM_PAGE":"' + pdf_page_index +
                '", "TOKEN_PARAM_SCALE":"' + pdf_scale +
                '", "TOKEN_PARAM_OPTIONS":"' + '1' +
                '" }';
            signoPADAPIWeb.send(message);
            logMessage(message);
        }

        function api_pdf_dialog_start_responses(obj) {
            if (obj.TOKEN_CMD_ORIGIN == "TOKEN_CMD_API_PDF_LOAD") {

                var ret = obj.TOKEN_PARAM_RETURN_CODE;
                if (ret < 0) {
                    alert("Failed to load pdf. Reason: " + obj.TOKEN_PARAM_ERROR_DESCRIPTION);
                    close_pad();
                    return;
                }

                pdfDialoStartState = pdfDialoStartStates.pdfGetPageCount;
                api_pdf_dialog_start();
            } else if (obj.TOKEN_CMD_ORIGIN == "TOKEN_CMD_API_PDF_GET_PAGE_COUNT") {

                var ret = obj.TOKEN_PARAM_RETURN_CODE;
                if (ret < 0) {
                    alert("Failed to get pdf page count. Reason: " + obj.TOKEN_PARAM_ERROR_DESCRIPTION);
                    close_pad();
                    return;
                }

                pdf_page_count = ret;

                pdfDialoStartState = pdfDialoStartStates.pdfGetWidth;
                api_pdf_dialog_start();
            } else if (obj.TOKEN_CMD_ORIGIN == "TOKEN_CMD_API_PDF_GET_WIDTH") {

                var ret = obj.TOKEN_PARAM_RETURN_CODE;
                if (ret < 0) {
                    alert("Failed to get pdf page width. Reason: " + obj.TOKEN_PARAM_ERROR_DESCRIPTION);
                    close_pad();
                    return;
                }

                pdf_page_width = parseFloat(ret);

                pdfDialoStartState = pdfDialoStartStates.pdfGetHeight;
                api_pdf_dialog_start();
            } else if (obj.TOKEN_CMD_ORIGIN == "TOKEN_CMD_API_PDF_GET_HEIGHT") {

                var ret = obj.TOKEN_PARAM_RETURN_CODE;
                if (ret < 0) {
                    alert("Failed to get pdf page height. Reason: " + obj.TOKEN_PARAM_ERROR_DESCRIPTION);
                    close_pad();
                    return;
                }

                pdf_page_height = parseFloat(ret);

                pdf_page_sizes.push(new pdf_page_size(pdf_page_width, pdf_page_height));

                if (pdf_page_index < pdf_page_count) {
                    api_pdf_get_width();
                } else {
                    var max_width_of_all_pdf_pages = 0.0;

                    for (var i = 0; i < pdf_page_sizes.length; i++) {
                        if (max_width_of_all_pdf_pages < pdf_page_sizes[i].width) {
                            max_width_of_all_pdf_pages = pdf_page_sizes[i].width;
                        }
                    }

                    pdf_scale = sigcanvas.width / (max_width_of_all_pdf_pages + 2 * pdf_pages_separator);

                    for (var i = 0; i < pdf_page_sizes.length; i++) {
                        pdf_page_sizes[i].width = pdf_page_sizes[i].width * pdf_scale;
                        pdf_page_sizes[i].height = pdf_page_sizes[i].height * pdf_scale;
                    }

                    for (var i = 0; i < pdf_page_sizes.length; i++) {
                        height_of_all_pdf_pages += pdf_page_sizes[i].height;
                    }

                    pdfDialoStartState = pdfDialoStartStates.displaySetTargetOverlay;
                    api_pdf_dialog_start();
                }
            } else if (obj.TOKEN_CMD_ORIGIN == "TOKEN_CMD_API_DISPLAY_SET_TARGET") {

                var ret = obj.TOKEN_PARAM_RETURN_CODE;
                if (ret < 0) {
                    alert("Failed to set display target. Reason: " + obj.TOKEN_PARAM_ERROR_DESCRIPTION);
                    close_pad();
                    return;
                }

                if (dialogType == dialogTypes.pdf) {
                    switch (setTargetState) {
                        case setTargetStates.setPdfToolbar:
                            pdfDialoStartState = pdfDialoStartStates.displaySetToolbarImage;
                            api_pdf_dialog_start();
                            break;

                        case setTargetStates.setPdf:
                            pdfDialoStartState = pdfDialoStartStates.displaySetPdfBackgroundImage;
                            api_pdf_dialog_start();
                            break;

                        case setTargetStates.setTargetForeground:
                            pdfDialoStartState = pdfDialoStartStates.displaySetImageFromStoreBackground;
                            api_pdf_dialog_start();
                            break;

                        default:
                            alert("invalid setTargetState");
                            close_pad();
                            return;
                    }
                } else if (dialogType == dialogTypes.signatur) {

                } else {
                    alert("invalid dialogType");
                    close_pad();
                    return;
                }
            } else if (obj.TOKEN_CMD_ORIGIN == "TOKEN_CMD_API_DISPLAY_SET_IMAGE") {

                var ret = obj.TOKEN_PARAM_RETURN_CODE;
                if (ret < 0) {
                    alert("Failed to set background image. Reason: " + obj.TOKEN_PARAM_ERROR_DESCRIPTION);
                    close_pad();
                    return;
                }

                if (dialogType == dialogTypes.pdf) {
                    switch (displaySetImageState) {
                        case displaySetImageStates.sensorAddHotSpot:
                            pdfDialoStartState = pdfDialoStartStates.sensorAddCancelHotSpot;
                            api_pdf_dialog_start();
                            break;

                        case displaySetImageStates.displaySetPdf:
                            pdfDialoStartState = pdfDialoStartStates.displaySetPDF
                            api_pdf_dialog_start();
                            break;

                        default:
                            alert("invalid displaySetImageState");
                            close_pad();
                            return;
                    }
                } else if (dialogType == dialogTypes.signatur) {

                } else {
                    alert("invalid dialogType");
                    close_pad();
                    return;
                }
            } else if (obj.TOKEN_CMD_ORIGIN == "TOKEN_CMD_API_SENSOR_ADD_HOT_SPOT") {

                var ret = obj.TOKEN_PARAM_RETURN_CODE;
                if (ret < 0) {
                    alert("Failed to add button. Reason: " + obj.TOKEN_PARAM_ERROR_DESCRIPTION);
                    close_pad();
                    return;
                }

                if (dialogType == dialogTypes.pdf) {
                    switch (addHotSpotState) {
                        case addHotSpotStates.addCancel:
                            cancelButton = ret;
                            pdfDialoStartState = pdfDialoStartStates.sensorAddConfirmHotSpot;
                            api_pdf_dialog_start();
                            break;

                        case addHotSpotStates.addConfirm:
                            confirmButton = ret;
                            pdfDialoStartState = pdfDialoStartStates.displaySetTargetBackground
                            api_pdf_dialog_start();
                            break;

                        default:
                            alert("invalid addHotSpotState");
                            close_pad();
                            return;
                    }
                } else if (dialogType == dialogTypes.signatur) {

                } else {
                    alert("invalid dialogType");
                    close_pad();
                    return;
                }
            } else if (obj.TOKEN_CMD_ORIGIN == "TOKEN_CMD_API_DISPLAY_SET_PDF") {

                var ret = obj.TOKEN_PARAM_RETURN_CODE;
                if (ret < 0) {
                    alert("Failed to set pdf on display. Reason: " + obj.TOKEN_PARAM_ERROR_DESCRIPTION);
                    close_pad();
                    return;
                }

                if (pdf_page_index < pdf_page_sizes.length) {
                    api_display_set_pdf();
                } else {
                    pdfDialoStartState = pdfDialoStartStates.displaySetOverlayRect;
                    api_pdf_dialog_start();
                }
            } else if (obj.TOKEN_CMD_ORIGIN == "TOKEN_CMD_API_DISPLAY_SET_OVERLAY_RECT") {

                var ret = obj.TOKEN_PARAM_RETURN_CODE;
                if (ret < 0) {
                    alert("Failed to set overlay rect on display. Reason: " + obj.TOKEN_PARAM_ERROR_DESCRIPTION);
                    close_pad();
                    return;
                }

                pdfDialoStartState = pdfDialoStartStates.displaySetTargetForeground;
                api_pdf_dialog_start();
            } else if (obj.TOKEN_CMD_ORIGIN == "TOKEN_CMD_API_DISPLAY_SET_IMAGE_FROM_STORE") {

                var ret = obj.TOKEN_PARAM_RETURN_CODE;
                if (ret < 0) {
                    alert("Failed to switch buffers. Reason: " + obj.TOKEN_PARAM_ERROR_DESCRIPTION);
                    close_pad();
                    return;
                }

                if (dialogType == dialogTypes.pdf) {
                    pdfDialoStartState = pdfDialoStartStates.sensorSetScrollArea;
                    api_pdf_dialog_start();
                } else if (dialogType == dialogTypes.signatur) {

                } else {
                    alert("invalid dialogType");
                    close_pad();
                    return;
                }
            } else if (obj.TOKEN_CMD_ORIGIN == "TOKEN_CMD_API_SENSOR_SET_SCROLL_AREA") {

                var ret = obj.TOKEN_PARAM_RETURN_CODE;
                if (ret < 0) {
                    alert("Failed to set scroll area on sensor. Reason: " + obj.TOKEN_PARAM_ERROR_DESCRIPTION);
                    close_pad();
                    return;
                }

                pdfDialoStartState = pdfDialoStartStates.sensorSetPenScrollingEnabledTrue;
                api_pdf_dialog_start();
            } else if (obj.TOKEN_CMD_ORIGIN == "TOKEN_CMD_API_SENSOR_SET_PEN_SCROLLING_ENABLED") {

                var ret = obj.TOKEN_PARAM_RETURN_CODE;
                if (ret < 0) {
                    alert("Failed to set pen scrolling enabled on sensor. Reason: " + obj.TOKEN_PARAM_ERROR_DESCRIPTION);
                    close_pad();
                    return;
                }

                if (sensor_pen_scrolling_enabled) {

                } else {

                }
            } else {

            }
        }

        function api_pdf_dialog_end() {
            var message;

            switch (pdfDialoEndState) {
                case pdfDialoEndStates.sensorSetPenScrollingEnabledFalse:
                    sensor_pen_scrolling_enabled = false;
                    message = '{ "TOKEN_TYPE":"TOKEN_TYPE_REQUEST", "TOKEN_CMD":"TOKEN_CMD_API_SENSOR_SET_PEN_SCROLLING_ENABLED' +
                        '", "TOKEN_PARAM_ENABLE":"' + 'FALSE' +
                        '" }';
                    break;
                case pdfDialoEndStates.sensorClearHotSpots:
                    message = '{ "TOKEN_TYPE":"TOKEN_TYPE_REQUEST", "TOKEN_CMD":"TOKEN_CMD_API_SENSOR_CLEAR_HOT_SPOTS' +
                        '" }';
                    break;
                case pdfDialoEndStates.displayErase:
                    message = '{ "TOKEN_TYPE":"TOKEN_TYPE_REQUEST", "TOKEN_CMD":"TOKEN_CMD_API_DISPLAY_ERASE' +
                        '" }';
                    break;
                default:
                    alert("invalid pdfDialoEndStates");
                    close_pad();
                    return;
            }

            signoPADAPIWeb.send(message);
            logMessage(message);
        }

        function api_pdf_dialog_end_responses(obj) {
            if (obj.TOKEN_CMD_ORIGIN == "TOKEN_CMD_API_SENSOR_SET_PEN_SCROLLING_ENABLED") {

                var ret = obj.TOKEN_PARAM_RETURN_CODE;
                if (ret < 0) {
                    alert("Failed to set pen scrolling enabled on sensor. Reason: " + obj.TOKEN_PARAM_ERROR_DESCRIPTION);
                    close_pad();
                    return;
                }

                if (sensor_pen_scrolling_enabled) {

                } else {
                    pdfDialoEndState = pdfDialoEndStates.sensorClearHotSpots;
                    api_pdf_dialog_end();
                }
            } else if (obj.TOKEN_CMD_ORIGIN == "TOKEN_CMD_API_SENSOR_CLEAR_HOT_SPOTS") {

                var ret = obj.TOKEN_PARAM_RETURN_CODE;
                if (ret < 0) {
                    alert("Failed to clear the hot spots on sensor. Reason: " + obj.TOKEN_PARAM_ERROR_DESCRIPTION);
                    close_pad();
                    return;
                }

                cancelButton = -1;
                retryButton = -1;
                confirmButton = -1;

                pdfDialoEndState = pdfDialoEndStates.displayErase;
                api_pdf_dialog_end();
            } else if (obj.TOKEN_CMD_ORIGIN == "TOKEN_CMD_API_DISPLAY_ERASE") {

                var ret = obj.TOKEN_PARAM_RETURN_CODE;
                if (ret < 0) {
                    alert("Failed to erase the display. Reason: " + obj.TOKEN_PARAM_ERROR_DESCRIPTION);
                    close_pad();
                    return;
                }

                if (supportsRSA) {
                    if (canStoreEncryptKey) {
                        if (encryption_cert_only_when_empty == "TRUE") {
                            api_encryption_cert_dochash();
                        } else {
                            encryptionCertDochashState = encryptionCertDochashStates.setEncryptionCertPw;
                            api_encryption_cert_dochash();
                        }
                    } else {
                        encryptionCertDochashState = encryptionCertDochashStates.setDochash;
                        api_encryption_cert_dochash();
                    }
                } else {
                    api_signature_start();
                }
            } else {

            }
        }

        function api_encryption_cert_dochash() {
            var message;
            var hashalgo;
            var options;
            var device_password;

            switch (encryptionCertDochashState) {
                case encryptionCertDochashStates.getEncryptionCertID:
                    getEncryptionCertIDState = getEncryptionCertIDStates.encryptionCertDochash;
                    message = '{ "TOKEN_TYPE":"TOKEN_TYPE_REQUEST", "TOKEN_CMD":"TOKEN_CMD_API_RSA_GET_ENCRYPTION_CERT_ID' +
                        '" }';
                    break;
                case encryptionCertDochashStates.setEncryptionCertPw:
                    device_password = "";
                    message = '{ "TOKEN_TYPE":"TOKEN_TYPE_REQUEST", "TOKEN_CMD":"TOKEN_CMD_API_RSA_SET_ENCRYPTION_CERT_PW' +
                        '", "TOKEN_PARAM_ENCRYPTION_CERT":"' + encryption_cert +
                        '", "TOKEN_PARAM_DEVICE_PASSWORD":"' + device_password +
                        '" }';
                    break;
                case encryptionCertDochashStates.setDochash:
                    switch (docHash_type) {
                        case docHashes.kSha256:
                            hashalgo = "SHA256";
                            api_dochash = sha256_dochash;
                            break;
                        default:
                            alert("unknown doc hash");
                            return;
                    }
                    options = 0;
                    message = '{ "TOKEN_TYPE":"TOKEN_TYPE_REQUEST", "TOKEN_CMD":"TOKEN_CMD_API_RSA_SET_HASH' +
                        '", "TOKEN_PARAM_HASH":"' + api_dochash +
                        '", "TOKEN_PARAM_HASHALGO":"' + hashalgo +
                        '", "TOKEN_PARAM_OPTIONS":"' + options +
                        '" }';
                    break;
                default:
                    alert("invalid encryptionCertDochashState");
                    close_pad();
                    return;
            }
            signoPADAPIWeb.send(message);
            logMessage(message);
        }

        function api_encryption_cert_dochash_responses(obj) {
            var encryption_cert_id;
            if (obj.TOKEN_CMD_ORIGIN == "TOKEN_CMD_API_RSA_GET_ENCRYPTION_CERT_ID") {

                var ret = obj.TOKEN_PARAM_RETURN_CODE;
                if (ret < 0 && ret != -28  ) {
                    alert("Failed to get encryption cert id. Reason: " + obj.TOKEN_PARAM_ERROR_DESCRIPTION);
                    close_pad();
                    return;
                }

                switch (getEncryptionCertIDState) {
                    case getEncryptionCertIDStates.encryptionCertDochash:
                        stpad_error_rsanokey = false;

                        if (ret == -28  ) {
                            stpad_error_rsanokey = true;

                            encryptionCertDochashState = encryptionCertDochashStates.setEncryptionCertPw;
                            api_encryption_cert_dochash();
                        } else {
                            encryption_cert_id = obj.TOKEN_PARAM_ENCRYPTION_CERT_ID;
                            document.getElementById("biometryCertID_0").value = encryption_cert_id;

                            encryptionCertDochashState = encryptionCertDochashStates.setDochash;
                            api_encryption_cert_dochash();
                        }
                        break;

                    case getEncryptionCertIDStates.rsaSignGetSignData:

                        break;

                    default:
                        alert("invalid getEncryptionCertIDState");
                        close_pad();
                        return;
                }
            } else if (obj.TOKEN_CMD_ORIGIN == "TOKEN_CMD_API_RSA_SET_ENCRYPTION_CERT_PW") {

                var ret = obj.TOKEN_PARAM_RETURN_CODE;
                if (ret < 0) {
                    alert("Failed to set encryption cert pw. Reason: " + obj.TOKEN_PARAM_ERROR_DESCRIPTION);
                    close_pad();
                    return;
                }

                if (encryption_cert_only_when_empty == "FALSE" || stpad_error_rsanokey  ) {
                    document.getElementById("biometryCertID_0").value = "The biometry certificate has been added.";
                }

                encryptionCertDochashState = encryptionCertDochashStates.setDochash;
                api_encryption_cert_dochash();
            } else if (obj.TOKEN_CMD_ORIGIN == "TOKEN_CMD_API_RSA_SET_HASH") {

                var ret = obj.TOKEN_PARAM_RETURN_CODE;
                if (ret < 0) {
                    alert("Failed to set api dochash. Reason: " + obj.TOKEN_PARAM_ERROR_DESCRIPTION);
                    close_pad();
                    return;
                }

                api_signature_start()
            } else {

            }
        }

        function api_signature_start() {
            var message;

            dialogType = dialogTypes.signatur;

            switch (preparationState) {
                case preparationStates.setDisplayRotation:
                    message = '{ "TOKEN_TYPE":"TOKEN_TYPE_REQUEST", "TOKEN_CMD":"TOKEN_CMD_API_DISPLAY_SET_ROTATION", "TOKEN_PARAM_ROTATION":"0" }';
                    break;

                case preparationStates.getDisplayRotation:
                    message = '{ "TOKEN_TYPE":"TOKEN_TYPE_REQUEST", "TOKEN_CMD":"TOKEN_CMD_API_DISPLAY_GET_ROTATION" }';
                    break;

                case preparationStates.setBackgroundTarget:
                    message = '{ "TOKEN_TYPE":"TOKEN_TYPE_REQUEST", "TOKEN_CMD":"TOKEN_CMD_API_DISPLAY_SET_TARGET", "TOKEN_PARAM_TARGET":"1" }';
                    break;

                case preparationStates.setBackgroundImage:
                    message = '{ "TOKEN_TYPE":"TOKEN_TYPE_REQUEST", "TOKEN_CMD":"TOKEN_CMD_API_DISPLAY_SET_IMAGE", "TOKEN_PARAM_X_POS":"0", "TOKEN_PARAM_Y_POS":"0", "TOKEN_PARAM_BITMAP":"' + backgroundImage + '" }';
                    break;

                case preparationStates.setCancelButton:
                case preparationStates.setRetryButton:
                case preparationStates.setConfirmButton:
                    switch (preparationState) {
                        case preparationStates.setCancelButton:
                            buttonDiff = sigcanvas.width / 3;
                            buttonLeft = (buttonDiff - buttonSize) / 2;
                            break;

                        case preparationStates.setRetryButton:
                        case preparationStates.setConfirmButton:
                            buttonLeft = buttonLeft + buttonDiff;
                            break;

                        default:
                            alert("invalid preparationState");
                            close_pad();
                            return;
                    }
                    message = '{ "TOKEN_TYPE":"TOKEN_TYPE_REQUEST", "TOKEN_CMD":"TOKEN_CMD_API_SENSOR_ADD_HOT_SPOT", "TOKEN_PARAM_LEFT":"' + Math.round(buttonLeft) + '", "TOKEN_PARAM_TOP":"' + buttonTop + '", "TOKEN_PARAM_WIDTH":"' + buttonSize + '", "TOKEN_PARAM_HEIGHT":"' + buttonSize + '" }';
                    break;

                case preparationStates.setSignRect:
                    var top;
                    switch (padType) {
                        case padTypes.sigmaUSB:
                        case padTypes.sigmaSerial:
                            top = 40;
                            break;

                        case padTypes.zetaUSB:
                        case padTypes.zetaSerial:
                            top = 40;
                            break;

                        case padTypes.omegaUSB:
                        case padTypes.omegaSerial:
                        case padTypes.gammaUSB:
                        case padTypes.gammaSerial:
                        case padTypes.deltaUSB:
                        case padTypes.deltaSerial:
                        case padTypes.deltaIP:
                            top = 56;
                            break;

                        case padTypes.alphaUSB:
                        case padTypes.alphaSerial:
                        case padTypes.alphaIP:
                            top = 100;
                            break;

                        default:
                            alert("unkown pad type");
                            return;
                    }
                    message = '{ "TOKEN_TYPE":"TOKEN_TYPE_REQUEST", "TOKEN_CMD":"TOKEN_CMD_API_SENSOR_SET_SIGN_RECT", "TOKEN_PARAM_LEFT":"0", "TOKEN_PARAM_TOP":"' + top + '", "TOKEN_PARAM_WIDTH":"0", "TOKEN_PARAM_HEIGHT":"0" }';
                    break;

                case preparationStates.setFieldName:
                    var left;
                    var top;
                    var width;
                    var height;
                    switch (padType) {
                        case padTypes.sigmaUSB:
                        case padTypes.sigmaSerial:
                            left = 15;
                            top = 43;
                            width = 285;
                            height = 18;
                            break;

                        case padTypes.zetaUSB:
                        case padTypes.zetaSerial:
                            left = 15;
                            top = 43;
                            width = 285;
                            height = 18;
                            break;

                        case padTypes.omegaUSB:
                        case padTypes.omegaSerial:
                            left = 40;
                            top = 86;
                            width = 570;
                            height = 40;
                            break;

                        case padTypes.gammaUSB:
                        case padTypes.gammaSerial:
                            left = 40;
                            top = 86;
                            width = 720;
                            height = 40;
                            break;

                        case padTypes.deltaUSB:
                        case padTypes.deltaSerial:
                        case padTypes.deltaIP:
                            left = 40;
                            top = 86;
                            width = 1200;
                            height = 50;
                            break;

                        case padTypes.alphaUSB:
                        case padTypes.alphaSerial:
                        case padTypes.alphaIP:
                            left = 20;
                            top = 120;
                            width = 730;
                            height = 30;
                            break;

                        default:
                            alert("unkown pad type");
                            return;
                    }
                    message = '{ "TOKEN_TYPE":"TOKEN_TYPE_REQUEST", "TOKEN_CMD":"TOKEN_CMD_API_DISPLAY_SET_TEXT_IN_RECT' +
                        '", "TOKEN_PARAM_LEFT":"' + left +
                        '", "TOKEN_PARAM_TOP":"' + top +
                        '", "TOKEN_PARAM_WIDTH":"' + width +
                        '", "TOKEN_PARAM_HEIGHT":"' + height +
                        '", "TOKEN_PARAM_ALIGNMENT":"3", "TOKEN_PARAM_TEXT":"Signature 1", "TOKEN_PARAM_OPTIONS":"0" }';
                    break;

                case preparationStates.setCustomText:
                    var left;
                    var top;
                    var width;
                    var height;
                    switch (padType) {
                        case padTypes.sigmaUSB:
                        case padTypes.sigmaSerial:
                            left = 15;
                            top = 110;
                            width = 265;
                            height = 18;
                            break;

                        case padTypes.zetaUSB:
                        case padTypes.zetaSerial:
                            left = 15;
                            top = 150;
                            width = 265;
                            height = 18;
                            break;

                        case padTypes.omegaUSB:
                        case padTypes.omegaSerial:
                            left = 40;
                            top = 350;
                            width = 520;
                            height = 40;
                            break;

                        case padTypes.gammaUSB:
                        case padTypes.gammaSerial:
                            left = 40;
                            top = 350;
                            width = 670;
                            height = 40;
                            break;

                        case padTypes.deltaUSB:
                        case padTypes.deltaSerial:
                        case padTypes.deltaIP:
                            left = 40;
                            top = 640;
                            width = 670;
                            height = 50;
                            break;

                        case padTypes.alphaUSB:
                        case padTypes.alphaSerial:
                        case padTypes.alphaIP:
                            left = 20;
                            top = 1316;
                            width = 730;
                            height = 30;
                            break;

                        default:
                            alert("unkown pad type");
                            return;
                    }
                    message = '{ "TOKEN_TYPE":"TOKEN_TYPE_REQUEST", "TOKEN_CMD":"TOKEN_CMD_API_DISPLAY_SET_TEXT_IN_RECT' +
                        '", "TOKEN_PARAM_LEFT":"' + left +
                        '", "TOKEN_PARAM_TOP":"' + top +
                        '", "TOKEN_PARAM_WIDTH":"' + width +
                        '", "TOKEN_PARAM_HEIGHT":"' + height +
                        '", "TOKEN_PARAM_ALIGNMENT":"3", "TOKEN_PARAM_TEXT":"Please sign!", "TOKEN_PARAM_OPTIONS":"0" }';
                    break;

                case preparationStates.setForegroundTarget:
                    message = '{ "TOKEN_TYPE":"TOKEN_TYPE_REQUEST", "TOKEN_CMD":"TOKEN_CMD_API_DISPLAY_SET_TARGET", "TOKEN_PARAM_TARGET":"0" }';
                    break;

                case preparationStates.switchBuffers:
                    message = '{ "TOKEN_TYPE":"TOKEN_TYPE_REQUEST", "TOKEN_CMD":"TOKEN_CMD_API_DISPLAY_SET_IMAGE_FROM_STORE", "TOKEN_PARAM_STORE_ID":"1" }';
                    break;

                case preparationStates.startSignature:
                    message = '{ "TOKEN_TYPE":"TOKEN_TYPE_REQUEST", "TOKEN_CMD":"TOKEN_CMD_API_SIGNATURE_START" }';
                    break;

                default:
                    alert("invalid preparationState");
                    close_pad();
                    return;
            }
            signoPADAPIWeb.send(message);
            logMessage(message);
        }

        function api_signature_start_responses(obj) {
            if (obj.TOKEN_CMD_ORIGIN == "TOKEN_CMD_API_DISPLAY_SET_ROTATION") {

                var ret = obj.TOKEN_PARAM_RETURN_CODE;
                if (ret < 0) {
                    alert("Failed to set background image. Reason: " + obj.TOKEN_PARAM_ERROR_DESCRIPTION);
                    close_pad();
                    return;
                }

                preparationState = preparationStates.getDisplayRotation;
                api_signature_start();
            } else if (obj.TOKEN_CMD_ORIGIN == "TOKEN_CMD_API_DISPLAY_GET_ROTATION") {
                var rotation = 0;

                var ret = obj.TOKEN_PARAM_RETURN_CODE;
                if (ret < 0) {
                    alert("Failed to set background image. Reason: " + obj.TOKEN_PARAM_ERROR_DESCRIPTION);
                    close_pad();
                    return;
                }

                rotation = obj.TOKEN_PARAM_RETURN_CODE;

                preparationState = preparationStates.setBackgroundTarget;
                api_signature_start();
            } else if (obj.TOKEN_CMD_ORIGIN == "TOKEN_CMD_API_DISPLAY_SET_TARGET") {

                var ret = obj.TOKEN_PARAM_RETURN_CODE;
                if (ret < 0) {
                    alert("Failed to set display target. Reason: " + obj.TOKEN_PARAM_ERROR_DESCRIPTION);
                    close_pad();
                    return;
                }

                if (dialogType == dialogTypes.signatur) {

                    switch (preparationState) {
                        case preparationStates.setBackgroundTarget:

                            preparationState = preparationStates.setBackgroundImage;
                            break;

                        case preparationStates.setForegroundTarget:

                            preparationState = preparationStates.switchBuffers;
                            break;

                        default:
                            alert("invalid preparationState");
                            close_pad();
                            return;
                    }

                    api_signature_start();
                } else if (dialogType == dialogTypes.pdf) {

                } else {
                    alert("invalid dialogType");
                    close_pad();
                    return;
                }
            } else if (obj.TOKEN_CMD_ORIGIN == "TOKEN_CMD_API_DISPLAY_SET_IMAGE") {

                var ret = obj.TOKEN_PARAM_RETURN_CODE;
                if (ret < 0) {
                    alert("Failed to set background image. Reason: " + obj.TOKEN_PARAM_ERROR_DESCRIPTION);
                    close_pad();
                    return;
                }

                if (dialogType == dialogTypes.signatur) {

                    preparationState = preparationStates.setCancelButton;
                    api_signature_start();
                } else if (dialogType == dialogTypes.pdf) {

                } else {
                    alert("invalid dialogType");
                    close_pad();
                    return;
                }
            } else if (obj.TOKEN_CMD_ORIGIN == "TOKEN_CMD_API_SENSOR_ADD_HOT_SPOT") {

                var ret = obj.TOKEN_PARAM_RETURN_CODE;
                if (ret < 0) {
                    alert("Failed to add button. Reason: " + obj.TOKEN_PARAM_ERROR_DESCRIPTION);
                    close_pad();
                    return;
                }

                if (dialogType == dialogTypes.signatur) {

                    switch (preparationState) {
                        case preparationStates.setCancelButton:
                            cancelButton = ret;

                            preparationState = preparationStates.setRetryButton;
                            break;

                        case preparationStates.setRetryButton:
                            retryButton = ret;

                            preparationState = preparationStates.setConfirmButton;
                            break;

                        case preparationStates.setConfirmButton:
                            confirmButton = ret;

                            preparationState = preparationStates.setSignRect;
                            break;

                        default:
                            alert("invalid preparationState");
                            close_pad();
                            return;
                    }

                    api_signature_start();
                } else if (dialogType == dialogTypes.pdf) {

                } else {
                    alert("invalid dialogType");
                    close_pad();
                    return;
                }
            } else if (obj.TOKEN_CMD_ORIGIN == "TOKEN_CMD_API_SENSOR_SET_SIGN_RECT") {

                var ret = obj.TOKEN_PARAM_RETURN_CODE;
                if (ret < 0) {
                    alert("Failed to set signature rectangle. Reason: " + obj.TOKEN_PARAM_ERROR_DESCRIPTION);
                    close_pad();
                    return;
                }

                preparationState = preparationStates.setFieldName;
                api_signature_start();
            } else if (obj.TOKEN_CMD_ORIGIN == "TOKEN_CMD_API_DISPLAY_SET_TEXT_IN_RECT") {

                var ret = obj.TOKEN_PARAM_RETURN_CODE;
                if (ret < 0) {
                    alert("Failed to set text. Reason: " + obj.TOKEN_PARAM_ERROR_DESCRIPTION);
                    close_pad();
                    return;
                }

                switch (preparationState) {
                    case preparationStates.setFieldName:

                        preparationState = preparationStates.setCustomText;
                        break;

                    case preparationStates.setCustomText:

                        preparationState = preparationStates.setForegroundTarget;
                        break;

                    default:
                        alert("invalid preparationState");
                        close_pad();
                        return;
                }

                api_signature_start();
            } else if (obj.TOKEN_CMD_ORIGIN == "TOKEN_CMD_API_DISPLAY_SET_IMAGE_FROM_STORE") {

                var ret = obj.TOKEN_PARAM_RETURN_CODE;
                if (ret < 0) {
                    alert("Failed to switch buffers. Reason: " + obj.TOKEN_PARAM_ERROR_DESCRIPTION);
                    close_pad();
                    return;
                }

                if (dialogType == dialogTypes.signatur) {

                    preparationState = preparationStates.startSignature;
                    api_signature_start();
                } else if (dialogType == dialogTypes.pdf) {

                } else {
                    alert("invalid dialogType");
                    close_pad();
                    return;
                }
            } else if (obj.TOKEN_CMD_ORIGIN == "TOKEN_CMD_API_SIGNATURE_START") {

                var ret = obj.TOKEN_PARAM_RETURN_CODE;
                if (ret < 0) {
                    alert("Failed to start signing process. Reason: " + obj.TOKEN_PARAM_ERROR_DESCRIPTION);
                    close_pad();
                    return;
                }
            } else {

            }
        }

        function getBackgroundImage(padName) {
            var img = new Image();
            img.setAttribute('crossOrigin', 'anonymous');
            img.onload = function() {
                var sigcanvas = document.createElement("canvas");
                sigcanvas.width = this.width;
                sigcanvas.height = this.height;

                var ctx = sigcanvas.getContext("2d");
                ctx.drawImage(this, 0, 0);

                var dataURL = sigcanvas.toDataURL("image/png");
                backgroundImage = dataURL.replace(/^data:image\/(png|jpg);base64,/, "");
            };
            var element = document.getElementById(padName);
            img.src = element.src;
        }

        function getReadableType(intTypeNumber) {
            switch (intTypeNumber) {
                case padTypes.sigmaUSB:
                    return "Sigma USB";
                case padTypes.sigmaSerial:
                    return "Sigma serial";
                case padTypes.zetaUSB:
                    return "Zeta USB";
                case padTypes.zetaSerial:
                    return "Zeta serial";
                case padTypes.omegaUSB:
                    return "Omega USB";
                case padTypes.omegaSerial:
                    return "Omega serial";
                case padTypes.gammaUSB:
                    return "Gamma USB";
                case padTypes.gammaSerial:
                    return "Gamma serial";
                case padTypes.deltaUSB:
                    return "Delta USB";
                case padTypes.deltaSerial:
                    return "Delta serial";
                case padTypes.deltaIP:
                    return "Delta IP";
                case padTypes.alphaUSB:
                    return "Alpha USB";
                case padTypes.alphaSerial:
                    return "Alpha serial";
                case padTypes.alphaIP:
                    return "Alpha IP";
                default:
                    return "Unknown";
            }
        }

        function clearSignature() {
            document.getElementById("Signature_0").src = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAgY0hSTQAAeiYAAICEAAD6AAAAgOgAAHUwAADqYAAAOpgAABdwnLpRPAAAAAlwSFlzAAAOwwAADsMBx2+oZAAAABp0RVh0U29mdHdhcmUAUGFpbnQuTkVUIHYzLjUuMTAw9HKhAAAADElEQVQYV2P4//8/AAX+Av6nNYGEAAAAAElFTkSuQmCC";
            document.getElementById("SignData_0").value = "";
            document.getElementById("RsaSignature_0").value = "";
            document.getElementById("Signature_b64_0").value = "";
        }

        function get_server_version() {
            var message;

            message = '{ "TOKEN_TYPE":"TOKEN_TYPE_REQUEST", "TOKEN_CMD":"TOKEN_CMD_GET_SERVER_VERSION" }';

            signoPADAPIWeb.send(message);

            console.log("Server version request sent successfully");
            logMessage(message);
        }

        function get_server_version_response(obj) {
            if (obj.TOKEN_CMD_ORIGIN == "TOKEN_CMD_GET_SERVER_VERSION") {

                var ret = obj.TOKEN_PARAM_RETURN_CODE;
                if (ret < 0) {
                    alert("The get server version failed. Reason: " + obj.TOKEN_PARAM_ERROR_DESCRIPTION);
                    os = OS_WINDOWS;
                    return;
                }

                if (obj.TOKEN_PARAM_OS == null) {
                    alert("The get server version failed. Reason: TOKEN_PARAM_OS == null");
                    os = OS_WINDOWS;
                    return;
                }

                os = obj.TOKEN_PARAM_OS;

                set_states_of_ui_elements();
            } else {

            }
        }

        function set_states_of_ui_elements() {
            var mln = "Default";
            var pctln = document.getElementById("PadConnectionTypeList");
            var cbse = document.getElementById("check_boxes_selectedElements");

            if (os == OS_LINUX) {
                mln.disabled = true;
                pctln.disabled = true;
                cbse.disabled = true;
            } else if (os == OS_WINDOWS) {

            } else {

            }
        }

        function clearArray(array) {
            while (array.length) {
                array.pop();
            }
        }

        function resetStates() {
            searchState = searchStates.setPadType;
            openState = openStates.openPad;
            preparationState = preparationStates.setDisplayRotation;
            pdfDialoStartState = pdfDialoStartStates.pdfLoad;
            pdfDialoEndState = pdfDialoEndStates.sensorSetPenScrollingEnabledFalse;
            setTargetState = setTargetStates.setPdfToolbar;
            addHotSpotState = addHotSpotStates.addCancel;
            displaySetImageState = displaySetImageStates.sensorAddHotSpot;
            encryptionCertDochashState = encryptionCertDochashStates.getEncryptionCertID;
            rsaSignGetSignDataState = rsaSignGetSignDataStates.rsaSign;
            getEncryptionCertIDState = getEncryptionCertIDStates.encryptionCertDochash;
        }

        function resetUserInterface() {

            document.getElementById("PadType_0").value = "";
            document.getElementById("SerialNumber_0").value = "";
            document.getElementById("FirmwareVersion_0").value = "";
            document.getElementById("RSASupport_0").value = "";
            document.getElementById("biometryCertID_0").value = "";
            document.getElementById("RSAScheme_0").value = "";
            document.getElementById("signatureCert_0").value = "";

            var ctx = sigcanvas.getContext("2d");
            ctx.clearRect(0, 0, sigcanvas.width, sigcanvas.height);
            document.getElementById("Signature_0").src = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAgY0hSTQAAeiYAAICEAAD6AAAAgOgAAHUwAADqYAAAOpgAABdwnLpRPAAAAAlwSFlzAAAOwwAADsMBx2+oZAAAABp0RVh0U29mdHdhcmUAUGFpbnQuTkVUIHYzLjUuMTAw9HKhAAAADElEQVQYV2P4//8/AAX+Av6nNYGEAAAAAElFTkSuQmCC";
            document.getElementById("SignData_0").value = "";
            document.getElementById("RsaSignature_0").value = "";
            document.getElementById("Signature_b64_0").value = "";
        }

        function onMessage(event) {

            logMessage(event.data);

            var obj = JSON.parse(event.data);

            if (obj.TOKEN_TYPE == "TOKEN_TYPE_SEND") {

                switch (obj.TOKEN_CMD) {
                    case "TOKEN_CMD_SELECTION_CONFIRM":

                        selection_confirm_send();
                        break;
                    case "TOKEN_CMD_SELECTION_CANCEL":

                        selection_cancel_send();
                        break;
                    case "TOKEN_CMD_SIGNATURE_CONFIRM":

                        signature_confirm_send();
                        break;
                    case "TOKEN_CMD_SIGNATURE_RETRY":

                        signature_retry_send();
                        break;
                    case "TOKEN_CMD_SIGNATURE_CANCEL":

                        signature_cancel_send();
                        break;
                    case "TOKEN_CMD_SIGNATURE_POINT":

                        signature_point_send(obj.TOKEN_PARAM_POINT.x, obj.TOKEN_PARAM_POINT.y, obj.TOKEN_PARAM_POINT.p)
                        break;
                    case "TOKEN_CMD_DISCONNECT":

                        disconnect_send(obj.TOKEN_PARAM_PAD_INDEX)
                        break;
                    case "TOKEN_CMD_ERROR":

                        error_send(obj.TOKEN_PARAM_ERROR_CONTEXT, obj.TOKEN_PARAM_RETURN_CODE, obj.TOKEN_PARAM_ERROR_DESCRIPTION);
                        break;
                    case "TOKEN_CMD_API_SENSOR_HOT_SPOT_PRESSED":

                        api_sensor_hot_spot_pressed_send(obj.TOKEN_PARAM_HOTSPOT_ID);
                        break;
                    case "TOKEN_CMD_API_DISPLAY_SCROLL_POS_CHANGED":

                        api_display_scroll_pos_changed_send(obj.TOKEN_PARAM_X_POS, obj.TOKEN_PARAM_Y_POS);
                        break;
                    default:
                        alert("Unknown token for send events. Token: " + obj.TOKEN_CMD);
                        break;
                }
            } else if (obj.TOKEN_TYPE == "TOKEN_TYPE_RESPONSE") {

                switch (obj.TOKEN_CMD_ORIGIN) {

                    case "TOKEN_CMD_GET_SERVER_VERSION":
                        get_server_version_response(obj);
                        break;

                    case "TOKEN_CMD_SEARCH_FOR_PADS":
                        search_for_pads_response(obj);
                        break;
                    case "TOKEN_CMD_OPEN_PAD":
                        open_pad_response(obj);
                        break;
                    case "TOKEN_CMD_SIGNATURE_START":
                        signature_start_response(obj);
                        break;

                    case "TOKEN_CMD_API_DEVICE_SET_COM_PORT":
                    case "TOKEN_CMD_API_DEVICE_GET_COUNT":
                    case "TOKEN_CMD_API_DEVICE_GET_INFO":
                    case "TOKEN_CMD_API_DEVICE_GET_VERSION":
                    case "TOKEN_CMD_API_DEVICE_GET_CAPABILITIES":
                        api_search_for_pads_responses(obj);
                        break;

                    case "TOKEN_CMD_API_RSA_GET_ENCRYPTION_CERT_ID":
                    case "TOKEN_CMD_API_RSA_SET_ENCRYPTION_CERT_PW":
                    case "TOKEN_CMD_API_RSA_SET_HASH":
                        api_encryption_cert_dochash_responses(obj);
                        api_rsa_sign_get_sign_data_responses(obj);
                        break;

                    case "TOKEN_CMD_API_DEVICE_OPEN":
                    case "TOKEN_CMD_API_DISPLAY_CONFIG_PEN":
                    case "TOKEN_CMD_API_DISPLAY_GET_WIDTH":
                    case "TOKEN_CMD_API_DISPLAY_GET_HEIGHT":
                    case "TOKEN_CMD_API_SIGNATURE_GET_RESOLUTION":
                    case "TOKEN_CMD_API_SENSOR_GET_SAMPLE_RATE_MODE":
                        api_device_open_responses(obj);
                        break;

                    case "TOKEN_CMD_API_DISPLAY_SET_ROTATION":
                    case "TOKEN_CMD_API_DISPLAY_GET_ROTATION":
                    case "TOKEN_CMD_API_DISPLAY_SET_TARGET":
                    case "TOKEN_CMD_API_DISPLAY_SET_IMAGE":
                    case "TOKEN_CMD_API_SENSOR_ADD_HOT_SPOT":
                    case "TOKEN_CMD_API_SENSOR_SET_SIGN_RECT":
                    case "TOKEN_CMD_API_DISPLAY_SET_TEXT_IN_RECT":
                    case "TOKEN_CMD_API_DISPLAY_SET_IMAGE_FROM_STORE":
                    case "TOKEN_CMD_API_SIGNATURE_START":
                    case "TOKEN_CMD_API_PDF_LOAD":
                    case "TOKEN_CMD_API_PDF_GET_PAGE_COUNT":
                    case "TOKEN_CMD_API_PDF_GET_WIDTH":
                    case "TOKEN_CMD_API_PDF_GET_HEIGHT":
                    case "TOKEN_CMD_API_DISPLAY_SET_PDF":
                    case "TOKEN_CMD_API_DISPLAY_SET_OVERLAY_RECT":
                    case "TOKEN_CMD_API_SENSOR_SET_SCROLL_AREA":
                    case "TOKEN_CMD_API_SENSOR_SET_PEN_SCROLLING_ENABLED":
                    case "TOKEN_CMD_API_SENSOR_CLEAR_HOT_SPOTS":
                    case "TOKEN_CMD_API_DISPLAY_ERASE":
                        api_signature_start_responses(obj);
                        api_pdf_dialog_start_responses(obj);
                        api_pdf_dialog_end_responses(obj);
                        break;

                    case "TOKEN_CMD_SIGNATURE_CONFIRM":
                    case "TOKEN_CMD_API_SIGNATURE_CONFIRM":
                        signature_confirm_response(obj);
                        break;

                    case "TOKEN_CMD_SIGNING_CERT":
                    case "TOKEN_CMD_API_RSA_SAVE_SIGNING_CERT_AS_STREAM":
                        signing_cert_response(obj);
                        break;

                    case "TOKEN_CMD_SIGNATURE_IMAGE":
                    case "TOKEN_CMD_API_SIGNATURE_SAVE_AS_STREAM_EX":
                        signature_image_response(obj);
                        break;

                    case "TOKEN_CMD_SIGNATURE_SIGN_DATA":
                    case "TOKEN_CMD_API_SIGNATURE_GET_SIGN_DATA":
                        signature_sign_data_response(obj);
                        break;

                    case "TOKEN_CMD_API_RSA_SIGN_PW":
                    case "TOKEN_CMD_API_RSA_GET_SIGN_DATA":
                        api_rsa_sign_get_sign_data_responses(obj);
                        break;

                    case "TOKEN_CMD_SIGNATURE_RETRY":
                    case "TOKEN_CMD_API_SIGNATURE_RETRY":
                        signature_retry_response(obj);
                        break;

                    case "TOKEN_CMD_SIGNATURE_CANCEL":
                    case "TOKEN_CMD_API_SIGNATURE_CANCEL":
                        signature_cancel_response(obj);
                        break;

                    case "TOKEN_CMD_CLOSE_PAD":
                    case "TOKEN_CMD_API_DEVICE_CLOSE":
                        close_pad_response(obj);
                        break;

                    case "TOKEN_CMD_SELECTION_DIALOG":
                        selection_dialog_response(obj);
                        break;

                    default:
                        alert("Unknown response token. Token: " + obj.TOKEN_CMD_ORIGIN);
                        break;
                }
            } else {
                alert("Unknown type token. Token: " + obj.TOKEN_TYPE);
            }
        }

		var signDataInput = document.getElementById('SignData_0');
		if (signDataInput) {
			signDataInput.addEventListener('input', saveRecord);
		}

		function saveRecord() {
			var saveButton = document.querySelector(".o_form_button_save");
			if (saveButton) {
				saveButton.click();
				console.log("Button clicked, stopping further attempts.");
			} else {
				console.warn("No button with class 'o_form_button_save' found.");
			}
		}

		window.addEventListener('load', function() {
			displaySignature();
		});

		document.addEventListener('DOMContentLoaded', function() {
			displaySignature();
		});

		var signatureInput = document.getElementById('Signature_b64_0');
		if (signatureInput) {
			signatureInput.addEventListener('input', function() {
				displaySignature();
			});
		}

		function displaySignature() {
			setTimeout(function() {
				var signatureInput = document.getElementById('Signature_b64_0');
				var signaturePreview = document.querySelector('img#Signature_preview');

				if (signatureInput && signaturePreview) {
					var signatureData = signatureInput.value;
					if (signatureData !== undefined && signatureData.trim() !== '') {
						signaturePreview.src = "data:image/png;base64," + signatureData;
						console.log("[DISPLAY] Signature preview image updated after 2 second delay");
						console.log("[DISPLAY] Preview image data length:", signatureData.length, "characters");
					}
				}
			}, 2000);
		}
