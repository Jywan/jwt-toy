# JWT Toy Project (FastAPI)

이 프로젝트는 **JWT (JSON Web Token)** 기반의 인증(Authentication) / 인가(Authorization) 흐름을 이해하고 구현하기 위한 **Python + FastAPI 토이프로젝트**입니다.

실무에서 자주 사용하는 구조와 보안 관행을 기준으로 단계적으로 확장하는 것을 목표로 합니다.

---

## 기술 스택

- **Language**: Python 3.9+
- **Framework**: FastAPI
- **Auth**: JWT (Access Token + Refresh Token)
- **Crypto**: bcrypt, passlib
- **JWT Library**: python-jose
- **Config**: pydantic-settings
- **Dev Tool**: VS Code, Postman

> DB 연동(PostgreSQL + SQLAlchemy + Alembic)은 다음 단계에서 진행 예정입니다.

---

## 인증 설계 개요

### 토큰 전략

#### Access Token
- 전달 방식: `Authorization: Bearer <token>`
- 수명: 15분
- 용도: API 접근 인증

#### Refresh Token
- 전달 방식: **HttpOnly Cookie**
- 수명: 30일
- 용도: Access Token 재발급

### 보안 포인트
- Refresh Token은 JavaScript에서 접근 불가(HttpOnly)
- Refresh Token 회전(Rotation) 적용
- 비밀번호는 bcrypt 해시로 저장

---

## 현재 구현된 기능

### Auth API

| Method | Endpoint       | Description |
|--------|----------------|-------------|
| POST   | /auth/login    | 로그인 (Access 발급 + Refresh 쿠키 설정) |
| POST   | /auth/refresh  | Refresh Token으로 Access 재발급 |
| POST   | /auth/logout   | Refresh Token 쿠키 삭제 |

> 현재는 **테스트용 fake user**를 메모리에 두고 인증 흐름을 검증하고 있습니다.

---

## 프로젝트 구조

```text
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
```

--- 

## 환경변수 설정 (.env)

아래는 로컬 개발 환경에서 사용하는 예시 환경변수입니다.

```env
APP_NAME=jwt-toy
ENV=dev

JWT_ISSUER=jwt-toy
JWT_AUDIENCE=jwt-toy-client
ACCESS_TOKEN_EXPIRES_MIN=15
REFRESH_TOKEN_EXPIRES_DAYS=30

JWT_SECRET_KEY=CHANGE_ME_TO_A_LONG_RANDOM_SECRET
JWT_ALGORITHM=HS256
```

---

로컬 실행 방법

1. 가상환경 생성 및 활성화
```
python -m venv .venv
source .venv/bin/activate   # macOS/Linux
```

2. 패키지 설치
```
pip install -r requirements.txt
```

3. 서버 실행
```
uvicorn app.main:app --reload
```
