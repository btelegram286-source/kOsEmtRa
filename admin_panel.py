#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
👑 Naofumi Bot Admin Paneli
Bot yönetimi ve istatistik sistemi
"""

import json
import time
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any

class AdminPanel:
    def __init__(self):
        """Admin paneli başlat"""
        self.stats_file = "bot_stats.json"
        self.admin_file = "admin_users.json"
        self.settings_file = "bot_settings.json"
        
        # Süper admin (kurucu) - kimse çıkaramaz
        self.SUPER_ADMIN_ID = 8486350475  # Sizin gerçek ID'niz
        
        # İstatistik verileri
        self.stats = self.load_stats()
        
        # Admin kullanıcıları
        self.admins = self.load_admins()
        
        # Bot ayarları
        self.settings = self.load_settings()
        
        # Admin komutları
        self.admin_commands = {
            '/admin_stats': self.get_admin_stats,
            '/admin_users': self.get_user_list,
            '/admin_ban': self.ban_user,
            '/admin_unban': self.unban_user,
            '/admin_settings': self.get_settings,
            '/admin_set': self.update_setting,
            '/admin_restart': self.restart_bot,
            '/admin_clean': self.clean_all_data,
            # Süper admin komutları
            '/super_admin_info': self.get_super_admin_info,
            '/super_admin_promote': self.promote_to_super_admin,
            '/super_admin_demote': self.demote_from_super_admin,
            '/super_admin_reset': self.reset_admin_system
        }
    
    def load_stats(self) -> Dict:
        """İstatistikleri yükle"""
        try:
            if os.path.exists(self.stats_file):
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"İstatistik yükleme hatası: {e}")
        
        # Varsayılan istatistikler
        return {
            'total_users': 0,
            'total_downloads': 0,
            'total_gui_commands': 0,
            'start_time': time.time(),
            'daily_stats': {},
            'user_activity': {},
            'command_usage': {},
            'errors': []
        }
    
    def load_admins(self) -> List[int]:
        """Admin kullanıcıları yükle"""
        try:
            if os.path.exists(self.admin_file):
                with open(self.admin_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Admin yükleme hatası: {e}")
        
        # Varsayılan admin (bot sahibi)
        return [123456789]  # Buraya kendi Telegram ID'nizi yazın
    
    def load_settings(self) -> Dict:
        """Bot ayarlarını yükle"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Ayarlar yükleme hatası: {e}")
        
        # Varsayılan ayarlar
        return {
            'max_file_size': 2 * 1024 * 1024 * 1024,  # 2GB
            'allowed_formats': ['mp3', 'mp4', 'avi', 'mkv'],
            'auto_delete_temp': True,
            'rate_limit_per_minute': 10,
            'maintenance_mode': False,
            'welcome_message': "Hoş geldiniz!",
            'banned_users': [],
            'feature_flags': {
                'video_download': True,
                'gui_control': True,
                'screenshot': True,
                'admin_panel': True
            }
        }
    
    def save_stats(self):
        """İstatistikleri kaydet"""
        try:
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump(self.stats, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"İstatistik kaydetme hatası: {e}")
    
    def save_admins(self):
        """Admin listesini kaydet"""
        try:
            with open(self.admin_file, 'w', encoding='utf-8') as f:
                json.dump(self.admins, f, indent=2)
        except Exception as e:
            print(f"Admin kaydetme hatası: {e}")
    
    def save_settings(self):
        """Ayarları kaydet"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Ayarlar kaydetme hatası: {e}")
    
    def is_admin(self, user_id: int) -> bool:
        """Kullanıcı admin mi kontrol et"""
        return user_id in self.admins or user_id == self.SUPER_ADMIN_ID
    
    def is_super_admin(self, user_id: int) -> bool:
        """Kullanıcı süper admin (kurucu) mi kontrol et"""
        return user_id == self.SUPER_ADMIN_ID
    
    def add_admin(self, user_id: int) -> bool:
        """Yeni admin ekle"""
        if user_id not in self.admins and user_id != self.SUPER_ADMIN_ID:
            self.admins.append(user_id)
            self.save_admins()
            return True
        return False
    
    def remove_admin(self, user_id: int) -> bool:
        """Admin yetkisini kaldır"""
        # Süper admin'i kimse çıkaramaz
        if user_id == self.SUPER_ADMIN_ID:
            return False
        
        if user_id in self.admins and len(self.admins) > 1:  # En az 1 admin kalmalı
            self.admins.remove(user_id)
            self.save_admins()
            return True
        return False
    
    def log_user_activity(self, user_id: int, action: str):
        """Kullanıcı aktivitesini kaydet"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        if today not in self.stats['daily_stats']:
            self.stats['daily_stats'][today] = {
                'users': set(),
                'downloads': 0,
                'gui_commands': 0,
                'total_commands': 0
            }
        
        # Set'i listeye çevir (JSON serialization için)
        if 'users' in self.stats['daily_stats'][today]:
            self.stats['daily_stats'][today]['users'] = list(self.stats['daily_stats'][today]['users'])
        
        self.stats['daily_stats'][today]['users'].append(user_id)
        self.stats['daily_stats'][today]['total_commands'] += 1
        
        # Komut kullanımını say
        if action not in self.stats['command_usage']:
            self.stats['command_usage'][action] = 0
        self.stats['command_usage'][action] += 1
        
        # Kullanıcı aktivitesini kaydet
        if user_id not in self.stats['user_activity']:
            self.stats['user_activity'][user_id] = {
                'first_seen': time.time(),
                'last_seen': time.time(),
                'total_commands': 0,
                'downloads': 0
            }
        
        self.stats['user_activity'][user_id]['last_seen'] = time.time()
        self.stats['user_activity'][user_id]['total_commands'] += 1
        
        if 'download' in action.lower():
            self.stats['user_activity'][user_id]['downloads'] += 1
            self.stats['total_downloads'] += 1
        
        self.save_stats()
    
    def get_admin_stats(self) -> str:
        """Admin istatistiklerini al"""
        uptime = time.time() - self.stats['start_time']
        uptime_str = str(timedelta(seconds=int(uptime)))
        
        # Bugünkü istatistikler
        today = datetime.now().strftime('%Y-%m-%d')
        today_stats = self.stats['daily_stats'].get(today, {})
        
        # En aktif kullanıcılar
        top_users = sorted(
            self.stats['user_activity'].items(),
            key=lambda x: x[1]['total_commands'],
            reverse=True
        )[:5]
        
        # En çok kullanılan komutlar
        top_commands = sorted(
            self.stats['command_usage'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        stats_text = f"""
👑 **ADMIN İSTATİSTİKLERİ** 👑

📊 **Genel Bilgiler:**
• Toplam Kullanıcı: {len(self.stats['user_activity'])}
• Toplam İndirme: {self.stats['total_downloads']}
• Bot Çalışma Süresi: {uptime_str}
• Admin Sayısı: {len(self.admins)}

📅 **Bugünkü İstatistikler:**
• Aktif Kullanıcı: {len(set(today_stats.get('users', [])))}
• Komut Sayısı: {today_stats.get('total_commands', 0)}
• İndirme Sayısı: {today_stats.get('downloads', 0)}

👥 **En Aktif Kullanıcılar:**
"""
        
        for i, (user_id, data) in enumerate(top_users, 1):
            stats_text += f"{i}. User {user_id}: {data['total_commands']} komut\n"
        
        stats_text += "\n🔥 **En Çok Kullanılan Komutlar:**\n"
        for i, (command, count) in enumerate(top_commands, 1):
            stats_text += f"{i}. {command}: {count} kez\n"
        
        return stats_text
    
    def ban_user(self, user_id: int) -> bool:
        """Kullanıcıyı banla"""
        if user_id not in self.settings['banned_users']:
            self.settings['banned_users'].append(user_id)
            self.save_settings()
            return True
        return False
    
    def unban_user(self, user_id: int) -> bool:
        """Kullanıcının banını kaldır"""
        if user_id in self.settings['banned_users']:
            self.settings['banned_users'].remove(user_id)
            self.save_settings()
            return True
        return False
    
    def is_user_banned(self, user_id: int) -> bool:
        """Kullanıcı banlı mı kontrol et"""
        return user_id in self.settings['banned_users']
    
    def get_user_list(self) -> str:
        """Kullanıcı listesini al"""
        if not self.stats['user_activity']:
            return "📝 Henüz hiç kullanıcı yok."
        
        user_text = "👥 **KULLANICI LİSTESİ** 👥\n\n"
        
        for user_id, data in list(self.stats['user_activity'].items())[:20]:  # İlk 20 kullanıcı
            last_seen = datetime.fromtimestamp(data['last_seen']).strftime('%d.%m.%Y %H:%M')
            user_text += f"🆔 {user_id}\n"
            user_text += f"   📊 {data['total_commands']} komut, {data['downloads']} indirme\n"
            user_text += f"   🕒 Son görülme: {last_seen}\n\n"
        
        return user_text
    
    def get_settings(self) -> str:
        """Mevcut ayarları göster"""
        settings_text = """
⚙️ **BOT AYARLARI** ⚙️

📁 **Dosya Ayarları:**
• Max Dosya Boyutu: {max_file_size} MB
• İzinli Formatlar: {allowed_formats}
• Otomatik Temizlik: {auto_delete_temp}

🚦 **Kısıtlamalar:**
• Dakika Başına Limit: {rate_limit_per_minute}
• Bakım Modu: {maintenance_mode}
• Banlı Kullanıcı Sayısı: {banned_count}

🎛️ **Özellik Bayrakları:**
• Video İndirme: {video_download}
• GUI Kontrol: {gui_control}
• Ekran Görüntüsü: {screenshot}
• Admin Paneli: {admin_panel}
        """.format(
            max_file_size=self.settings['max_file_size'] // (1024*1024),
            allowed_formats=', '.join(self.settings['allowed_formats']),
            auto_delete_temp='✅' if self.settings['auto_delete_temp'] else '❌',
            rate_limit_per_minute=self.settings['rate_limit_per_minute'],
            maintenance_mode='✅' if self.settings['maintenance_mode'] else '❌',
            banned_count=len(self.settings['banned_users']),
            video_download='✅' if self.settings['feature_flags']['video_download'] else '❌',
            gui_control='✅' if self.settings['feature_flags']['gui_control'] else '❌',
            screenshot='✅' if self.settings['feature_flags']['screenshot'] else '❌',
            admin_panel='✅' if self.settings['feature_flags']['admin_panel'] else '❌'
        )
        
        return settings_text
    
    def update_setting(self, setting_key: str, value: Any) -> bool:
        """Ayar güncelle"""
        try:
            if '.' in setting_key:
                # Nested setting (örn: feature_flags.gui_control)
                keys = setting_key.split('.')
                current = self.settings
                for key in keys[:-1]:
                    current = current[key]
                current[keys[-1]] = value
            else:
                self.settings[setting_key] = value
            
            self.save_settings()
            return True
        except Exception as e:
            print(f"Ayar güncelleme hatası: {e}")
            return False
    
    def clean_all_data(self) -> str:
        """Tüm verileri temizle"""
        try:
            # İstatistikleri sıfırla
            self.stats = {
                'total_users': 0,
                'total_downloads': 0,
                'total_gui_commands': 0,
                'start_time': time.time(),
                'daily_stats': {},
                'user_activity': {},
                'command_usage': {},
                'errors': []
            }
            self.save_stats()
            
            # Geçici dosyaları temizle
            import shutil
            temp_dirs = ['downloads', 'temp']
            cleaned_files = 0
            
            for temp_dir in temp_dirs:
                if os.path.exists(temp_dir):
                    for root, dirs, files in os.walk(temp_dir):
                        for file in files:
                            try:
                                os.remove(os.path.join(root, file))
                                cleaned_files += 1
                            except:
                                pass
            
            return f"🧹 **Temizlik tamamlandı!**\n🗑️ {cleaned_files} dosya silindi.\n📊 İstatistikler sıfırlandı."
            
        except Exception as e:
            return f"❌ Temizlik hatası: {e}"
    
    def restart_bot(self):
        """Bot'u yeniden başlat"""
        return "Bot yeniden başlatılıyor..."
    
    # Süper admin fonksiyonları
    def get_super_admin_info(self) -> str:
        """Süper admin bilgilerini getir"""
        return f"""👑 **SÜPER ADMIN BİLGİLERİ** 👑

🆔 **Süper Admin ID:** `{self.SUPER_ADMIN_ID}`
🔒 **Durum:** Kurucu (Kimse çıkaramaz)
⚡ **Yetkiler:** Tüm admin yetkileri + Süper admin yetkileri
🛡️ **Koruma:** Aktif (Silinemez)

📋 **Mevcut Adminler:**
{chr(10).join([f"• {admin_id}" for admin_id in self.admins])}

💡 **Süper Admin Komutları:**
`/super_admin_info` - Bu bilgileri göster
`/super_admin_promote USER_ID` - Kullanıcıyı süper admin yap
`/super_admin_demote USER_ID` - Süper admin yetkisini kaldır
`/super_admin_reset` - Admin sistemini sıfırla"""
    
    def promote_to_super_admin(self, user_id: int) -> str:
        """Kullanıcıyı süper admin yap (sadece mevcut süper admin yapabilir)"""
        if user_id == self.SUPER_ADMIN_ID:
            return "❌ Zaten süper adminsiniz!"
        
        # Yeni süper admin ID'sini güncelle
        self.SUPER_ADMIN_ID = user_id
        self.save_settings()
        
        return f"✅ Kullanıcı {user_id} süper admin yapıldı!\n👑 Artık kurucu yetkilerine sahip."
    
    def demote_from_super_admin(self, user_id: int) -> str:
        """Süper admin yetkisini kaldır (sadece kendisi yapabilir)"""
        if user_id != self.SUPER_ADMIN_ID:
            return "❌ Sadece kendinizi süper admin'den çıkarabilirsiniz!"
        
        return "❌ Kurucu süper admin'i çıkaramaz! Bu güvenlik önlemidir."
    
    def reset_admin_system(self) -> str:
        """Admin sistemini sıfırla (sadece süper admin yapabilir)"""
        # Sadece süper admin yapabilir
        self.admins = [self.SUPER_ADMIN_ID]  # Sadece süper admin kalsın
        self.save_admins()
        
        return f"""🔄 **Admin Sistemi Sıfırlandı!**

👑 **Süper Admin:** `{self.SUPER_ADMIN_ID}` (Değişmedi)
👥 **Adminler:** Sadece süper admin kaldı
🛡️ **Güvenlik:** Tüm admin yetkileri sıfırlandı

⚠️ **Dikkat:** Diğer tüm adminlerin yetkileri kaldırıldı!"""

# Global admin panel instance
admin_panel = AdminPanel()
