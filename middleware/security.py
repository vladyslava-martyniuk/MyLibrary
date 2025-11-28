import time
import hmac
import base64

SECRET_KEY = b"12345678"

class CSRFProtectionMiddleware:
   
    @staticmethod
    def generate_token(session_id):
        timestemp = str(int(time.time()))
        msg = f"{session_id}:{timestemp}".encode()
        sign = hmac.new(SECRET_KEY, msg, 'sha256').digest()
        return base64.b64encode(msg +b":" + sign).decode()
       

    @staticmethod
    def verify_token(token, session_id, max_age=3600):
        try:
            decode = base64.b64decode(token.encode())
            msg, sign = decode.rsplit(b":", 1)
            
            expected_sign = hmac.new(SECRET_KEY, msg, 'sha256').digest()
            if sign != expected_sign:
                return False
            
            timestamp = int(msg.split(b":")[1])
            if time.time() - timestamp > max_age:
                return False
            
            if msg.split(b":")[0].decode() != session_id:
                return False
            return True
        except:
            return False