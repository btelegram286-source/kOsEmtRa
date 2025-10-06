import os
import logging

logger = logging.getLogger(__name__)

def find_downloaded_file(original_file_path, logger_context=""):
    """
    İndirilen dosyayı farklı konumlarda arar
    """
    logger.info(f"{logger_context} - Aranan dosya: {original_file_path}")
    
    # Dosya varsa direkt dön
    if os.path.exists(original_file_path):
        logger.info(f"{logger_context} - Dosya bulundu: {original_file_path}")
        return original_file_path
    
    # Dosya yoksa farklı yolları dene
    base_name = os.path.basename(original_file_path)
    logger.warning(f"{logger_context} - Dosya bulunamadı: {original_file_path}")
    
    # 1. /tmp klasöründe ara
    tmp_file = f"/tmp/{base_name}"
    if os.path.exists(tmp_file):
        logger.info(f"✅ {logger_context} - Dosya /tmp'de bulundu: {tmp_file}")
        return tmp_file
    
    # 2. Mevcut dizinde ara
    current_dir_file = os.path.join(os.getcwd(), base_name)
    if os.path.exists(current_dir_file):
        logger.info(f"✅ {logger_context} - Dosya mevcut dizinde bulundu: {current_dir_file}")
        return current_dir_file
    
    # 3. Tüm olası uzantıları dene
    possible_extensions = ['.mp3', '.m4a', '.webm', '.mp4']
    for ext in possible_extensions:
        test_file = original_file_path.rsplit('.', 1)[0] + ext
        if os.path.exists(test_file):
            logger.info(f"✅ {logger_context} - Dosya farklı uzantıyla bulundu: {test_file}")
            return test_file
    
    # 4. /tmp klasöründe en son MP3 dosyasını bul
    try:
        tmp_files = os.listdir('/tmp')
        mp3_files = [f for f in tmp_files if f.endswith('.mp3')]
        if mp3_files:
            latest_file = max(mp3_files, key=lambda x: os.path.getctime(os.path.join('/tmp', x)))
            latest_path = f"/tmp/{latest_file}"
            logger.info(f"✅ {logger_context} - En son MP3 dosyası bulundu: {latest_path}")
            return latest_path
    except Exception as e:
        logger.error(f"{logger_context} - /tmp klasörü listelenemedi: {e}")
    
    # 5. Mevcut dizinde en son MP3 dosyasını bul
    try:
        current_files = os.listdir(os.getcwd())
        mp3_files = [f for f in current_files if f.endswith('.mp3')]
        if mp3_files:
            latest_file = max(mp3_files, key=lambda x: os.path.getctime(os.path.join(os.getcwd(), x)))
            latest_path = os.path.join(os.getcwd(), latest_file)
            logger.info(f"✅ {logger_context} - En son MP3 dosyası mevcut dizinde bulundu: {latest_path}")
            return latest_path
    except Exception as e:
        logger.error(f"{logger_context} - Mevcut dizin listelenemedi: {e}")
    
    # Dosya bulunamadı
    raise Exception(f"{logger_context} - Dosya hiçbir yerde bulunamadı. Aranan: {original_file_path}")
