from django.db import migrations


IF_SUPERUSER = """
DO $$
DECLARE
  is_super BOOLEAN;
BEGIN
  is_super := (SELECT USESUPER FROM pg_user WHERE usename = CURRENT_USER);
  IF is_super THEN
    {}
  END IF;
END $$;
"""

CREATE_EXTENSION = IF_SUPERUSER.format(
    'CREATE EXTENSION IF NOT EXISTS pgcrypto;'
)
DROP_EXTENSION = IF_SUPERUSER.format('DROP EXTENSION pgcrypto;')



class Migration(migrations.Migration):

    dependencies = []

    operations = [
        migrations.RunSQL(CREATE_EXTENSION, DROP_EXTENSION),
    ]
