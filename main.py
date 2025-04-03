import csv
import paramiko
import time
import pandas as pd
from PyQt5.QtCore import QAbstractTableModel
from datetime import datetime
def connect_proxy(host):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username='root', password='123456')
    stdin, stdout, stderr = ssh.exec_command(cmd)
    lines = stdout.readlines()

    result = []
    for i in lines:
        re = str(i).replace('\n', '')
        arr = re.split(' | ')
        new_arr = [i.replace(' ', '') for i in arr]
        if new_arr[0] == "CreationTime" or len(new_arr[0]) == 0:
            continue
        result.append(new_arr)
    
    stdin.close()
    ssh.close()
    return result

def interruptible_sleep(seconds, is_running):
    end_time = time.time() + seconds
    while time.time() < end_time and is_running():
        time.sleep(0.1)

def split_line(lst:str) -> list:
    return [item.strip().rstrip('\n') for item in lst.split(' | ')]

def get_session(ip:str, username:str, password:str) -> pd.DataFrame:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip, username=username, password=password)
    stdin, stdout, stderr = ssh.exec_command('/opt/mwg/bin/mwg-core -S connections')
    lines = stdout.readlines()

    try:
        lines.pop(-1)
        header = split_line(lines[1])
        data = [split_line(line) for line in lines[2:]]
        session = pd.DataFrame(data, columns=header)
    except:
        session = None
    
    stdin.close()
    ssh.close()
    return session

def get_uniq_clients_from_session(session:pd.DataFrame) -> int:
    clients = session['Client IP']
    clients = clients.apply(lambda x: x.split(':')[0])
    uniq_clients = len(set(clients))
    return uniq_clients

def get_memory(ip:str, username:str, password:str):
    command = '''awk '/MemTotal/ {total=$2} /MemAvailable/ {available=$2} END {printf "%.0f", 100 - (available / total * 100)} /proc/meminfo'''
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip, username=username, password=password)
    stdin, stdout, stderr = ssh.exec_command(command)
    memory_value = stdout.readlines()
    stdin.close()
    ssh.close()
    try:
        memory_value = int(memory_value)
        return memory_value
    except:
        return "N/A"

class DataFrameModel(QAbstractTableModel):
    def __init__(self, df=pd.DataFrame(), parent=None):
        super(DataFrameModel, self).__init__(parent)
        self._df = df

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self._df.columns[section]
            if orientation == Qt.Vertical:
                return str(self._df.index[section])
        return None
    
    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return str(self._df.iloc[index.row(), index.column()])
        return None
    
    def rowCount(self, parent=None):
        return self._df.shape[0]
    
    def columnCount(self, parent=None):
        return self._df.shape[1]
    
    def sort(self, column, order):
        self.layoutAboutToChanged.emit()
        colname = self._df.columns[column]
        self._df = self._df.sort_values(colname, ascending=order == Qt.AscendingOrder)
        self.layoutChanged.emit()

