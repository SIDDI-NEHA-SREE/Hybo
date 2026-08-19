import re
from typing import Optional, Tuple
from app.config import settings
from app.utils.logger import logger

class TwilioService:
    @staticmethod
    def normalize_phone_number(phone_number: str) -> str:
        """
        Normalizes a phone number to standard E.164 format.
        Defaults to +91 (India) if 10 digits are provided without a country code.
        """
        cleaned = re.sub(r"[\s\-\(\)]", "", phone_number.strip())
        if not cleaned.startswith("+"):
            if len(cleaned) == 10:
                cleaned = "+91" + cleaned
            else:
                cleaned = "+" + cleaned
        return cleaned

    @classmethod
    def send_sms_otp(cls, phone_number: str, otp: str) -> Tuple[bool, str, bool]:
        """
        Sends an SMS OTP using Twilio Messaging API.
        Returns: (success: bool, message: str, dev_mode: bool)
        """
        normalized_phone = cls.normalize_phone_number(phone_number)

        if not settings.is_twilio_configured:
            logger.info(f"[DEV FALLBACK] Twilio credentials not configured. Mock OTP for {normalized_phone}: {otp}")
            return True, "Development mode: OTP generated successfully", True

        try:
            from twilio.rest import Client
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

            # Option A: Twilio Verify Service if SID is configured
            if settings.TWILIO_VERIFY_SERVICE_SID:
                verification = client.verify.v2.services(settings.TWILIO_VERIFY_SERVICE_SID).verifications.create(
                    to=normalized_phone,
                    channel="sms"
                )
                logger.info(f"Twilio Verify OTP initiated for {normalized_phone}, status: {verification.status}")
                return True, "Verification code sent via Twilio Verify", False

            # Option B: Twilio Standard SMS Messaging API
            if not settings.TWILIO_PHONE_NUMBER:
                logger.warning("TWILIO_PHONE_NUMBER is not set. Defaulting to dev fallback.")
                return True, "Twilio phone number unconfigured; dev OTP generated", True

            body_message = f"Your HYBO Smart City Assistant verification code is: {otp}. Valid for {settings.OTP_EXPIRE_MINUTES} minutes. Do not share this code."
            
            message = client.messages.create(
                body=body_message,
                from_=settings.TWILIO_PHONE_NUMBER,
                to=normalized_phone
            )
            logger.info(f"Twilio SMS sent to {normalized_phone}, SID: {message.sid}")
            return True, "Verification code sent via SMS", False

        except Exception as e:
            logger.error(f"Failed to send Twilio SMS to {normalized_phone}: {str(e)}")
            return False, f"Failed to send SMS: {str(e)}", False

    @classmethod
    def verify_with_twilio_service(cls, phone_number: str, otp: str) -> Tuple[bool, str]:
        """
        If Twilio Verify Service SID is used, checks code against Twilio Verify API.
        Returns: (approved: bool, message: str)
        """
        if not settings.is_twilio_configured or not settings.TWILIO_VERIFY_SERVICE_SID:
            return False, "Twilio Verify Service not active"

        try:
            from twilio.rest import Client
            normalized_phone = cls.normalize_phone_number(phone_number)
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            
            verification_check = client.verify.v2.services(settings.TWILIO_VERIFY_SERVICE_SID).verification_checks.create(
                to=normalized_phone,
                code=otp
            )
            if verification_check.status == "approved":
                return True, "Verification approved"
            return False, "Invalid or expired verification code"
        except Exception as e:
            logger.error(f"Twilio Verify check error: {str(e)}")
            return False, f"Verification failed: {str(e)}"
