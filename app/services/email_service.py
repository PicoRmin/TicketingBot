"""
سرویس ارسال ایمیل پیشرفته برای سیستم تیکتینگ
Email Service for sending notifications via SMTP
"""
from __future__ import annotations

import asyncio
import logging
from typing import List, Optional, Dict, Any
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime

import aiosmtplib
from jinja2 import Environment, FileSystemLoader, Template
from sqlalchemy.orm import Session

from app.config import settings
from app.core.enums import Language
from app.i18n.translator import translate

logger = logging.getLogger(__name__)

# تنظیمات Jinja2 برای قالب‌های ایمیل
template_env = Environment(
    loader=FileSystemLoader('app/templates/email'),
    autoescape=True,
    trim_blocks=True,
    lstrip_blocks=True
)


class EmailService:
    """
    کلاس سرویس ایمیل برای ارسال ایمیل‌های سیستم
    Email service class for sending system emails
    """
    
    def __init__(self):
        """مقداردهی اولیه سرویس ایمیل"""
        self.enabled = settings.EMAIL_ENABLED
        self.smtp_host = settings.EMAIL_SMTP_HOST
        self.smtp_port = settings.EMAIL_SMTP_PORT
        self.smtp_user = settings.EMAIL_SMTP_USER
        self.smtp_password = settings.EMAIL_SMTP_PASSWORD
        self.use_tls = settings.EMAIL_SMTP_USE_TLS
        self.use_ssl = settings.EMAIL_SMTP_USE_SSL
        self.from_address = settings.EMAIL_FROM_ADDRESS
        self.from_name = settings.EMAIL_FROM_NAME
        self.reply_to = settings.EMAIL_REPLY_TO
        self.bcc_addresses = self._parse_bcc_addresses(settings.EMAIL_BCC_ADDRESSES)
    
    def _parse_bcc_addresses(self, bcc_string: Optional[str]) -> List[str]:
        """
        تبدیل رشته BCC به لیست
        Parse BCC addresses string to list
        """
        if not bcc_string:
            return []
        return [addr.strip() for addr in bcc_string.split(",") if addr.strip()]
    
    async def _create_smtp_client(self) -> Optional[aiosmtplib.SMTP]:
        """
        ایجاد اتصال SMTP
        Create SMTP client connection
        """
        if not self.enabled:
            logger.debug("Email service is disabled")
            return None
        
        if not self.smtp_user or not self.smtp_password:
            logger.warning("SMTP credentials not configured")
            return None
        
        try:
            smtp = aiosmtplib.SMTP(
                hostname=self.smtp_host,
                port=self.smtp_port,
                use_tls=self.use_tls,
                start_tls=self.use_tls and not self.use_ssl
            )
            
            await smtp.connect()
            
            if self.use_ssl:
                await smtp.starttls()
            
            await smtp.login(self.smtp_user, self.smtp_password)
            
            return smtp
        except Exception as e:
            logger.error(f"Failed to connect to SMTP server: {e}", exc_info=True)
            return None
    
    async def _send_email(
        self,
        to_addresses: List[str],
        subject: str,
        html_body: str,
        text_body: Optional[str] = None,
        cc_addresses: Optional[List[str]] = None,
        attachments: Optional[List[Dict[str, Any]]] = None
    ) -> bool:
        """
        ارسال ایمیل
        Send email message
        
        Args:
            to_addresses: لیست آدرس‌های گیرنده
            subject: موضوع ایمیل
            html_body: محتوای HTML ایمیل
            text_body: محتوای متنی ایمیل (اختیاری)
            cc_addresses: لیست آدرس‌های CC (اختیاری)
            attachments: لیست فایل‌های پیوست (اختیاری)
        
        Returns:
            True if sent successfully, False otherwise
        """
        if not self.enabled:
            logger.debug("Email service is disabled; skipping email send")
            return False
        
        if not to_addresses:
            logger.warning("No recipient addresses provided")
            return False
        
        smtp = await self._create_smtp_client()
        if not smtp:
            return False
        
        try:
            # ایجاد پیام ایمیل
            message = MIMEMultipart('alternative')
            message['From'] = f"{self.from_name} <{self.from_address}>"
            message['To'] = ", ".join(to_addresses)
            message['Subject'] = subject
            message['Date'] = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S +0000')
            
            if self.reply_to:
                message['Reply-To'] = self.reply_to
            
            if cc_addresses:
                message['Cc'] = ", ".join(cc_addresses)
            
            # افزودن محتوای متنی
            if text_body:
                text_part = MIMEText(text_body, 'plain', 'utf-8')
                message.attach(text_part)
            
            # افزودن محتوای HTML
            html_part = MIMEText(html_body, 'html', 'utf-8')
            message.attach(html_part)
            
            # افزودن فایل‌های پیوست
            if attachments:
                for attachment in attachments:
                    try:
                        part = MIMEBase('application', 'octet-stream')
                        with open(attachment['path'], 'rb') as f:
                            part.set_payload(f.read())
                        encoders.encode_base64(part)
                        part.add_header(
                            'Content-Disposition',
                            f'attachment; filename= {attachment.get("filename", "attachment")}'
                        )
                        message.attach(part)
                    except Exception as e:
                        logger.error(f"Failed to attach file {attachment.get('path')}: {e}")
            
            # ارسال ایمیل
            recipients = to_addresses.copy()
            if cc_addresses:
                recipients.extend(cc_addresses)
            if self.bcc_addresses:
                recipients.extend(self.bcc_addresses)
            
            await smtp.send_message(message, recipients=recipients)
            
            logger.info(f"Email sent successfully to {', '.join(to_addresses)}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}", exc_info=True)
            return False
        finally:
            try:
                await smtp.quit()
            except Exception:
                pass
    
    def _render_template(
        self,
        template_name: str,
        language: Language,
        context: Dict[str, Any]
    ) -> str:
        """
        رندر کردن قالب ایمیل
        Render email template
        
        Args:
            template_name: نام فایل قالب (بدون پسوند)
            language: زبان قالب (FA یا EN)
            context: داده‌های قالب
        
        Returns:
            محتوای HTML رندر شده
        """
        try:
            # نام فایل قالب بر اساس زبان
            template_file = f"{template_name}_{language.value}.html"
            template = template_env.get_template(template_file)
            return template.render(**context)
        except Exception as e:
            logger.error(f"Failed to render email template {template_name}: {e}", exc_info=True)
            # Fallback به قالب ساده
            return self._create_simple_html(context.get('title', ''), context.get('content', ''))
    
    def _create_simple_html(self, title: str, content: str) -> str:
        """
        ایجاد قالب HTML ساده در صورت خطا
        Create simple HTML template as fallback
        """
        return f"""
        <!DOCTYPE html>
        <html dir="rtl" lang="fa">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{title}</title>
        </head>
        <body style="font-family: Tahoma, Arial, sans-serif; direction: rtl; text-align: right;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2>{title}</h2>
                <div>{content}</div>
            </div>
        </body>
        </html>
        """
    
    async def send_ticket_created_email(
        self,
        to_email: str,
        ticket_number: str,
        ticket_title: str,
        ticket_category: str,
        language: Language = Language.FA
    ) -> bool:
        """
        ارسال ایمیل ایجاد تیکت
        Send ticket created notification email
        
        Args:
            to_email: آدرس ایمیل گیرنده
            ticket_number: شماره تیکت
            ticket_title: عنوان تیکت
            ticket_category: دسته‌بندی تیکت
            language: زبان ایمیل
        
        Returns:
            True if sent successfully
        """
        subject = translate("emails.ticket_created.subject", language) or (
            "تیکت جدید ایجاد شد" if language == Language.FA else "New Ticket Created"
        )
        
        context = {
            'ticket_number': ticket_number,
            'ticket_title': ticket_title,
            'ticket_category': ticket_category,
            'app_name': settings.APP_NAME,
            'support_url': f"{settings.API_BASE_URL}/user-portal"
        }
        
        html_body = self._render_template('ticket_created', language, context)
        
        return await self._send_email(
            to_addresses=[to_email],
            subject=subject,
            html_body=html_body
        )
    
    async def send_ticket_status_changed_email(
        self,
        to_email: str,
        ticket_number: str,
        ticket_title: str,
        previous_status: str,
        new_status: str,
        language: Language = Language.FA
    ) -> bool:
        """
        ارسال ایمیل تغییر وضعیت تیکت
        Send ticket status changed notification email
        """
        subject = translate("emails.ticket_status_changed.subject", language) or (
            "وضعیت تیکت تغییر کرد" if language == Language.FA else "Ticket Status Changed"
        )
        
        context = {
            'ticket_number': ticket_number,
            'ticket_title': ticket_title,
            'previous_status': previous_status,
            'new_status': new_status,
            'app_name': settings.APP_NAME,
            'ticket_url': f"{settings.API_BASE_URL}/user-tickets/{ticket_number}"
        }
        
        html_body = self._render_template('ticket_status_changed', language, context)
        
        return await self._send_email(
            to_addresses=[to_email],
            subject=subject,
            html_body=html_body
        )
    
    async def send_ticket_assigned_email(
        self,
        to_email: str,
        ticket_number: str,
        ticket_title: str,
        assigned_by: str,
        language: Language = Language.FA
    ) -> bool:
        """
        ارسال ایمیل تخصیص تیکت
        Send ticket assigned notification email
        """
        subject = translate("emails.ticket_assigned.subject", language) or (
            "تیکت به شما تخصیص داده شد" if language == Language.FA else "Ticket Assigned to You"
        )
        
        context = {
            'ticket_number': ticket_number,
            'ticket_title': ticket_title,
            'assigned_by': assigned_by,
            'app_name': settings.APP_NAME,
            'ticket_url': f"{settings.API_BASE_URL}/tickets/{ticket_number}"
        }
        
        html_body = self._render_template('ticket_assigned', language, context)
        
        return await self._send_email(
            to_addresses=[to_email],
            subject=subject,
            html_body=html_body
        )
    
    async def send_comment_added_email(
        self,
        to_email: str,
        ticket_number: str,
        ticket_title: str,
        comment_author: str,
        comment_text: str,
        language: Language = Language.FA
    ) -> bool:
        """
        ارسال ایمیل افزودن کامنت
        Send comment added notification email
        """
        subject = translate("emails.comment_added.subject", language) or (
            "پیام جدید در تیکت" if language == Language.FA else "New Comment on Ticket"
        )
        
        context = {
            'ticket_number': ticket_number,
            'ticket_title': ticket_title,
            'comment_author': comment_author,
            'comment_text': comment_text,
            'app_name': settings.APP_NAME,
            'ticket_url': f"{settings.API_BASE_URL}/user-tickets/{ticket_number}"
        }
        
        html_body = self._render_template('comment_added', language, context)
        
        return await self._send_email(
            to_addresses=[to_email],
            subject=subject,
            html_body=html_body
        )
    
    async def send_sla_warning_email(
        self,
        to_email: str,
        ticket_number: str,
        ticket_title: str,
        warning_type: str,  # 'response' or 'resolution'
        remaining_time: str,
        language: Language = Language.FA
    ) -> bool:
        """
        ارسال ایمیل هشدار SLA
        Send SLA warning notification email
        """
        subject = translate("emails.sla_warning.subject", language) or (
            "هشدار SLA" if language == Language.FA else "SLA Warning"
        )
        
        context = {
            'ticket_number': ticket_number,
            'ticket_title': ticket_title,
            'warning_type': warning_type,
            'remaining_time': remaining_time,
            'app_name': settings.APP_NAME,
            'ticket_url': f"{settings.API_BASE_URL}/tickets/{ticket_number}"
        }
        
        html_body = self._render_template('sla_warning', language, context)
        
        return await self._send_email(
            to_addresses=[to_email],
            subject=subject,
            html_body=html_body
        )
    
    async def send_sla_breach_email(
        self,
        to_email: str,
        ticket_number: str,
        ticket_title: str,
        breach_type: str,  # 'response' or 'resolution'
        delay_time: str,
        language: Language = Language.FA
    ) -> bool:
        """
        ارسال ایمیل نقض SLA
        Send SLA breach notification email
        """
        subject = translate("emails.sla_breach.subject", language) or (
            "نقض SLA" if language == Language.FA else "SLA Breach"
        )
        
        context = {
            'ticket_number': ticket_number,
            'ticket_title': ticket_title,
            'breach_type': breach_type,
            'delay_time': delay_time,
            'app_name': settings.APP_NAME,
            'ticket_url': f"{settings.API_BASE_URL}/tickets/{ticket_number}"
        }
        
        html_body = self._render_template('sla_breach', language, context)
        
        return await self._send_email(
            to_addresses=[to_email],
            subject=subject,
            html_body=html_body
        )
    
    async def send_custom_email(
        self,
        to_addresses: List[str],
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        cc_addresses: Optional[List[str]] = None,
        attachments: Optional[List[Dict[str, Any]]] = None
    ) -> bool:
        """
        ارسال ایمیل سفارشی
        Send custom email message
        
        Args:
            to_addresses: لیست آدرس‌های گیرنده
            subject: موضوع ایمیل
            html_content: محتوای HTML
            text_content: محتوای متنی (اختیاری)
            cc_addresses: لیست آدرس‌های CC (اختیاری)
            attachments: لیست فایل‌های پیوست (اختیاری)
        
        Returns:
            True if sent successfully
        """
        return await self._send_email(
            to_addresses=to_addresses,
            subject=subject,
            html_body=html_content,
            text_body=text_content,
            cc_addresses=cc_addresses,
            attachments=attachments
        )


# نمونه سراسری سرویس ایمیل
email_service = EmailService()

