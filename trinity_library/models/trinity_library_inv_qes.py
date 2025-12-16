# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import uuid
import base64
import hashlib
import logging
import subprocess
from datetime import datetime
from lxml import etree
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

_logger = logging.getLogger(__name__)

# Constants
PRIVATE_KEY_PASSPHRASE = open('/opt/odoo18/custom/addons/trinity_file_assets/static/src/certificates/OpenSSL/supermed2025pass.txt').read().strip()
KEY_FILE_PATH = '/opt/odoo18/custom/addons/trinity_file_assets/static/src/certificates/OpenSSL/supermed2025_private.pem'
CERT_FILE_PATH = '/opt/odoo18/custom/addons/trinity_file_assets/static/src/certificates/OpenSSL/supermed2025_certificate.crt'

class TrinityLibraryInvQes(models.AbstractModel):
    _name = "trinity.library.inv.qes"
    _description = "Trinity Library Invoice Qes"
    _inherit = ["trinity.library.user.company.fields"]

    @api.model
    def get_supermed_certificate_value(self):
        try:
            with open(CERT_FILE_PATH, 'r') as cert_file:
                return cert_file.read()
        except IOError as e:
            _logger.error("Error reading certificate file: %s", e)
            return 'Error: Certificate file not found or could not be read.'

    def reset_to_default_supermed_certificate(self):
        for record in self:
            record.supermed_certificate = self.get_supermed_certificate_value()

    supermed_certificate = fields.Text(string="SuperMed Certificate", default=get_supermed_certificate_value)

    ############################################################################
    #                                XAdES SIGN                                #
    ############################################################################

    def prepare_first_digest(self, field_name, signedinfo, is_signed, signedinfo_signature):
        unsigned_xml_content = getattr(self, field_name)
        tree = etree.fromstring(unsigned_xml_content.encode())

        canonicalized_xml = etree.tostring(tree, method="c14n", exclusive=False, with_comments=False)

        hash_object = hashlib.sha256(canonicalized_xml)
        hash_value = hash_object.digest()
        first_digest_value = base64.b64encode(hash_value).decode('utf-8')

        self.insert_signature_element(field_name, signedinfo, is_signed, signedinfo_signature, first_digest_value)

    def insert_signature_element(self, field_name, signedinfo, is_signed, signedinfo_signature, first_digest_value):
        unsigned_xml_content = getattr(self, field_name)
        if not unsigned_xml_content:
            return

        xades_base_value = self.compute_xades_base()
        modified_xml_content = unsigned_xml_content.replace("</ELECTRONIC_INVOICE>", f"{xades_base_value}</ELECTRONIC_INVOICE>")

        setattr(self, field_name, modified_xml_content)

        self.insert_first_digest(field_name, signedinfo, is_signed, signedinfo_signature, first_digest_value)

    def insert_first_digest(self, field_name, signedinfo, is_signed, signedinfo_signature, first_digest_value):
        tree = etree.fromstring(getattr(self, field_name).encode())

        # Find the first <ds:DigestValue> element
        namespaces = {"ds": "http://www.w3.org/2000/09/xmldsig#"}
        digest_element = tree.find(".//ds:DigestValue", namespaces=namespaces)
        if digest_element is None:
            raise ValueError("DigestValue element not found!")

        digest_element.text = first_digest_value

        updated_xml = etree.tostring(tree, encoding='utf-8').decode('utf-8')
        setattr(self, field_name, updated_xml)

        self.replace_certificate(field_name, signedinfo, is_signed, signedinfo_signature)
        return True

    def replace_certificate(self, field_name, signedinfo, is_signed, signedinfo_signature):
        doctor = self.env['trinity.medical.facility.doctors'].search([('is_administrator', '=', True)], limit=1)
        if not doctor:
            raise UserError(_("Грешка: Не е намерен лекар-администратор. Моля, проверете настройките на профила или се свържете с администратор."))

        doctor_token_certificate = doctor.token_certificate if hasattr(doctor, 'token_certificate') else None
        if not isinstance(doctor_token_certificate, str) or not doctor_token_certificate.strip():
            _logger.error("Invalid doctor_token_certificate: %s", doctor_token_certificate)
            return False

        certificate_data = "-----BEGIN CERTIFICATE-----\n" + doctor_token_certificate + "\n-----END CERTIFICATE-----"
        certificate_data = certificate_data.encode('utf-8')

        certificate = x509.load_pem_x509_certificate(certificate_data, default_backend())

        certificate_der = certificate.public_bytes(encoding=serialization.Encoding.DER)

        encoded_certificate = base64.b64encode(certificate_der).decode('utf-8')

        xml_content = getattr(self, field_name)
        tree = etree.fromstring(xml_content.encode())

        x509_certificate_element = tree.find(".//ds:X509Certificate", namespaces={"ds": "http://www.w3.org/2000/09/xmldsig#"})
        if x509_certificate_element is None:
            raise ValueError("X509Certificate element not found!")

        x509_certificate_element.text = encoded_certificate

        updated_xml = etree.tostring(tree, encoding='utf-8').decode('utf-8')
        setattr(self, field_name, updated_xml)

        self.extract_certificate_hash(field_name, signedinfo, is_signed, signedinfo_signature)

        return True

    def extract_certificate_hash(self, field_name, signedinfo, is_signed, signedinfo_signature):
        tree = etree.fromstring(getattr(self, field_name).encode())

        # Find the X509Certificate element
        x509_certificate_element = tree.find(".//ds:X509Certificate", namespaces={"ds": "http://www.w3.org/2000/09/xmldsig#"})
        if x509_certificate_element is None:
            raise ValueError("X509Certificate element not found!")

        # Extract the certificate value, decode from base64, compute its hash, and encode the hash as base64
        certificate_value = x509_certificate_element.text.strip()
        decoded_certificate = base64.b64decode(certificate_value)
        certificate_hash = hashlib.sha256(decoded_certificate).digest()
        encoded_hash = base64.b64encode(certificate_hash).decode('utf-8')

        # Use the XML from field
        xml_content = getattr(self, field_name)

        # Find the starting and ending indices of the <ds:DigestValue> element within <xades:CertDigest>
        start_index = xml_content.find("<ds:DigestValue>", xml_content.find("<xades:CertDigest>"))
        end_index = xml_content.find("</ds:DigestValue></xades:CertDigest>", start_index)

        if start_index == -1 or end_index == -1:
            raise ValueError("Could not find <ds:DigestValue> element within <xades:CertDigest>!")

        # Replace the content within the <ds:DigestValue> element
        updated_xml = xml_content[:start_index + len("<ds:DigestValue>")] + encoded_hash + xml_content[end_index:]

        # Update field
        setattr(self, field_name, updated_xml)

        self.regenerate_and_replace_digests(field_name, signedinfo, is_signed, signedinfo_signature)

    def regenerate_and_replace_digests(self, field_name, signedinfo, is_signed, signedinfo_signature):
        xml_content = getattr(self, field_name)
        tree = etree.fromstring(xml_content.encode())

        # Locate the reference elements starting from the second one
        reference_elements = tree.xpath("//ds:Reference[position() > 1]", namespaces={"ds": "http://www.w3.org/2000/09/xmldsig#"})

        for index, reference_element in enumerate(reference_elements, start=2):
            reference_uri = reference_element.get("URI").lstrip("#")

            # Use the reference URI to get the target XML element
            target_element = tree.xpath(f"//*[@Id='{reference_uri}']")
            if not target_element:
                raise ValueError(f"Couldn't find an XML element with Id '{reference_uri}'!")
            target_element = target_element[0]

            # Canonicalize the XML element
            canonicalized_xml = etree.tostring(target_element, method="c14n", exclusive=False, with_comments=False)

            # Compute the digest using OpenSSL
            hash_process = subprocess.run(["openssl", "dgst", "-sha256", "-binary"], input=canonicalized_xml, capture_output=True, check=True, text=False)

            # Convert the digest to base64
            hash_base64 = base64.b64encode(hash_process.stdout).decode('utf-8')

            # Find the DigestValue element of the current reference
            digest_value_element = reference_element.find("ds:DigestValue", namespaces={"ds": "http://www.w3.org/2000/09/xmldsig#"})
            if digest_value_element is None:
                raise ValueError(f"DigestValue element not found in the reference: {reference_element}")

            # Replace the content of the DigestValue element with the new digest value
            digest_value_element.text = hash_base64

        # Update field
        updated_xml = etree.tostring(tree, encoding='utf-8').decode('utf-8')
        setattr(self, field_name, updated_xml)

        self.generate_SignedInfo(field_name, signedinfo, is_signed, signedinfo_signature)

        return True

    def generate_SignedInfo(self, field_name, signedinfo, is_signed, signedinfo_signature):
        xml_content = getattr(self, field_name)
        tree = etree.fromstring(xml_content.encode())

        # Directly locate the SignedInfo element
        signed_info_element = tree.xpath("//ds:SignedInfo", namespaces={"ds": "http://www.w3.org/2000/09/xmldsig#"})
        if not signed_info_element:
            raise ValueError("Couldn't find the SignedInfo element!")
        signed_info_element = signed_info_element[0]

        # Canonicalize the SignedInfo element using lxml
        canonicalized_xml = etree.tostring(signed_info_element, method="c14n", exclusive=False, with_comments=False)

        # Compute the digest of the canonicalized XML using OpenSSL
        hash_process = subprocess.run(["openssl", "dgst", "-sha256", "-binary"], input=canonicalized_xml, capture_output=True, check=True)
        hash_result = hash_process.stdout

        # Sign the hash of the SignedInfo using OpenSSL
        sign_hash_process = subprocess.run(["openssl", "dgst", "-sha256", "-sign", KEY_FILE_PATH, "-passin", f"pass:{PRIVATE_KEY_PASSPHRASE}"], input=hash_result, capture_output=True, check=True)
        signature = sign_hash_process.stdout

        # Store the B64 value of the canonicalized SignedInfo
        setattr(self, signedinfo, base64.b64encode(canonicalized_xml).decode('utf-8'))
        setattr(self, signedinfo_signature, base64.b64encode(signature).decode('utf-8'))
        setattr(self, is_signed, 'not signed')

        return

    def compute_xades_base(self):
        for record in self:
            uuid_value_01 = uuid.uuid4().hex
            uuid_value_02 = uuid.uuid4().hex
            signing_time = fields.Datetime.now().strftime("%Y-%m-%dT%H:%M:%S+00:00")
            xades_base = f"""<ds:Signature xmlns:ds="http://www.w3.org/2000/09/xmldsig#" xmlns:xades="http://uri.etsi.org/01903/v1.3.2#" Id="SignXMLSignature{uuid_value_01}"><ds:SignedInfo><ds:CanonicalizationMethod Algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315"/><ds:SignatureMethod Algorithm="http://www.w3.org/2001/04/xmldsig-more#rsa-sha256"/><ds:Reference URI="" Id="SignXMLReferenceE76228DD"><ds:Transforms><ds:Transform Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature"/><ds:Transform Algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315"/></ds:Transforms><ds:DigestMethod Algorithm="http://www.w3.org/2001/04/xmlenc#sha256"/><ds:DigestValue>|---digestValue---|</ds:DigestValue></ds:Reference><ds:Reference URI="#SignXMLSignature{uuid_value_01}-SignedProperties{uuid_value_02}" Type="http://uri.etsi.org/01903#SignedProperties"><ds:DigestMethod Algorithm="http://www.w3.org/2001/04/xmlenc#sha256"/><ds:DigestValue>|---digestValue---|</ds:DigestValue></ds:Reference><ds:Reference URI="#SignXMLCertificate4B173CB7"><ds:DigestMethod Algorithm="http://www.w3.org/2001/04/xmlenc#sha256"/><ds:DigestValue>|---digestValue---|</ds:DigestValue></ds:Reference></ds:SignedInfo><ds:SignatureValue>|---signatureValue---|</ds:SignatureValue><ds:KeyInfo Id="SignXMLCertificate4B173CB7"><ds:X509Data><ds:X509Certificate>M=</ds:X509Certificate></ds:X509Data></ds:KeyInfo><ds:Object><xades:QualifyingProperties Target="#SignXMLSignature{uuid_value_01}"><xades:SignedProperties Id="SignXMLSignature{uuid_value_01}-SignedProperties{uuid_value_02}"><xades:SignedSignatureProperties><xades:SigningTime>{signing_time}</xades:SigningTime><xades:SigningCertificateV2><xades:Cert><xades:CertDigest><ds:DigestMethod Algorithm="http://www.w3.org/2001/04/xmlenc#sha256"/><ds:DigestValue>/e=</ds:DigestValue></xades:CertDigest></xades:Cert></xades:SigningCertificateV2></xades:SignedSignatureProperties><xades:SignedDataObjectProperties><xades:DataObjectFormat ObjectReference="#SignXMLReferenceE76228DD"><xades:Description>XAdES payload</xades:Description><xades:MimeType>text/xml</xades:MimeType></xades:DataObjectFormat></xades:SignedDataObjectProperties></xades:SignedProperties></xades:QualifyingProperties></ds:Object></ds:Signature>"""
            return xades_base
