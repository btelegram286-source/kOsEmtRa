import os
import logging

logger = logging.getLogger(__name__)

def find_downloaded_file(original_file_path, logger_context=""):
    """
    İndirilen dosyayı farklı konumlarda arar - Render.com uyumlu
    """
    logger.info(f"{logger_context} - Aranan dosya: {original_file_path}")
    
    # Dosya varsa direkt dön
    if os.path.exists(original_file_path):
        logger.info(f"{logger_context} - Dosya bulundu: {original_file_path}")
        return original_file_path
    
    # Dosya yoksa farklı yolları dene
    base_name = os.path.basename(original_file_path)
    logger.warning(f"{logger_context} - Dosya bulunamadı: {original_file_path}")
    
    # 1. /tmp klasöründe ara (Render.com ana dizin)
    tmp_file = f"/tmp/{base_name}"
    if os.path.exists(tmp_file):
        logger.info(f"✅ {logger_context} - Dosya /tmp'de bulundu: {tmp_file}")
        return tmp_file
    
    # 2. Mevcut dizinde ara
    current_dir_file = os.path.join(os.getcwd(), base_name)
    if os.path.exists(current_dir_file):
        logger.info(f"✅ {logger_context} - Dosya mevcut dizinde bulundu: {current_dir_file}")
        return current_dir_file
    
    # 3. Render.com'da /opt/render/project/src/ dizininde ara
    render_file = f"/opt/render/project/src/{base_name}"
    if os.path.exists(render_file):
        logger.info(f"✅ {logger_context} - Dosya Render dizininde bulundu: {render_file}")
        return render_file
    
    # 4. Tüm olası uzantıları dene
    possible_extensions = ['.mp3', '.m4a', '.webm', '.mp4']
    for ext in possible_extensions:
        # Orijinal dosya adından uzantıyı çıkar
        base_without_ext = original_file_path.rsplit('.', 1)[0] if '.' in original_file_path else original_file_path
        test_file = base_without_ext + ext
        
        # Farklı konumlarda dene
        for test_path in [test_file, f"/tmp/{os.path.basename(test_file)}", f"/opt/render/project/src/{os.path.basename(test_file)}"]:
            if os.path.exists(test_path):
                logger.info(f"✅ {logger_context} - Dosya farklı uzantıyla bulundu: {test_path}")
                return test_path
    
    # 5. /tmp klasöründe en son MP3 dosyasını bul
    try:
        tmp_files = os.listdir('/tmp')
        mp3_files = [f for f in tmp_files if f.endswith('.mp3')]
        if mp3_files:
            latest_file = max(mp3_files, key=lambda x: os.path.getctime(os.path.join('/tmp', x)))
            latest_path = f"/tmp/{latest_file}"
            logger.info(f"✅ {logger_context} - En son MP3 dosyası /tmp'de bulundu: {latest_path}")
            return latest_path
    except Exception as e:
        logger.error(f"{logger_context} - /tmp klasörü listelenemedi: {e}")
    
    # 6. Mevcut dizinde en son MP3 dosyasını bul
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
    
    # 7. Render.com proje dizininde en son MP3 dosyasını bul
    try:
        render_files = os.listdir('/opt/render/project/src')
        mp3_files = [f for f in render_files if f.endswith('.mp3')]
        if mp3_files:
            latest_file = max(mp3_files, key=lambda x: os.path.getctime(os.path.join('/opt/render/project/src', x)))
            latest_path = f"/opt/render/project/src/{latest_file}"
            logger.info(f"✅ {logger_context} - En son MP3 dosyası Render dizininde bulundu: {latest_path}")
            return latest_path
    except Exception as e:
        logger.error(f"{logger_context} - Render dizin listelenemedi: {e}")
    
    # 8. YENİ: Tüm /tmp klasöründeki dosyaları listele ve en son indirileni bul
    try:
        tmp_files = os.listdir('/tmp')
        logger.info(f"📁 /tmp klasöründeki tüm dosyalar: {tmp_files}")
        
        # Tüm audio/video dosyalarını bul
        media_files = []
        for file in tmp_files:
            if any(file.lower().endswith(ext) for ext in ['.mp3', '.m4a', '.webm', '.mp4', '.wav', '.aac']):
                media_files.append(file)
        
        if media_files:
            # En son oluşturulan dosyayı bul
            latest_file = max(media_files, key=lambda x: os.path.getctime(os.path.join('/tmp', x)))
            latest_path = f"/tmp/{latest_file}"
            logger.info(f"✅ {logger_context} - En son medya dosyası /tmp'de bulundu: {latest_path}")
            return latest_path
    except Exception as e:
        logger.error(f"{logger_context} - /tmp klasörü detaylı listelenemedi: {e}")
    
    # 9. YENİ: Dosya adındaki özel karakterleri düzelt ve tekrar ara
    try:
        # Türkçe karakterleri düzelt
        corrected_name = base_name.replace('ı', 'i').replace('ğ', 'g').replace('ü', 'u').replace('ş', 's').replace('ö', 'o').replace('ç', 'c')
        corrected_path = f"/tmp/{corrected_name}"
        
        if os.path.exists(corrected_path):
            logger.info(f"✅ {logger_context} - Düzeltilmiş dosya adıyla bulundu: {corrected_path}")
            return corrected_path
    except Exception as e:
        logger.error(f"{logger_context} - Dosya adı düzeltme hatası: {e}")
    
    # Dosya bulunamadı
    raise Exception(f"{logger_context} - Dosya hiçbir yerde bulunamadı. Aranan: {original_file_path}")
