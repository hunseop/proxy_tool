"""정책 모듈 설정

Skyhigh SWG API 및 정책 관련 설정을 관리합니다.
"""

import os
from typing import Optional

class Config:
    # Skyhigh SWG API 설정
    SKYHIGH_BASE_URL: str = os.getenv('SKYHIGH_BASE_URL', 'https://api.skyhighsecurity.com')
    SKYHIGH_USERNAME: Optional[str] = os.getenv('SKYHIGH_USERNAME')
    SKYHIGH_PASSWORD: Optional[str] = os.getenv('SKYHIGH_PASSWORD')
    
    # 출력 설정
    EXPORT_DIR: str = os.getenv('EXPORT_DIR', 'exports')
    EXCEL_OUTPUT_DIR: str = os.getenv('EXCEL_OUTPUT_DIR', 'output')
    
    # 파싱 설정
    MAX_POLICY_SIZE: int = int(os.getenv('MAX_POLICY_SIZE', '10000'))  # 최대 정책 크기
    BATCH_SIZE: int = int(os.getenv('BATCH_SIZE', '1000'))  # 배치 처리 크기 