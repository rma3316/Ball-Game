# 🧱 Many Bricks Breaker (Python Clone)

파이썬(Pygame)으로 만든 'Many Bricks Breaker' 스타일의 하이퍼 캐주얼 벽돌 깨기 게임입니다.
수백 개의 공이 쏟아지는 쾌감과 다양한 특수 아이템을 즐겨보세요!

## 🎮 조작 방법 (Controls)
*   **이동:** 마우스 커서 이동 (좌/우)
*   **시작/재시작:** 마우스 클릭 또는 R 키

## 🎁 아이템 설명 (Items)
*   🔵 **+1**: 공이 1개 추가됩니다.
*   🟢 **x2**: 현재 화면의 모든 공이 2배로 복제됩니다.
*   🔴 **P (Power)**: 5초간 **관통 모드**! 일반 블록을 뚫고 지나가며, 단단한 블록(회색)을 파괴할 수 있습니다.
*   🟣 **M (Magnet)**: 자석 모드! 떨어지는 아이템을 패들 쪽으로 끌어당깁니다.
*   🟡 **L (Laser)**: 레이저 모드! 패들 양쪽에서 레이저가 나가 블록을 녹입니다.

## 🗺️ 맵 에디터 (Level Editor)
`main.py` 파일의 `LEVELS` 리스트를 수정하여 나만의 맵을 만들 수 있습니다.
*   `#`: 무지개 블록
*   `@`: 단단한 블록 (회색, 관통탄으로만 파괴 가능)
*   ` `: 빈 공간

## 🚀 실행 방법 (How to Run)
1. Python 설치
2. Pygame 설치: `pip install pygame`
3. 게임 실행: `python main.py`

## 🎨 Credits
*   **Development:** [본인 이름/닉네임]
*   **Engine:** Python + Pygame
*   **Font:** NanumGothic (Naver)
