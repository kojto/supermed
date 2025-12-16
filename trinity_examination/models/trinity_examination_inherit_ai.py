import json
import httpx
import logging
import re
from odoo import models, fields
from odoo.exceptions import UserError

logger = logging.getLogger(__name__)

def _compact_conversation(conversation: str) -> str:
    return json.dumps({"conversation": conversation}, ensure_ascii=False, separators=(",", ":"))

class TrinityExamination(models.Model):
    _inherit = "trinity.examination"

    def _get_medical_facility(self):
        self.ensure_one()
        company_id = self.env.user.company_id.id
        medical_facility = self.env['trinity.medical.facility'].search([
            ('hospital_id', '=', company_id)
        ], limit=1)
        return medical_facility

    def _get_api_config(self):
        self.ensure_one()
        medical_facility = self._get_medical_facility()

        if not medical_facility:
            raise UserError("Регистрирайте лечебно заведение")

        if not medical_facility.ai_external_api_url:
            raise UserError("Настройте API URL в лечебното заведение")
        if not medical_facility.ai_external_api_key:
            raise UserError("Настройте API ключ в лечебното заведение")
        if not medical_facility.ai_external_model:
            raise UserError("Настройте AI модел в лечебното заведение")

        return {
            "type": medical_facility.ai_external_provider,
            "url": medical_facility.ai_external_api_url,
            "key": medical_facility.ai_external_api_key,
            "model": medical_facility.ai_external_model,
        }

    def _patient_header(self):
        age = int(self.patient_age) if self.patient_age else "неизвестна възраст"
        gender = (self.patient_gender.description or "неизвестен пол").lower()
        visits = self.env["trinity.examination"].search_count([("patient_identifier_id", "=", self.patient_identifier_id.id), ("id", "!=", self.id)])
        visits_txt = f"{visits} предходни посещения" if visits > 1 else "1 предходно посещение" if visits == 1 else "идва за първи път"
        last = self.env["trinity.examination"].search([("patient_identifier_id", "=", self.patient_identifier_id.id), ("id", "!=", self.id)], order="examination_open_dtm desc", limit=1)
        last_txt = f" Последно: {last.examination_open_dtm.strftime('%d.%m.%Y')}." if last and last.examination_open_dtm else ""
        last_diagnosis = f"Предходна/и диагноза/и: {last.diagnosis}" if last and last.diagnosis else ""
        return f"{gender} на {age} години. {visits_txt}.{last_txt}. {last_diagnosis}"

    def _call_ai(self, messages):
        config = self._get_api_config()
        medical_facility = self._get_medical_facility()

        temperature = medical_facility.ai_external_temperature
        top_p = medical_facility.ai_external_top_p
        max_tokens = medical_facility.ai_external_max_tokens
        timeout = medical_facility.ai_external_api_timeout
        retries = medical_facility.ai_external_api_retries

        payload = {
            "messages": messages,
            "model": config["model"],
            "stream": False,
            "temperature": temperature,
        }

        if top_p:
            payload["top_p"] = top_p
        if max_tokens:
            payload["max_tokens"] = max_tokens

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {config['key']}"
        }

        for attempt in range(retries):
            try:
                r = httpx.post(config["url"], headers=headers, json=payload, timeout=timeout)
                r.raise_for_status()
                data = r.json()
                return (data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()) or None
            except httpx.HTTPStatusError as e:
                logger.warning("AI API call failed with status %s: %s", e.response.status_code, e)
                if attempt == retries - 1:
                    raise UserError(f"Грешка при извикване на AI API: {e.response.status_code}")
            except httpx.RequestError as e:
                logger.warning("AI API request failed: %s", e)
                if attempt == retries - 1:
                    raise UserError(f"Грешка при свързване с AI API: {str(e)}")
            except Exception as e:
                logger.warning("AI call failed (%s): %s", config["type"], e)
                if attempt == retries - 1:
                    raise UserError(f"Неочаквана грешка при извикване на AI: {str(e)}")

        return None

    def generate_anamnesis_with_ai(self):
        for rec in self:
            if not rec.conversation_with_patient:
                continue

            header = rec._patient_header()
            conv = _compact_conversation(rec.conversation_with_patient)

            system_prompt = (
                "Систематизирай разговора между лекар и пациент, създай анамнеза и върни резултата в един параграф текст. "
                "JSON обектът трябва да съдържа следните ключове: диагноза, анамнеза, обективно, изследвания, терапия и заключение "
                "Всяка стойност трябва да е един параграф текст. Ако няма данни за някоя секция, използвай празен низ (\"\"). "
                "Върни САМО валиден JSON, без допълнителен текст преди или след него."
            )

            user_prompt = (
                f"{header}\n\n"
                f"Разговор с пациента:\n{conv}\n\n"
                "Систематизирай всичко като амбулаторен лист и върни JSON с ключове: диагноза, анамнеза, обективно, изследвания, терапия и заключение"
            )

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]

            result = rec._call_ai(messages)
            if result:
                try:
                    json_match = re.search(r'\{.*\}', result, re.DOTALL)
                    json_str = json_match.group(0) if json_match else result
                    data = json.loads(json_str)

                    field_mapping = {
                        #"диагноза": "diagnosis",
                        "анамнеза": "medical_history",
                        #"обективно": "objective_condition",
                        #"изследвания": "assessment_notes",
                        #"терапия": "therapy_note",
                        #"заключение": "conclusion"
                    }

                    updates = {}
                    for bg_key, field_name in field_mapping.items():
                        value = data.get(bg_key, "")
                        if isinstance(value, str):
                            value = value.strip()
                        elif value is None:
                            value = ""
                        else:
                            value = str(value).strip()
                        updates[field_name] = value

                    if updates:
                        rec.write(updates)
                except (json.JSONDecodeError, AttributeError) as e:
                    logger.warning("Failed to parse AI response as JSON: %s | Response: %s", e, result)
            rec.conversation_with_patient = False

        return {"type": "ir.actions.client", "tag": "reload"}

    def emptyButton(self):
        return
