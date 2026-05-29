import logging

class SMSService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    async def send_alert(self, phone_number: str, message: str):
        """
        Gửi tin nhắn SMS cảnh báo.
        """
        # Mocking SMS sending logic
        self.logger.info(f"Sending SMS to {phone_number}: {message}")
        print(f"[SMS ALERT] to {phone_number}: {message}")
        return True

sms_service = SMSService()
