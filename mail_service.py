
import imaplib
import email
from email.header import decode_header
from config import GMAIL_USER, GMAIL_PASSWORD, IMAP_SERVER, IMAP_PORT

# ============================================
# ФУНКЦИЯ 1: ПОДКЛЮЧЕНИЕ К GMAIL
# ============================================
def connect_to_gmail():
    """
    Подключается к Gmail по протоколу IMAP
    
    Возвращает:
        imaplib.IMAP4_SSL: Объект подключения к почте
        
    Вызывает исключение:
        Exception: Если ошибка подключения или аутентификации
    """
    try:
        # Создаем безопасное SSL подключение
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        
        # Авторизуемся с логином и паролем
        mail.login(GMAIL_USER, GMAIL_PASSWORD)
        
        # Выбираем папку входящие
        mail.select('inbox')
        
        return mail
        
    except imaplib.IMAP4.error as e:
        raise Exception(f"Ошибка аутентификации Gmail: {e}")
    except Exception as e:
        raise Exception(f"Ошибка подключения: {e}")

# ============================================
# ФУНКЦИЯ 2: ПОЛУЧЕНИЕ ПОСЛЕДНЕГО ПИСЬМА
# ============================================
def get_latest_email():
    """
    Получает последнее письмо из Gmail
    
    Возвращает:
        dict: Словарь с данными письма
            {
                'from': 'sender@example.com',
                'subject': 'Тема письма',
                'body': 'Текст письма',
                'date': 'Дата'
            }
        None: Если писем нет
        
    Вызывает исключение:
        Exception: Если ошибка подключения
    """
    mail = None
    try:
        # Шаг 1: Подключаемся к Gmail
        mail = connect_to_gmail()
        
        # Шаг 2: Ищем все письма в папке
        status, messages = mail.search(None, 'ALL')
        
        # Шаг 3: Получаем список ID всех писем
        mail_ids = messages[0].split()
        
        # Шаг 4: Проверяем - есть ли письма?
        if not mail_ids:
            return None
        
        # Шаг 5: Берем ID последнего письма
        latest_email_id = mail_ids[-1]
        
        # Шаг 6: Получаем данные письма
        status, msg_data = mail.fetch(latest_email_id, '(RFC822)')
        
        # Шаг 7: Парсим письмо
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                # Создаем объект письма из байтов
                msg = email.message_from_bytes(response_part[1])
                
                # Извлекаем отправителя
                from_header = msg.get('From', '')
                
                # Извлекаем тему
                subject_header = msg.get('Subject', '')
                # Декодируем тему (может быть в base64)
                subject = decode_email_header(subject_header)
                
                # Извлекаем дату
                date = msg.get('Date', '')
                
                # Извлекаем текст письма
                body = parse_email_body(msg)
                
                # Возвращаем данные
                return {
                    'from': from_header,
                    'subject': subject,
                    'body': body,
                    'date': date
                }
        
        return None
        
    finally:
        # Всегда закрываем соединение
        if mail:
            try:
                mail.close()
                mail.logout()
            except:
                pass

# ============================================
# ФУНКЦИЯ 3: ПАРСИНГ ТЕЛА ПИСЬМА
# ============================================
def parse_email_body(msg):
    """
    Извлекает текст из сообщения
    
    Аргументы:
        msg: объект email.message.Message
        
    Возвращает:
        str: Текст письма
    """
    body = ""
    
    # Проверяем, является ли письмо multipart (состоит из частей)
    if msg.is_multipart():
        # Письмо состоит из нескольких частей (текст, HTML, вложения)
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get('Content-Disposition', ''))
            
            # Ищем текстовую часть (не вложение)
            if content_type == 'text/plain' and 'attachment' not in content_disposition:
                try:
                    # Получаем payload и декодируем
                    payload = part.get_payload(decode=True)
                    if payload:
                        # Пробуем разные кодировки
                        try:
                            body = payload.decode('utf-8')
                        except:
                            try:
                                body = payload.decode('latin-1')
                            except:
                                body = payload.decode('utf-8', errors='ignore')
                        break
                except Exception as e:
                    print(f"Ошибка декодирования части письма: {e}")
                    continue
    else:
        # Простое письмо (одна часть)
        try:
            payload = msg.get_payload(decode=True)
            if payload:
                try:
                    body = payload.decode('utf-8')
                except:
                    try:
                        body = payload.decode('latin-1')
                    except:
                        body = payload.decode('utf-8', errors='ignore')
        except Exception as e:
            print(f"Ошибка декодирования письма: {e}")
            body = ""
    
    return body

# ============================================
# ФУНКЦИЯ 4: ДЕКОДИРОВАНИЕ ЗАГОЛОВКОВ
# ============================================
def decode_email_header(header):
    """
    Декодирует заголовок письма (тема, отправитель)
    
    Аргументы:
        header: Строка заголовка
        
    Возвращает:
        str: Декодированная строка
    """
    if not header:
        return ""
    
    decoded_parts = decode_header(header)
    decoded_string = ""
    
    for part, encoding in decoded_parts:
        if isinstance(part, bytes):
            try:
                if encoding:
                    decoded_string += part.decode(encoding)
                else:
                    decoded_string += part.decode('utf-8', errors='ignore')
            except:
                decoded_string += part.decode('utf-8', errors='ignore')
        else:
            decoded_string += str(part)
    
    return decoded_string
