
# plotly-mcp

## 프로젝트 개요
plotly-mcp는 SQL 쿼리 결과를 시각화하기 위한 Model Context Protocol(MCP) 도구입니다. LLM이 데이터 시각화 도구로 Plotly를 활용할 수 있도록 설계되었습니다.

## 프로젝트 구조
```
plotly-mcp/
  ├── plot_desc.json     # 시각화 유형별 설명
  ├── plot_examples.json # 각 시각화 유형의 예제 데이터 형식
  ├── plot_tools.py      # MCP 도구 구현
  └── viz_tools.ipynb    # 개발 및 테스트용 노트북
```

## 주요 기능 요구사항
1. **SQL 쿼리 결과 처리**: SQL 실행 결과를 입력으로 받아 적절한 시각화 형식으로 변환
2. **다양한 시각화 지원**: 40+ Plotly 차트 유형 지원 (막대, 산점도, 파이 차트 등)
3. **자동 시각화 추천**: 데이터 특성에 맞는 최적의 시각화 유형 제안
4. **시각화 커스터마이징**: 색상, 레이아웃, 레이블 등 사용자 정의 옵션 제공
5. **MCP 인터페이스**: LLM이 시각화 도구에 접근할 수 있는 표준화된 인터페이스 제공

## 기술 요구사항
- Python 3.8+
- Plotly 5.0+
- pandas
- numpy
- LangChain 또는 유사한 MCP 프레임워크

## 설치 방법
```bash
git clone https://github.com/dshomin/plotly-mcp.git
cd plotly-mcp
pip install -r requirements.txt
```

## 사용 예시
```python
from plot_tools import PlotlyMCP

# SQL 쿼리 결과 (예시)
sql_result = {
    "columns": ["category", "value"],
    "data": [
        ["A", 10], 
        ["B", 15], 
        ["C", 7], 
        ["D", 12]
    ]
}

# MCP 초기화
viz_mcp = PlotlyMCP()

# 시각화 생성
fig = viz_mcp.visualize(
    data=sql_result,
    plot_type="bar",  # 선택적 - 지정하지 않으면 자동 추천
    title="카테고리별 값",
    x_label="카테고리",
    y_label="값"
)

# 결과 표시
fig.show()
```

## 개발 로드맵
1. **Phase 1**: 기본 MCP 인터페이스 구현 및 주요 차트 유형 지원
2. **Phase 2**: 자동 시각화 추천 알고리즘 개발
3. **Phase 3**: 고급 시각화 옵션 및 사용자 정의 기능 확장
4. **Phase 4**: 다중 데이터 소스 통합 및 결과 결합

## 개발 가이드
### 새 차트 유형 추가
1. `plot_desc.json`에 차트 설명 추가
2. `plot_examples.json`에 데이터 형식 예제 추가
3. `plot_tools.py`에 변환 로직 구현

### 데이터 처리 파이프라인
1. SQL 결과 → DataFrame 변환
2. 데이터 전처리 (타입 변환, 누락 값 처리 등)
3. 시각화 유형 선택/추천 
4. Plotly 차트 구성 및 렌더링

## API 명세 (계획)
```python
class PlotlyMCP:
    def visualize(data, plot_type=None, **kwargs):
        """주어진 데이터를 시각화하여 Plotly 그림 객체 반환"""
        
    def recommend_plot_type(data):
        """데이터 구조에 기반하여 최적의 시각화 유형 추천"""
        
    def get_plot_description(plot_type):
        """특정 시각화 유형에 대한 설명 반환"""
        
    def get_example(plot_type):
        """특정 시각화 유형의 예제 데이터와 코드 반환"""
```

## 데이터 형식
MCP는 다음과 같은 SQL 결과 형식을 처리할 수 있습니다:

1. **테이블 형식**: 열 이름 목록과 행 데이터 목록
2. **JSON 형식**: 레코드 배열 또는 객체 배열
3. **CSV 문자열**: 쉼표로 구분된 테이블 데이터

## 기여 방법
1. 이슈 등록 또는 기능 요청 제출
2. 포크 및 개발 브랜치 생성
3. 코드 변경 및 테스트 추가
4. 풀 리퀘스트 제출

## 라이선스
MIT

## 미래 확장 계획
- 대시보드 생성 기능
- 대화형 시각화 조정
- 다중 SQL 쿼리 결과 결합 및 비교
- 시각화 템플릿 및 스타일 라이브러리
- 시각화 결과 내보내기 (PNG, PDF, HTML)
