JWT Toy Project (FastAPI)

이 프로젝트는 JWT(Json Web Token) 기반의 인증(Authentication) / 인가(Authorization) 흐름을 이해하고 구현하기 위한 Python + FastAPI 토이프로젝트입니다.

실무에서 자주 사용하는 구조와 보안 관행을 기준으로 단계적으로 확장하는 것을 목표로 합니다.

1. 기술 스택

Language: Python 3.9+

Framework: FastAPI

Auth: JWT (Access Token + Refresh Token)

Crypto: bcrypt, passlib

JWT Library: python-jose

Config: pydantic-settings

Dev Tool: VS Code, Postman

DB 연동(PostgreSQL + SQLAlchemy + Alembic)은 다음 단계에서 진행 예정

2. 인증 설계 개요

토큰 전략

Access Token

전달 방식: Authorization: Bearer <token>

수명: 15분

용도: API 접근 인증

Refresh Token

전달 방식: HttpOnly Cookie

수명: 30일

용도: Access Token 재발급

보안 포인트

Refresh Token은 JavaScript에서 접근 불가(HttpOnly)

Refresh Token 회전(Rotation) 적용

비밀번호는 bcrypt 해시로 저장

3. 현재 구현된 기능

Auth API

Method

Endpoint

Description

POST

/auth/login

로그인 (Access 발급 + Refresh 쿠키 설정)

POST

/auth/refresh

Refresh Token으로 Access 재발급

POST

/auth/logout

Refresh Token 쿠키 삭제

현재는 테스트용 fake user를 메모리에 두고 동작 확인

4. 프로젝트 구조

jwt-toy/
├─ app/
│  ├─ main.py              # FastAPI 엔트리포인트
│  ├─ core/
│  │  ├─ config.py         # 환경변수 설정
│  │  └─ security.py       # JWT / bcrypt 유틸
│  └─ routers/
│     └─ auth.py           # 인증 API
├─ .env                    # 환경변수 (gitignore)
├─ requirements.txt
├─ README.md

5. 환경변수 (.env)

APP_NAME=jwt-toy
ENV=dev

JWT_ISSUER=jwt-toy
JWT_AUDIENCE=jwt-toy-client
ACCESS_TOKEN_EXPIRES_MIN=15
REFRESH_TOKEN_EXPIRES_DAYS=30

JWT_SECRET_KEY=CHANGE_ME_TO_A_LONG_RANDOM_SECRET
JWT_ALGORITHM=HS256

6. 로컬 실행 방법

1) 가상환경 생성 및 활성화

python -m venv .venv
source .venv/bin/activate   # macOS/Linux

2) 패키지 설치

pip install -r requirements.txt

3) 서버 실행

uvicorn app.main:app --reload

API: http://127.0.0.1:8000

Swagger: http://127.0.0.1:8000/docs

7. Postman 테스트 가이드

로그인

POST /auth/login
Content-Type: application/json

{
  "email": "jywan@test.com",
  "password": "test"
}

Response Body: Access Token

Cookie: refresh_token (HttpOnly)

Refresh

POST /auth/refresh

Cookie 기반으로 Access Token 재발급

Logout

POST /auth/logout

Refresh Token 쿠키 삭제

8. 다음 단계 계획



9. 목적

이 프로젝트는 단순 JWT 사용 예제가 아니라,

Access / Refresh 분리 전략

쿠키 기반 Refresh Token 운용

실무에 가까운 인증 흐름 설계

를 직접 구현하고 이해하는 것을 목표로 합니다.