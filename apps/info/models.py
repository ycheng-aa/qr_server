from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models

# Create your models here.
import io
import qrcode
from apps.common.models import CommonInfoModel
from qr_server import settings


class Message(CommonInfoModel):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sent_messages')
    info = models.CharField(max_length=255, null=True, blank=True)
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='received_messages')
    qrcode = models.ImageField(upload_to='qrcode/%Y/%m/%d/', blank=True, null=True)

    def __str__(self):
        return u"{} to {}".format(self.sender, self.receiver)

    def generate_qr_code(self):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=6,
            border=0,
        )
        qr.add_data(self.info)
        qr.make(fit=True)

        img = qr.make_image()

        buffer = io.BytesIO()
        img.save(buffer)
        filename = 'info-%s.png' % self.id
        filebuffer = InMemoryUploadedFile(
            buffer, None, filename, 'image/png', None, None)
        self.qrcode.save(filename, filebuffer)
