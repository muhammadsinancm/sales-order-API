from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("suppliers", "0005_fix_rfqitem_schema"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                ALTER TABLE suppliers_rfqitem
                DROP COLUMN product;

                ALTER TABLE suppliers_rfqitem
                RENAME COLUMN ntes TO notes;

                ALTER TABLE suppliers_rfqitem
                ADD COLUMN product_id bigint NOT NULL;

                ALTER TABLE suppliers_rfqitem
                ADD CONSTRAINT suppliers_rfqitem_product_id_fk
                FOREIGN KEY (product_id)
                REFERENCES products_product (id)
                DEFERRABLE INITIALLY DEFERRED;
            """,
            reverse_sql="""
                ALTER TABLE suppliers_rfqitem
                DROP CONSTRAINT suppliers_rfqitem_product_id_fk;

                ALTER TABLE suppliers_rfqitem
                DROP COLUMN product_id;

                ALTER TABLE suppliers_rfqitem
                RENAME COLUMN notes TO ntes;

                ALTER TABLE suppliers_rfqitem
                ADD COLUMN product VARCHAR(255);
            """,
        ),
    ]