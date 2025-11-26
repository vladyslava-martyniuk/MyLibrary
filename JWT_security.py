import jwt
import time


def generate_jwt(payload: dict, secret: str, algorithm: str = 'HS512') -> str:
    '''
    Створює JWT
    '''
    return jwt.encode(
        headers={
            "alg": algorithm,
            "typ": "JWT"
        },
        payload=payload,
        key=secret,
        algorithm=algorithm
    )


def decode_jwt(token: str, secret: str, algorithms: list = ['HS512']) -> dict:
    '''
    Декодує JWT.
    '''
    return jwt.decode(
            jwt=token,
            key=secret,
            algorithms=algorithms
    )


if __name__ == "__main__":
    time_now = int(time.time())
    secret_key = "12345678"
    payload_data = {
        "sub": "123",
        "name": "some name",
        "email": "someemail@gmail.com",
        "iat": time_now,
        "exp": time_now + 60 * 15
    }

jwt_token = generate_jwt(payload=payload_data, secret=secret_key)
print(f"Generated Token: {jwt_token}")

decoded_jwt_token = decode_jwt(token=jwt_token, secret=secret_key)
print(f"Decoded Payload: {decoded_jwt_token}")
