import os
import time
import subprocess
import psutil
from translation import translations

players = ['Microsoft.Media.Player.exe', 'vlc.exe', 'PotPlayerMini64.exe']


def get_player_pid():
    for proc in psutil.process_iter(['pid', 'name']):
        pid = proc.info.get('pid')
        name = proc.info.get('name')
        if not pid or not name:
            continue
        if any(player.lower() in name.lower() for player in players):
            return pid
    return None

class VideoPlayer:
    def __init__(self, decrypted_path, language, message_callback):
        self.decrypted_path = decrypted_path
        self.language = language
        self.message_callback = message_callback
        self.is_play = False

    def play(self):
        self.is_play = True
        try:
            self.process = subprocess.Popen(
                f'start "" "{self.decrypted_path}"',
                 shell=True,
                 stdout=subprocess.PIPE,
                 stderr=subprocess.PIPE)
            found = False
            pid = None
            while not found:
                time.sleep(3)
                pid = get_player_pid()
                if not pid:
                    self.message_callback(translations[self.language]['player_pid_not_found'])
                    self.is_play = False
                else:
                    found = True
            self.message_callback(translations[self.language]['player_pid'].format(pid=pid))
            while psutil.pid_exists(pid):
                time.sleep(1)
            self.message_callback(translations[self.language]['player_closed'])
            self.delete_video_file()
            self.is_play = False
        except Exception as e:
            self.message_callback(translations[self.language]['play_error'].format(e=e))
            self.is_play = False

    def delete_video_file(self):
        for i in range(1, 11):
            self.message_callback(translations[self.language]['wait_delete_video'].format
                                  (s=11-i, decrypted_path=self.decrypted_path))
            time.sleep(1)
        if os.path.exists(self.decrypted_path):
            try:
                os.remove(self.decrypted_path)
                self.message_callback(translations[self.language]['video_deleted'].format
                                      (decrypted_path=self.decrypted_path))
            except Exception as e:
                self.message_callback(translations[self.language]['delete_video_error'].format(e=e))
                self.message_callback(translations[self.language]['delete_video_again'])
                self.delete_video_file()
        else:
            self.message_callback(translations[self.language]['file_not_exist'])