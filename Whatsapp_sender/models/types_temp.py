from odoo import models, fields, api


class TypeTemplatesEdit(models.Model):
    _name = "type.temp.database"
    _description = "types of the templates"

    name = fields.Char(string="Name")
    color = fields.Selection([
        ("red", "Red"),
        ("blue", "Blue"),
        ("purple", "Purple"),
        ("green", "Green"),
        ("brown", "Brown")
    ], string="Color")

    handle = fields.Integer()
