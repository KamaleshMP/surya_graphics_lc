from odoo import models, fields, api


class TemplatesEdit(models.Model):
    _name = "temp.database"
    _description = "Storge all templates messages."
    _order = "type"

    name = fields.Char(string="Templates name", required=True)
    type = fields.Many2one("type.temp.database", ondelete="restrict")
    color = fields.Char(compute="_color_pick")

    template = fields.Text(string="Message", required=True)

    _sql_constraints = [
        ('name', 'unique (name)', 'The name already Exists!'),
    ]

    @api.depends("type")
    def _color_pick(self):
        for rec in self:
            rec.color = rec.type.color

    def copy(self, default=None):
        if default is None:
            default = {}

        if not default.get('name'):
            default['name'] = f"{self.name} (copy)"

        return super(TemplatesEdit, self).copy(default)

    def name_get(self):
        names = []
        for rec in self:
            if type(rec.type.name) == bool:
                type_handle = 1000
            else:
                type_handle = rec.type.handle
            names.append((rec.id, type_handle, rec.type.name, rec.name))

        names = sorted(names, key=lambda x: x[1])

        result = []
        for name in names:
            n = f"[{name[2]}] {name[3]}" if name[1] != 1000 else name[3]
            result.append((name[0], n))

        return result
