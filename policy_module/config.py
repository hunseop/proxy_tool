"""정책 모듈 설정

Skyhigh SWG API 및 정책 관련 설정을 관리합니다.
"""

from typing import Optional, List
from dataclasses import dataclass

@dataclass
class ProxyConfig:
    """프록시 설정 클래스"""
    base_url: str
    username: str
    password: str
    is_main: bool = False
    cluster_name: Optional[str] = None

class Config:
    """설정 관리 클래스"""
    def __init__(
        self,
        proxies: List[ProxyConfig],
    ):
        self.proxies = proxies
        
        # Main 프록시 검증
        main_proxies = [p for p in proxies if p.is_main]
        if not main_proxies:
            raise ValueError("메인 프록시가 지정되지 않았습니다.")
        if len(main_proxies) > 1:
            raise ValueError("메인 프록시는 하나만 지정할 수 있습니다.")
        
        # 클러스터 검증
        clusters = {}
        for proxy in proxies:
            if proxy.cluster_name:
                if proxy.cluster_name not in clusters:
                    clusters[proxy.cluster_name] = []
                clusters[proxy.cluster_name].append(proxy)
        
        self.clusters = clusters
    
    @property
    def main_proxy(self) -> ProxyConfig:
        """메인 프록시 설정 반환"""
        return next(p for p in self.proxies if p.is_main)
    
    def get_cluster_proxies(self, cluster_name: str) -> List[ProxyConfig]:
        """클러스터에 속한 프록시 목록 반환"""
        return self.clusters.get(cluster_name, []) 