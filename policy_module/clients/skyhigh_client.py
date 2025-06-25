"""Skyhigh SWG API 클라이언트

정책 데이터를 가져오고 관리하기 위한 Skyhigh Security Web Gateway API 클라이언트입니다.
"""

import requests
from requests.auth import HTTPBasicAuth
from urllib.parse import urljoin
import xml.etree.ElementTree as ET
import logging
import urllib3
from datetime import datetime
import os
import re
import xmltodict
import json

from ..config import Config, ProxyConfig

# 보안 경고 무시
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 로깅 설정
logger = logging.getLogger(__name__)

class SkyhighSWGClient:
    """Skyhigh SWG API 클라이언트
    
    정책 데이터를 가져오고 관리하기 위한 클라이언트입니다.
    세션 관리와 정책 데이터 내보내기 기능을 제공합니다.
    """
    
    def __init__(self, proxy_config: ProxyConfig):
        """
        Args:
            proxy_config (ProxyConfig): 프록시 설정
        """
        self.proxy_config = proxy_config
        self.session = requests.Session()
        self.session_id = None

    def login(self):
        """API 로그인 및 세션 설정"""
        login_url = urljoin(self.proxy_config.base_url + '/', 'login')
        response = self.session.post(
            login_url, 
            auth=HTTPBasicAuth(self.proxy_config.username, self.proxy_config.password), 
            verify=False
        )
        
        if response.status_code == 200:
            if 'Set-Cookie' in response.headers:
                for cookie in response.headers['Set-Cookie'].split(';'):
                    if cookie.strip().startswith('JSESSIONID='):
                        self.session_id = cookie.strip().split('=')[1]
                        break
            if self.session_id:
                logger.info(f"프록시 {self.proxy_config.base_url} 로그인 성공")
            else:
                raise Exception("세션 ID를 찾을 수 없습니다.")
        else:
            raise Exception(f"로그인 실패: {response.status_code} {response.text}")

    def _build_url(self, endpoint):
        """API 엔드포인트 URL 생성"""
        if not self.session_id:
            raise Exception("세션 ID가 없습니다. 먼저 로그인해야 합니다.")
        return urljoin(self.proxy_config.base_url + '/', f"{endpoint};jsessionid={self.session_id}")

    def logout(self):
        """API 로그아웃"""
        logout_url = self._build_url('logout')
        response = self.session.post(logout_url, verify=False)
        if response.ok:
            logger.info(f"프록시 {self.proxy_config.base_url} 로그아웃 완료")
        else:
            raise Exception(f"로그아웃 실패: {response.status_code} {response.text}")

    def list_rulesets(self, top_level_only=False, page=1, page_size=-1):
        """Rule Set 목록 조회
        
        Args:
            top_level_only (bool): 최상위 Rule Set만 조회
            page (int): 페이지 번호
            page_size (int): 페이지 크기
            
        Returns:
            list: Rule Set 목록
        """
        params = {
            'topLevelOnly': str(top_level_only).lower(),
            'page': page,
            'pageSize': page_size
        }
        url = self._build_url('rulesets')
        response = self.session.get(url, params=params, verify=False)
        
        if response.ok:
            try:
                root = ET.fromstring(response.text)
                rulesets = []
                for entry in root.findall('entry'):
                    rule = {
                        'id': entry.findtext('id', default=''),
                        'title': entry.findtext('title', default=''),
                        'position': entry.findtext('position', default=''),
                        'enabled': entry.findtext('enabled', default=''),
                        'no_of_child': entry.findtext('noOfChild', default=''),
                        'link': entry.find('link').get('href') if entry.find('link') is not None else None,
                        'parent_id': None
                    }
                    rulesets.append(rule)
                return rulesets
            except ET.ParseError as e:
                logger.error(f"XML 파싱 오류: {e}")
                raise
        else:
            raise Exception(f"Rule Set 목록 조회 실패: {response.status_code} {response.text}")

    def export_ruleset(self, ruleset_id, title):
        """Rule Set을 내보내고 파싱
        
        Args:
            ruleset_id (str): Rule Set ID
            title (str): Rule Set 제목
            
        Returns:
            뭐라고 해야해 이거
        """
        url = self._build_url(f'rulesets/rulegroups/{ruleset_id}/export')
        response = self.session.post(url, verify=False)
        
        if response.ok:
            logger.info(f"Rule Set '{title}'이(가) 추출 되었습니다.")
            return response.content
        else:
            raise Exception(f"Rule Set '{title}' 내보내기 실패: {response.status_code} {response.text}")

    def __enter__(self):
        self.login()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logout()    