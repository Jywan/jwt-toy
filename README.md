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
- **DB**: MySQL
- **ORM / Migration**: SQLAlchemy, Alembic
- **Dev Tool**: VS Code, Postman

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

---

### 보안 포인트

- Access / Refresh Token 분리 전략
- Refresh Token은 JavaScript에서 접근 불가(HttpOnly)
- Refresh Token **DB 영속화**
- Refresh Token **원문 미저장 (SHA-256 해시 저장)**
- Refresh Token **Rotation(회전)** 적용
- 폐기된 Refresh Token 재사용 시 **세션 체인 전체 폐기**
- 비밀번호는 bcrypt 해시로 저장

---

## 현재 구현된 기능

### Auth API

| Method | Endpoint       | Description |
|--------|----------------|-------------|
| POST   | /auth/login    | 로그인 (Access 발급 + Refresh 쿠키 설정) |
| POST   | /auth/refresh  | Refresh Token 회전(Rotation) 및 Access 재발급 |
| POST   | /auth/logout   | Refresh Token 폐기 및 쿠키 삭제 |

---

### 인증 / 보안 구현 상세

- User 테이블 기반 인증
- Refresh Token 테이블을 통한 토큰 관리
- Refresh Token은 1회성 사용
- 토큰 탈취/재사용 탐지 시 동일 family_id 전체 무효화
- 로그아웃 시 Refresh Token 폐기

---

## 프로젝트 구조

```text
jwt-toy/
├─ app/
│  ├─ main.py              # FastAPI 엔트리포인트
│  ├─ core/
│  │  ├─ config.py         # 환경변수 설정
│  │  ├─ security.py       # JWT / bcrypt / token 유틸
│  │  └─ deps.py           # DB Session 의존성
│  ├─ db/
│  │  ├─ base.py           # SQLAlchemy Base
│  │  └─ models.py         # User / RefreshToken 모델
│  └─ routers/
│     └─ auth.py           # 인증 API
├─ alembic/                # DB 마이그레이션
├─ scripts/
│  └─ seed_user.py         # 초기 사용자 시드
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

DATABASE_URL=mysql+pymysql://jwttoy:jwttoy_pw@localhost:3306/jwttoy
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

3. DB 실행 (Docker)
```
docker compose up -d
```

4. 마이그레이션 적용
```
alembic upgrade head
```

5. 테스트 사용자 생성
```
python -m script.seed_user
```

6. 서버 실행
```
uvicorn app.main:app --reload
```
