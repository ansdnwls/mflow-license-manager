import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.utils import formataddr

class EmailSender:
    def __init__(self, sender_email, sender_password, debug=False):
        self.sender_email = "y2k_woojin@naver.com"
        self.sender_password = "C8989EPPXB2V"
        self.debug = debug  # 디버깅 모드 활성화 여부

    def send_license_email(self, recipient_email, license_data, template):
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = formataddr(('Mflow License', self.sender_email))
            msg['To'] = recipient_email
            msg['Subject'] = Header('Mflow Paste 라이센스 발급', 'utf-8')

            # 🔍 디버깅: 데이터 확인
            print("라이센스 데이터:", license_data)
            
            # 템플릿의 플레이스홀더 치환 ({email}, {license_key}, {grade}, {expiry_date})
            email_content = template
            for key, value in license_data.items():
                placeholder = f"{{{key}}}"  # {license_key} 같은 단일 중괄호 사용
                email_content = email_content.replace(placeholder, str(value))


            print("변환된 이메일 내용:", email_content)  # 디버깅용 출력

            # HTML 여부 확인
            is_html = '<html' in email_content.lower() or '<body' in email_content.lower()
            text_part = MIMEText(email_content, 'html' if is_html else 'plain', 'utf-8')
            msg.attach(text_part)

            # SMTP 연결
            server = smtplib.SMTP_SSL('smtp.naver.com', 465)
            server.login(self.sender_email, self.sender_password)
            server.send_message(msg)
            server.quit()

            return True, f"{recipient_email}로 라이센스 정보가 성공적으로 발송되었습니다."

        except Exception as e:
            return False, f"이메일 발송 오류: {str(e)}"