class GetResource(QThread):
    resource_data = pyqtSignal(dict)

    def __init__(self, proxy_ip, delay_time):
        super().__init__()
        self.proxy_ip = proxy_ip
        self.is_running = False
        self.delay_time = delay_time
        self.proxy_id = 'root'
        self.proxy_pw = '123456' # 수정필요

        self.previous_http = 0
        self.previous_https = 0
        self.previous_ftp = 0

        # 수정필요
        self.oid_dict_os12 = {
            'CPU': '1.3.6.1.2.1.25.3.3.1.2.1',
            'Memory': '1.3.6.1.2.1.25.2.2.1.1',
            'CC': '1.3.6.1.2.1.25.4.2.1.2',
            'CS': '1.3.6.1.2.1.25.4.2.1.3',
            'HTTP': '1.3.6.1.2.1.25.4.2.1.2',
            'HTTPS': '1.3.6.1.2.1.25.4.2.1.3',
            'FTP': '1.3.6.1.2.1.25.4.2.1.4',
        }

    def run(self):
        self.is_running = True
        while self.is_running:
            try:
                start_time = time.time()
                oid_set = self.oid_dict_os12

                snmp_data = self.fetch_snmp_data(self.proxy_ip, oid_set)
                mem = get_memory(self.proxy_ip, self.proxy_id, self.proxy_pw)
                uc = get_uniq_clients_from_session(get_session(self.proxy_ip, self.proxy_id, self.proxy_pw))
                current_http = snmp_data['HTTP']
                current_https = snmp_data['HTTPS']
                current_ftp = snmp_data['FTP']
                http_diff = "계산중" if self.previous_http == 0 else f"{round((int(current_http) - int(self.previous_http))/1000000, 2)}MB"
                https_diff = "계산중" if self.previous_https == 0 else f"{round((int(current_https) - int(self.previous_https))/1000000, 2)}MB"
                ftp_diff = "계산중" if self.previous_ftp == 0 else f"{round((int(current_ftp) - int(self.previous_ftp))/1000000, 2)}MB"

                data = {
                    'date': str(datetime.now().strftime('%Y-%m-%d')),
                    'time': str(datetime.now().strftime('%H:%M:%S')),
                    'device': str(self.proxy_ip),
                    'cpu': str(snmp_data['CPU']),
                    'memory': str(mem),
                    'uc': str(uc),
                    'cc': str(snmp_data['CC']),
                    'cs': str(snmp_data['CS']),
                    'http': str(http_diff),
                    'https': str(https_diff),
                    'ftp': str(ftp_diff),
                }
            except:
                data = {
                    'date': str(datetime.now().strftime('%Y-%m-%d')),
                    'time': str(datetime.now().strftime('%H:%M:%S')),
                    'device': str(self.proxy_ip),
                    'cpu': "error",
                    'memory': "error",
                    'uc': "error",
                    'cc': "error",
                    'cs': "error",
                    'http': "error",
                    'https': "error",
                    'ftp': "error",
                }
            end_time = time.time()
            processing_time = end_time - start_time
            correction_time = round(self.delay_time - processing_time)
            self.resource_data.emit(data)
            interruptible_sleep(correction_time, self.is_running)
    
    def stop(self):
        self.is_running = False
    
    def fetch_snmp_data(self, server, oid_dict):
        odis = [ObjectType(ObjectIdentity(oid_dict[description])) for description in oid_dict]
        errorIndication, errorStatus, errorIndex, varBinds = next(
            getCmd(SnmpEngine(),
                   CommunityData('public'), # 수정필요
                   UdpTransportTarget((server, 161)),
                   ContextData(),
                   *odis
                   )
        )
        result_dict = {}

        if errorIndication:
            print(errorIndication)
        elif errorStatus:
            print(errorStatus)
        else:
            for varBind in varBind:
                oid, value = varBind
                description = [desc for desc, oid_str in oid_dict.items() if str(oid) == oid_str][0]
                result_dict[description] = value.prettyPrint()
        
        return result_dict
    
class GetSession(QThread):
    session_data = pyqtSignal(pd.DataFrame)

    def __init__(self, ip, username, password, cmd):
        super().__init__()
        self.ip = ip
        self.username = username
        self.password = password
        self.cmd = cmd

    def run(self):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(self.ip, username=self.username, password=self.password)
        stdin, stdout, stderr = ssh.exec_command(self.cmd)
        lines = stdout.readlines()

        session = []
        for i in lines:
            re = str(i).replace('\n', '')
            arr = re.split(' | ')
            new_arr = [i.replace(' ', '') for i in arr]
            if new_arr[0] == "CreationTime" or len(new_arr[0]) == 0:
                continue
            session.append(new_arr)
        
        stdin.close()
        ssh.close()
        
        session_df = pd.DataFrame(session)
        self.session_data.emit(session_df)

