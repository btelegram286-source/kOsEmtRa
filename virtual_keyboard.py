#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
⌨️ Sanal Klavye Modülü
Telegram bot için tıklamalı sanal klavye özelliği
"""

from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Dict, Optional

class VirtualKeyboard:
    def __init__(self):
        """Sanal klavye sınıfını başlat"""
        self.current_text = ""
        self.caps_lock = False
        self.shift_pressed = False
        self.special_mode = False
        
        # Checkbox sistemi
        self.checkboxes = {}  # {id: {"text": "Metin", "checked": True/False}}
        self.checkbox_counter = 0
        
        # Not defteri sistemi
        self.notes = []  # [{"id": 1, "title": "Başlık", "content": "İçerik", "created": "tarih"}]
        self.note_counter = 0
        
        # Klavye düzenleri
        self.qwerty_layout = {
            'lower': [
                ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p'],
                ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l'],
                ['z', 'x', 'c', 'v', 'b', 'n', 'm']
            ],
            'upper': [
                ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
                ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
                ['Z', 'X', 'C', 'V', 'B', 'N', 'M']
            ]
        }
        
        self.turkish_layout = {
            'lower': [
                ['q', 'w', 'e', 'r', 't', 'y', 'u', 'ı', 'o', 'p', 'ğ', 'ü'],
                ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'ş', 'i'],
                ['z', 'x', 'c', 'v', 'b', 'n', 'm', 'ö', 'ç']
            ],
            'upper': [
                ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P', 'Ğ', 'Ü'],
                ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', 'Ş', 'İ'],
                ['Z', 'X', 'C', 'V', 'B', 'N', 'M', 'Ö', 'Ç']
            ]
        }
        
        self.numbers_layout = [
            ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'],
            ['-', '=', '[', ']', '\\', ';', "'", ',', '.', '/']
        ]
        
        self.symbols_layout = [
            ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')'],
            ['_', '+', '{', '}', '|', ':', '"', '<', '>', '?']
        ]
    
    def get_keyboard(self, layout_type: str = 'qwerty') -> InlineKeyboardMarkup:
        """Sanal klavye oluştur"""
        keyboard = []
        
        # Ana klavye düzeni
        if layout_type == 'turkish':
            layout = self.turkish_layout
        else:
            layout = self.qwerty_layout
        
        # Büyük/küçük harf durumuna göre layout seç
        current_layout = layout['upper'] if (self.caps_lock or self.shift_pressed) else layout['lower']
        
        # Harf tuşları
        for row in current_layout:
            keyboard_row = []
            for key in row:
                keyboard_row.append(
                    InlineKeyboardButton(key, callback_data=f"vk_key_{key}")
                )
            keyboard.append(keyboard_row)
        
        # Özel tuşlar
        special_row = [
            InlineKeyboardButton("⇧", callback_data="vk_shift"),
            InlineKeyboardButton("⌫", callback_data="vk_backspace"),
            InlineKeyboardButton("123", callback_data="vk_numbers"),
            InlineKeyboardButton("🌐", callback_data="vk_symbols"),
            InlineKeyboardButton("🔤", callback_data="vk_letters"),
            InlineKeyboardButton("Space", callback_data="vk_space"),
            InlineKeyboardButton("↵", callback_data="vk_enter")
        ]
        keyboard.append(special_row)
        
        # Kutucuklu alan tuşları
        checkbox_row = [
            InlineKeyboardButton("☑️ Kutucuk Ekle", callback_data="vk_checkbox_add"),
            InlineKeyboardButton("📋 Kutucuk Listesi", callback_data="vk_checkbox_list"),
            InlineKeyboardButton("✅ Seçili Kutucuklar", callback_data="vk_checkbox_checked")
        ]
        keyboard.append(checkbox_row)
        
        # Kontrol tuşları
        control_row = [
            InlineKeyboardButton("Caps", callback_data="vk_caps"),
            InlineKeyboardButton("Clear", callback_data="vk_clear"),
            InlineKeyboardButton("❌", callback_data="vk_close")
        ]
        keyboard.append(control_row)
        
        return InlineKeyboardMarkup(keyboard)
    
    def get_numbers_keyboard(self) -> InlineKeyboardMarkup:
        """Sayı klavyesi oluştur"""
        keyboard = []
        
        # Sayı tuşları
        for row in self.numbers_layout:
            keyboard_row = []
            for key in row:
                keyboard_row.append(
                    InlineKeyboardButton(key, callback_data=f"vk_key_{key}")
                )
            keyboard.append(keyboard_row)
        
        # Özel tuşlar
        special_row = [
            InlineKeyboardButton("⌫", callback_data="vk_backspace"),
            InlineKeyboardButton("🔤", callback_data="vk_letters"),
            InlineKeyboardButton("Space", callback_data="vk_space"),
            InlineKeyboardButton("↵", callback_data="vk_enter")
        ]
        keyboard.append(special_row)
        
        # Kutucuklu alan tuşları
        checkbox_row = [
            InlineKeyboardButton("☑️ Kutucuk Ekle", callback_data="vk_checkbox_add"),
            InlineKeyboardButton("📋 Kutucuk Listesi", callback_data="vk_checkbox_list"),
            InlineKeyboardButton("✅ Seçili Kutucuklar", callback_data="vk_checkbox_checked")
        ]
        keyboard.append(checkbox_row)
        
        # Kontrol tuşları
        control_row = [
            InlineKeyboardButton("Clear", callback_data="vk_clear"),
            InlineKeyboardButton("❌", callback_data="vk_close")
        ]
        keyboard.append(control_row)
        
        return InlineKeyboardMarkup(keyboard)
    
    def get_symbols_keyboard(self) -> InlineKeyboardMarkup:
        """Sembol klavyesi oluştur"""
        keyboard = []
        
        # Sembol tuşları
        for row in self.symbols_layout:
            keyboard_row = []
            for key in row:
                keyboard_row.append(
                    InlineKeyboardButton(key, callback_data=f"vk_key_{key}")
                )
            keyboard.append(keyboard_row)
        
        # Özel tuşlar
        special_row = [
            InlineKeyboardButton("⌫", callback_data="vk_backspace"),
            InlineKeyboardButton("🔤", callback_data="vk_letters"),
            InlineKeyboardButton("Space", callback_data="vk_space"),
            InlineKeyboardButton("↵", callback_data="vk_enter")
        ]
        keyboard.append(special_row)
        
        # Kutucuklu alan tuşları
        checkbox_row = [
            InlineKeyboardButton("☑️ Kutucuk Ekle", callback_data="vk_checkbox_add"),
            InlineKeyboardButton("📋 Kutucuk Listesi", callback_data="vk_checkbox_list"),
            InlineKeyboardButton("✅ Seçili Kutucuklar", callback_data="vk_checkbox_checked")
        ]
        keyboard.append(checkbox_row)
        
        # Kontrol tuşları
        control_row = [
            InlineKeyboardButton("Clear", callback_data="vk_clear"),
            InlineKeyboardButton("❌", callback_data="vk_close")
        ]
        keyboard.append(control_row)
        
        return InlineKeyboardMarkup(keyboard)
    
    def process_key(self, key: str) -> str:
        """Tuş işleme"""
        if key == "vk_shift":
            self.shift_pressed = not self.shift_pressed
            return self.current_text
        
        elif key == "vk_caps":
            self.caps_lock = not self.caps_lock
            return self.current_text
        
        elif key == "vk_backspace":
            if self.current_text:
                self.current_text = self.current_text[:-1]
            return self.current_text
        
        elif key == "vk_space":
            self.current_text += " "
            return self.current_text
        
        elif key == "vk_clear":
            self.current_text = ""
            return self.current_text
        
        elif key == "vk_enter":
            return self.current_text + "\n"
        
        elif key.startswith("vk_key_"):
            char = key[7:]  # "vk_key_" kısmını çıkar
            self.current_text += char
            return self.current_text
        
        return self.current_text
    
    def get_current_text(self) -> str:
        """Mevcut metni al"""
        return self.current_text
    
    def set_text(self, text: str):
        """Metni ayarla"""
        self.current_text = text
    
    def add_char(self, char: str):
        """Karakter ekle"""
        self.current_text += char
    
    def backspace(self):
        """Son karakteri sil"""
        if self.current_text:
            self.current_text = self.current_text[:-1]
    
    def clear(self):
        """Metni temizle"""
        self.current_text = ""
    
    def reset(self):
        """Klavyeyi sıfırla"""
        self.current_text = ""
        self.caps_lock = False
        self.shift_pressed = False
        self.special_mode = False
    
    def get_keyboard_by_type(self, keyboard_type: str) -> InlineKeyboardMarkup:
        """Klavye tipine göre klavye al"""
        if keyboard_type == "numbers":
            return self.get_numbers_keyboard()
        elif keyboard_type == "symbols":
            return self.get_symbols_keyboard()
        else:
            return self.get_keyboard()
    
    def get_quick_keyboard(self) -> InlineKeyboardMarkup:
        """Hızlı erişim klavyesi"""
        keyboard = [
            [
                InlineKeyboardButton("⚡ Hızlı İndirme", callback_data="vk_fast_download"),
                InlineKeyboardButton("🎵 MP3 İndir", callback_data="vk_mp3_download"),
                InlineKeyboardButton("📺 MP4 İndir", callback_data="vk_mp4_download")
            ],
            [
                InlineKeyboardButton("🔤 Harfler", callback_data="vk_letters"),
                InlineKeyboardButton("🔢 Sayılar", callback_data="vk_numbers"),
                InlineKeyboardButton("🌐 Semboller", callback_data="vk_symbols")
            ],
            [
                InlineKeyboardButton("🇹🇷 Türkçe", callback_data="vk_turkish"),
                InlineKeyboardButton("🇺🇸 English", callback_data="vk_english")
            ],
            [
                InlineKeyboardButton("☑️ Checkbox Alanı", callback_data="vk_checkbox_menu"),
                InlineKeyboardButton("📝 Not Defteri", callback_data="vk_notepad")
            ],
            [
                InlineKeyboardButton("👑 Admin Panel", callback_data="vk_admin_panel"),
                InlineKeyboardButton("📊 İstatistikler", callback_data="vk_stats")
            ],
            [
                InlineKeyboardButton("❌ Kapat", callback_data="vk_close")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def get_emoji_keyboard(self) -> InlineKeyboardMarkup:
        """Emoji klavyesi"""
        keyboard = [
            [
                InlineKeyboardButton("😀", callback_data="vk_emoji_😀"),
                InlineKeyboardButton("😂", callback_data="vk_emoji_😂"),
                InlineKeyboardButton("😍", callback_data="vk_emoji_😍"),
                InlineKeyboardButton("🤔", callback_data="vk_emoji_🤔"),
                InlineKeyboardButton("😎", callback_data="vk_emoji_😎")
            ],
            [
                InlineKeyboardButton("👍", callback_data="vk_emoji_👍"),
                InlineKeyboardButton("👎", callback_data="vk_emoji_👎"),
                InlineKeyboardButton("❤️", callback_data="vk_emoji_❤️"),
                InlineKeyboardButton("🔥", callback_data="vk_emoji_🔥"),
                InlineKeyboardButton("💯", callback_data="vk_emoji_💯")
            ],
            [
                InlineKeyboardButton("🎉", callback_data="vk_emoji_🎉"),
                InlineKeyboardButton("🎊", callback_data="vk_emoji_🎊"),
                InlineKeyboardButton("🎈", callback_data="vk_emoji_🎈"),
                InlineKeyboardButton("🎁", callback_data="vk_emoji_🎁"),
                InlineKeyboardButton("🎂", callback_data="vk_emoji_🎂")
            ],
            [
                InlineKeyboardButton("⌫", callback_data="vk_backspace"),
                InlineKeyboardButton("🔤", callback_data="vk_letters"),
                InlineKeyboardButton("Space", callback_data="vk_space"),
                InlineKeyboardButton("↵", callback_data="vk_enter")
            ],
            [
                InlineKeyboardButton("❌", callback_data="vk_close")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def process_emoji_key(self, emoji: str) -> str:
        """Emoji tuş işleme"""
        if emoji.startswith("vk_emoji_"):
            emoji_char = emoji[9:]  # "vk_emoji_" kısmını çıkar
            self.current_text += emoji_char
        return self.current_text
    
    def get_admin_keyboard(self):
        """Admin paneli klavyesi"""
        keyboard = [
            [
                InlineKeyboardButton("📊 İstatistikler", callback_data="vk_admin_stats"),
                InlineKeyboardButton("👥 Kullanıcılar", callback_data="vk_admin_users")
            ],
            [
                InlineKeyboardButton("⚙️ Ayarlar", callback_data="vk_admin_settings"),
                InlineKeyboardButton("🔄 Yeniden Başlat", callback_data="vk_admin_restart")
            ],
            [
                InlineKeyboardButton("🚫 Kullanıcı Engelle", callback_data="vk_admin_ban"),
                InlineKeyboardButton("✅ Kullanıcı Engeli Kaldır", callback_data="vk_admin_unban")
            ],
            [
                InlineKeyboardButton("🧹 Temizle", callback_data="vk_admin_clean"),
                InlineKeyboardButton("📝 Loglar", callback_data="vk_admin_logs")
            ],
            [
                InlineKeyboardButton("👑 Süper Admin Bilgileri", callback_data="vk_super_admin_info"),
                InlineKeyboardButton("🔄 Admin Sistemi Sıfırla", callback_data="vk_super_admin_reset")
            ],
            [
                InlineKeyboardButton("🔙 Ana Menü", callback_data="vk_main_menu"),
                InlineKeyboardButton("❌ Kapat", callback_data="vk_close")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def get_stats_keyboard(self) -> InlineKeyboardMarkup:
        """İstatistik klavyesi"""
        keyboard = [
            [
                InlineKeyboardButton("📈 Genel İstatistikler", callback_data="vk_stats_general"),
                InlineKeyboardButton("📊 Günlük İstatistikler", callback_data="vk_stats_daily")
            ],
            [
                InlineKeyboardButton("👥 Kullanıcı İstatistikleri", callback_data="vk_stats_users"),
                InlineKeyboardButton("📱 Platform İstatistikleri", callback_data="vk_stats_platforms")
            ],
            [
                InlineKeyboardButton("💾 Dosya İstatistikleri", callback_data="vk_stats_files"),
                InlineKeyboardButton("⏱️ Performans", callback_data="vk_stats_performance")
            ],
            [
                InlineKeyboardButton("🔙 Admin Panel", callback_data="vk_admin_panel"),
                InlineKeyboardButton("❌ Kapat", callback_data="vk_close")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def get_settings_keyboard(self) -> InlineKeyboardMarkup:
        """Ayarlar klavyesi"""
        keyboard = [
            [
                InlineKeyboardButton("🔧 Bot Ayarları", callback_data="vk_settings_bot"),
                InlineKeyboardButton("📁 Dosya Ayarları", callback_data="vk_settings_files")
            ],
            [
                InlineKeyboardButton("🎥 Video Ayarları", callback_data="vk_settings_video"),
                InlineKeyboardButton("🔊 Ses Ayarları", callback_data="vk_settings_audio")
            ],
            [
                InlineKeyboardButton("🛡️ Güvenlik", callback_data="vk_settings_security"),
                InlineKeyboardButton("📝 Bildirimler", callback_data="vk_settings_notifications")
            ],
            [
                InlineKeyboardButton("🔙 Admin Panel", callback_data="vk_admin_panel"),
                InlineKeyboardButton("❌ Kapat", callback_data="vk_close")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def get_user_management_keyboard(self) -> InlineKeyboardMarkup:
        """Kullanıcı yönetimi klavyesi"""
        keyboard = [
            [
                InlineKeyboardButton("👥 Tüm Kullanıcılar", callback_data="vk_users_all"),
                InlineKeyboardButton("🆕 Yeni Kullanıcılar", callback_data="vk_users_new")
            ],
            [
                InlineKeyboardButton("🚫 Engellenenler", callback_data="vk_users_banned"),
                InlineKeyboardButton("⭐ VIP Kullanıcılar", callback_data="vk_users_vip")
            ],
            [
                InlineKeyboardButton("🔍 Kullanıcı Ara", callback_data="vk_users_search"),
                InlineKeyboardButton("📊 Kullanıcı Detayları", callback_data="vk_users_details")
            ],
            [
                InlineKeyboardButton("🔙 Admin Panel", callback_data="vk_admin_panel"),
                InlineKeyboardButton("❌ Kapat", callback_data="vk_close")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def get_checkbox_keyboard(self) -> InlineKeyboardMarkup:
        """Checkbox klavyesi"""
        keyboard = [
            [
                InlineKeyboardButton("📝 Yeni Checkbox Ekle", callback_data="vk_checkbox_add"),
                InlineKeyboardButton("🗑️ Checkbox Sil", callback_data="vk_checkbox_delete")
            ],
            [
                InlineKeyboardButton("✅ Tümünü Seç", callback_data="vk_checkbox_select_all"),
                InlineKeyboardButton("❌ Tümünü Temizle", callback_data="vk_checkbox_clear_all")
            ],
            [
                InlineKeyboardButton("📋 Checkbox Listesi", callback_data="vk_checkbox_list"),
                InlineKeyboardButton("💾 Kaydet", callback_data="vk_checkbox_save")
            ],
            [
                InlineKeyboardButton("🔙 Ana Menü", callback_data="vk_main_menu"),
                InlineKeyboardButton("❌ Kapat", callback_data="vk_close")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def get_checkbox_list_keyboard(self) -> InlineKeyboardMarkup:
        """Checkbox listesi klavyesi"""
        keyboard = []
        
        if not self.checkboxes:
            keyboard.append([
                InlineKeyboardButton("📝 Henüz checkbox yok. Ekle!", callback_data="vk_checkbox_add")
            ])
        else:
            for checkbox_id, checkbox_data in self.checkboxes.items():
                text = checkbox_data["text"]
                checked = checkbox_data["checked"]
                status = "✅" if checked else "☐"
                
                keyboard.append([
                    InlineKeyboardButton(
                        f"{status} {text}", 
                        callback_data=f"vk_checkbox_toggle_{checkbox_id}"
                    )
                ])
        
        # Kontrol tuşları
        keyboard.append([
            InlineKeyboardButton("➕ Yeni Ekle", callback_data="vk_checkbox_add"),
            InlineKeyboardButton("🗑️ Seçilenleri Sil", callback_data="vk_checkbox_delete_selected")
        ])
        keyboard.append([
            InlineKeyboardButton("🔙 Checkbox Menü", callback_data="vk_checkbox_menu"),
            InlineKeyboardButton("❌ Kapat", callback_data="vk_close")
        ])
        
        return InlineKeyboardMarkup(keyboard)
    
    def add_checkbox(self, text: str) -> int:
        """Yeni checkbox ekle"""
        self.checkbox_counter += 1
        checkbox_id = self.checkbox_counter
        self.checkboxes[checkbox_id] = {
            "text": text,
            "checked": False
        }
        return checkbox_id
    
    def toggle_checkbox(self, checkbox_id: int) -> bool:
        """Checkbox durumunu değiştir"""
        if checkbox_id in self.checkboxes:
            self.checkboxes[checkbox_id]["checked"] = not self.checkboxes[checkbox_id]["checked"]
            return self.checkboxes[checkbox_id]["checked"]
        return False
    
    def delete_checkbox(self, checkbox_id: int) -> bool:
        """Checkbox sil"""
        if checkbox_id in self.checkboxes:
            del self.checkboxes[checkbox_id]
            return True
        return False
    
    def get_checked_checkboxes(self) -> List[Dict]:
        """Seçili checkbox'ları al"""
        return [
            {"id": cid, "text": data["text"]} 
            for cid, data in self.checkboxes.items() 
            if data["checked"]
        ]
    
    def select_all_checkboxes(self):
        """Tüm checkbox'ları seç"""
        for checkbox_id in self.checkboxes:
            self.checkboxes[checkbox_id]["checked"] = True
    
    def clear_all_checkboxes(self):
        """Tüm checkbox'ları temizle"""
        for checkbox_id in self.checkboxes:
            self.checkboxes[checkbox_id]["checked"] = False
    
    def get_checkbox_summary(self) -> str:
        """Checkbox özeti"""
        total = len(self.checkboxes)
        checked = len(self.get_checked_checkboxes())
        
        if total == 0:
            return "📝 Henüz checkbox yok"
        
        return f"📋 **Checkbox Özeti:**\n✅ Seçili: {checked}/{total}\n📝 Toplam: {total}"
    
    def reset_checkboxes(self):
        """Checkbox'ları sıfırla"""
        self.checkboxes = {}
        self.checkbox_counter = 0
    
    def get_notepad_keyboard(self) -> InlineKeyboardMarkup:
        """Not defteri klavyesi"""
        keyboard = [
            [
                InlineKeyboardButton("📝 Yeni Not", callback_data="vk_note_add"),
                InlineKeyboardButton("📋 Not Listesi", callback_data="vk_note_list")
            ],
            [
                InlineKeyboardButton("🔍 Not Ara", callback_data="vk_note_search"),
                InlineKeyboardButton("🗑️ Not Sil", callback_data="vk_note_delete")
            ],
            [
                InlineKeyboardButton("💾 Tümünü Kaydet", callback_data="vk_note_save_all"),
                InlineKeyboardButton("📤 Dışa Aktar", callback_data="vk_note_export")
            ],
            [
                InlineKeyboardButton("🔙 Ana Menü", callback_data="vk_main_menu"),
                InlineKeyboardButton("❌ Kapat", callback_data="vk_close")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def add_note(self, title: str, content: str = "") -> int:
        """Yeni not ekle"""
        self.note_counter += 1
        note_id = self.note_counter
        import datetime
        self.notes.append({
            "id": note_id,
            "title": title,
            "content": content,
            "created": datetime.datetime.now().strftime("%d.%m.%Y %H:%M")
        })
        return note_id
    
    def get_note(self, note_id: int) -> Optional[Dict]:
        """Not al"""
        for note in self.notes:
            if note["id"] == note_id:
                return note
        return None
    
    def update_note(self, note_id: int, title: str = None, content: str = None) -> bool:
        """Not güncelle"""
        for note in self.notes:
            if note["id"] == note_id:
                if title is not None:
                    note["title"] = title
                if content is not None:
                    note["content"] = content
                return True
        return False
    
    def delete_note(self, note_id: int) -> bool:
        """Not sil"""
        for i, note in enumerate(self.notes):
            if note["id"] == note_id:
                del self.notes[i]
                return True
        return False
    
    def search_notes(self, query: str) -> List[Dict]:
        """Not ara"""
        query = query.lower()
        results = []
        for note in self.notes:
            if (query in note["title"].lower() or 
                query in note["content"].lower()):
                results.append(note)
        return results
    
    def get_notes_summary(self) -> str:
        """Not özeti"""
        total = len(self.notes)
        if total == 0:
            return "📝 Henüz not yok"
        
        return f"📝 **Not Defteri Özeti:**\n📄 Toplam Not: {total}\n🕒 Son Güncelleme: {self.notes[-1]['created'] if self.notes else 'Yok'}"
    
    def reset_notes(self):
        """Not defterini sıfırla"""
        self.notes = []
        self.note_counter = 0

# Global instance
virtual_keyboard = VirtualKeyboard()

# Test fonksiyonu
def test_virtual_keyboard():
    """Sanal klavye testi"""
    vk = VirtualKeyboard()
    
    print("Sanal Klavye Testi:")
    print("1. QWERTY Klavye:")
    print(vk.get_keyboard())
    
    print("\n2. Türkçe Klavye:")
    print(vk.get_keyboard('turkish'))
    
    print("\n3. Sayı Klavyesi:")
    print(vk.get_numbers_keyboard())
    
    print("\n4. Sembol Klavyesi:")
    print(vk.get_symbols_keyboard())
    
    print("\n5. Emoji Klavyesi:")
    print(vk.get_emoji_keyboard())

if __name__ == "__main__":
    test_virtual_keyboard()
