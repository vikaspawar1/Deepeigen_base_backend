from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('course', '0005_order_no_of_installments'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='razorpay_order_id',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
    ]