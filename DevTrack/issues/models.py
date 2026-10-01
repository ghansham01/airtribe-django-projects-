"""
Issue tracker models.

Issue fields:
id - unique integer
title - short summary
description - full details
status - one of: open, in_progress, resolved, closed
priority - one of: low, medium, high, critical
reporter - the Reporter who filed this (stored as reporter_id in the DB)
created_at - timestamp, set automatically
"""

from django.db import models
from django.forms.models import model_to_dict


class BaseEntity:
      """
      Plain mixin (no ABC), so it doesn't clash with Django's ModelBase metaclass.
      Subclasses must implement validate().
      """

      def validate(self):
            raise NotImplementedError("Subclasses must implement validate()")

      def to_dict(self):
            return model_to_dict(self)


class Reporter(BaseEntity, models.Model):
      id = models.AutoField(primary_key=True)
      name = models.CharField(max_length=255)
      email = models.EmailField()
      team = models.CharField(max_length=255)

      def validate(self):
            if not self.name:
                  raise ValueError("Name cannot be empty")

            if "@" not in self.email:
                  raise ValueError("Invalid email")

      def save(self, *args, **kwargs):
            self.validate()
            super().save(*args, **kwargs)

      def __str__(self):
            return self.name


class Issue(BaseEntity, models.Model):
      ALLOWED_STATUSES = [
            "open",
            "in_progress",
            "resolved",
            "closed",
      ]

      ALLOWED_PRIORITIES = [
            "low",
            "medium",
            "high",
            "critical",
      ]

      id = models.AutoField(primary_key=True)
      title = models.CharField(max_length=255)
      description = models.TextField()
      status = models.CharField(
            max_length=50,
            choices=[(s, s) for s in ALLOWED_STATUSES],
            default="open",
      )
      priority = models.CharField(
            max_length=50,
            choices=[(p, p) for p in ALLOWED_PRIORITIES],
            default="medium",
      )
      # Django automatically exposes the raw ID as `issue.reporter_id`
      reporter = models.ForeignKey(Reporter, on_delete=models.CASCADE)
      created_at = models.DateTimeField(auto_now_add=True)

      def validate(self):
            if not self.title:
                  raise ValueError("Invalid title")

            if self.status not in self.ALLOWED_STATUSES:
                  raise ValueError("Invalid status")

            if self.priority not in self.ALLOWED_PRIORITIES:
                  raise ValueError("Invalid priority")

      def save(self, *args, **kwargs):
            self.validate()
            super().save(*args, **kwargs)

      def describe(self):
            return f"{self.title} [{self.status}]"

      def __str__(self):
            return self.describe()


class CriticalIssue(Issue):
      class Meta:
            proxy = True  # same table as Issue, only behavior differs

      def describe(self):
            return f"[URGENT] {self.title} — needs immediate attention"


class LowPriorityIssue(Issue):
      class Meta:
            proxy = True

      def describe(self):
            return f"{self.title} — low priority, handle when free"