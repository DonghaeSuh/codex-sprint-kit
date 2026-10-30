# 공개 릴리스와 반입
공개 대상은 codex-sprint-kit 폴더 하나입니다. 상위 폴더나 운영 문서를 올리지 않습니다.
이 과정은 평가 시작 **전**에 완료하세요. 제한된 시험 중 Git push·외부 업로드를 하지 않습니다.

## 이 저장소의 사전 업데이트
공개 주소는 https://github.com/DonghaeSuh/codex-sprint-kit 입니다.
이미 생성된 저장소이므로 `gh repo create`를 다시 실행하지 않습니다.
아래는 시험 **전 준비 PC**의 kit 폴더에서만 쓰는 유지보수 명령입니다.
응시 세션의 시작 명령은 [README](../README.md)에 있습니다.

```bash
git status --short
python3 -m unittest discover -s tests -v
python3 scripts/provenance.py
gh auth status
git push origin main
git rev-parse HEAD
gh repo view DonghaeSuh/codex-sprint-kit --json visibility,url
```

`git push`는 이미 검토·커밋된 범용 키트 변경만 게시합니다.
미커밋 변경이 있다면 먼저 실제 과제 자료가 없는지 diff를 검토하고 해당 파일만 커밋합니다.
공개 후 로그인 없는 경로에서 고정 커밋을 clone하여 확인하세요.
결과 통지 전까지 공개를 유지하고, 평가 중 새 자료를 공급하는 저장소로 쓰지 않습니다.

## 응시 환경에서 허용된 반입
제공 환경의 과제 루트에서 허용되는 경우 실행합니다. 치환할 계정명·커밋 값이 없습니다.
가져온 버전은 SESSION.md 절차에 따라 STATE에 기록하고 세션 중 pull/update하지 않습니다.

```bash
git clone https://github.com/DonghaeSuh/codex-sprint-kit.git codex-sprint-kit
codex 'codex-sprint-kit/SESSION.md를 읽고 세션 시작 절차를 수행해줘. 실제 과제 README와 기존 지침을 우선하고, 실제 구현과 실험 및 기록은 이 응시 작업 공간 안에서만 진행해줘.'
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
