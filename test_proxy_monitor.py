#!/usr/bin/env python3
import argparse
import os
from proxy_monitor_core import ResourceMonitor, SessionManager, Config
from tabulate import tabulate
import json
from datetime import datetime

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

def save_session_to_excel(sessions, host):
    """세션 데이터를 엑셀 파일로 저장"""
    if sessions.empty:
        print("저장할 세션 데이터가 없습니다.")
        return
    
    # 현재 시간을 파일명에 포함
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'session_data_{host}_{timestamp}.xlsx'
    
    try:
        # DataFrame을 엑셀로 저장
        sessions.to_excel(filename, index=False, engine='openpyxl')
        print(f"\n세션 데이터가 '{filename}' 파일로 저장되었습니다.")
        
        # 데이터 기본 정보 출력
        print("\n=== 데이터 정보 ===")
        print(f"총 레코드 수: {len(sessions)}")
        print("\n=== 컬럼별 null 값 개수 ===")
        print(sessions.isnull().sum())
        print("\n=== 컬럼별 unique 값 개수 ===")
        print(sessions.nunique())
        
        # Username과 Proxy IP 컬럼의 유니크 값들 출력
        print("\n=== Username 고유 값 ===")
        print(sessions['Username'].unique())
        print("\n=== Proxy IP 고유 값 ===")
        print(sessions['Proxy IP'].unique())
        
    except Exception as e:
        print(f"엑셀 파일 저장 중 오류 발생: {e}")

def format_resource_data(data):
    """리소스 데이터를 보기 좋게 포맷팅"""
    # 데이터를 보기 좋게 정렬
    formatted = [
        ["시간", f"{data['date']} {data['time']}"],
        ["장비", data['device']],
        ["CPU 사용률", f"{data['cpu']}%"],
        ["메모리 사용률", f"{data['memory']}%"],
        ["고유 클라이언트", data['uc']],
        ["현재 연결", data['cc']],
        ["현재 세션", data['cs']],
        ["HTTP", data['http']],
        ["HTTPS", data['https']],
        ["FTP", data['ftp']]
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
    parser.add_argument('--excel', '-e', action='store_true',
                      help='세션 데이터를 엑셀 파일로 저장')
    
    args = parser.parse_args()
    
    # 설정 로드
    load_config(args)
    
    try:
        if args.type in ['session', 'both']:
            print("\n=== 세션 정보 ===")
            session_manager = SessionManager(args.host)
            sessions = session_manager.get_session()
            save_session_to_excel(sessions, args.host)
        
        if args.type in ['resource', 'both']:
            print("\n=== 리소스 정보 ===")
            monitor = ResourceMonitor(args.host)
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