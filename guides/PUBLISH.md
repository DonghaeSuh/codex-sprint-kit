# 공개 릴리스와 반입
공개 대상은 codex-sprint-kit 폴더 하나입니다. 상위 폴더나 운영 문서를 올리지 않습니다.
이 과정은 평가 시작 **전**에 완료하세요. 제한된 시험 중 Git push·외부 업로드를 하지 않습니다.

## 사전 공개
먼저 현재 폴더가 kit인지 확인하고 파일 목록과 release manifest를 검토합니다.
네트워크와 GitHub 인증이 정상인 사용자 터미널에서 실행합니다.
아래 owner는 본인 계정으로 바꾸고, 이미 존재하는 저장소를 덮어쓰지 않습니다.

```bash
git status --short
python3 -m unittest discover -s tests -v
python3 scripts/provenance.py
gh auth status
# 인증이 필요할 때만 사용자 터미널에서 gh auth login 실행. 토큰을 채팅에 붙이지 마세요.
gh repo create OWNER/codex-sprint-kit --public --source=. --remote=origin --push
git rev-parse HEAD
gh repo view OWNER/codex-sprint-kit --json visibility,url
```

위 git 명령은 kit가 독립 Git 저장소로 준비된 뒤 사용합니다.
공개 후 로그인 없는 경로에서 고정 커밋을 clone하여 확인하세요.
결과 통지 전까지 공개를 유지하고, 평가 중 새 자료를 공급하는 저장소로 쓰지 않습니다.

## 응시 환경에서 허용된 반입
제공 환경의 과제 루트에서 허용되는 경우 실행합니다. COMMIT은 사전에 확인한 40자리 SHA입니다.
주소가 공개되기 전에는 아래 명령으로 다운로드할 수 없습니다.

```bash
git clone https://github.com/OWNER/codex-sprint-kit.git codex-sprint-kit
git -C codex-sprint-kit checkout --detach COMMIT
python3 codex-sprint-kit/scripts/doctor.py --root .
python3 codex-sprint-kit/scripts/init_workspace.py --root .
codex
```

clone이 차단되면 대체 접속 경로로 우회하지 않습니다.
허용된 제공 도구로 실제 작업 환경 안에서 짧은 작업 계획을 직접 작성하고 진행합니다.
로컬 파일 업로드·별도 비공개 저장소는 반입 경로가 아닙니다.

## 공개 전 확인
- 원본 과제·스크린샷·메일·개인 URL·키·토큰·실제 결과물이 없음.
- 새로 작성한 범용 지침·스크립트·합성 연습만 포함.
- .sprint 실행 로그와 개인 운영 문서는 Git에 포함되지 않음.
- 출처는 reference-only이며 재배포 불명확한 파일을 복사하지 않음.
- 제공 AI·Codex 버전·보안 설정을 자동 변경하지 않음.
- archive와 manifest는 검수 대상이며 공개되었다는 증거는 별도 필요.
