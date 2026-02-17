# Discord Custom TTS Bot

Qwen3-TTS 기반 Discord 음성 클론 봇

## 특징

- 🎙️ Qwen3-TTS Voice Clone (0.6B 모델)
- ⚡ FlashAttention2 최적화 (2-3배 빠름)
- 🔥 torch.compile() JIT 컴파일
- 🎵 병렬 스트리밍 재생
- 🇰🇷 한국어 TTS 지원

## 요구사항

- Python 3.10+
- Windows 10/11
- NVIDIA GPU (CUDA 12.4+)
- Discord Bot Token

## 설치

```bash
# 1. 가상환경 생성
python -m venv venv

# 2. 의존성 설치
venv\Scripts\pip.exe install -r requirements.txt

# 3. FlashAttention2 설치 (Windows)
# kingbri1/flash-attention releases에서 적절한 wheel 다운로드
venv\Scripts\pip.exe install flash_attn-2.8.2+cu124torch2.6.0cxx11abiFALSE-cp310-cp310-win_amd64.whl

# 4. .env 파일 생성
copy .env.example .env
# DISCORD_TOKEN, GUILD_ID 등 설정
```

## 실행

### Windows (권장)

```bash
# 시작
start.bat

# 또는 PowerShell
.\start.ps1

# 종료
stop.bat
```

### 수동 실행

```bash
venv\Scripts\python.exe bot.py
```

## 환경 변수 (.env)

```env
DISCORD_TOKEN=your_discord_bot_token
GUILD_ID=your_guild_id
DEFAULT_VOICE=jang
DEVICE=cuda:0
ADMIN_IDS=your_user_id
MODEL_SIZE=0.6B
USE_FLASH_ATTN=true
```

## 명령어

- `!tts <텍스트>` - TTS 생성
- `!stream <텍스트>` - 스트리밍 TTS (병렬 처리)
- `!join` - 음성 채널 참가
- `!leave` - 음성 채널 나가기
- `!voices` - 사용 가능한 목소리 목록
- `!clone <이름>` - 새 목소리 추가 (관리자)
- `!commands` - 도움말

## 음성 프로필 추가

1. 3초 이상의 깨끗한 음성 녹음 (WAV)
2. `voices/<이름>/reference.wav`로 저장
3. `voices/<이름>/reference.txt`에 녹음 텍스트 입력
4. Discord에서 `!clone <이름>` 명령어로 등록

## 성능 최적화

**현재 구성:**
- 0.6B 모델: 1.7B 대비 2-3배 빠름
- FlashAttention2: 추가 2-3배 향상
- torch.compile(): 20-30% 향상
- **전체: 기본 대비 5-7배 빠름**

**모델 변경:**
```env
MODEL_SIZE=0.6B  # 빠름, 품질 약간 낮음
MODEL_SIZE=1.7B  # 느림, 품질 높음
```

**FlashAttention2 비활성화:**
```env
USE_FLASH_ATTN=false  # dtype 에러 시
```

## 트러블슈팅

### FlashAttention2 dtype 에러
```env
USE_FLASH_ATTN=false
```

### GPU 메모리 부족
```env
MODEL_SIZE=0.6B  # 더 작은 모델 사용
```

### 봇이 응답하지 않음
- Discord Privileged Intents 활성화 확인
- MESSAGE CONTENT INTENT 필수

## 라이선스

MIT

## 기술 스택

- [Qwen3-TTS](https://github.com/QwenLM/Qwen-Audio) - 음성 합성
- [discord.py](https://github.com/Rapptz/discord.py) - Discord API
- [Flash-Attention](https://github.com/Dao-AILab/flash-attention) - 최적화
- [PyTorch](https://pytorch.org/) - 딥러닝 프레임워크
