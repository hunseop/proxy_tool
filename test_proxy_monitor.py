#!/usr/bin/env python3
import argparse
import os
from proxy_monitor_core import ResourceMonitor, Config
from tabulate import tabulate
import json

def load_config(args):
    """커맨드 라인 인자로 설정 업데이트"""
    if args.username:
        Config.SSH_USERNAME = args.username
    if args.password:
        Config.SSH_PASSWORD = args.password
    
    # 환경 변수에서도 설정을 가져올 수 있도록 함
    Config.SSH_USERNAME = os.getenv('PROXY_SSH_USER', Config.SSH_USERNAME)
    Config.SSH_PASSWORD = os.getenv('PROXY_SSH_PASS', Config.SSH_PASSWORD)
    Config.SNMP_COMMUNITY = os.getenv('PROXY_SNMP_COMMUNITY', Config.SNMP_COMMUNITY)

def format_session_data(sessions):
    """세션 데이터를 테이블 형식으로 포맷팅"""
    if sessions.empty:
        return "세션 데이터가 없습니다."
    
    return tabulate(sessions, headers='keys', tablefmt='grid', showindex=False)

def format_resource_data(data):
    """리소스 데이터를 보기 좋게 포맷팅"""
    # 데이터를 보기 좋게 정렬
    formatted = [
        ["시간", f"{data['date']} {data['time']}"],
        ["장비", data['device']],
        ["CPU 사용률", f"{data['cpu']}%"],
        ["메모리 사용률", f"{data['memory']}%"],
        ["고유 클라이언트", data['uc']],
        ["동시접속자", data['cc']],
        ["현재세션수", data['cs']],
        ["HTTP 트래픽", data['http']],
        ["HTTPS 트래픽", data['https']],
        ["FTP 트래픽", data['ftp']]
    ]
    
    return tabulate(formatted, tablefmt='grid')

def main():
    parser = argparse.ArgumentParser(description='프록시 서버 모니터링 도구')
    parser.add_argument('host', help='프록시 서버 IP 주소')
    parser.add_argument('--username', '-u', default=None, help='SSH 사용자명')
    parser.add_argument('--password', '-p', default=None, help='SSH 비밀번호')
    parser.add_argument('--type', '-t', choices=['session', 'resource', 'both'], 
                      default='both', help='조회할 데이터 유형')
    parser.add_argument('--json', '-j', action='store_true', 
                      help='JSON 형식으로 출력')
    
    args = parser.parse_args()
    
    # 설정 로드
    load_config(args)
    
    try:
        monitor = ResourceMonitor(args.host)  # username과 password는 Config에서 가져옴
        
        if args.type in ['session', 'both']:
            print("\n=== 세션 정보 ===")
            sessions = monitor.session_manager.get_session()
            if args.json:
                print(sessions.to_json(orient='records', force_ascii=False))
            else:
                print(format_session_data(sessions))
        
        if args.type in ['resource', 'both']:
            print("\n=== 리소스 정보 ===")
            resource_data = monitor.get_resource_data()
            if args.json:
                print(json.dumps(resource_data, ensure_ascii=False, indent=2))
            else:
                print(format_resource_data(resource_data))
                
    except Exception as e:
        print(f"오류 발생: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())