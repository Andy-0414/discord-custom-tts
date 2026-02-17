# Discord Custom TTS Bot

Qwen3-TTS를 사용한 Discord 음성 클론 봇입니다. 3초 길이의 오디오 샘플로 목소리를 클론하여, Discord 채팅 메시지를 해당 목소리로 읽어줍니다.

## 특징

- 🎙️ **Voice Cloning**: Qwen3-TTS 기반 음성 클론 (3초 샘플로 가능)
- 🤖 **Discord Integration**: Discord.py를 활용한 음성 채널 연동
- 🚀 **GPU Acceleration**: CUDA 지원으로 빠른 음성 생성
- 🇰🇷 **한국어 지원**: 한국어 TTS 완벽 지원
- 🔧 **확장 가능**: 여러 목소리 프로필 관리

## 요구사항

### 하드웨어
- NVIDIA GPU (CUDA 지원)
- 최소 8GB VRAM 권장

### 소프트웨어
- Python 3.10+
- CUDA Toolkit 11.8+
- FFmpeg (Discord 음성 재생용)

## 설치

### 1. 저장소 클론

```bash
git clone https://github.com/Andy-0414/discord-custom-tts.git
cd discord-custom-tts
```

### 2. 가상환경 생성

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. 의존성 설치

```bash
pip install -r requirements.txt
```

### 4. 환경 설정

`.env.example`을 복사해서 `.env` 파일을 만듭니다:

```bash
cp .env.example .env
```

`.env` 파일을 수정해서 Discord 봇 토큰과 설정을 입력합니다:

```env
DISCORD_TOKEN=your_discord_bot_token_here
GUILD_ID=your_guild_id_here
DEFAULT_VOICE=jonghun
DEVICE=cuda:0
ADMIN_IDS=123456789012345678
```

### 5. 목소리 프로필 설정

`voices/jonghun/` 디렉토리에 참조 오디오를 준비합니다:

1. **reference.wav**: 3초 이상의 깨끗한 음성 샘플 (WAV 형식)
2. **reference.txt**: 참조 오디오의 정확한 텍스트 (한국어)

예시:
```
voices/
└── jonghun/
    ├── reference.wav
    └── reference.txt (내용: "안녕하세요, 저는 종훈입니다.")
```

### 6. Discord 봇 설정

1. [Discord Developer Portal](https://discord.com/developers/applications)에서 봇 생성
2. **Bot** 탭에서 토큰 복사 → `.env`의 `DISCORD_TOKEN`에 입력
3. **Privileged Gateway Intents** 활성화:
   - ✅ MESSAGE CONTENT INTENT
   - ✅ SERVER MEMBERS INTENT
4. **OAuth2 → URL Generator**:
   - Scopes: `bot`
   - Bot Permissions: `Send Messages`, `Connect`, `Speak`, `Use Voice Activity`
   - 생성된 URL로 봇을 서버에 초대

## 실행

### 로컬 실행

```bash
python bot.py
```

### Docker 실행

```bash
docker-compose up -d
```

봇이 시작되면 Discord에서 "온라인" 상태가 됩니다.

## 사용법

### 기본 명령어

- **!tts <텍스트>**: 텍스트를 음성으로 변환하여 재생
  ```
  !tts 안녕하세요! 오늘 날씨가 좋네요.
  ```

- **!join**: 봇을 현재 음성 채널로 초대
  ```
  !join
  ```

- **!leave**: 봇을 음성 채널에서 내보내기
  ```
  !leave
  ```

- **!voices**: 사용 가능한 목소리 프로필 목록
  ```
  !voices
  ```

- **!help**: 도움말 표시
  ```
  !help
  ```

### 관리자 명령어

- **!clone <이름>**: 새로운 목소리 프로필 생성 (오디오 파일 첨부 필요)
  ```
  !clone myvoice
  (오디오 파일 첨부)
  ```

## 프로젝트 구조

```
discord-custom-tts/
├── bot.py                 # Discord 봇 메인 로직
├── tts_engine.py          # Qwen3-TTS 래퍼
├── voice_manager.py       # Discord 음성 채널 관리
├── config.py              # 설정 관리
├── requirements.txt       # Python 의존성
├── .env.example           # 환경변수 템플릿
├── .gitignore             # Git 무시 파일
├── Dockerfile             # Docker 이미지 정의
├── docker-compose.yml     # Docker Compose 설정
├── README.md              # 프로젝트 설명서
├── voices/                # 목소리 프로필 디렉토리
│   └── jonghun/
│       ├── reference.wav
│       └── reference.txt
└── temp/                  # 임시 오디오 파일 (자동 생성)
```

## 기술 스택

- **TTS Engine**: [Qwen3-TTS](https://github.com/QwenLM/Qwen3-TTS) (Voice Clone 1.7B Base)
- **Discord Library**: discord.py 2.3+
- **ML Framework**: PyTorch 2.0+
- **Audio Processing**: soundfile, PyNaCl

## 트러블슈팅

### CUDA 메모리 부족

모델 로드 시 메모리 부족 오류가 발생하면:

1. `config.py`에서 `dtype`을 `torch.float16`으로 변경
2. 다른 GPU 프로그램 종료
3. GPU 메모리가 8GB 미만이면 CPU 모드 사용 (`DEVICE=cpu`)

### 음성 재생 안 됨

FFmpeg가 설치되어 있는지 확인:

```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Windows
# https://ffmpeg.org/download.html
```

### 봇이 음성 채널에 연결 안 됨

Discord 봇 권한 확인:
- ✅ Connect (음성 채널 연결)
- ✅ Speak (음성 재생)
- ✅ Use Voice Activity (음성 활동 사용)

## 라이선스

MIT License

## 기여

이슈 및 Pull Request 환영합니다!

## 작성자

Andy-0414 (pjh8667@gmail.com)
