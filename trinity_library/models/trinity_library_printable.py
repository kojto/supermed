from odoo import tools, models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import base64

from weasyprint import HTML


class KojtoLibraryPrintable(models.AbstractModel):
    _name = "trinity.library.printable"
    _description = "Kojto Library Printable"

    pdf_attachment_id = fields.Many2one("ir.attachment", string="Attachments")
    language_id = fields.Many2one("res.lang", string="Language", default=lambda self: self.env['res.lang'].search([('code', '=', 'bg_BG')], limit=1) or self.env['res.lang'].search([('active', '=', True)], limit=1))

    def print_document_as_pdf(self, report_ref=None, report_css_ref=None):
        report_ref = report_ref or getattr(self, "_report_ref", None)
        report_css_ref = report_css_ref or getattr(self, "_report_css_ref", None)

        if not report_ref:
            raise UserError("No report_ref provided or defined on the model.")

        html = self.generate_report_html(report_ref)
        html = self.inject_report_css(html, report_css_ref)
        attachment = self.create_pdf_attachment(html)

        return {
            "type": "ir.actions.act_url",
            "url": f"/web/content/{attachment.id}?download=true",
            "target": "new",
        }

    def generate_report_html(self, report_ref):
        lang_code = self.language_id.code or "en_US"
        report = self.env["ir.actions.report"]._get_report_from_name(report_ref)
        if not report:
            raise UserError(f"Report {report_ref} not found.")

        try:
            html_content, _ = report.with_context(lang=lang_code)._render_qweb_html(
                report_ref=report_ref, docids=[self.id]
            )
            html_string = html_content.decode("utf-8")
            return html_string
        except Exception as e:
            raise UserError(f"Failed to generate HTML: {e}")

    def inject_report_css(self, html, report_css_ref):
        if not report_css_ref:
            return html

        file_path = tools.misc.file_path(f"trinity_file_assets/static/src/css/{report_css_ref}")
        try:
            with open(file_path, "r") as f:
                css = f.read()
        except Exception as e:
            raise UserError(f"Could not read CSS file at {file_path}: {e}")

        style = (
            "<style>"
            "@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&subset=cyrillic&display=swap');"
            f"{css}</style>"
        )

        if "</head>" in html:
            return html.replace("</head>", f"{style}</head>")
        elif "<head>" in html:
            return html.replace("<head>", f"<head>{style}")
        else:
            return f"<html><head>{style}</head><body>{html}</body></html>"

    def create_pdf_attachment(self, html):
        try:
            pdf = HTML(string=html).write_pdf()
        except Exception as e:
            raise UserError(f"Failed to generate PDF: {e}")

        filename = f"{self.name}.pdf"
        attachment = self.env["ir.attachment"].search([
            ("res_model", "=", self._name),
            ("res_id", "=", self.id),
            ("name", "=", filename)
        ], limit=1)

        vals = {
            "datas": base64.b64encode(pdf).decode("utf-8"),
            "mimetype": "application/pdf",
            "store_fname": filename,
            "name": filename,
            "type": "binary",
            "res_model": self._name,
            "res_id": self.id,
        }

        if attachment:
            attachment.write(vals)
        else:
            attachment = self.env["ir.attachment"].create(vals)

        self.write({"pdf_attachment_id": attachment.id})
        return attachment
