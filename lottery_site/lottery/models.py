from django.db import models


class Prize(models.Model):
    name = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField()
    order = models.PositiveIntegerField()
    remaining = models.PositiveIntegerField()

    def __str__(self):
        return self.name

    # 在保存时设置 `order`
    def save(self, *args, **kwargs):
        if not self.order:
            # 查找当前最大值并加 1 作为新的 order
            max_order = Prize.objects.aggregate(models.Max('order'))['order__max']
            self.order = max_order + 1 if max_order else 1
        super().save(*args, **kwargs)


class Participant(models.Model):
    name = models.CharField(max_length=100)  # 参赛者姓名

    def __str__(self):
        return self.name


class Winner(models.Model):
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)
    prize = models.ForeignKey(Prize, on_delete=models.CASCADE)
    draw_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.prize.name} - {self.participant.name}"