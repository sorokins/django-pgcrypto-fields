from django.db import migrations
from django.db.migrations import RunPython
from .mixins import PGPMixin


class PgCryptoDataMigration(migrations.Migration):
    """
    Encrypt and decrypt existing data when fields migrated to pgcrypto

    Usage:
    just inherit migration class from PgCryptoDataMigration:

    class Migration(PgCryptoDataMigration):
        ....
    """
    migration_data = {}

    def get_encrypted_fields(self):
        """
        Return [(model_name, field_name), ...]
        """
        operations = filter(
            lambda x: getattr(x, 'field', None) and isinstance(x.field, PGPMixin),
            self.operations
        )
        model_field_names = [(x.model_name, x.name) for x in operations]
        return model_field_names

    def get_decrypted_data(self, apps, schema_editor):
        """
        Collect not-encrypted data
        """
        for model_name, field_name in self.get_encrypted_fields():

            Model = apps.get_model(self.app_label, model_name)
            self.migration_data['%s.%s' % (self.app_label, model_name)] = \
                list(Model.objects.values_list('id', field_name))

    def encrypt_data(self, apps, schema_editor):
        """
        Update model
        """
        for model_name, field_name in self.get_encrypted_fields():
            Model = apps.get_model(self.app_label, model_name)

            for pk, value in self.migration_data['%s.%s' % (self.app_label, model_name)]:
                Model.objects.filter(id=pk).update(**{field_name: value})

    def __init__(self, name, app_label):
        super(PgCryptoDataMigration, self).__init__(name, app_label)
        self.operations = [RunPython(self.get_decrypted_data, self.encrypt_data), ] + \
                          self.operations + \
                          [RunPython(self.encrypt_data, self.get_decrypted_data), ]
