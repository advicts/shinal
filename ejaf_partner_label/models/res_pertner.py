from odoo.exceptions import UserError
from odoo import models, fields, api, _
from odoo.http import request
import qrcode, base64
from io import BytesIO