class MainWindow(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.setWindowTitle('Proxy Resource Monitor')
        self.hide_menu_hide()

        self.stackedWidget.setCurrentIndex(0)
        self.config_btn.clicked.connect(self.config_btn_clicked)
        
        # UI 부분 생략

    def start_get_session(self):
        proxy_id = "root"
        proxy_pw = "123456"
        devices = self.get_item_list()
        search_data = self.search_check()
        self.device_threads = {}
        self.total_threads = len(devices)
        self.completed_threads = 0

        global cmd
        cmd = """/opt/mwg/bin/mwg-core -S connections | awk -F " \\\\\\| " '{print $2" | "%5" | "%6" | "%6" | "%7" | "%18" | "%10" | "%11" | "%15"}'"""
        if search_data:
            cmd = cmd = """/opt/mwg/bin/mwg-core -S connections | awk -F " \\\\\\| " '{print $2" | "%5" | "%6" | "%6" | "%7" | "%18" | "%10" | "%11" | "%15"}' | grep \"""" + search_data + "\""
        for device in devices:
            self.device_threads[device] = GetSession(device, proxy_id, proxy_pw, cmd)
        
        session_result = []
        for device, thread in self.device_threads.items():
            thread.session_data.connect(self.store_dataframe)
            thread.finished.connect(self.on_thread_finished)
            thread.start()
    
    def on_thread_finished(self):
        self.completed_threads += 1
        if self.completed_threads == self.total_threads:
            self.update_session_table()
    
    def store_dataframe(self, df):
        self.dataframes.append(df)

    def update_session_table(self):
        if self.dataframes:
            try:
                merged_df = pd.concat(self.dataframes, ignore_index=True)
                merged_df.columns = ['Creation Time', 'Username', 'Client IP', 'Proxy IP', 'URL', 'CL Bytes Received', 'CL Bytes Sent', 'Age(seconds)']
                merged_df['CL Bytes Received'] = pd.to_numeric(merged_df['CL Bytes Received'])
                merged_df['CL Bytes Sent'] = pd.to_numeric(merged_df['CL Bytes Sent'])
                merged_df['Age(seconds)'] = pd.to_numeric(merged_df['Age(seconds)'])

                row_length = len(merged_df)
                
                if row_length == 0:
                    QMessageBox.warning(self, '경고', '세션 데이터가 없습니다.')
                else:
                    self.model = DataFrameModel(merged_df)
                    self.tableView.setModel(self.model)
                    self.tableView.resizeColumnsToContents()
                    self.tableView.setColumnWidth(4, 300)
            except Exception as e:
                QMessageBox.warning(self, '경고', f'세션 데이터 업데이트 중 오류 발생: {e}')
                self.tableView.setModel(None)
        else:
            QMessageBox.warning(self, '경고', '세션 데이터가 없습니다.')
        self.dataframes = []
    
    def config_btn_clicked(self):
        self.stackedWidget.setCurrentIndex(1)
    
    def start_get_resource(self):
        self.device_threads = {}
        self.row_positions = {}
        devices = self.get_item_list()
        self.device_row_mapping = {}
        delay_time = int(self.time_comboBox.currentText())
        for device in devices:
            self.device_threads[device] = GetResource(device, delay_time)
        
        self.resource_table.setRowCount(len(devices))
        QMessageBox.information(self, '알림', '자원 모니터링을 시작합니다.')
        row_position = 0
        for device, thread in self.device_threads.items():
            self.row_positions[device] = row_position
            row_position += 1
            thread.resource_data.connect(self.update_resource_table)
            thread.resource_data.connect(self.log_resource)
            thread.start()
    
    def log_resource(self, data):
        filename = datetime.now().strftime('%Y-%m-%d') + '_log.csv'
        with open(filename, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['date', 'time', 'device', 'cpu', 'memory', 'uc', 'cc', 'cs', 'http', 'https', 'ftp'])

            if not file_exists:
                writer.writeheader()
            
            writer.writerow(data)
    
    def stop_get_resource(self):
        for thread in self.device_threads.values():
            thread.stop()
    
    def update_resource_table(self, data):
        proxy_ip = data['device']
        row_position = self.row_positions[proxy_ip]

        field_names = ['date', 'time', 'device', 'cpu', 'memory', 'uc', 'cc', 'cs', 'http', 'https', 'ftp']
        cpu_threshold = 10
        mem_threshold = 21
        for i, name in enumerate(field_names):
            item = QTableWidgetItem(str(data[name]))
            if name == 'cpu':
                if data[name] == 'error':item.setForeground(QColor("red"))
                elif int(data[name]) >= int(cpu_threshold): item.setForeground(QColor("red"))
            elif name == 'mem':
                if data[name] == 'error': item.setForeground(QColor("red"))
                elif int(data[name]) >= int(mem_threshold): item.setForeground(QColor("red"))
            
            self.resource_table.setItem(row_position, i, item)
        
        self.adjust_sizes()
    
    def adjust_sizes(self):
        pass
    
    # 생략