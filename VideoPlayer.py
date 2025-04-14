import os
import time
import subprocess
import psutil

players = ['Microsoft.Media.Player.exe', 'vlc.exe', 'PotPlayerMini64.exe']

class VideoPlayer:
    def __init__(self, decrypted_path, message_callback):
        self.decrypted_path = decrypted_path
        self.message_callback = message_callback
        self.is_play = False

    def get_player_pid(self):
        for proc in psutil.process_iter(['pid', 'name']):
            pid = proc.info.get('pid')
            name = proc.info.get('name')
            if not pid or not name:
                continue
            if any(player.lower() in name.lower() for player in players):
                return pid
        return None

    def play(self):
        self.is_play = True
        try:
            self.process = subprocess.Popen(
                f'start "" "{self.decrypted_path}"',
                 shell=True,
                 stdout=subprocess.PIPE,
                 stderr=subprocess.PIPE)
            time.sleep(10)
            pid = self.get_player_pid()
            if not pid:
                self.message_callback('未找到播放器的進程\n')
                self.is_play = False
                return
            self.message_callback(f'播放器的進程 PID: {pid}\n')
            while psutil.pid_exists(pid):
                time.sleep(1)
            self.message_callback(f'已關閉播放器進程\n')
            self.delete_video_file()
            self.is_play = False
        except Exception as e:
            self.message_callback(f'播放錯誤: {e}\n')
            self.is_play = False

    def delete_video_file(self):
        for i in range(1, 11):
            self.message_callback(f'等待{11 - i}秒後刪除檔案: {self.decrypted_path}\n')
            time.sleep(1)
        if os.path.exists(self.decrypted_path):
            try:
                os.remove(self.decrypted_path)
                self.message_callback(f'檔案 {self.decrypted_path} 已刪除\n')
            except Exception as e:
                self.message_callback(f'刪除檔案錯誤: {e}\n')
                self.message_callback('再次嘗試刪除檔案')
                self.delete_video_file()
        else:
            self.message_callback('檔案不存在\n')